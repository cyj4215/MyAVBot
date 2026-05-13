from telegram import Update
from telegram.ext import CommandHandler, ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 *MyAVBot 欢迎你！*\n\n"
        "搜索欧美成人女优资料、最新作品、磁力链接。\n\n"
        "常用命令：\n"
        "/actress `名字` - 搜索女优\n"
        "/work `标题` - 搜索作品\n"
        "/magnet `关键词` - 磁力搜索\n"
        "/latest - 最新作品\n"
        "/help - 完整帮助\n\n"
        "由 CloakBrowser 技术支持 🛡",
        parse_mode="Markdown",
    )


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "*MyAVBot 命令列表*\n\n"
        "/actress `<name>` - 搜索女优资料\n"
        "/work `<title>` - 搜索作品\n"
        "/magnet `<keyword>` - 磁力搜索\n"
        "/latest `[studio]` - 最新作品\n"
        "/studio `<name>` - 片商信息\n"
        "/new - 近期新人\n"
        "/trending - 热门内容\n"
        "/help - 本帮助",
        parse_mode="Markdown",
    )


start_handler = CommandHandler("start", start)
help_handler_cmd = CommandHandler("help", help_handler)
