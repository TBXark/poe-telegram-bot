#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position

import logging
import poe
import json
import sys
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

chat_bots = {}


class PoeChat:
    def __init__(self, client_token, chat_model):
        self.client = poe.Client(client_token)
        self.model = chat_model

    def chat(self, message):
        return self.client.send_message(self.model, message)

    def all_models(self):
        return self.client.bot_names

    def update_token(self, client_token):
        self.client = poe.Client(client_token)

    def update_model(self, chat_model):
        self.model = chat_model

    def new_conversation(self):
        self.client.send_chat_break(self.model)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_bot = chat_bots[update.message.from_user.id]
    if chat_bot is None:
        return
    chat_bot.new_conversation()
    logger.info("Started conversation with {}".format(update.message.from_user.id))
    await update.message.reply_text("New conversation started")


async def models(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_bot = chat_bots[update.message.from_user.id]
    if chat_bot is None:
        return
    names = chat_bot.all_models()
    text = ""
    for name in names:
        text += f"{name}: {names[name]}\n"
    await update.message.reply_text(text)


async def model(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_bot = chat_bots[update.message.from_user.id]
    if chat_bot is None:
        return
    new_model = context.args[0]
    chat_bot.update_model(new_model)
    await update.message.reply_text("Bot set to {}".format(new_model))


async def token(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_bot = chat_bots[update.message.from_user.id]
    if chat_bot is None:
        return
    chat_bot.update_token(context.args[0])
    await update.message.reply_text(f"Updated token")


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("Received message from {}: {}".format(update.message.from_user.id, update.message.text))

    chat_bot = chat_bots[update.message.from_user.id]
    if chat_bot is None:
        return

    full_text = ""
    edit_count = 0
    length_delta = 0

    msg = await update.message.reply_text("Thinking...")
    for chunk in chat_bot.chat(update.message.text):
        length_delta += len(chunk["text"]) - len(full_text)
        full_text = chunk["text"]
        if length_delta < 25:
            continue
        if edit_count >= 90:
            if edit_count == 90:
                await msg.edit_text(full_text + "...")
            continue
        try:
            await msg.edit_text(full_text)
            edit_count += 1
            length_delta = 0
        except Exception as e:
            logger.info("Failed to edit message: {}".format(str(e)))

    try:
        await msg.edit_text(full_text, parse_mode="MarkdownV2")
    except Exception as e:
        logger.info("Failed to edit message: {}".format(str(e)))
        await msg.edit_text(full_text)


async def set_my_commands(bot):
    try:
        await bot.set_my_commands([
            ("start", "Start a new conversation"),
            ("models", "List all models"),
            ("model", "Set the model"),
            ("token", "Set the token"),
        ])
    except Exception as e:
        logger.info("Failed to set commands: {}".format(str(e)))


def main() -> None:
    config_path = "config.json"
    if len(sys.argv) > 1 and sys.argv.index("-c") < len(sys.argv) - 1:
        config_path = sys.argv[sys.argv.index("-c") + 1]
    if config_path is None:
        logger.error("No config file specified")
        exit(1)
    with open(config_path) as f:
        config = json.load(f)
        telegram_token = config["token"]
        for user_id, user_config in config["chatbot"].items():
            chat_bots[int(user_id)] = PoeChat(user_config["token"], user_config["bot"])

    application = Application.builder().token(telegram_token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("models", models))
    application.add_handler(CommandHandler("model", model))
    application.add_handler(CommandHandler("token", token))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    loop = asyncio.get_event_loop()
    loop.run_until_complete(set_my_commands(application.bot))

    logger.info("Starting application")
    application.run_polling()


if __name__ == "__main__":
    main()
