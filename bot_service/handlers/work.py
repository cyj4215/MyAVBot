from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from bot_service.clients import client
from bot_service.formatters import format_work_card


async def search_work(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("用法: /work 作品标题或编号\n例: /work VIXEN")
        return
    title = " ".join(context.args)
    try:
        await update.message.reply_text(f"🔍 搜索 \"{title}\"...")
        data = await client.search_work(title)
        results = data.get("results", [])
    except Exception:
        await update.message.reply_text("⚠️ 搜索失败，服务暂时不可用")
        return
    if not results:
        await update.message.reply_text("😞 没有找到结果")
        return
    for r in results[:5]:
        text = format_work_card(r)
        if r.get("cover_image"):
            await update.message.reply_photo(r["cover_image"],
                caption=text, parse_mode="Markdown")
        else:
            await update.message.reply_text(text, parse_mode="Markdown")


async def latest_works(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        studio_id = int(context.args[0]) if context.args and context.args[0].isdigit() else None
        data = await client.latest_works(studio_id)
        results = data.get("results", [])
    except Exception:
        await update.message.reply_text("⚠️ 获取失败，服务暂时不可用")
        return
    if not results:
        await update.message.reply_text("暂无最新作品")
        return
    for r in results[:5]:
        text = format_work_card(r)
        if r.get("cover_image"):
            await update.message.reply_photo(r["cover_image"],
                caption=text, parse_mode="Markdown")
        else:
            await update.message.reply_text(text, parse_mode="Markdown")


work_handler = CommandHandler("work", search_work)
latest_handler = CommandHandler("latest", latest_works)
