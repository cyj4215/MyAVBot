from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from bot_service.clients import client
from bot_service.formatters import format_work_card


async def search_work(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "🎥 *MyAVBot · 作品搜索*\n\n"
            "用法: `/work 标题`\n"
            "例: `/work VIXEN`",
            parse_mode="Markdown",
        )
        return
    title = " ".join(context.args)
    try:
        await update.message.reply_text(f"🔍 正在搜索 “{title}”...")
        data = await client.search_work(title)
        results = data.get("results", [])
    except Exception:
        await update.message.reply_text("⚠️ 搜索失败，服务暂时不可用")
        return
    if not results:
        await update.message.reply_text(f"😞 未找到 “{title}” 的相关作品")
        return
    await update.message.reply_text(f"🎬 共找到 {len(results)} 部作品", parse_mode="Markdown")
    for r in results[:10]:
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
        await update.message.reply_text("⚠️ 获取最新作品失败，服务暂时不可用")
        return
    if not results:
        await update.message.reply_text("😞 暂无最新作品")
        return
    label = f"片商 #{studio_id}" if studio_id else "全网"
    await update.message.reply_text(f"🔥 *{label}最新作品*", parse_mode="Markdown")
    for r in results[:10]:
        text = format_work_card(r)
        if r.get("cover_image"):
            await update.message.reply_photo(r["cover_image"],
                caption=text, parse_mode="Markdown")
        else:
            await update.message.reply_text(text, parse_mode="Markdown")


work_handler = CommandHandler("work", search_work)
latest_handler = CommandHandler("latest", latest_works)
