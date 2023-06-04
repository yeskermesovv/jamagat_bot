#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to send timed Telegram messages.

This Bot uses the Application class to handle the bot and the JobQueue to send
timed messages.

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Prayer Time Bot example, sends a poll on scheduled time fetched from google sheet.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.

Note:
To use the JobQueue, you must install PTB via
`pip install python-telegram-bot[job-queue]`

google sheet link https://docs.google.com/spreadsheets/d/1uOqBUEvdDM1ivlwTkOERaC5crawN4TinqB5rmT-kyS8/edit#gid=0
"""
import logging
import pandas as pd

from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import (
    Update,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
# Best practice would be to replace context with an underscore,
# since context is an unused local variable.
# This being an example and not having context present confusing beginners,
# we decided to have it present as context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends explanation on how to use the bot."""
    await update.message.reply_text("Hi! Use /set to set prayer time")


async def sendPoll(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the alarm message."""
    job = context.job
    questions = ["Гоу", "Позже"]
    await context.bot.send_poll(
        job.chat_id,
        "Че там?",
        questions,
        is_anonymous=False,
        allows_multiple_answers=True,
    )


async def set_timer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_message.chat_id

    """Clean all existing jobs"""
    remove_job_if_exists(str(chat_id), context)

    try:
        """Fetch prayer time from google sheet."""
        SHEET_ID = '1uOqBUEvdDM1ivlwTkOERaC5crawN4TinqB5rmT-kyS8'
        SHEET_NAME = 'prayer'
        url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}'
        df = pd.read_csv(url, index_col=0, parse_dates=['Time'])

        """Add a job to the queue."""
        for index, row in df.iterrows():
            print('time: ', row['Time'])

            context.job_queue.run_once(sendPoll, chat_id=chat_id, name=str(chat_id), when=row['Time'])

        text = "Timer successfully set!"
        await update.effective_message.reply_text(text)

    except (IndexError, ValueError):
        await update.effective_message.reply_text("Usage: /set")

def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


async def test(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    SHEET_ID = '1uOqBUEvdDM1ivlwTkOERaC5crawN4TinqB5rmT-kyS8'
    SHEET_NAME = 'prayer'
    url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}'
    df = pd.read_csv(url, index_col=0, parse_dates=['Time'])
    for index, row in df.iterrows():
        print('timeeee: ', row['Time'])


def main() -> None:
    """Run bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("6148899700:AAEJLBN9YocI3UO_Fv92sAYfl8Q3Ly_vPlg").build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler(["start", "help"], start))
    application.add_handler(CommandHandler("set", set_timer))
    application.add_handler(CommandHandler("test", test))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()