import datetime
import os
import json
import logging
from dotenv import load_dotenv
from typing import Dict

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from core import manager

# load_dotenv()

TOKEN = os.getenv("TOKEN", "none")
ALLOWED_USERS = int(os.getenv("ALLOWED_USERS", 0))

TAGS_PK = json.loads(os.getenv('TAGS_PK'))
ACCOUNTS_PK = json.loads(os.getenv('ACCOUNTS_PK'))

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

(
    CHOOSING,
    TYPING_REPLY,
    TYPING_CHOICE,
    CHOOSINGCATEGORY,
    CHOOSINGPLACE,
    CHOOSINGAMOUNT,
    CHOOSINGDATE,
    CHOOSINGACCOUNT,
    END,
) = range(9)


def facts_to_str(user_data: Dict[str, str]) -> str:
    """Helper function for formatting the gathered user info."""
    facts = [f"{key} - {value}" for key, value in user_data.items()]
    return "\n".join(facts).join(["\n", "\n"])

def _get_categories_menu_keyboard() -> ReplyKeyboardMarkup:
    """Helper function for formatting the categories menu keyboard."""
    CATEGORIES_PK = json.loads(os.getenv('CATEGORIES_PK'))

    reply_keyboard = []
    aux = []
    c = 0
    for category in CATEGORIES_PK.keys():
        if c == 5:
            reply_keyboard.append(aux)
            aux = []
            c = 0
        aux.append(category)
        c += 1
    reply_keyboard.append(aux)

    # add cancel option
    reply_keyboard.append(["Cancel transaction"])
    logger.debug(reply_keyboard)
    return reply_keyboard

def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Helper function for formatting the main menu keyboard."""
    reply_keyboard = [
        ["Create Transaction"],
        ["Create category", "Create tag"],
        ["Done"],
    ]
    return ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and ask user for input."""
    markup = get_main_menu_keyboard()
    await update.message.reply_text(
        "Hi! My name is Finance Bot. "
        "Why don't you tell me what is your transaction?",
        reply_markup=markup,
    )
    return CHOOSING


async def create_simple_operation(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Create a Category or a Tag."""
    user = update.message.from_user
    text = update.message.text

    context.user_data["choice"] = text
    field = text.split()[1]
    logger.info(f"USER @{user.username}:{user.id} - {text} operation started.")
    await update.message.reply_text(f"Please enter the new {field} name:")
    return TYPING_REPLY


async def received_information_simple_operation(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:

    user_data = context.user_data
    new_name_of_instance = update.message.text
    operation = user_data["choice"].split()[1]
    user_data[user_data["choice"]] = new_name_of_instance
    del user_data["choice"]
    user = update.message.from_user

    if user.id != ALLOWED_USERS:
        msg = f"Sorry {user.first_name}, you are not allowed to use this bot."
        await update.message.reply_text(msg, reply_markup=ReplyKeyboardRemove())
        user_data.clear()
        return ConversationHandler.END

    # request to create a new operation
    manager.create_simple_entity(entity=operation, name=new_name_of_instance)

    markup = get_main_menu_keyboard()
    msg = f"New `{new_name_of_instance}` {operation} created."
    await update.message.reply_text(
        msg,
        reply_markup=markup,
    )
    return CHOOSING


async def start_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask the user for a description of a custom category."""
    user = update.message.from_user
    logger.info(f"USER @{user.username}:{user.id} - Transaction.")

    keyboard_options_category = _get_categories_menu_keyboard()

    await update.message.reply_text(
        "Please choose from the following options:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard_options_category,
            resize_keyboard=True,
            one_time_keyboard=True,
            input_field_placeholder="Choose an option...",
        ),
    )
    return CHOOSINGCATEGORY


