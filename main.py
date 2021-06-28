import telebot
import settings
import sqlite3
import datetime
import menu
import text
import logic
from telebot import types
from random import choice
from string import ascii_uppercase


def start_bot():

    bot = telebot.TeleBot(settings.BOT_TOKEN)

    @bot.message_handler(commands=['start'])
    def start(message):
        conn = sqlite3.connect('base_pyramid.sqlite')
        cursor = conn.cursor()

        cursor.execute(f'SELECT * FROM access WHERE user_id = "{message.chat.id}"')
        row = cursor.fetchall()

        if len(row) == 0:
            cursor.execute(f'SELECT * FROM users WHERE user_id = "{message.chat.id}"')
            row = cursor.fetchall()

            if len(row) == 0:
                who_invite = 0
                if message.text[7:] == '':
                    who_invite = 0
                else:
                    who_invite = message.text[7:]
                referral_code = ''.join(choice(ascii_uppercase) for i in range(12))
                cursor.execute(f'INSERT INTO users VALUES ("{message.chat.id}", "{message.from_user.username}", "{datetime.datetime.now()}", "{who_invite}", "{referral_code}", "no")')
                conn.commit()

                bot.send_message(chat_id=message.chat.id,
                                 text=text.start_menu.format(name=message.from_user.first_name, id=message.chat.id),
                                 reply_markup=menu.menu_access_no)
            if len(row) > 0:
                bot.send_message(chat_id=message.chat.id,
                                 text=text.start_menu.format(name=message.from_user.first_name, id=message.chat.id),
                                 reply_markup=menu.menu_access_no)
        else:
            bot.send_message(chat_id=message.chat.id,
                             text=text.start_menu.format(name=message.from_user.first_name, id=message.chat.id),
                             reply_markup=menu.menu_access_yes)

    @bot.message_handler(commands=['admin'])
    def admin(message):
        if message.chat.id == settings.ADMIN_ID:
            bot.send_message(chat_id=message.chat.id,
                             text=text.admin_menu.format(name=message.from_user.first_name),
                             reply_markup=menu.menu_admin)

    @bot.message_handler(content_types=['text'])
    def free(message):
        lzt = f'{settings.CODE_ACCESS}{str(datetime.datetime.now())[:10]}'
        if message.text == lzt:
            conn = sqlite3.connect('base_pyramid.sqlite')
            cursor = conn.cursor()

            cursor.execute(f'SELECT * FROM access WHERE user_id = "{message.chat.id}"')
            row = cursor.fetchall()

            if len(row) == 0:
                print('tyt')
                logic.free(message.chat.id, lzt)
                bot.send_message(message.chat.id,
                                 text=f'Доступ успешно получен по коду - {lzt}',
                                 reply_markup=menu.menu_access_yes)

    @bot.callback_query_handler(func=lambda call: True)
    def handler_call(call):
        chat_id = call.message.chat.id
        message_id = call.message.message_id

        if call.data == 'buy_access':
            bot.edit_message_text(chat_id=chat_id,
                                  message_id=message_id,
                                  text=logic.buy_access(user_id=chat_id),
                                  reply_markup=menu.menu_buy_access)

        if call.data == 'check_payment':
            check = logic.check_payment(user_id=chat_id)

            if check[1] == 0:
                bot.send_message(chat_id=chat_id,
                                 text=check[0],
                                 reply_markup=menu.btn_close)
            if check[1] == 1:
                bot.edit_message_text(chat_id=chat_id,
                                      message_id=message_id,
                                      text=check[0],
                                      reply_markup=menu.menu_access_yes)

        if call.data == 'cancel_payment':
            bot.edit_message_text(chat_id=chat_id,
                                  message_id=message_id,
                                  text=logic.cancel_payment(user_id=chat_id),
                                  reply_markup=menu.menu_access_no)

        if call.data == 'close':
            try:
                bot.delete_message(chat_id=chat_id,
                                   message_id=message_id)
            except: pass

        if call.data == 'profile':
            try:
                profile = logic.profile(user_id=chat_id, name=call.from_user.first_name)
                bot.edit_message_text(chat_id=chat_id,
                                      message_id=message_id,
                                      text=profile[0],
                                      reply_markup=profile[1])
            except: pass

        if call.data == 'access_no_info':
            try:
                bot.edit_message_text(chat_id=chat_id,
                                      message_id=message_id,
                                      text=text.access_no_info,
                                      reply_markup=menu.menu_access_no)
            except: pass

        if call.data == 'access_yes_info':
            try:
                bot.edit_message_text(chat_id=chat_id,
                                      message_id=message_id,
                                      text=logic.access_yes_info(chat_id),
                                      reply_markup=menu.menu_access_yes)
            except: pass

        if call.data == 'support_no':
            try:
                bot.edit_message_text(chat_id=chat_id,
                                      message_id=message_id,
                                      text=text.support,
                                      reply_markup=menu.menu_access_no)
            except: pass

        if call.data == 'support_yes':
            try:
                bot.edit_message_text(chat_id=chat_id,
                                      message_id=message_id,
                                      text=text.support,
                                      reply_markup=menu.menu_access_yes)
            except: pass

        if call.data == 'admin_profit':
            try:
                bot.edit_message_text(chat_id=chat_id,
                                      message_id=message_id,
                                      text=logic.admin_profit(),
                                      reply_markup=menu.menu_admin)
            except: pass

        if call.data == 'admin_info':
            try:
                bot.edit_message_text(chat_id=chat_id,
                                      message_id=message_id,
                                      text=logic.admin_info(),
                                      reply_markup=menu.menu_admin)
            except: pass

        if call.data == 'admin_list_order_payment':
            msg = bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f'❗️ Список запросов на вывод\n\n' \
                     f'{logic.admin_list_order_payment()}'
                     f'\n❗️ Введите номер запроса для получения подробной информации',
                reply_markup=menu.btn_back_to_admin_menu)

            bot.register_next_step_handler(msg, info_order_payment)

        if call.data == 'back_to_admin_menu':
            bot.edit_message_text(chat_id=chat_id,
                                  message_id=message_id,
                                  text='Админ меню',
                                  reply_markup=menu.menu_admin)

        if call.data == 'del_order':
            bot.send_message(chat_id=chat_id,
                             text=logic.del_order(logic.num_order),
                             reply_markup=menu.btn_back_to_admin_menu)

        if call.data == 'go_main_menu':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            markup.add(types.KeyboardButton('Yes'))

            msg = bot.send_message(chat_id, '❗️ Вы хотите выйти из меню админа?', reply_markup=markup)
            bot.register_next_step_handler(msg, start)

        if call.data == 'order_payout':
            info = logic.order_payout(chat_id)
            msg = bot.send_message(chat_id, text=info[0])

            balance = logic.Balance(chat_id)

            logic.balance_dict[chat_id] = balance

            balance = logic.balance_dict[chat_id]
            balance.balance = info[1]
            bot.register_next_step_handler(msg, order_payout_2)

    def info_order_payment(message):
        try:
            info = logic.admin_info_order_payment(message.text)

            bot.send_message(chat_id=message.chat.id,
                             text=info[0],
                             reply_markup=menu.admin_order_info)

            logic.num_order = info[1]

        except Exception as e:
            bot.send_message(chat_id=message.chat.id,
                             text='Упсс, что-то пошло не по плану',
                             reply_markup=menu.btn_back_to_admin_menu)

    def order_payout_2(message):
        try:
            balance = logic.balance_dict[message.chat.id]
            balance.sum = float(message.text)
            if float(message.text) < settings.MIN_PAYOUT:
                bot.send_message(message.chat.id,
                                 text='❌ Введенная сумма меньше минимальной',
                                 reply_markup=menu.menu_access_yes)
            if float(message.text) > balance.balance:
                bot.send_message(message.chat.id,
                                 text='❌ На балансе недостаточно средст',
                                 reply_markup=menu.menu_access_yes)
            if float(message.text) >= settings.MIN_PAYOUT and float(message.text) <= float(balance.balance):
                msg = bot.send_message(message.chat.id,
                                       text=f'❗️ Сумма - {balance.sum}\n'
                                            f'❗️ Введите свой номер qiwi, на него будет произведена выплата!\n')
                bot.register_next_step_handler(msg, order_payout_3)
        except Exception as e:
            pass
            bot.send_message(chat_id=message.chat.id,
                             text='Упсс, что-то пошло не по плану',
                             reply_markup=menu.menu_access_yes)

    def order_payout_3(message):
        balance = logic.balance_dict[message.chat.id]
        balance.number = message.text

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add('Yes', 'No')

        msg = bot.send_message(text=f'❗️ Проверьте данные и подтвердите запрос\n\n'
                               f'❕ Сумма - {balance.sum}\n'
                               f'❕ Номер - {balance.number}\n\n'
                               f'❗️ Запросить вывод?',
                               chat_id=message.chat.id,
                               reply_markup=markup)

        bot.register_next_step_handler(msg, order_payout_4)

    def order_payout_4(message):
        balance = logic.balance_dict[message.chat.id]
        if message.text == 'Yes':
            logic.order_payout_2(message.chat.id, balance.sum, message.from_user.username, balance.number)
            bot.send_message(message.chat.id,
                             text='✅ Запрос на вывод успешно создан',
                             reply_markup=menu.menu_access_yes)
        if message.text == 'No':
            bot.send_message(message.chat.id,
                             text='❌ Вы отменили создание запроса на вывод средств',
                             reply_markup=menu.menu_access_yes)

    bot.polling(none_stop=True)


start_bot()

