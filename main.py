#!/usr/bin/env python3
"""
EXTREME MODE BOT v2.0
32MB Chunks × 5 Queue = 160MB Buffer
Complete File Manipulation System
"""

import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.network import connection
from aiohttp import web

import config
from handlers import register_handlers

# --- EXTREME CLIENT SETUP ---
user_client = TelegramClient(
    StringSession(config.STRING_SESSION), 
    config.API_ID, 
    config.API_HASH,
    connection=connection.ConnectionTcpFull,
    use_ipv6=False,
    connection_retries=None,
    flood_sleep_threshold=120,
    request_retries=20,
    auto_reconnect=True
)

bot_client = TelegramClient(
    'bot_session', 
    config.API_ID, 
    config.API_HASH,
    connection=connection.ConnectionTcpFull,
    use_ipv6=False,
    connection_retries=None,
    flood_sleep_threshold=120,
    request_retries=20,
    auto_reconnect=True
)

# --- WEB SERVER ---
async def handle(request):
    return web.Response(
        text="🔥 EXTREME MODE v2.0 - 32MB×5 Active | File Manipulation Enabled"
    )

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', config.PORT)
    await site.start()
    config.logger.info(f"⚡ EXTREME MODE Web Server - Port {config.PORT}")

# --- MAIN ---
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    
    config.logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    config.logger.info("🚀 EXTREME MODE BOT v2.0 Starting...")
    config.logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    config.logger.info("⚡ Config: 32MB chunks × 5 queue = 160MB buffer")
    config.logger.info("📝 Features: File manipulation enabled")
    config.logger.info("🔥 Maximum speed + Smart controls")
    config.logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    config.logger.info("⚠️  WARNING: High RAM usage - Monitor closely!")
    config.logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    # Start clients
    user_client.start()
    bot_client.start(bot_token=config.BOT_TOKEN)
    
    # Register all handlers
    register_handlers(user_client, bot_client)
    
    # Start web server
    loop.create_task(start_web_server())
    
    config.logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    config.logger.info("✅ EXTREME MODE Active!")
    config.logger.info("🔥 Bot is ready for transfers!")
    config.logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    # Run bot
    bot_client.run_until_disconnected()
