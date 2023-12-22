from telegram import Update, ParseMode
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, Dispatcher
from telegram.ext import MessageHandler, CommandHandler, CallbackQueryHandler
from telegram.ext import CallbackContext
from telegram.ext import Filters


from fum import register_handler

import logging
import datetime
TOKEN = "6376650036:AAHf858D7GreG8iQAanhR-Ypqmt_aZVt1k0"
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(name)s: %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)





def main():
    updater = Updater(token=TOKEN)

    dispatcher: Dispatcher = updater.dispatcher

    echo_handler = MessageHandler(Filters.text, do_echo)
    start_handler = CommandHandler(['start', 'help'], do_start)
    keyboard_handler = CommandHandler('keyboard', do_keyboard)
    inline_keyboard_handler = CommandHandler('inline_keyboard', do_inline_keyboard)
    callback_handler = CallbackQueryHandler(keyboard_react)
    start_timer_handler = CommandHandler('set_timer', set_timer)
    stop_timer_handler = CommandHandler('stop_timer', stop_timer)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(keyboard_handler)
    dispatcher.add_handler(inline_keyboard_handler)
    dispatcher.add_handler(callback_handler)
    dispatcher.add_handler(register_handler)
    dispatcher.add_handler(start_timer_handler)
    dispatcher.add_handler(stop_timer_handler)
    dispatcher.add_handler(echo_handler)


    updater.start_polling()
    logger.info(updater.bot.getMe())
    updater.idle()


def do_echo(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    text = update.message.text

    logger.info(f'{username=} {user_id=} вызвал функцию echo')
    answer = [
        f'Твой {user_id=}',
        f'Твой {username=}',
        f'Ты написал {text}'
    ]
    answer = '\n'.join(answer)
    update.message.reply_text(answer, reply_markup=ReplyKeyboardRemove())


def do_start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    logger.info(f'{user_id=} вызвал функцию start')
    text = ['Приветствую тебя, кожаный мешок!',
            f'Твой {user_id=}',
            'Я знаю команды:',
            '/start',
            '/keyboard',
            '/register',
            '/inline_keyboard',
            "<B>Жирный</B>"]
    text = '\n'.join(text)
    # context.bot.send_message(user_id, text)
    update.message.reply_text(text, parse_mode=ParseMode.HTML)


def do_keyboard(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    logger.info(f'{user_id=} вызвал функцию do_keyboard')
    buttons = [  # 3 ряда кнопок
        ['Раз', 'Два'],
        ['Три', 'Четыре'],
        ['нажми сюда']
    ]
    logger.info(f'Созданы кнопки {buttons}')
    keyboard = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    logger.info(f'Создана клавиатура {keyboard}')
    text = 'Выбери одну из опций на клавиатуре'
    update.message.reply_text(text, reply_markup=keyboard)
    logger.info(f'Ответ улетел')


def do_inline_keyboard(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    logger.info(f'{user_id=} вызвал функцию do_inline_keyboard')
    buttons = [
        ['Раз', 'Два'],
        ['Три', 'Четыре'],
        ['Погода в Москве']
    ]
    keyboard_buttons = [[InlineKeyboardButton(text=text, callback_data=text) for text in row] for row in buttons]
    keyboard = InlineKeyboardMarkup(keyboard_buttons)
    logger.info(f'Создана клавиатура {keyboard}')
    text = 'Выбери одну из опций на клавиатуре'
    update.message.reply_text(text, reply_markup=keyboard)
    logger.info(f'Ответ улетел')


def keyboard_react(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = update.effective_user.id
    logger.info(f'{user_id=} вызвал функцию keyboard_react')
    buttons = [
        ['Раз', 'Два'],
        ['Три', 'Четыре'],
        ['Погода в Москве']
    ]
    for row in buttons:
        if query.data in row:
            row.pop(row.index(query.data))
    keyboard_buttons = [[InlineKeyboardButton(text=text, callback_data=text) for text in row] for row in buttons]
    keyboard = InlineKeyboardMarkup(keyboard_buttons)
    text = 'Выбери другую опцию на клавиатуре'
    query.edit_message_text(text,
        reply_markup=keyboard
    )

def set_timer(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    context.bot_data['user_id'] = user_id
    context.bot_data['timer'] = datetime.datetime.now()
    context.bot_data['timer_job'] = context.job_queue.run_repeating(show_seconds, 1)


def show_seconds(context: CallbackContext):
    logger.info(f'таймер работает {context.job_queue.jobs()}')
    message_id = context.bot_data.get('message_id', None)
    logger.info(f"{message_id}")
    user_id = context.bot_data['user_id']
    timer = datetime.datetime.now() - context.bot_data['timer']
    timer = timer.seconds
    text = f'ты молишься уже {timer} секунд.'
    text += '\nнажми /stop, чтобы остановить таймер.'
    if not message_id:
        message = context.bot.send_message(user_id, text)
        context.bot_data['message_id'] = message.message_id
    else:
        context.bot.edit_message_text(text, chat_id=user_id, message_id=message_id)


def stop_timer(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    logger.info(f'{user_id} запутсил delete_timer')
    timer = datetime.datetime.now() - context.bot_data['timer']
    timer = timer.seconds
    context.bot_data['timer_job'].schedule_removal()
    update.message.reply_text(f'Таймер молитв остановлен. Ты молился {timer} секунд.')
    context.bot_data["message_id"] = None






if __name__ == "__main__":
    main()
