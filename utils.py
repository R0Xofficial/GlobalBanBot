# --- utils.py ---
import html
import database as db
import telegram
import aiosqlite
from telegram import Update
from telegram.constants import ChatType
from datetime import datetime, timezone

def safe_escape(text: str) -> str:
    return html.escape(str(text)).replace("&#x27;", "’")

async def create_user_link(user_id: int, context) -> str:
    try:
        chat = await context.bot.get_chat(user_id)
        name = chat.first_name or "User"
        return f'<a href="tg://user?id={user_id}">{safe_escape(name)}</a>'
    except:
        return f'Unknown User'

async def resolve_id(update: Update, context, input_str: str):
    input_str = input_str.strip()

    if update.message and update.message.entities:
        for entity in update.message.entities:
            if entity.type == 'text_mention' and entity.user:
                return entity.user.id, None

    if input_str.isdigit() or (input_str.startswith("-") and input_str[1:].isdigit()):
        uid = int(input_str)
        if uid < 0: return None, "🧐 Channels cannot be globally banned."
        return uid, None
    
    if input_str.startswith("@"):
        db_id = await db.get_user_by_username(input_str)
        if db_id: return db_id, None
        try:
            res = await context.bot.get_chat(input_str)
            if res.type == ChatType.PRIVATE: return res.id, None
        except: pass

    return None, "I can't find this user. Try replying to them or using their ID."

async def send_safe_reply(update: Update, context, text: str, **kwargs):
    try:
        return await update.message.reply_html(text, **kwargs)
    except telegram.error.BadRequest as e:
        if "Message to be replied not found" in str(e):
            return await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=text,
                parse_mode='HTML',
                **kwargs
            )
        raise e

async def get_utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

async def get_target_from_command(update: Update, context):
    if update.message.reply_to_message and not update.message.reply_to_message.forum_topic_created:
        return update.message.reply_to_message.from_user.id, None
    elif context.args:
        return await resolve_id(update, context, context.args[0])
    return None, "Who is the target of the command? The stars in the sky?"
