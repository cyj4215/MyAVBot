from telegram import Update
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes
from bot_service.clients import client
from bot_service.formatters import format_magnet_result
from bot_service.keyboards import magnet_category_keyboard, pagination_keyboard

MAGNET_PAGE = 10


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

    # Handle all magnet_* callbacks
    if data.startswith("magnet_search:") or data.startswith("m_s:"):
        parts = data.split(":")
        keyword = parts[1]
        category = parts[2] if len(parts) > 2 else "adult_eu"
        context.user_data["magnet_q"] = keyword
        context.user_data["magnet_cat"] = category
        await query.edit_message_text(f"🔍 搜索磁力 \"{keyword}\"...")
        await _show_magnet_page(query, keyword, category, 1)
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

    if data.startswith("mg:"):
        page = int(data.split(":")[2])
        keyword = context.user_data.get("magnet_q", "")
        category = context.user_data.get("magnet_cat", "adult_eu")
        if not keyword:
            await query.edit_message_text("😞 搜索已过期，请重新搜索")
            return
        await _show_magnet_page(query, keyword, category, page)


async def _show_magnet_page(query, keyword: str, category: str, page: int):
    result = await client.search_magnet(keyword, category, page=page)
    items = result.get("results", [])
    total = result.get("total", 0)
    if not items:
        await query.edit_message_text("😞 没有找到磁力链接")
        return
    total_pages = (total + MAGNET_PAGE - 1) // MAGNET_PAGE
    page_items = items[:MAGNET_PAGE]
    lines = [format_magnet_result(m) for m in page_items]
    text = "\n\n".join(lines)
    if total_pages > 1:
        text += f"\n\n第 {page}/{total_pages} 页（共 {total} 条）"
    kb = pagination_keyboard("mg", page, total_pages) if total_pages > 1 else None
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)


magnet_handler = CommandHandler("magnet", search_magnet)
magnet_cb_handler = CallbackQueryHandler(magnet_callback, pattern="^(m_s:|magnet_|mg:)")
