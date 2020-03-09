import telegram, os, firedb
from telegram.ext import Updater, CommandHandler


def query_callback(update, context):
    try:
        query = " ".join(context.args)
        data = {"query": query}
        firedb.update_document("search", data)
        update.message.reply_text(f"Query sucessfully updated to: {query}")
    except Exception as e:
        error = f"Error during 'tg.query_callback()' execution: {e}"
        send_error_message(error)

def stars_callback(update, context):
    try:
        stars = int(" ".join(context.args))
        data = {"min_stars": stars}
        firedb.update_document("search", data)
        update.message.reply_text(f"The new min number of repo stars is: {stars}")
    except Exception as e:
        error = f"Error during 'tg.stars_callback()' execution: {e}"
        send_error_message(error)

def send_issues(msg):
    """Send isssues"""
    try:
        for iss in msg:
            new_msg = ""
            for key, item in iss.items():
                new_msg += f"{key}: {item}\n"
            bot.send_message(chat_id=os.environ["TELEGRAM_USERID"], text=new_msg)
    except Exception as e:
        error = f"Error during 'tg.send_issues()' execution: {e}"
        send_error_message(error)
        
def send_error_message(msg):
    """Send error message"""
    bot.send_message(chat_id=os.environ["TELEGRAM_USERID"], text=msg)

def info_callback(update, context):
    try:
        info = firedb.get_document("search")
        update.message.reply_text(f"Actual parameters: {info}")
    except Exception as e:
        error = f"Error during 'tg.info_callback()' execution: {e}"
        send_error_message(error)


# Auth
bot = telegram.Bot(os.environ["TELEGRAM_TOKEN"])
updater = Updater(token=os.environ["TELEGRAM_TOKEN"], use_context=True)

# Define bot commands
dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler("query", query_callback))
dispatcher.add_handler(CommandHandler("stars", stars_callback))
dispatcher.add_handler(CommandHandler("info", info_callback))


# Start the Bot
updater.start_polling()
