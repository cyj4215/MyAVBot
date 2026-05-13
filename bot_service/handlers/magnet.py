from telegram import Update
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes
from bot_service.clients import client
from bot_service.formatters import format_magnet_result
from bot_service.keyboards import magnet_category_keyboard


async def search_magnet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("用法: /magnet 关键词")
        return
    keyword = " ".join(context.args)
    await update.message.reply_text(
        "选择搜索范围:",
        reply_markup=magnet_category_keyboard(keyword),
    )


async def magnet_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("magnet_search:"):
        parts = data.split(":")
        keyword = parts[1]
        category = parts[2]
        await query.edit_message_text(f"🔍 搜索磁力 \"{keyword}\"...")
        result = await client.search_magnet(keyword, category)
        items = result.get("results", [])
        if not items:
            await query.edit_message_text("😞 没有找到磁力链接")
            return
        lines = [format_magnet_result(m) for m in items[:10]]
        await query.edit_message_text("\n\n".join(lines), parse_mode="Markdown")
        return

    if data.startswith("magnet_actress:"):
        actress_id = int(data.split(":")[1])
        actress = await client.get_actress(actress_id)
        name = actress.get("name", "")
        await query.edit_message_text(
            f"🔍 搜索 \"{name}\" 的磁力资源，选择范围:",
            reply_markup=magnet_category_keyboard(name),
        )
        return


magnet_handler = CommandHandler("magnet", search_magnet)
magnet_cb_handler = CallbackQueryHandler(magnet_callback, pattern="^magnet_")
