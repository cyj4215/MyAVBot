from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from bot_service.clients import client


async def search_studio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("用法: /studio 片商名称\n例: /studio VIXEN")
        return
    name = " ".join(context.args)
    try:
        results = await client.search_studio(name)
    except Exception:
        await update.message.reply_text("⚠️ 查询失败，服务暂时不可用")
        return
    if not results:
        await update.message.reply_text("😞 没有找到该片商")
        return
    for s in results[:5]:
        text = f"🏢 *{s['name']}*"
        await update.message.reply_text(text, parse_mode="Markdown")


studio_handler = CommandHandler("studio", search_studio)
