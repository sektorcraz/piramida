import requests
import telebot
import json
import settings
import text as txt
import sqlite3
import datetime
import text
import menu
import random
import traceback

list_order_payment = []

num_order = None

balance_dict = {}


class Balance:
    def __init__(self, user_id):
        self.user_id = user_id
        self.balance = None
        self.sum = None
        self.number = None


def check_payment(user_id):
    conn = sqlite3.connect('base_pyramid.sqlite')
    cursor = conn.cursor()
    check = 0
    
    session = requests.Session()
    session.headers['authorization'] = 'Bearer ' + settings.QIWI_TOKEN
    parameters = {'rows': '5'}
    h = session.get(
        'https://edge.qiwi.com/payment-history/v1/persons/{}/payments'.format(settings.QIWI_NUMBER),
        params=parameters)
    req = json.loads(h.text)
    result = cursor.execute(f'SELECT * FROM check_payment WHERE user_id = {user_id}').fetchone()
    comment = result[2]
    suma = result[1]

    for i in range(len(req['data'])):
        if comment in str(req['data'][i]['comment']):
            if str(suma) in str(req['data'][i]['sum']['amount']):
                cursor.execute(f'DELETE FROM check_payment WHERE user_id = "{user_id}"')
                conn.commit()

                cursor.execute(f'INSERT INTO access VALUES ("{user_id}", "0")')
                conn.commit()

                create_table_user(user_id)

                distribution_pay(user_id)

                distribution_pay_2(user_id)

                check = 1
    if check == 0:
        msg = '❌ Оплата не найдена'
        return msg, check
    if check == 1:
        msg = '✅ Оплата прошла, вы получили доступ!\n\n'
        return msg, check

    


def create_table_user(user_id):
    conn = sqlite3.connect('base_pyramid.sqlite')
    cursor = conn.cursor()

    cursor.execute(f'CREATE TABLE "{user_id}_list" (network text)')

    cursor.execute(f'CREATE TABLE "{user_id}_balance" (balance text, from_whom text, data text)')

    cursor.execute(f'SELECT * FROM users WHERE user_id = "{user_id}"')
    row = cursor.fetchall()

    if row[0][3] == '0':
        cursor.execute(f'INSERT INTO "{user_id}_list" VALUES ("{settings.ADMIN_ID}");')
        conn.commit()
    else:
        cursor.execute(f'INSERT INTO "{user_id}_list" VALUES ("{settings.ADMIN_ID}")')
        conn.commit()

        cursor.execute(f'SELECT * FROM users WHERE referral_code = "{row[0][3]}"')
        row = cursor.fetchall()

        cursor.execute(f'INSERT INTO "{user_id}_list" VALUES ("{row[0][0]}")')
        conn.commit()
        try:
            if row[0][3] == '0':
                pass
            else:
                cursor.execute(f'SELECT * FROM users WHERE referral_code = "{row[0][3]}"')
                row = cursor.fetchall()
                
                cursor.execute(f'INSERT INTO "{user_id}_list" VALUES ("{row[0][0]}")')
                conn.commit()
                
                print(row)
                if row[0][3] == '0':
                    pass
                else:
                    cursor.execute(f'SELECT * FROM users WHERE referral_code = "{row[0][3]}"')
                    row = cursor.fetchall()

                    cursor.execute(f'INSERT INTO "{user_id}_list" VALUES ("{row[0][0]}")')
                    conn.commit()
        except: pass


def distribution_pay(user_id):
    conn = sqlite3.connect('base_pyramid.sqlite')
    cursor = conn.cursor()

    cursor.execute(f'SELECT * FROM "{user_id}_list"')
    row = cursor.fetchall()

    data = datetime.datetime.now()

    count = 0

    if len(row) < 4:
        ln = len(row)

        ln = ln - 1

        if ln == 2:
            cursor.execute(f'''INSERT INTO "{row[1][0]}_balance" VALUES ("{settings.ACCESS_COST * settings.PERCENT_1}",
                                             "{user_id}", "{data}")''')
            conn.commit()

            cursor.execute(f'''INSERT INTO "{row[2][0]}_balance" VALUES ("{settings.ACCESS_COST * settings.PERCENT_2}",
                                                         "{user_id}", "{data}")''')
            conn.commit()

            percent_admin = 1 - (settings.PERCENT_1 + settings.PERCENT_2)

            cursor.execute(f'''INSERT INTO ADMIN_BALANCE VALUES ("{settings.ACCESS_COST * percent_admin}",
                         "{user_id}", "{data}")''')
            conn.commit()
        if ln == 1:
            cursor.execute(f'''INSERT INTO "{row[1][0]}_balance" VALUES ("{settings.ACCESS_COST * settings.PERCENT_1}",
                                                         "{user_id}", "{data}")''')
            conn.commit()

            percent_admin = 1 - settings.PERCENT_1

            cursor.execute(f'''INSERT INTO ADMIN_BALANCE VALUES ("{settings.ACCESS_COST * percent_admin}",
                                     "{user_id}", "{data}")''')
            conn.commit()
    else:
        for i in row:
            if i == settings.ADMIN_ID:
                cursor.execute(f'''INSERT INTO ADMIN_BALANCE VALUES ("{settings.ACCESS_COST * settings.PERCENT_ADMIN}",
                 "{user_id}", "{data}")''')
                conn.commit()
            else:
                if count == 1:
                    cursor.execute(f'''INSERT INTO "{i[0]}_balance" VALUES ("{settings.ACCESS_COST * settings.PERCENT_1}",
                                     "{user_id}", "{data}")''')
                    conn.commit()
                if count == 2:
                    cursor.execute(f'''INSERT INTO "{i[0]}_balance" VALUES ("{settings.ACCESS_COST * settings.PERCENT_2}",
                                     "{user_id}", "{data}")''')
                    conn.commit()
                if count == 3:
                    cursor.execute(f'''INSERT INTO "{i[0]}_balance" VALUES ("{settings.ACCESS_COST * settings.PERCENT_3}",
                                     "{user_id}", "{data}")''')
                    conn.commit()
            count += 1