async def choose_tag_for_transaction(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Ask the user for a description of a custom category."""
    text = update.message.text
    keyboard_options_tags = [
        ["Holiday", "None"],
        ["Cancel transaction"],
    ]

    if text == "Cancel transaction":
        await update.message.reply_text(
            "Transaction cancelled.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationHandler.END
    context.user_data["category"] = text
    await update.message.reply_text(
        "Please choose from the following options:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard_options_tags,
            resize_keyboard=True,
            one_time_keyboard=True,
            input_field_placeholder="Choose an option...",
        ),
    )
    return CHOOSINGPLACE


async def choose_place_for_transaction(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Ask the user for a description of a custom category."""
    tag = update.message.text

    if tag == "Cancel transaction":
        await update.message.reply_text(
            "Transaction cancelled.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationHandler.END

    context.user_data["tag"] = None
    if tag != "None":
        context.user_data["tag"] = tag

    await update.message.reply_text("Please enter the `place` name:")

    return CHOOSINGAMOUNT


async def choose_amount_for_transaction(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Ask the user for a description of a custom category."""
    place = update.message.text

    if place == "Cancel transaction":
        await update.message.reply_text(
            "Transaction cancelled.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationHandler.END
    context.user_data["place"] = place
    await update.message.reply_text("Please enter the `amount` you spent €:")
    return CHOOSINGDATE


async def choose_date_for_transaction(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Ask the user for a description of a custom category."""
    amount = update.message.text

    if amount == "Cancel transaction":
        await update.message.reply_text(
            "Transaction cancelled.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationHandler.END
    context.user_data["amount"] = amount
    await update.message.reply_text("Please enter the `date` (YYYY-MM-DD) or `today`:")
    return CHOOSINGACCOUNT


async def choose_account_for_transaction(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Ask the user for a description of a custom category."""
    date = update.message.text

    if date.lower() == "today":
        date = datetime.datetime.now().strftime("%Y-%m-%d")

    context.user_data["date"] = date

    keyboard_options_accounts = [
        ["Revolut", "Wise", "BOI"],
        ["Cancel transaction"],
    ]
    await update.message.reply_text(
        "Please choose a `account` from the following options:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard_options_accounts, resize_keyboard=True, one_time_keyboard=True
        ),
    )
    return END


async def complete_transaction(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Ask the user for a description of a custom category."""
    account = update.message.text

    if account == "Cancel transaction":
        await update.message.reply_text(
            "Transaction cancelled.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationHandler.END
    context.user_data["account"] = account
    data = context.user_data

    manager.create_transaction(
        category=data["category"],
        tag=data["tag"],
        place=data["place"],
        amount=data["amount"],
        date=data["date"],
        account=data["account"],
    )

    markup = get_main_menu_keyboard()
    await update.message.reply_text(
        "Cool! Transaction completed.",
        reply_markup=markup,
    )
    return CHOOSING


async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Display the gathered info and end the conversation."""
    user_data = context.user_data
    if "choice" in user_data:
        del user_data["choice"]

    await update.message.reply_text(
        "I learned these facts about you:" f"{facts_to_str(user_data)}Until next time!",
        reply_markup=ReplyKeyboardRemove(),
    )

    user_data.clear()
    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [
                MessageHandler(
                    filters.Regex("^Create +(tag|category)$"), create_simple_operation
                ),
                MessageHandler(
                    filters.Regex("^Create Transaction$"), start_transaction
                ),
            ],
            CHOOSINGCATEGORY: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")),
                    choose_tag_for_transaction,
                )
            ],
            CHOOSINGPLACE: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")),
                    choose_place_for_transaction,
                )
            ],
            CHOOSINGAMOUNT: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")),
                    choose_amount_for_transaction,
                )
            ],
            CHOOSINGDATE: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")),
                    choose_date_for_transaction,
                )
            ],
            CHOOSINGACCOUNT: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")),
                    choose_account_for_transaction,
                )
            ],
            END: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")),
                    complete_transaction,
                )
            ],
            TYPING_REPLY: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")),
                    received_information_simple_operation,
                )
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^Done$"), done)],
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
