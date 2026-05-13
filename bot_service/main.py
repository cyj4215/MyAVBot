from telegram import Update
from telegram.ext import ApplicationBuilder, Application, CallbackQueryHandler
from shared.config import settings
from bot_service.handlers.start import start_handler, help_handler_cmd, COMMANDS
from bot_service.handlers.actress import actress_handler, actress_cb_handler, works_cb_handler, paginate_handler
from bot_service.handlers.work import work_handler, latest_handler
from bot_service.handlers.magnet import magnet_handler, magnet_cb_handler
from bot_service.handlers.studio import studio_handler
from bot_service.handlers.trending import trending_handler


async def set_commands(app: Application):
    await app.bot.set_my_commands(COMMANDS)


async def noop(update: Update, context):
    """Silently handle noop button presses."""
    await update.callback_query.answer()


def build_application() -> Application:
    app = (
        ApplicationBuilder()
        .token(settings.telegram_bot_token)
        .post_init(set_commands)
        .build()
    )
    app.add_handler(start_handler)
    app.add_handler(help_handler_cmd)
    app.add_handler(actress_handler)
    app.add_handler(actress_cb_handler)
    app.add_handler(works_cb_handler)
    app.add_handler(paginate_handler)
    app.add_handler(CallbackQueryHandler(noop, pattern="^noop$"))
    app.add_handler(work_handler)
    app.add_handler(latest_handler)
    app.add_handler(magnet_handler)
    app.add_handler(magnet_cb_handler)
    app.add_handler(studio_handler)
    app.add_handler(trending_handler)
    return app


if __name__ == "__main__":
    app = build_application()
    print("🤖 MyAVBot started in polling mode...")
    app.run_polling()
