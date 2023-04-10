#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position

import logging
import poe
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

poe_configs = {}


class PoeConfig:
    def __init__(self, client, bot):
        self.client = client
        self.bot = bot


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    poe_cfg = poe_configs[str(update.message.from_user.id)]
    poe_cfg.client.send_chat_break(poe_cfg.bot)
    await update.message.reply_text("New conversation started")


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = await update.message.reply_text("Thinking...")
    poe_cfg = poe_configs.get(str(update.message.from_user.id))
    logger.info("Received message from {}: {}".format(update.message.from_user.id, update.message.text))
    for chunk in poe_cfg.client.send_message(poe_cfg.bot, update.message.text):
        try:
            await msg.edit_text(chunk["text"])
        except Exception as e:
            logger.info("Failed to edit message: {}".format(str(e)))


def main() -> None:
    with open("config.json") as f:
        config = json.load(f)
        telegram_token = config["token"]
        for user_id, user_config in config["chatbot"].items():
            poe_configs[user_id] = PoeConfig(
                poe.Client(user_config["token"]),
                user_config["bot"]
            )

    application = Application.builder().token(telegram_token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    application.run_polling()


if __name__ == "__main__":
    main()
