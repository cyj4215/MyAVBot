from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from bot_service.clients import client


async def trending(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = await client.latest_works()
        results = data.get("results", [])[:10]
    except Exception:
        await update.message.reply_text("⚠️ 获取热门失败，服务暂时不可用")
        return
    if not results:
        await update.message.reply_text("😞 暂无数据")
        return
    lines = ["🔥 *热门作品 TOP 10*", "`──────────────`"]
    for i, r in enumerate(results, 1):
        year = r.get("release_date", "")[:4] if r.get("release_date") else ""
        title = r["title"][:50]
        lines.append(f"\n{i}. *{title}*")
        if year:
            lines.append(f"   📅 {year}")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


trending_handler = CommandHandler("trending", trending)
