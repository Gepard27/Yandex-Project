# Импортируем необходимые классы.
import logging
from datetime import datetime

from sqlalchemy import desc, select
from telegram import ReplyKeyboardMarkup
from telegram.ext import (Application, CommandHandler, ConversationHandler,
                          MessageHandler, filters)

from config import BOT_TOKEN
from db.base import session_factory
from db.models import Expence

# Запускаем логгирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG,
)

logger = logging.getLogger(__name__)

NAME, PRICE, DATE = range(3)

reply_keyboard = [["/help", "/budget"], ["/add", "/delete"]]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)


async def start(update, context):
    await update.message.reply_text(
        "Я бот-справочник. Какая информация вам нужна?", reply_markup=markup
    )


async def help_command(update, context):
    await update.message.reply_text(
        "Это справочник со всеми командами: \n "
        "'/budget'- Команда, показывающая все твои траты/зароботки \n "
        "'/add' - добавить расход/доход,\n "
        " '/delete' - удалить расход/доход",
        reply_markup=markup,
    )


async def budget_command(update, context):
    with session_factory() as session:
        query = (
            select(Expence)
            .filter(Expence.user_id == update.message.from_user.id)
            .order_by(desc(Expence.expence_date))
        )
        cursor = session.execute(query)
        answ = []
        for i in cursor.scalars().all():
            answ.append(
                f"#: {i.id} Наименование: {i.name} Цена: {i.cost} Дата: {i.expence_date.strftime('%Y-%m-%d')} \n"
            )
        await update.message.reply_text("".join(answ))


async def delete_command(update, context):
    try:
        expence_id = int(context.args[0])
        if expence_id <= 0:
            await update.message.reply_text(
                "Id не может быть меньше или равным нулю"
            )
        else:
            with session_factory() as session:
                expence = session.get(Expence, expence_id)
                if expence is None:
                    await update.message.reply_text(
                        "Траты/дохода с таким id не найден"
                    )
                session.delete(expence)
                session.commit()
                await update.message.reply_text("запись успешно удалена")
    except ValueError:
        await update.message.reply_text("id должен быть числом")
    except IndexError:
        await update.message.reply_text(
            "введите id записи, вы не ввели id, общая форма команды выглядит как: /delete int"
        )


async def start_adding(update, context) -> int:
    await update.message.reply_text(
        "Ты попал в раздел добавления дохода/расхода. \n"
        "Также отменить добавление можно комадой /cancel"
        "Напиши название траты/дохода, которое будет отображаться в статистике:",
        reply_markup=ReplyKeyboardMarkup(
            [["/cancel"]], one_time_keyboard=True
        ),
    )

    return NAME


async def name(update, context) -> int:
    text = update.message.text
    context.user_data["name"] = text

    await update.message.reply_text(
        "Окей, теперь введи доход/расход с этого действия\n"
        "Если это был расход введи со знаком '-', например: -1337 \n"
        "Если это был доход - введи без знаком, например 1337",
        reply_markup=ReplyKeyboardMarkup(
            [["/cancel"]], one_time_keyboard=True
        ),
    )

    return PRICE


async def price(update, context) -> int:
    text = update.message.text
    context.user_data["price"] = text
    await update.message.reply_text(
        "Супер, теперь введи дату дохода/расхода в формате: YYYY-MM-dd\n",
        reply_markup=ReplyKeyboardMarkup(
            [["/cancel"]], one_time_keyboard=True
        ),
    )
    return DATE


async def end_adding(update, context):
    user_date = update.message.text
    user = update.message.from_user
    try:
        py_date = datetime.strptime(user_date, "%Y-%m-%d")
        price = context.user_data["price"]
        name = context.user_data["name"]
        with session_factory() as session:
            new_expence = Expence(
                user_id=user.id, cost=price, expence_date=py_date, name=name
            )
            session.add(new_expence)
            session.commit()
        await update.message.reply_text(
            "Запись добавлена",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True
            ),
        )
    except ValueError:
        await update.message.reply_text(
            "Дата не в формате YYYY-MM-dd, попробуй еще раз"
        )
        return DATE
    return ConversationHandler.END


async def cancel(update, context) -> int:
    await update.message.reply_text(
        "Вы отменили добавление расхода/траты",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True
        ),
    )
    return ConversationHandler.END


def main():

    # Создаём объект Application.
    # Вместо слова "TOKEN" надо разместить полученный от @BotFather токен
    application = Application.builder().token(BOT_TOKEN).build()

    # Создаём обработчик сообщений типа filters.TEXT
    # из описанной выше асинхронной функции echo()
    # После регистрации обработчика в приложении
    # эта асинхронная функция будет вызываться при получении сообщения
    # с типом "текст", т. е. текстовых сообщений.
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("add", start_adding)],
        states={
            NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, name),
            ],
            PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, price)],
            DATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, end_adding)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("budget", budget_command))
    application.add_handler(CommandHandler("delete", delete_command))

    # Запускаем приложение.
    application.run_polling()


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == "__main__":
    main()
