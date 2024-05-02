import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from pyunpack import Archive

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to handle /start command
def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_text(f"Hello {user.first_name}! Welcome to Unzip Upto4gb File Bot. Please send me a zip file to unzip.")

# Function to handle zip file
def handle_zip(update: Update, context: CallbackContext) -> None:
    file = context.bot.getFile(update.message.document.file_id)
    file_name = update.message.document.file_name
    file_size = file.file_size
    if file_size <= 4 * 1024 * 1024 * 1024:  # Check if file size is less than or equal to 4GB
        update.message.reply_text(f"Received {file_name}. Starting to unzip...")

        # Callback function to track progress
        def progress(current, total):
            percent = (current / total) * 100
            update.message.reply_text(f"Unzipping... {percent:.2f}% completed ({current/1024/1024:.2f}MB / {total/1024/1024:.2f}MB)")

        try:
            # Unzip the file
            Archive(file.download_as_bytearray()).extractall('.', auto_create_dir=True, progress=progress)
            update.message.reply_text("Unzipping complete. Here are the files:")
            
            # Send back all unzipped files
            for unzipped_file in os.listdir('.'):
                if os.path.isfile(unzipped_file):
                    context.bot.send_document(update.effective_chat.id, open(unzipped_file, 'rb'))
                    
        except Exception as e:
            update.message.reply_text(f"Error occurred while unzipping the file: {str(e)}")
    else:
        update.message.reply_text("File size exceeds 4GB. Please upload a file with size less than or equal to 4GB.")

# Function to handle unknown commands
def unknown(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Sorry, I didn't understand that command.")

def main() -> None:
    # Get the Telegram bot token from environment variable
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    if not TOKEN:
        print("Please set TELEGRAM_TOKEN environment variable.")
        return

    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    # Add handlers for commands and messages
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.document.mime_type("application/zip"), handle_zip))
    dispatcher.add_handler(MessageHandler(Filters.command, unknown))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