def distribution_pay_2(user_id):
    try:
        conn = sqlite3.connect('base_pyramid.sqlite')
        cursor = conn.cursor()

        cursor.execute(f'SELECT * FROM "{user_id}_list"')
        row = cursor.fetchall()

        count = 0

        if len(row) < 4:
            ln = len(row)

            ln = ln - 1

            if ln == 2:
                cursor.execute(f'SELECT * FROM access WHERE user_id = "{row[1][0]}"')
                price = settings.ACCESS_COST * settings.PERCENT_1
                balance_user = float(cursor.fetchall()[0][1]) + price
                cursor.execute(f'UPDATE access SET balance = "{balance_user}" WHERE user_id = "{row[1][0]}"')
                conn.commit()

                cursor.execute(f'SELECT * FROM access WHERE user_id = "{row[2][0]}"')
                price = settings.ACCESS_COST * settings.PERCENT_2
                balance_user = float(cursor.fetchall()[0][1]) + price
                cursor.execute(f'UPDATE access SET balance = "{balance_user}" WHERE user_id = "{row[2][0]}"')
                conn.commit()

            if ln == 1:
                cursor.execute(f'SELECT * FROM access WHERE user_id = "{row[1][0]}"')
                price = settings.ACCESS_COST * settings.PERCENT_1
                balance_user = float(cursor.fetchall()[0][1]) + price
                cursor.execute(f'UPDATE access SET balance = "{balance_user}" WHERE user_id = "{row[1][0]}"')
                conn.commit()

        else:
            for i in row[0]:
                if count == 1:
                    cursor.execute(f'SELECT * FROM access WHERE user_id = "{i[0]}"')
                    price = settings.ACCESS_COST * settings.PERCENT_1
                    balance_user = float(cursor.fetchall()[0][1]) + price
                    cursor.execute(f'UPDATE access SET balance = "{balance_user}" WHERE user_id = "{i[0]}"')
                    conn.commit()
                if count == 2:
                    cursor.execute(f'SELECT * FROM access WHERE user_id = "{i[0]}"')
                    price = settings.ACCESS_COST * settings.PERCENT_2
                    balance_user = float(cursor.fetchall()[0][1]) + price
                    cursor.execute(f'UPDATE access SET balance = "{balance_user}" WHERE user_id = "{i[0]}"')
                    conn.commit()
                if count == 3:
                    cursor.execute(f'SELECT * FROM access WHERE user_id = "{i[0]}"')
                    price = settings.ACCESS_COST * settings.PERCENT_3
                    balance_user = float(cursor.fetchall()[0][1]) + price
                    cursor.execute(f'UPDATE access SET balance = "{balance_user}" WHERE user_id = "{i[0]}"')
                    conn.commit()
                count += 1

        price = settings.ACCESS_COST * settings.PERCENT_ADMIN
        cursor.execute(f'INSERT INTO ADMIN_BALANCE VALUES ("{price}", "{user_id}", "{datetime.datetime.now()}")')
        conn.commit()

    except Exception as e:
        pass

def profile(user_id, name):
    conn = sqlite3.connect('base_pyramid.sqlite')
    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM access WHERE user_id = "{user_id}"')
    row = cursor.fetchall()

    if len(row) == 0:
        return text.profile.format(id=user_id, name=name, access='❌'), menu.menu_access_no
    if len(row) > 0:
        return text.profile.format(id=user_id, name=name, access='✅'), menu.menu_access_yes


def buy_access(user_id):
    conn = sqlite3.connect('base_pyramid.sqlite')
    cursor = conn.cursor()

    code = random.randint(1111111111, 9999999999)

    msg = text.buy_access.format(code=code)

    cursor.execute(f'INSERT INTO check_payment VALUES ("{user_id}", "{settings.ACCESS_COST}", "{code}")')
    conn.commit()

    return msg


