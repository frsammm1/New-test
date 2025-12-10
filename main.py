#!/usr/bin/env python3
"""
EXTREME MODE BOT v2.0
32MB Chunks × 5 Queue = 160MB Buffer
Complete File Manipulation System
"""

import asyncio
try:
    import uvloop
    # We set the policy here, but we will apply it effectively when using asyncio.run
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.network import connection
from aiohttp import web

import config
from handlers import register_handlers

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
async def main():
    config.logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    config.logger.info("🚀 EXTREME MODE BOT v2.0 Starting...")
    config.logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    config.logger.info("⚡ Config: 32MB chunks × 5 queue = 160MB buffer")
    config.logger.info("📝 Features: File manipulation enabled")
    config.logger.info("🔥 Maximum speed + Smart controls")
    config.logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    config.logger.info("⚠️  WARNING: High RAM usage - Monitor closely!")
    config.logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    # --- EXTREME CLIENT SETUP ---
    # Initialize clients inside the event loop
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
    
    # Start clients
    await user_client.start()
    await bot_client.start(bot_token=config.BOT_TOKEN)
    
    # Register all handlers
    register_handlers(user_client, bot_client)
    
    # Start web server
    # We create a task for the web server so it runs in the background
    asyncio.create_task(start_web_server())
    
    config.logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    config.logger.info("✅ EXTREME MODE Active!")
    config.logger.info("🔥 Bot is ready for transfers!")
    config.logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    # Run bot
    await bot_client.run_until_disconnected()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
