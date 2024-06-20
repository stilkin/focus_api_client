import logging
import time

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from fc_methods import *

load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')

PROMPT_CMD = '/focus '
CONFIG_CMD = '/focus_cfg '

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and context.

async def generate_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.from_user.is_bot:
        return

    parts = update.message.text.split()
    if len(parts) < 2:
        reply = f'I am sorry, but your command {update.message.text} appears to be missing some parameters...'
        await update.message.from_user.send_message(reply)
        return

    prompt = update.message.text.replace(PROMPT_CMD, '', 1)
    reply = f'So you want me to show you *{prompt}* , okay. \nPlease wait a minute...'
    await update.message.reply_markdown(reply, reply_to_message_id=update.message.message_id)

    print(f'Currently working on: "{prompt}"')
    start_time = time.time()
    local_copy = image_from_prompt(prompt, update.effective_user.id)
    end_time = time.time()
    duration = round(end_time - start_time, 1)
    reply = f'*{prompt}*\nI worked on it for {duration} seconds.'

    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=open(local_copy, 'rb'),
        caption=reply,
        parse_mode='Markdown',
        reply_to_message_id=update.message.message_id,
        has_spoiler=True
    )
    os.remove(local_copy)


async def update_config(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.from_user.is_bot:
        return

    parts = update.message.text.split()
    if len(parts) < 2:
        reply = f'I am sorry, but your command {update.message.text} appears to be missing some parameters...'
        await update.message.from_user.send_message(reply)
        return

    response = handle_config_request(update.message.text, update.effective_user.id)
    await update.message.reply_markdown(response, reply_to_message_id=update.message.message_id)


def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("focus",
                                           callback=generate_image,
                                           filters=filters.COMMAND | filters.CHAT))

    application.add_handler(CommandHandler("focus_cfg",
                                           callback=update_config,
                                           filters=filters.COMMAND | filters.CHAT))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
