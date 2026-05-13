from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def actress_detail_keyboard(actress_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📖 资料详情", callback_data=f"actress_detail:{actress_id}"),
            InlineKeyboardButton("🎥 作品列表", callback_data=f"actress_works:{actress_id}"),
        ],
        [
            InlineKeyboardButton("🔗 磁力搜索", callback_data=f"magnet_actress:{actress_id}"),
        ],
    ])


def magnet_category_keyboard(keyword: str) -> InlineKeyboardMarkup:
    kw = keyword[:40]
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔞 欧美成人", callback_data=f"m_s:{kw}:adult_eu"),
            InlineKeyboardButton("🌐 通用搜索", callback_data=f"m_s:{kw}:general"),
        ],
    ])


def pagination_keyboard(prefix: str, page: int, total_pages: int) -> InlineKeyboardMarkup:
    buttons = []
    row = []
    if page > 1:
        row.append(InlineKeyboardButton("◀ 上一页", callback_data=f"pg:{prefix}:{page - 1}"))
    txt = f"📄 {page}/{total_pages}"
    row.append(InlineKeyboardButton(txt, callback_data="noop"))
    if page < total_pages:
        row.append(InlineKeyboardButton("下一页 ▶", callback_data=f"pg:{prefix}:{page + 1}"))
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(buttons)


def works_page_keyboard(actress_id: int, page: int, total_pages: int) -> InlineKeyboardMarkup:
    buttons = []
    row = []
    if page > 1:
        row.append(InlineKeyboardButton("◀ 上一页", callback_data=f"pw:{actress_id}:{page - 1}"))
    row.append(InlineKeyboardButton(f"📄 {page}/{total_pages}", callback_data="noop"))
    if page < total_pages:
        row.append(InlineKeyboardButton("下一页 ▶", callback_data=f"pw:{actress_id}:{page + 1}"))
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(buttons)
