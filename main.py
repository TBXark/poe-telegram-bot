#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position

import logging
import poe
import json
import sys
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
    if poe_cfg is None:
        return
    poe_cfg.client.send_chat_break(poe_cfg.bot)
    logger.info("Started conversation with {}".format(update.message.from_user.id))
    await update.message.reply_text("New conversation started")


async def roles(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    poe_cfg = poe_configs[str(update.message.from_user.id)]
    if poe_cfg is None:
        return
    names = poe_cfg.client.bot_names
    text = ""
    for name in names:
        text += f"{name}: {names[name]}\n"
    await update.message.reply_text(text)


async def role(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    poe_cfg = poe_configs[str(update.message.from_user.id)]
    if poe_cfg is None:
        return
    poe_cfg.bot = context.args[0]
    await update.message.reply_text(f"Bot set to {poe_cfg.bot}")


async def token(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    poe_cfg = poe_configs[str(update.message.from_user.id)]
    if poe_cfg is None:
        return
    poe_cfg.client = poe.Client(context.args[0])
    await update.message.reply_text(f"Updated token")


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    poe_cfg = poe_configs.get(str(update.message.from_user.id))
    if poe_cfg is None:
        return
    msg = await update.message.reply_text("Thinking...")
    logger.info("Received message from {}: {}".format(update.message.from_user.id, update.message.text))
    for chunk in poe_cfg.client.send_message(poe_cfg.bot, update.message.text):
        try:
            await msg.edit_text(chunk["text"])
        except Exception as e:
            logger.info("Failed to edit message: {}".format(str(e)))


def set_my_commands(bot):
    try:
        bot.set_my_commands([
            ("start", "Start a new conversation"),
            ("roles", "List all roles"),
            ("role", "Set the role"),
            ("token", "Set the token"),
        ])
    except Exception as e:
        logger.info("Failed to set commands: {}".format(str(e)))


def main() -> None:
    config_path = sys.argv[sys.argv.index("-c") + 1]
    if config_path is None:
        logger.error("No config file specified")
        exit(1)
    with open(config_path) as f:
        config = json.load(f)
        telegram_token = config["token"]
        for user_id, user_config in config["chatbot"].items():
            poe_configs[user_id] = PoeConfig(
                poe.Client(user_config["token"]),
                user_config["bot"]
            )

    application = Application.builder().token(telegram_token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("roles", roles))
    application.add_handler(CommandHandler("role", role))
    application.add_handler(CommandHandler("token", token))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    set_my_commands(application.bot)

    application.run_polling()


if __name__ == "__main__":
    main()
