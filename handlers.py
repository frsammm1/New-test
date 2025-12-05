import asyncio
import uuid
from telethon import events
import config
from keyboards import (
    get_settings_keyboard, get_confirm_keyboard,
    get_skip_keyboard, get_clone_info_keyboard
)
from transfer import transfer_process

def register_handlers(user_client, bot_client):
    """Register all bot handlers - FIXED VERSION"""
    
    @bot_client.on(events.NewMessage(pattern='/start'))
    async def start_handler(event):
        await event.respond(
            "🚀 **File Transfer Bot v2.0**\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"⚡ Optimized for Free Tier\n"
            f"💾 Buffer: 16MB (8MB × 2)\n"
            f"🔥 Safe & Reliable\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "**Features:**\n"
            "✅ All file types support\n"
            "✅ Video → MP4 conversion\n"
            "✅ Filename manipulation\n"
            "✅ Caption manipulation\n\n"
            "**Commands:**\n"
            "`/clone SOURCE_ID DEST_ID` - Start transfer\n"
            "`/stats` - Bot statistics\n"
            "`/help` - Usage guide\n"
            "`/stop` - Stop transfer",
            buttons=get_clone_info_keyboard()
        )
    
    @bot_client.on(events.NewMessage(pattern='/help'))
    async def help_handler(event):
        await event.respond(
            "📚 **User Guide**\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "**Step 1:** Use `/clone` command\n"
            "`/clone -1001234567 -1009876543`\n\n"
            "**Step 2:** Configure (optional)\n"
            "• Filename Find & Replace\n"
            "• Caption Find & Replace\n"
            "• Add Extra Caption\n\n"
            "**Step 3:** Click '✅ Done'\n\n"
            "**Step 4:** Send message range\n"
            "`https://t.me/c/xxx/10 - https://t.me/c/xxx/20`\n\n"
            "**Tips:**\n"
            "• Get IDs using @userinfobot\n"
            "• Bot must be admin in destination\n"
            "• Use `/stop` to cancel transfer"
        )
    
    @bot_client.on(events.NewMessage(pattern='/clone'))
    async def clone_init(event):
        if config.is_running: 
            return await event.respond(
                "⚠️ **Transfer in progress!**\n"
                "Use `/stop` to cancel it first."
            )
        
        try:
            args = event.text.split()
            if len(args) < 3:
                raise ValueError("Need source and destination IDs")
            
            source_id = int(args[1])
            dest_id = int(args[2])
            
            # Validate IDs
            if source_id == dest_id:
                return await event.respond("❌ Source and destination cannot be same!")
            
            # Create session
            session_id = str(uuid.uuid4())
            config.active_sessions[session_id] = {
                'source': source_id,
                'dest': dest_id,
                'settings': {},
                'chat_id': event.chat_id,
                'step': 'settings'
            }
            
            await event.respond(
                f"✅ **Clone Setup**\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"📥 Source: `{source_id}`\n"
                f"📤 Destination: `{dest_id}`\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                f"Configure your settings below:\n"
                f"(All optional - click Done to skip)",
                buttons=get_settings_keyboard(session_id)
            )
            
        except ValueError:
            await event.respond(
                "❌ **Invalid Format**\n\n"
                "**Usage:**\n"
                "`/clone SOURCE_ID DEST_ID`\n\n"
                "**Example:**\n"
                "`/clone -1001234567890 -1009876543210`\n\n"
                "💡 Get IDs: @userinfobot"
            )
    
    @bot_client.on(events.CallbackQuery(pattern=b'clone_help'))
    async def clone_help_callback(event):
        await event.answer()
        await event.respond(
            "📖 **Clone Command Guide**\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "**Step 1:** Get IDs\n"
            "Forward any message from source/dest to @userinfobot\n\n"
            "**Step 2:** Run command\n"
            "`/clone -1001234 -1009876`\n\n"
            "**Step 3:** Configure (optional)\n"
            "Set filename/caption changes\n\n"
            "**Step 4:** Click 'Done'\n\n"
            "**Step 5:** Send range\n"
            "Two message links with '-' between\n\n"
            "That's it! Transfer starts automatically."
        )
    
    @bot_client.on(events.CallbackQuery(pattern=b'bot_stats'))
    async def stats_callback(event):
        await event.answer()
        await event.respond(
            f"📊 **Bot Statistics**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"⚡ Chunk Size: **8MB**\n"
            f"💾 Queue: **2 chunks**\n"
            f"📦 Buffer: **16MB**\n"
            f"📤 Upload Parts: **8MB**\n"
            f"🔄 Max Retries: **{config.MAX_RETRIES}**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🚀 Status: **{'🟢 Running' if config.is_running else '🔴 Idle'}**\n"
            f"📊 Sessions: **{len(config.active_sessions)}**"
        )
    
    @bot_client.on(events.CallbackQuery(pattern=r'set_fname_(.+)'))
    async def set_filename_callback(event):
        session_id = event.data.decode().split('_')[2]
        if session_id not in config.active_sessions:
            return await event.answer("❌ Session expired! Start over with /clone", alert=True)
        
        config.active_sessions[session_id]['step'] = 'fname_find'
        await event.edit(
            "📝 **Filename: Find Text**\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Type the text to FIND in filenames:\n\n"
            "Example: `S01E` or `720p`\n\n"
            "(Or click Skip)",
            buttons=get_skip_keyboard(session_id)
        )
    
    @bot_client.on(events.CallbackQuery(pattern=r'set_fcap_(.+)'))
    async def set_caption_find_callback(event):
        session_id = event.data.decode().split('_')[2]
        if session_id not in config.active_sessions:
            return await event.answer("❌ Session expired! Start over", alert=True)
        
        config.active_sessions[session_id]['step'] = 'cap_find'
        await event.edit(
            "💬 **Caption: Find Text**\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Type the text to FIND in captions:\n\n"
            "Example: `@OldChannel`\n\n"
            "(Or click Skip)",
            buttons=get_skip_keyboard(session_id)
        )
    
    @bot_client.on(events.CallbackQuery(pattern=r'set_xcap_(.+)'))
    async def set_extra_caption_callback(event):
        session_id = event.data.decode().split('_')[2]
        if session_id not in config.active_sessions:
            return await event.answer("❌ Session expired!", alert=True)
        
        config.active_sessions[session_id]['step'] = 'extra_cap'
        await event.edit(
            "➕ **Extra Caption**\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Type text to ADD at caption end:\n\n"
            "Example: `Join @MyChannel`\n\n"
            "(Or click Skip)",
            buttons=get_skip_keyboard(session_id)
        )
    
    @bot_client.on(events.CallbackQuery(pattern=r'skip_(.+)'))
    async def skip_callback(event):
        session_id = event.data.decode().split('_')[1]
        if session_id not in config.active_sessions:
            return await event.answer("❌ Session expired!", alert=True)
        
        config.active_sessions[session_id]['step'] = 'settings'
        await event.answer("⏭️ Skipped!")
        await event.edit(
            "✅ **Settings Menu**\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Configure your transfer:",
            buttons=get_settings_keyboard(session_id)
        )
    
    @bot_client.on(events.CallbackQuery(pattern=r'confirm_(.+)'))
    async def confirm_callback(event):
        session_id = event.data.decode().split('_')[1]
        if session_id not in config.active_sessions:
            return await event.answer("❌ Session expired!", alert=True)
        
        settings = config.active_sessions[session_id]['settings']
        settings_text, keyboard = get_confirm_keyboard(session_id, settings)
        
        await event.edit(
            f"🔍 **Review Your Settings**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{settings_text}"
            f"Ready to proceed?",
            buttons=keyboard
        )
    
    @bot_client.on(events.CallbackQuery(pattern=r'back_(.+)'))
    async def back_callback(event):
        session_id = event.data.decode().split('_')[1]
        if session_id not in config.active_sessions:
            return await event.answer("❌ Session expired!", alert=True)
        
        config.active_sessions[session_id]['step'] = 'settings'
        await event.edit(
            "✅ **Settings Menu**\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Configure your transfer:",
            buttons=get_settings_keyboard(session_id)
        )
    
    @bot_client.on(events.CallbackQuery(pattern=r'clear_(.+)'))
    async def clear_callback(event):
        session_id = event.data.decode().split('_')[1]
        if session_id not in config.active_sessions:
            return await event.answer("❌ Session expired!", alert=True)
        
        config.active_sessions[session_id]['settings'] = {}
        config.active_sessions[session_id]['step'] = 'settings'
        await event.answer("🗑️ Cleared!")
        await event.edit(
            "✅ **Settings Cleared**\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Configure again or click Done:",
            buttons=get_settings_keyboard(session_id)
        )
    
    @bot_client.on(events.CallbackQuery(pattern=r'start_(.+)'))
    async def start_transfer_callback(event):
        session_id = event.data.decode().split('_')[1]
        if session_id not in config.active_sessions:
            return await event.answer("❌ Session expired!", alert=True)
        
        config.active_sessions[session_id]['step'] = 'range'
        await event.edit(
            "📍 **Send Message Range**\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Send TWO message links like this:\n"
            "`link1 - link2`\n\n"
            "**Example:**\n"
            "`https://t.me/c/1234/10 - https://t.me/c/1234/20`\n\n"
            "**How to get links:**\n"
            "1. Open source channel\n"
            "2. Right-click on message\n"
            "3. Copy message link\n"
            "4. Do this for start & end messages\n"
            "5. Send both with '-' between them"
        )
    
    @bot_client.on(events.CallbackQuery(pattern=r'cancel_(.+)'))
    async def cancel_callback(event):
        session_id = event.data.decode().split('_')[1]
        if session_id in config.active_sessions:
            del config.active_sessions[session_id]
        await event.answer("❌ Cancelled!")
        await event.edit("❌ **Cancelled**\n\nUse `/clone` to start again.")
    
    @bot_client.on(events.CallbackQuery(pattern=b'stop_transfer'))
    async def stop_transfer_callback(event):
        if not config.is_running:
            return await event.answer("No transfer running!", alert=True)
        
        config.stop_flag = True
        config.is_running = False
        await event.answer("🛑 Stopping...", alert=True)
        
        if config.current_task and not config.current_task.done():
            config.current_task.cancel()
    
    @bot_client.on(events.NewMessage())
    async def message_handler(event):
        # Find active session
        session_id = None
        for sid, data in config.active_sessions.items():
            if data['chat_id'] == event.chat_id:
                session_id = sid
                break
        
        if not session_id:
            return
        
        session = config.active_sessions[session_id]
        step = session.get('step')
        
        # Handle steps
        if step == 'fname_find':
            session['settings']['find_name'] = event.text.strip()
            session['step'] = 'fname_replace'
            await event.respond(
                f"✅ Find: `{event.text.strip()}`\n\n"
                "Now type REPLACEMENT text:",
                buttons=get_skip_keyboard(session_id)
            )
        
        elif step == 'fname_replace':
            session['settings']['replace_name'] = event.text.strip()
            session['step'] = 'settings'
            await event.respond(
                "✅ **Filename rule set!**\n\n"
                f"Find: `{session['settings']['find_name']}`\n"
                f"Replace: `{event.text.strip()}`",
                buttons=get_settings_keyboard(session_id)
            )
        
        elif step == 'cap_find':
            session['settings']['find_cap'] = event.text.strip()
            session['step'] = 'cap_replace'
            await event.respond(
                f"✅ Find: `{event.text.strip()}`\n\n"
                "Now type REPLACEMENT text:",
                buttons=get_skip_keyboard(session_id)
            )
        
        elif step == 'cap_replace':
            session['settings']['replace_cap'] = event.text.strip()
            session['step'] = 'settings'
            await event.respond(
                "✅ **Caption rule set!**\n\n"
                f"Find: `{session['settings']['find_cap']}`\n"
                f"Replace: `{event.text.strip()}`",
                buttons=get_settings_keyboard(session_id)
            )
        
        elif step == 'extra_cap':
            session['settings']['extra_cap'] = event.text.strip()
            session['step'] = 'settings'
            await event.respond(
                "✅ **Extra caption set!**\n\n"
                f"Text: `{event.text.strip()[:50]}...`",
                buttons=get_settings_keyboard(session_id)
            )
        
        elif step == 'range':
            if "t.me" not in event.text:
                return await event.respond(
                    "❌ Invalid format!\n\n"
                    "Send like: `link1 - link2`"
                )
            
            try:
                parts = event.text.strip().split("-")
                if len(parts) != 2:
                    raise ValueError("Need exactly 2 links separated by -")
                
                msg1 = int(parts[0].strip().split("/")[-1])
                msg2 = int(parts[1].strip().split("/")[-1])
                
                if msg1 > msg2: 
                    msg1, msg2 = msg2, msg1
                
                if msg1 == msg2:
                    return await event.respond("❌ Start and end must be different!")
                
                # Start transfer
                config.is_running = True
                config.stop_flag = False
                config.current_task = asyncio.create_task(
                    transfer_process(
                        event, 
                        user_client,
                        bot_client,
                        session['source'], 
                        session['dest'], 
                        msg1, 
                        msg2,
                        session_id
                    )
                )
                
            except Exception as e: 
                config.logger.error(f"Range parse error: {e}")
                await event.respond(
                    f"❌ **Invalid Format**\n\n"
                    f"Expected:\n"
                    f"`https://t.me/c/xxx/10 - https://t.me/c/xxx/20`\n\n"
                    f"Error: `{str(e)}`"
                )
    
    @bot_client.on(events.NewMessage(pattern='/stats'))
    async def stats_handler(event):
        await event.respond(
            f"📊 **Bot Statistics**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"⚡ Chunk: **8MB**\n"
            f"💾 Buffer: **16MB** (8MB × 2)\n"
            f"📤 Upload: **8MB parts**\n"
            f"🔄 Retries: **{config.MAX_RETRIES}**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"Status: **{'🟢 Running' if config.is_running else '🔴 Idle'}**\n"
            f"Sessions: **{len(config.active_sessions)}**"
        )
    
    @bot_client.on(events.NewMessage(pattern='/stop'))
    async def stop_handler(event):
        if not config.is_running:
            return await event.respond("⚠️ No transfer to stop!")
        
        config.stop_flag = True
        config.is_running = False
        
        if config.current_task and not config.current_task.done():
            config.current_task.cancel()
        
        await event.respond("🛑 **Stopping...**\n\nPlease wait...")
    
    config.logger.info("✅ All handlers registered!")
