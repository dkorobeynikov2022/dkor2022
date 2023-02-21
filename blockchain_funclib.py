import time
from datetime import datetime
import psycopg2
import base64
import asyncio
import requests
from ton import TonlibClient
from main_config import cdll_filepath_win, cdll_filepath, guarantor_wallet_seed, guarantor_wallet
from main_funclib import get_now
from wallets_funclib import address_to_bounceable

########################################################################################
class AccountTrans:
    def __init__(self):
        self.lt = None
        self.hash = None
        self.time_id = None
        self.direction = None
        self.amount = None
        self.fee = None
        self.message = None
        self.wallet = None
        self.other_wallet = None

    def load_trans(self, trans):
        self.lt = trans.transaction_id.lt
        self.hash = trans.transaction_id.hash
        self.time_id = datetime.fromtimestamp(trans.utime)
        self.fee = float(round(int(trans.fee) / 10 ** 9, 9))
        if trans.in_msg.source.account_address == "":
            self.direction = "out"
            info = trans.out_msgs[0]
            self.wallet = info.source.account_address
            self.other_wallet = info.destination.account_address
        else:
            self.direction = "in"
            info = trans.in_msg
            self.wallet = info.destination.account_address
            self.other_wallet = info.source.account_address

        self.amount = float(round(int(info.value)/ 10 ** 9, 9))

        if info.msg_data.type == "msg.dataText":
            self.message =base64.b64decode(info.msg_data.text).decode('utf-8')
        else:
            self.message = ""

    def get_data_array(self):
        return [self.lt, self.hash, self.wallet, self.other_wallet, self.direction,
                (self.time_id).strftime("%d.%m.%Y %H:%M:%S"), self.amount, self.fee, self.message]

    def show_info(self):
        print(str(self.get_data_array()))

#############################################################################################################
#асинхронное получение баланса кошелька
async def get_balance_async(wallet):
    try:
        client = TonlibClient()
        #await client.init_tonlib(cdll_path = cdll_filepath_win)
        await client.init_tonlib(cdll_path=cdll_filepath)

        account = await client.find_account(wallet)
        balance = await account.get_balance()

        return float(round(int(balance)/ 10 ** 9, 9))

    except Exception as err:
        print(err)

#############################################################################################################
#асинхронное получение списка последних транзакций
async def get_transactions_async(wallet, last_trans_count):
    try:
        client = TonlibClient()
        #await client.init_tonlib(cdll_path = cdll_filepath_win)
        await client.init_tonlib(cdll_path=cdll_filepath)

        account = await client.find_account(wallet)
        transactions = await account.get_transactions(limit=last_trans_count)

        transactions_list = []
        for t in transactions:
            trans_obj = AccountTrans()
            trans_obj.load_trans(t)
            transactions_list.append(trans_obj)

        return transactions_list

    except Exception as err:
        print(err)

#############################################################################################################
# отправка токенов по указанному адресу
async def send_money_async(to_address, amount, message):
    try:
        client = TonlibClient()
        # await client.init_tonlib(cdll_path=cdll_filepath_win)
        await client.init_tonlib(cdll_path = cdll_filepath)
        wallet = await client.import_wallet(guarantor_wallet_seed)
        balance1_nano = await wallet.get_balance()
        balance1 = balance1_nano/(10**9)
        print(get_now() + " - The guarantor bot wallet: " + str(wallet.account_address.account_address) + ", balance: " + str(balance1) + " TON")

        amount_nano = int(amount * (10 ** 9))
        print(get_now() + " - Sending " + str(amount) + " TON to the wallet " + to_address)
        await wallet.transfer(to_address, amount_nano, comment=message)
        print(get_now() + " - Command to transfer was send")

        return balance1

    except Exception as err:
        print(err)

#################
#синхронная обёртка для функции отправки токенов
def send_money(to_address, amount, message):
    try:
        t = asyncio.run(send_money_async(to_address, amount, message))
    except Exception as err:
        print(err)


###############################################################################################################
# Постановка платежа в очередь
def send_payment_to_queue(from_wallet, to_wallet, amount, comment, payment_type, param):
    try:
        connect1 = psycopg2.connect(host=param[0], port=param[1], dbname=param[2], user=param[3],  password=param[4])
        schema = param[5]

        cursor1 = connect1.cursor()
        insert_sql = "insert into " +schema+".f_send_money_queue (from_wallet,to_wallet,amount,comment,payment_type) values (" \
            + "'"+str(from_wallet)+"','"+str(to_wallet)+"',"+str(float(amount))+",'"+str(comment)+"','"+str(payment_type)+"')"
        cursor1.execute(insert_sql)
        connect1.commit()
        cursor1.close()

    except Exception as err:
        print(err)
    finally:
        connect1.close()


