from telegram import Update, BotCommand
from telegram.ext import CommandHandler, ContextTypes

COMMANDS = [
    BotCommand("actress", "搜索女优资料"),
    BotCommand("work", "搜索作品"),
    BotCommand("magnet", "磁力搜索"),
    BotCommand("latest", "最新作品"),
    BotCommand("studio", "片商信息"),
    BotCommand("trending", "热门"),
    BotCommand("help", "帮助"),
]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 *MyAVBot*\n\n"
        "欧美成人女优资料库 & 磁力搜索工具。\n\n"
        "*功能介绍*\n"
        "👩 搜索女优 — 姓名、生日、身高三围、生涯作品\n"
        "🎥 作品查询 — 标题/编号搜索、最新发行\n"
        "🔗 磁力搜索 — 按关键词搜磁力，支持欧美/通用双模式\n"
        "🏢 片商信息 — 制作公司资料\n\n"
        "*数据来源*\n"
        "• IAFD 女优资料库 + 作品表\n"
        "• 磁力索引站实时搜索\n"
        "• CloakBrowser 反爬技术支持\n\n"
        "输入 /help 查看完整命令列表，或直接输入命令开始使用。",
        parse_mode="Markdown",
    )


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "*MyAVBot 命令列表*\n\n"
        "👩 `/actress <name>` — 搜索女优资料\n"
        "   例: `/actress Angela White`\n\n"
        "🎥 `/work <title>` — 搜索作品\n"
        "   例: `/work VIXEN`\n\n"
        "🔗 `/magnet <keyword>` — 磁力搜索\n"
        "   支持欧美成人/通用双搜索范围\n"
        "   例: `/magnet Angela White`\n\n"
        "📅 `/latest [studio]` — 最新作品\n"
        "   可选按片商筛选\n\n"
        "🏢 `/studio <name>` — 片商信息\n\n"
        "🔥 `/trending` — 热门内容\n\n"
        "💡 提示: 在女优搜索结果中点击按钮可查看详情、作品、磁力",
        parse_mode="Markdown",
    )


start_handler = CommandHandler("start", start)
help_handler_cmd = CommandHandler("help", help_handler)
