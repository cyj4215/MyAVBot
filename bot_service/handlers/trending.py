from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from bot_service.clients import client


async def trending(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 获取热门内容...")
    data = await client.latest_works()
    results = data.get("results", [])[:5]
    if not results:
        await update.message.reply_text("暂无数据")
        return
    for r in results:
        text = f"🔥 *{r['title']}*\n📅 {r.get('release_date', 'N/A')}"
        await update.message.reply_text(text, parse_mode="Markdown")


trending_handler = CommandHandler("trending", trending)
