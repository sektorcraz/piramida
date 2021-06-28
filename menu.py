from telebot import types


menu_access_no = types.InlineKeyboardMarkup(row_width=3)
menu_access_no.add(
    types.InlineKeyboardButton(text='Купить доступ', callback_data='buy_access'),                       # +
    types.InlineKeyboardButton(text='Профиль', callback_data='profile'),                                # +
    types.InlineKeyboardButton(text='Информаци', callback_data='access_no_info'),                       # +
    types.InlineKeyboardButton(text='Тех. Поддержка', callback_data='support_no')                       # +
)

menu_access_yes = types.InlineKeyboardMarkup(row_width=2)
menu_access_yes.add(
    types.InlineKeyboardButton(text='Профиль', callback_data='profile'),                                # +
    types.InlineKeyboardButton(text='Информация', callback_data='access_yes_info'),                     # +
    types.InlineKeyboardButton(text='Запросить выплату', callback_data='order_payout'),                 # +
    types.InlineKeyboardButton(text='Тех. Поддержка', callback_data='support_yes')                      # -
)

menu_admin = types.InlineKeyboardMarkup(row_width=2)
menu_admin.add(
    types.InlineKeyboardButton(text='Информация', callback_data='admin_info'),                          # +
    types.InlineKeyboardButton(text='Запросы на вывод', callback_data='admin_list_order_payment'),      # +
    types.InlineKeyboardButton(text='Прибыль', callback_data='admin_profit'),                           # +
    types.InlineKeyboardButton(text='Выйти из админки', callback_data='go_main_menu')                   # +
)

btn_close = types.InlineKeyboardMarkup(row_width=3)
btn_close.add(
    types.InlineKeyboardButton(text='❌', callback_data='close')
)

menu_buy_access = types.InlineKeyboardMarkup(row_width=3)
menu_buy_access.add(
    types.InlineKeyboardButton(text='🔄 Проверить оплату', callback_data='check_payment'),
    types.InlineKeyboardButton(text='Отменить покупку', callback_data='cancel_payment')
)

btn_back_to_admin_menu = types.InlineKeyboardMarkup(row_width=3)
btn_back_to_admin_menu.add(
    types.InlineKeyboardButton(text='Вернуться в админ меню', callback_data='back_to_admin_menu')
)

admin_order_info = types.InlineKeyboardMarkup(row_width=3)
admin_order_info.add(
    types.InlineKeyboardButton(text='Удалить из списка', callback_data='del_order'),
    types.InlineKeyboardButton(text='Выйти', callback_data='back_to_admin_menu')
)