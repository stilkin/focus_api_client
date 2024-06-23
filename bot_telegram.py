import logging
import os
import time

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, filters

from fc_methods import image_from_prompt, handle_config_request
from or_calls import prompt_to_style

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
    if update.message is None:
        print(f'Message is none: \n{update}')
        return

    if update.message.from_user.is_bot:
        return

    parts = update.message.text.split()
    if len(parts) < 2:
        reply = f'I am sorry, but your command *{update.message.text}* appears to be missing some parameters...'
        await update.message.reply_markdown(reply)
        return

    prompt = update.message.text.partition(' ')[2]
    print(f'Currently working on: "{prompt}"')
    # reply = f'Okay, please hold ⏳'

    style_arr = None
    if 'style' in prompt:
        style_arr = prompt_to_style(prompt)  # TODO: rework this into basic RAG with chromaDB
        reply = f'I will use these styles: *{style_arr}*.\nPlease hold ⏳'
    # await update.message.reply_markdown(reply, reply_to_message_id=update.message.message_id)

    start_time = time.time()
    local_copy = image_from_prompt(prompt, update.effective_user.id, style_arr)
    end_time = time.time()
    duration = round(end_time - start_time, 1)
    reply = f'I worked on it for {duration} seconds.'

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
    if update.message is None:
        print(f'Message is none: \n{update}')
        return

    if update.message.from_user.is_bot:
        return

    parts = update.message.text.split()
    if len(parts) < 2:
        reply = f'I am sorry, but your command *{update.message.text}* appears to be missing some parameters...'
        await update.message.reply_markdown(reply)
        return

    cfg_command = update.message.text.partition(' ')[2]
    response = handle_config_request(cfg_command, update.effective_user.id)
    await update.message.reply_text(response, reply_to_message_id=update.message.message_id)


def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("focus",
                                           callback=generate_image,
                                           filters=filters.ALL))

    application.add_handler(CommandHandler("focus_cfg",
                                           callback=update_config,
                                           filters=filters.ALL))

    application.run_polling(allowed_updates=Update.MESSAGE)


if __name__ == "__main__":
    main()
