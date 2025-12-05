import asyncio
import time
import math
import config
from utils import human_readable_size, time_formatter

async def progress_callback(current, total, start_time, file_name, status_msg):
    """Update progress with reduced frequency"""
    now = time.time()
    
    # Update every UPDATE_INTERVAL seconds
    if now - config.last_update_time < config.UPDATE_INTERVAL: 
        return 
    config.last_update_time = now
    
    percentage = current * 100 / total if total > 0 else 0
    time_diff = now - start_time
    speed = current / time_diff if time_diff > 0 else 0
    eta = (total - current) / speed if speed > 0 else 0
    
    filled = math.floor(percentage / 10)
    bar = "█" * filled + "░" * (10 - filled)
    
    try:
        await status_msg.edit(
            f"📦 **Transferring...**\n"
            f"📂 `{file_name[:30]}...`\n"
            f"**{bar} {round(percentage, 1)}%**\n"
            f"⚡ `{human_readable_size(speed)}/s` | ETA: `{time_formatter(eta)}`\n"
            f"💾 `{human_readable_size(current)} / {human_readable_size(total)}`"
        )
    except Exception as e:
        config.logger.debug(f"Progress update failed: {e}")

class ExtremeBufferedStream:
    """
    Optimized streaming with 8MB chunks and 2-queue buffer (16MB total)
    Perfect for Render free tier (512MB RAM)
    """
    def __init__(self, client, location, file_size, file_name, start_time, status_msg):
        self.client = client
        self.location = location
        self.file_size = file_size
        self.name = file_name
        self.start_time = start_time
        self.status_msg = status_msg
        self.current_bytes = 0
        
        # Optimized settings for free tier
        self.chunk_size = config.CHUNK_SIZE
        self.queue = asyncio.Queue(maxsize=config.QUEUE_SIZE)  # 16MB buffer
        
        self.downloader_task = None
        self.buffer = b""
        self.closed = False
        self._started = False
        
        config.logger.info(f"📦 Stream initialized: {file_name} ({human_readable_size(file_size)})")

    async def _start_download(self):
        """Start the download worker"""
        if self._started:
            return
        self._started = True
        self.downloader_task = asyncio.create_task(self._worker())

    async def _worker(self):
        """Background worker to download chunks"""
        try:
            config.logger.info(f"📥 Starting download: {self.name}")
            async for chunk in self.client.iter_download(
                self.location, 
                chunk_size=self.chunk_size,
                request_size=self.chunk_size
            ):
                if self.closed:
                    config.logger.info("Download worker: closed flag detected")
                    break
                    
                await self.queue.put(chunk)
                
            # Signal end of stream
            await self.queue.put(None)
            config.logger.info(f"✅ Download complete: {self.name}")
            
        except asyncio.CancelledError:
            config.logger.info("Download worker cancelled")
            await self.queue.put(None)
            
        except Exception as e:
            config.logger.error(f"⚠️ Download error: {e}")
            await self.queue.put(None)

    def __len__(self):
        return self.file_size

    async def read(self, size=-1):
        """Read data from stream"""
        # Start download on first read
        if not self._started:
            await self._start_download()
        
        if self.closed:
            return b""
            
        if size == -1: 
            size = self.chunk_size
            
        # Fill buffer to requested size
        while len(self.buffer) < size and not self.closed:
            try:
                chunk = await asyncio.wait_for(self.queue.get(), timeout=30.0)
                
                if chunk is None:
                    # End of stream
                    if self.current_bytes < self.file_size:
                        config.logger.warning(
                            f"⚠️ Incomplete transfer: {self.current_bytes}/{self.file_size} bytes"
                        )
                    self.closed = True
                    break
                
                self.buffer += chunk
                self.current_bytes += len(chunk)
                
                # Update progress (fire-and-forget)
                asyncio.create_task(progress_callback(
                    self.current_bytes, 
                    self.file_size, 
                    self.start_time, 
                    self.name,
                    self.status_msg
                ))
                
            except asyncio.TimeoutError:
                config.logger.error("❌ Download timeout")
                self.closed = True
                break
            except Exception as e:
                config.logger.error(f"Read error: {e}")
                self.closed = True
                break
            
        # Return requested data
        data = self.buffer[:size]
        self.buffer = self.buffer[size:]
        return data

    async def close(self):
        """Clean shutdown of stream"""
        if self.closed:
            return
            
        config.logger.info(f"🔒 Closing stream: {self.name}")
        self.closed = True
        
        # Cancel download task
        if self.downloader_task and not self.downloader_task.done():
            self.downloader_task.cancel()
            try:
                await asyncio.wait_for(self.downloader_task, timeout=2.0)
            except (asyncio.CancelledError, asyncio.TimeoutError):
                pass
        
        # Clear buffer
        self.buffer = b""
        
        # Drain queue
        while not self.queue.empty():
            try:
                self.queue.get_nowait()
            except:
                break
        
        config.logger.info(f"✅ Stream closed: {self.name}")
