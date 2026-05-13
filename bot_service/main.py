from telegram.ext import ApplicationBuilder, Application
from shared.config import settings
from bot_service.handlers.start import start_handler, help_handler_cmd
from bot_service.handlers.actress import actress_handler, actress_cb_handler
from bot_service.handlers.work import work_handler, latest_handler
from bot_service.handlers.magnet import magnet_handler, magnet_cb_handler
from bot_service.handlers.studio import studio_handler
from bot_service.handlers.trending import trending_handler


def build_application() -> Application:
    app = ApplicationBuilder().token(settings.telegram_bot_token).build()
    app.add_handler(start_handler)
    app.add_handler(help_handler_cmd)
    app.add_handler(actress_handler)
    app.add_handler(actress_cb_handler)
    app.add_handler(work_handler)
    app.add_handler(latest_handler)
    app.add_handler(magnet_handler)
    app.add_handler(magnet_cb_handler)
    app.add_handler(studio_handler)
    app.add_handler(trending_handler)
    return app


if __name__ == "__main__":
    app = build_application()
    app.run_webhook(
        listen="0.0.0.0",
        port=8080,
        url_path=settings.telegram_bot_token,
        webhook_url=f"{settings.telegram_webhook_url}/{settings.telegram_bot_token}",
    )
