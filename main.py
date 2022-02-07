from constants import CreationState
from Functions.answers import answer_ck, answer_query
from Functions.forms import view_forms_ck, view_query
from Functions.bot_callbacks import (
    answering,
    cancel_command,
    creating_form,
    help_command,
    invalid_qn_number,
    invalid_title,
    invalid_typing_in_answers,
    invalid_typing_in_questions,
    no_of_questions,
    questions_started,
    start_command,
    show_menu,
    stats,
    title_of_form,
    typing_commands_in_CH,
    unknown_commands,
    unknown_messages,
)
import logging

from telegram.botcommand import BotCommand
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    Filters,
    MessageHandler,
    Updater,
)

from Functions.database import db_connect, db_intialize
from CONFIG import api_token

logging.basicConfig(
    filename="logs.log",
    filemode="w",
    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    level=logging.DEBUG,
)

logger = logging.getLogger(__name__)


def main():

    logging.info("\n------LOGGING STARTED-----\n")

    db_intialize(db_connect())

    updater = Updater(api_token)

    d = updater.dispatcher

    d.add_handler(
        ConversationHandler(
            entry_points=[
                (CommandHandler("create", creating_form)),
                MessageHandler(Filters.regex('Create 📝'),creating_form),
                CommandHandler("start", start_command),
            ],
            states={
                CreationState.RECIEVING_ANSWERS: [
                    MessageHandler(Filters.command, typing_commands_in_CH),
                    MessageHandler(Filters.text, answering),
                    MessageHandler(Filters.all, invalid_typing_in_answers),
                ],
                CreationState.RECIEVING_TITLE: [
                    MessageHandler(Filters.command, typing_commands_in_CH),
                    MessageHandler(
                        Filters.text & ~Filters.regex("Cancel"), title_of_form
                    ),
                    MessageHandler(
                        Filters.all & ~Filters.regex("Cancel"), invalid_title
                    ),
                ],
                CreationState.RECIEVING_QUESTION_COUNT: [
                    MessageHandler(Filters.command, typing_commands_in_CH),
                    MessageHandler(Filters.regex("^[0-9]*$"), no_of_questions),
                    MessageHandler(
                        Filters.all & ~Filters.regex("Cancel"), invalid_qn_number
                    ),
                ],
                CreationState.RECIEVING_QUESTIONS: [
                    MessageHandler(Filters.command, typing_commands_in_CH),
                    MessageHandler(
                        Filters.text & ~Filters.regex("Cancel"), questions_started
                    ),
                    MessageHandler(
                        Filters.all & ~Filters.regex("Cancel"),
                        invalid_typing_in_questions,
                    ),
                ],
            },
            fallbacks=[MessageHandler(Filters.regex("Cancel"), cancel_command)],
        )
    )

    d.add_handler(CommandHandler("view_forms", view_forms_ck))
    d.add_handler(CallbackQueryHandler(pattern = "^view_*",callback = view_query))

    d.add_handler(CommandHandler("answers", answer_ck))
    d.add_handler(CallbackQueryHandler(pattern = "^answer_*",callback = answer_query))

    d.add_handler(CommandHandler("help", help_command))
    d.add_handler(CommandHandler("stats", stats))

    d.add_handler(MessageHandler(Filters.regex('🧾 Menu'),show_menu))
    d.add_handler(MessageHandler(Filters.regex("View 🔎"),view_forms_ck))
    d.add_handler(MessageHandler(Filters.regex("Answers ✍"),answer_ck))
    d.add_handler(MessageHandler(Filters.regex('Help ℹ'),help_command))
    d.add_handler(MessageHandler(Filters.regex('Bot Stats 📈'),stats))
    
    
    d.add_handler(MessageHandler(Filters.command, unknown_commands))
    d.add_handler(MessageHandler(Filters.all, unknown_messages))

    updater.bot.set_my_commands(
        [
            BotCommand("start", "Start Me"),
            BotCommand("create", "Form Creation"),
            BotCommand("view_forms", "Your Forms"),
            BotCommand("answers", "Answers for your Forms"),
            BotCommand("help", "Available commands"),
            BotCommand("stats", "Get bot statistics"),
        ]
    )
    updater.start_polling()

    updater.idle()


if __name__ == "__main__":
    main()
