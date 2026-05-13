from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def actress_detail_keyboard(actress_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📖 详细资料", callback_data=f"actress_detail:{actress_id}"),
            InlineKeyboardButton("🎥 作品列表", callback_data=f"actress_works:{actress_id}"),
        ],
        [
            InlineKeyboardButton("🔍 磁力搜索", callback_data=f"magnet_actress:{actress_id}"),
        ],
    ])


def magnet_category_keyboard(keyword: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🌍 欧美成人", callback_data=f"magnet_search:{keyword}:adult_eu"),
            InlineKeyboardButton("🌐 通用搜索", callback_data=f"magnet_search:{keyword}:general"),
        ],
    ])


def pagination_keyboard(base_cmd: str, page: int, total: int, data_id: str = None) -> InlineKeyboardMarkup:
    buttons = []
    row = []
    if page > 1:
        cb = f"{base_cmd}:{page - 1}:{data_id}" if data_id else f"{base_cmd}:{page - 1}"
        row.append(InlineKeyboardButton("◀ 上一页", callback_data=cb))
    if page < total:
        cb = f"{base_cmd}:{page + 1}:{data_id}" if data_id else f"{base_cmd}:{page + 1}"
        row.append(InlineKeyboardButton("下一页 ▶", callback_data=cb))
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(buttons)
