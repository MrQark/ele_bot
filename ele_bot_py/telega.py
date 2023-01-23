"""
How to program a Telegram bot in python: https://www.youtube.com/watch?v=PTAkiukJK7E
How to create a public API: https://www.youtube.com/watch?v=z6q9kug0PL0
http://127.0.0.1:5000/ele_bot_ping
"""
import os
import json
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes


absolute_path = os.path.dirname(os.path.abspath(__file__))
cfg_file_path = os.path.join(absolute_path, "", "ele_bot_cfg.json")


def elebot_write_cfg(elebot_cfg) -> None:
    with open(cfg_file_path, 'w') as f:
        f.write(json.dumps(elebot_cfg))


def elebot_load_cfg():
    elebot_cfg = None
    try:
        with open(cfg_file_path) as f:
            elebot_cfg = json.load(f)
    except IOError:
        print("ele_bot_cfg.json seems not existing!")
    if not all(key in elebot_cfg for key in ("id", "token", "subscribers")):
        print("ele_bot_cfg.json seems wrongly configured! Check, if id, token, and subscribers "
              "keys exist.")
        elebot_cfg = None
    return elebot_cfg


def get_ping_counter():
    cfg = elebot_load_cfg()
    return cfg['counter']


ELEBOT_CFG = elebot_load_cfg()
PING_COUNTER = get_ping_counter()
ping_counter = PING_COUNTER
ELEBOT_TIMER = 0
ELEBOT_STATE = 2
ELEBOT_PREVSTATE = 0


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    This handler will be called when user sends `/start` command
    """
    chat_id = update.effective_message.chat_id
    if not chat_id in ELEBOT_CFG["subscribers"]:
        # Notify adding to the list of subsribers
        print(f"New subsriber was succesfully added: {chat_id}")
        ELEBOT_CFG["subscribers"].append(chat_id)
        elebot_write_cfg(ELEBOT_CFG)
        await update.message.reply_text("You are successfully subscribed! I we keep you notified on "
                            "electricity changes.")
    else:
        print(f"The user {chat_id} is already subsribed!")
        await update.message.reply_text("You are already subscribed! Wait for coming notifications.")


async def elebot_notify_users(context, message):
    for chat_id in  ELEBOT_CFG["subscribers"]:
        await context.bot.send_message(chat_id=chat_id, text=message)


entry_time = time.time()
elebot_cnt = 0


async def elebot_handler(context: ContextTypes.DEFAULT_TYPE) -> None:
    global ping_counter
    global PING_COUNTER
    global ELEBOT_TIMER
    global ELEBOT_STATE
    global elebot_cnt
    global exit_time
    global entry_time

    exit_time = time.time()
    # Start of the handler
    PING_COUNTER = get_ping_counter()
    if PING_COUNTER != ping_counter:
        ELEBOT_TIMER = 0
        ping_counter = PING_COUNTER
    ELEBOT_TIMER = ELEBOT_TIMER + 1 if ELEBOT_TIMER < 10 else ELEBOT_TIMER
    if ELEBOT_STATE == 0 and ELEBOT_TIMER <= 2:
        elebot_cnt = elebot_cnt + 1 if elebot_cnt < 10 else elebot_cnt
        if elebot_cnt >= 5:
            elebot_cnt = 0
            ELEBOT_STATE = 1
            msg = "🌞 Світло з'явилось"
            await elebot_notify_users(context, msg)
    elif ELEBOT_STATE == 1 and ELEBOT_TIMER >= 5:
        ELEBOT_STATE = 0
        msg = "🌑 Світло зникло"
        await elebot_notify_users(context, msg)
    elif ELEBOT_STATE > 1 and ELEBOT_TIMER >= 5:
        ELEBOT_STATE = 0
    elif ELEBOT_STATE > 1 and ELEBOT_TIMER < 2:
        elebot_cnt = elebot_cnt + 1 if elebot_cnt < 10 else elebot_cnt
        if elebot_cnt >= 2:
            elebot_cnt = 0
            ELEBOT_STATE = 1

    # End of the handler
    print(f"dt: {exit_time - entry_time}, state: {ELEBOT_STATE}, timer: {ELEBOT_TIMER}, "
          f"cnt: {elebot_cnt}")
    entry_time = time.time()


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    tappl = Application.builder().token(ELEBOT_CFG["token"]).build()
    job_queue = tappl.job_queue
    job_queue.run_repeating(elebot_handler, 30)
    # on different commands - answer in Telegram
    tappl.add_handler(CommandHandler("start", start))

    # Run the bot until the user presses Ctrl-C
    tappl.run_polling()


main()