def cancel_payment(user_id):
    conn = sqlite3.connect('base_pyramid.sqlite')
    cursor = conn.cursor()

    cursor.execute(f'DELETE FROM check_payment WHERE user_id = "{user_id}"')
    conn.commit()

    msg = '❕ Покупка отменена\n' \
          '❕ Вы перемещены в главное меню'

    return msg


def admin_profit():
    conn = sqlite3.connect('base_pyramid.sqlite')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM ADMIN_BALANCE')
    row = cursor.fetchall()

    profit = 0

    for i in range(len(row)):
        profit += float(row[i][0])

    return text.admin_profit.format(profit)


def admin_info():
    conn = sqlite3.connect('base_pyramid.sqlite')
    cursor = conn.cursor()

    cursor.execute(f'SELECT * FROM users')
    row = cursor.fetchall()

    users = len(row)

    cursor.execute(f'SELECT * FROM access')
    row = cursor.fetchall()

    all_deposit = len(row)

    return text.admin_info.format(users=users, deposit=all_deposit)


def admin_list_order_payment():
    conn = sqlite3.connect('base_pyramid.sqlite')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM order_payment')
    row = cursor.fetchall()

    text = ''
    num = 0

    global list_order_payment
    list_order_payment = row

    for i in range(len(row)):
        text += f'🔥 {num} | USER ID {row[i][1]} | Сумма {row[i][3]}\n'
        num += 1

    return text


def admin_info_order_payment(num):
    num = int(num)
    msg = text.order_payment.format(
        list_order_payment[num][0],
        list_order_payment[num][1],
        list_order_payment[num][2],
        list_order_payment[num][3],
        list_order_payment[num][4],
        list_order_payment[num][5],
    )
    id_order = list_order_payment[num][0]

    return msg, id_order


def del_order(num):
    conn = sqlite3.connect('base_pyramid.sqlite')
    cursor = conn.cursor()

    cursor.execute(f'DELETE FROM order_payment WHERE ID = {num}')
    conn.commit()

    msg = '✅ Запрос успешно удалён'
    return msg


def access_yes_info(user_id):
    # code url profit users
    conn = sqlite3.connect('base_pyramid.sqlite')
    cursor = conn.cursor()

    cursor.execute(f'SELECT * FROM users WHERE user_id = "{user_id}"')
    ref_code = cursor.fetchone()[4]
    ref_url = f'https://tele.gg/{settings.BOT_LOGIN}?start={ref_code}'

    cursor.execute(f'SELECT * FROM users')
    row = cursor.fetchall()
    amount_invite_users = 0

    for i in range(len(row)):
        if row[i][3] == ref_code:
            amount_invite_users += 1

    cursor.execute(f'SELECT * FROM access WHERE user_id ="{user_id}"')
    profit = cursor.fetchone()[1]

    msg = text.access_yes_info.format(ref_code=ref_code,
                                      ref_url=ref_url,
                                      profit=profit,
                                      amount_invite_users=amount_invite_users)

    return msg


def order_payout(user_id):
    conn = sqlite3.connect('base_pyramid.sqlite')
    cursor = conn.cursor()

    cursor.execute(f'SELECT * FROM access WHERE user_id = "{user_id}"')
    profit = cursor.fetchone()

    msg = text.withdraw.format(profit[1])

    return msg, profit[1]


def order_payout_2(user_id, sum, name, qiwi):
    ID = random.randint(1111111111, 9999999999)
    data = datetime.datetime.now()

    conn = sqlite3.connect('base_pyramid.sqlite')
    cursor = conn.cursor()

    cursor.execute(f'INSERT INTO order_payment VALUES ("{ID}", "{user_id}", "{name}", "{sum}", "{data}", "{qiwi}")')
    conn.commit()

    cursor.execute(f'SELECT * FROM access WHERE user_id = "{user_id}"')
    balance = cursor.fetchone()[1]

    balance = float(balance) - float(sum)

    cursor.execute(f'UPDATE access SET balance = "{balance}" WHERE user_id = "{user_id}"')
    conn.commit()

def free(user_id, code):
    conn = sqlite3.connect('base_pyramid.sqlite')
    cursor = conn.cursor()

    cursor.execute(f'INSERT INTO access VALUES ("{user_id}", "0")')
    conn.commit()

    cursor.execute(f'UPDATE users SET who_invite = "{code}" WHERE user_id = "{user_id}"')
    conn.commit()

    cursor.execute(f'CREATE TABLE "{user_id}_list" (network text)')

    cursor.execute(f'CREATE TABLE "{user_id}_balance" (balance text, from_whom text, data text)')

    cursor.execute(f'INSERT INTO "{user_id}_list" VALUES ("{settings.ADMIN_ID}")')
    conn.commit()













