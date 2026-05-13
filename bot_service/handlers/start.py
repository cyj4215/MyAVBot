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
        "┏━━━━━━━━━━━━━━━━━━━━┓\n"
        "┃      🎬 *MyAVBot*      ┃\n"
        "┃  欧美女优资料 & 磁力搜索  ┃\n"
        "┗━━━━━━━━━━━━━━━━━━━━┛\n\n"
        "📖 *功能介绍*\n"
        "  👩 搜索女优 · 资料详情\n"
        "  🎥 作品查询 · 最新发行\n"
        "  🔗 磁力搜索 · 多源聚合\n\n"
        "⚡ *快速开始*\n"
        "  `/actress Angela White`\n"
        "  `/magnet Riley Reid`\n"
        "  `/help` — 完整命令\n\n"
        "🛡 Powered by CloakBrowser",
        parse_mode="Markdown",
    )


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "━━━━━━━━━━━━━━━━━━\n"
        "   🎬 *MyAVBot 命令表*\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "👩 `/actress <name>`\n"
        "  → 搜索女优资料、详情、作品\n\n"
        "🎥 `/work <title>`\n"
        "  → 搜索作品信息\n\n"
        "🔗 `/magnet <keyword>`\n"
        "  → 磁力搜索（欧美/通用）\n\n"
        "📅 `/latest [studio]`\n"
        "  → 最新作品\n\n"
        "🏢 `/studio <name>`\n"
        "  → 片商信息\n\n"
        "🔥 `/trending`\n"
        "  → 热门内容\n\n"
        "💡 *提示:* 搜索结果中点击按钮\n"
        "可查看详情、翻页、磁力搜索",
        parse_mode="Markdown",
    )


start_handler = CommandHandler("start", start)
help_handler_cmd = CommandHandler("help", help_handler)
