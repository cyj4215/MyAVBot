from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes
from bot_service.clients import client
from bot_service.formatters import format_actress_card
from bot_service.keyboards import actress_detail_keyboard, pagination_keyboard, works_page_keyboard

PAGE_SIZE = 5
WORKS_PAGE_SIZE = 20


async def search_actress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("用法: /actress 女优名字\n例: /actress Angela White")
        return
    name = " ".join(context.args)
    context.user_data["actress_q"] = name
    await _show_actress_page(update.message, name, 1)


async def _show_actress_page(msg, name: str, page: int):
    try:
        data = await client.search_actress(name, page=page)
        results = data.get("results", [])
        total = data.get("total", 0)
    except Exception:
        await msg.reply_text("⚠️ 搜索失败，服务暂时不可用，请稍后再试")
        return
    if not results:
        await msg.reply_text("😞 没有找到结果")
        return
    total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
    for r in results[:PAGE_SIZE]:
        text = format_actress_card(r)
        await msg.reply_text(text, parse_mode="Markdown",
            reply_markup=actress_detail_keyboard(r["id"]))
    if total_pages > 1:
        await msg.reply_text(f"第 {page}/{total_pages} 页（共 {total} 条）",
            reply_markup=pagination_keyboard("pa", page, total_pages))


async def actress_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    try:
        if data.startswith("actress_detail:"):
            actress_id = int(data.split(":")[1])
            actress = await client.get_actress(actress_id)
            text = format_actress_card(actress)
            if actress.get("bio_text"):
                text += f"\n\n📝 {actress['bio_text'][:300]}"
            if actress.get("profile_image"):
                await query.message.reply_photo(
                    actress["profile_image"], caption=text, parse_mode="Markdown")
                return
            await query.edit_message_text(text, parse_mode="Markdown",
                reply_markup=actress_detail_keyboard(actress_id))
            return

        if data.startswith("actress_works:"):
            actress_id = int(data.split(":")[1])
            await query.edit_message_text("🎥 同步作品数据中（首次需 10-20 秒）...")
            actress = await client.get_actress(actress_id, sync_works=True)
            await _show_works_page(query, actress_id, 1)
    except Exception as e:
        await safe_edit(query, f"⚠️ 操作失败: {str(e)[:100]}")


async def _show_works_page(query, actress_id: int, page: int):
    try:
        works = await client.works_by_actress(actress_id)
        items = works.get("results", [])
    except Exception:
        await safe_edit(query, "⚠️ 获取作品列表失败")
        return
    if not items:
        await safe_edit(query, "😞 该女优暂无收录作品")
        return
    total = len(items)
    total_pages = (total + WORKS_PAGE_SIZE - 1) // WORKS_PAGE_SIZE
    start = (page - 1) * WORKS_PAGE_SIZE
    page_items = items[start:start + WORKS_PAGE_SIZE]
    lines = [f"🎥 *作品列表*（{total} 部）"]
    for w in page_items:
        lines.append(f"\n🎬 {w['title']}")
        if w.get("release_date"):
            lines.append(f"    📅 {w['release_date']}")
    kb = works_page_keyboard(actress_id, page, total_pages) if total_pages > 1 else None
    await safe_edit(query, "\n".join(lines), kb)


async def works_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        parts = query.data.split(":")
        await _show_works_page(query, int(parts[1]), int(parts[2]))
    except Exception as e:
        await safe_edit(query, f"⚠️ 翻页失败: {str(e)[:100]}")


async def paginate_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        parts = query.data.split(":")
        prefix = parts[1]
        page = int(parts[2])

        if prefix == "pa":
            name = context.user_data.get("actress_q", "")
            if not name:
                await safe_edit(query, "😞 搜索已过期，请重新 /actress")
                return
            await safe_edit(query, f"🔍 第 {page} 页...")
            await _show_actress_page(query.message, name, page)
    except Exception as e:
        await safe_edit(query, f"⚠️ 翻页失败: {str(e)[:100]}")


async def safe_edit(query, text: str, kb=None):
    """Edit message safely — falls back to reply if edit fails."""
    try:
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)
    except Exception:
        await query.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)


actress_handler = CommandHandler("actress", search_actress)
actress_cb_handler = CallbackQueryHandler(actress_callback, pattern="^actress_")
works_cb_handler = CallbackQueryHandler(works_callback, pattern="^pw:")
paginate_handler = CallbackQueryHandler(paginate_callback, pattern="^pg:")
