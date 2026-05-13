from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes
from bot_service.clients import client
from bot_service.formatters import format_actress_card
from bot_service.keyboards import actress_detail_keyboard


async def search_actress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("用法: /actress 女优名字")
        return
    name = " ".join(context.args)
    await update.message.reply_text(f"🔍 搜索 \"{name}\"...")
    data = await client.search_actress(name)
    results = data.get("results", [])
    if not results:
        await update.message.reply_text("😞 没有找到结果")
        return
    for r in results[:5]:
        text = format_actress_card(r)
        await update.message.reply_text(
            text,
            parse_mode="Markdown",
            reply_markup=actress_detail_keyboard(r["id"]),
        )


async def actress_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("actress_detail:"):
        actress_id = int(data.split(":")[1])
        actress = await client.get_actress(actress_id)
        text = format_actress_card(actress)
        if actress.get("bio_text"):
            text += f"\n\n📝 {actress['bio_text'][:300]}"
        if actress.get("profile_image"):
            await query.message.reply_photo(
                actress["profile_image"], caption=text, parse_mode="Markdown"
            )
            return
        await query.edit_message_text(
            text, parse_mode="Markdown",
            reply_markup=actress_detail_keyboard(actress_id),
        )
        return

    if data.startswith("actress_works:"):
        actress_id = int(data.split(":")[1])
        await query.edit_message_text("🎥 同步作品数据...")
        # Trigger sync + get actress name
        actress = await client.get_actress(actress_id, sync_works=True)
        name = actress.get("name", "")
        works = await client.works_by_actress(actress_id)
        items = works.get("results", [])
        if items:
            lines = [f"🎥 *{name}* 的作品（{len(items)}）"]
            for w in items[:20]:
                line = f"\n🎬 {w['title']}"
                if w.get("release_date"):
                    line += f"\n    📅 {w['release_date']}"
                lines.append(line)
            await query.edit_message_text("\n".join(lines), parse_mode="Markdown")
        else:
            kb = InlineKeyboardMarkup([[
                InlineKeyboardButton("🔍 磁力搜索", switch_inline_query_current_chat=name),
            ]])
            await query.edit_message_text(
                f"😞 {name} 的作品暂未同步成功。\n\n点击下方按钮搜索磁力资源：",
                reply_markup=kb,
            )
        return


actress_handler = CommandHandler("actress", search_actress)
actress_cb_handler = CallbackQueryHandler(actress_callback, pattern="^actress_")
