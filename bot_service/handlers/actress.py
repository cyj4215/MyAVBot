from telegram import Update
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes
from bot_service.clients import client
from bot_service.formatters import format_actress_card, format_works_header
from bot_service.keyboards import actress_detail_keyboard, pagination_keyboard, works_page_keyboard

PAGE_SIZE = 5
WORKS_PAGE_SIZE = 10


async def search_actress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "┏━━━━━━━━━━━━━━━━━━┓\n"
            "┃  🎬 MyAVBot · 女优搜索  ┃\n"
            "┗━━━━━━━━━━━━━━━━━━┛\n\n"
            "用法: `/actress 名字`\n"
            "例: `/actress Angela White`",
            parse_mode="Markdown",
        )
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
        await msg.reply_text("⚠️ 搜索失败，服务暂时不可用")
        return
    if not results:
        await msg.reply_text(f"😞 未找到 \"{name}\" 的相关结果")
        return
    total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
    header = f"🎬 🔍 “{name}” 搜索结果\n`{'─'*18}`"
    await msg.reply_text(header, parse_mode="Markdown")
    for r in results[:PAGE_SIZE]:
        text = format_actress_card(r)
        await msg.reply_text(text, parse_mode="Markdown",
            reply_markup=actress_detail_keyboard(r["id"]))
    if total_pages > 1:
        nav = f"📊 第 {page}/{total_pages} 页 | 共 {total} 条"
        await msg.reply_text(nav, reply_markup=pagination_keyboard("pa", page, total_pages))


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
                text += f"\n💬 _{actress['bio_text'][:200]}_"
            if actress.get("profile_image"):
                await query.message.reply_photo(
                    actress["profile_image"], caption=text, parse_mode="Markdown")
                return
            await safe_edit(query, text, actress_detail_keyboard(actress_id))
            return

        if data.startswith("actress_works:"):
            actress_id = int(data.split(":")[1])
            await safe_edit(query, "⏳ 正在同步作品数据（首次需 10-20 秒）...")
            actress = await client.get_actress(actress_id, sync_works=True)
            await _show_works_page(query, actress_id, 1)
    except Exception as e:
        await safe_edit(query, f"⚠️ {str(e)[:80]}")


async def _show_works_page(query, actress_id: int, page: int):
    try:
        works = await client.works_by_actress(actress_id)
        items = works.get("results", [])
    except Exception:
        await safe_edit(query, "⚠️ 获取作品列表失败")
        return
    if not items:
        await safe_edit(query, "😞 该女优暂未收录作品")
        return
    total = len(items)
    total_pages = (total + WORKS_PAGE_SIZE - 1) // WORKS_PAGE_SIZE
    start = (page - 1) * WORKS_PAGE_SIZE
    page_items = items[start:start + WORKS_PAGE_SIZE]

    # Get actress name from first work's cast context
    lines = []
    for i, w in enumerate(page_items):
        year = w.get("release_date", "")[:4] if w.get("release_date") else ""
        tag = "🔥 " if year == "2026" else ""
        lines.append(
            f"{tag}*{w['title']}*"
        )
        meta = ""
        if year:
            meta += f"  📅 {year}"
        if w.get("duration"):
            meta += f"  ⏱ {w['duration']}min"
        if meta:
            lines.append(meta)

    text = f"🎬 *作品目录* — 共 {total} 部 | 第 {page}/{total_pages} 页\n"
    text += f"`{'─'*22}`\n"
    text += "\n".join(lines)
    kb = works_page_keyboard(actress_id, page, total_pages) if total_pages > 1 else None
    await safe_edit(query, text, kb)


async def works_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        parts = query.data.split(":")
        await _show_works_page(query, int(parts[1]), int(parts[2]))
    except Exception as e:
        await safe_edit(query, f"⚠️ {str(e)[:60]}")


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
        await safe_edit(query, f"⚠️ {str(e)[:60]}")


async def safe_edit(query, text: str, kb=None):
    try:
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)
    except Exception:
        await query.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)


actress_handler = CommandHandler("actress", search_actress)
actress_cb_handler = CallbackQueryHandler(actress_callback, pattern="^actress_")
works_cb_handler = CallbackQueryHandler(works_callback, pattern="^pw:")
paginate_handler = CallbackQueryHandler(paginate_callback, pattern="^pg:")