###############################################################################################################
#отправка платежей ,стоящих в очереди
def send_money_by_queue(param):
    try:
        payments_count = 1 #число платежей в один период отправки

        connect1 = psycopg2.connect(host=param[0], port=param[1], dbname=param[2], user=param[3],  password=param[4])
        schema = param[5]

        cursor1 = connect1.cursor()
        select_sql = "select id, to_wallet,amount,comment from " +schema+".f_send_money_queue "\
            + " where status='queued' order by (case when payment_type='buyer' then 1 else 2 end), queue_ts limit "+str(payments_count)
        cursor1.execute(select_sql)
        data = cursor1.fetchall()
        cursor1.close()

        if data is None or len(data)==0:
            return 0
        else:
            for send in data:
                id = send[0]
                to_wallet = send[1]
                amount = float(send[2])
                comment = send[3]

                #отправляем платёж
                balance = asyncio.run(send_money_async(to_wallet, amount, comment))

                #обновляем информацию в базе
                cursor2 = connect1.cursor()
                update_sql = "update " +schema+".f_send_money_queue " \
                + "set status='sent', from_wallet_balance="+str(balance) + ", send_ts=now() " \
                + " where id="+str(id)

                cursor2.execute(update_sql)
                connect1.commit()
                cursor2.close()
                time.sleep(20)

    except Exception as err:
        print(err)
        return -1
    finally:
        connect1.close()


########################################################################################################
# проверка , что была совершена транзакция с соответствующим комментарием и суммой
def check_wallet_payment0(from_wallet, to_wallet, comment, amount):
    try:
        api_link = "https://tonapi.io/v1/blockchain/getTransactions?account="

        # считываем последние X транзакции верификационного кошелька
        limit = 10
        check_url1 = api_link + to_wallet + "&limit="+str(limit)
        print(get_now() + " Transactions check link: " + check_url1)
        resp2 = requests.get(check_url1).json()
        for trans in resp2["transactions"]:
            if "source" in trans["in_msg"] and trans["in_msg"]["msg_data"]["@type"] == "msg.dataText":
                source_hex = trans["in_msg"]["source"]["address"]
                source = address_to_bounceable(source_hex)
                message_b64 = trans["in_msg"]["msg_data"]["text"]
                message = base64.b64decode(message_b64).decode('utf-8')
                value = int(trans["in_msg"]["value"])/(10**9)

                #ищем транзакцию с нужного кошелька, с нужным комментом и суммой больше положенной
                if source == from_wallet and message == comment and value >= amount - 0.01: #погрешность рассчёта комиссии сети
                    return 1 # нужная транзакция найдена

        return 0 #среди транзакций не найдено нужной

    except Exception as err:
        print(err)
        return -1 # ошибка в API

########################################################################################################
def check_wallet_payment1(from_wallet, to_wallet, comment, amount):
    try:
        api_link = "https://tonapi.io/v1/blockchain/getTransactions?account="

        # считываем последние X транзакции верификационного кошелька
        limit = 10
        check_url1 = api_link + to_wallet + "&limit="+str(limit)
        print(" Transactions check link: " + check_url1)
        resp2 = requests.get(check_url1).json()
        for trans in resp2["transactions"]:
            if "source" in trans["in_msg"]:
                source_hex = trans["in_msg"]["source"]["address"]
                source = address_to_bounceable(source_hex)
                message_b64 = trans["in_msg"]["msg_data"]
                message = (base64.b64decode(message_b64).decode('utf-8'))
                value = int(trans["in_msg"]["value"])/(10**9)

                #ищем транзакцию с нужного кошелька, с нужным комментом и суммой больше положенной
                if source == from_wallet and (comment in message) and float(value) >= float(amount) - float(0.01): #погрешность рассчёта комиссии сети
                    return 1 # нужная транзакция найдена

        return 0 #среди транзакций не найдено нужной

    except Exception as err:
        print(err)
        return -1 # ошибка в API

########################################################################################################
def check_wallet_payment(from_wallet, to_wallet, comment, amount):
    try:
        user_wallet = from_wallet
        bot_wallet = to_wallet

        # считываем последние X транзакции кошелька бота
        transactions = asyncio.run(get_transactions_async(bot_wallet, 20))
        for t in transactions:
            if t.direction == 'in' \
                and t.other_wallet == user_wallet \
                and t.message == comment \
                and t.amount >= float(amount) - float(0.01): #погрешность рассчёта комиссии сети
                return 1  # нужная транзакция найдена

        return 0  # среди транзакций не найдено нужной

    except Exception as err:
        print(err)
        return -1 # ошибка в API


