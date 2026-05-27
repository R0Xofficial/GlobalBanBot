# --- utils.py ---
import html
from telegram.constants import ChatType

def safe_escape(text: str) -> str:
    return html.escape(str(text)).replace("&#x27;", "’")

async def create_user_link(user_id: int, context) -> str:
    try:
        chat = await context.bot.get_chat(user_id)
        name = chat.first_name or "User"
        return f'<a href="tg://user?id={user_id}">{safe_escape(name)}</a>'
    except:
        return f'Unknown User'

async def resolve_id(context, input_str: str):
    input_str = input_str.strip()
    if input_str.isdigit() or (input_str.startswith("-") and input_str[1:].isdigit()):
        uid = int(input_str)
        if uid < 0: return None, "🧐 Channels/Chats cannot be globally banned."
        return uid, None
    try:
        if not input_str.startswith("@"): input_str = f"@{input_str}"
        res = await context.bot.get_chat(input_str)
        if res.type != ChatType.PRIVATE: return None, "🧐 This action only applies to users."
        return res.id, None
    except:
        return None, "I can't find this user. Ensure I have seen them before."
