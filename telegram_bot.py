import asyncio
import logging
import threading
import requests

logger = logging.getLogger(__name__)


class TelegramRemote:
    """
    Runs a Telegram bot in a background thread.
    Each incoming message is handed to `on_message(text, chat_id)`.
    """
    def __init__(self, token: str, allowed_chat_id: str = ""):
        self.token = token
        self.allowed = str(allowed_chat_id) if allowed_chat_id else None
        self.on_message = None
        self._stop = False
        self._loop = None

    def start(self):
        if not self.token:
            logger.info("Telegram token empty — skipping Telegram.")
            return
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        try:
            from telegram.ext import Application, MessageHandler, filters
        except ImportError:
            logger.error("pip install python-telegram-bot (v20+)")
            return

        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        async def handle(update, context):
            try:
                cid = str(update.effective_chat.id)
                logger.info("Telegram message from %s: %s", cid, update.message.text)
                if self.allowed and cid != self.allowed:
                    await update.message.reply_text("Unauthorized.")
                    return
                if self.on_message:
                    # Run the (blocking) command handler in a thread pool
                    self._loop.run_in_executor(
                        None, self.on_message, update.message.text, cid
                    )
                else:
                    await update.message.reply_text(
                        "Assistant not ready yet."
                    )
            except Exception as e:
                logger.exception("Telegram handler error: %s", e)

        async def main_async():
            app = Application.builder().token(self.token).build()
            app.add_handler(
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle)
            )
            await app.initialize()
            await app.start()
            await app.updater.start_polling()
            logger.info("Telegram bot online.")
            while not self._stop:
                await asyncio.sleep(0.5)
            await app.updater.stop()
            await app.stop()
            await app.shutdown()

        try:
            self._loop.run_until_complete(main_async())
        except Exception as e:
            logger.exception("Telegram bot crashed: %s", e)

    def send(self, chat_id: str, text: str):
        try:
            r = requests.post(
                f"https://api.telegram.org/bot{self.token}/sendMessage",
                json={"chat_id": chat_id, "text": text[:4000]},
                timeout=10,
            )
            if r.status_code != 200:
                logger.error("Telegram send failed: %s", r.text)
        except Exception as e:
            logger.error("Telegram send error: %s", e)

    def stop(self):
        self._stop = True