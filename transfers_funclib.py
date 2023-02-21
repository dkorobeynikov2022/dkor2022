import psycopg2
from telebot import types
from main_config import transfer_commission, explorer_api_link, guarantor_wallet
from messages import translate_txt


class Transfer:
    def __init__(self):
        self.id = None
        self.status = None
        self.start_ts = None
        self.end_ts = None
        self.owner_user_id = None
        self.owner_wallet = None
        self.owner_fullname = None
        self.owner_lang = None
        self.collection_id = None
        self.collection_address = None
        self.collection_name = None
        self.nft_id = None
        self.nft_address = None
        self.nft_name = None
        self.nft_description = None
        self.nft_image = None
        self.amount = None
        self.bot_commission = None
        self.buyer_user_id = None
        self.buyer_wallet = None
        self.buyer_fullname = None
        self.buyer_lang = None
        self.bot_id = None


    def fill_by_id(self, transfer_id, param):
        try:
            connect1 = psycopg2.connect(host=param[0], port=param[1], dbname=param[2], user=param[3], password=param[4])
            schema = param[5]
            cursor1 = connect1.cursor()
            fields_list = "id, status, start_ts, end_ts, amount, bot_commission, owner_user_id, owner_wallet, owner_fullname, owner_lang, "\
                + "buyer_user_id, buyer_wallet, buyer_fullname, buyer_lang, nft_id, nft_address, nft_name, nft_description, nft_image, "\
                + "collection_id, collection_name, collection_address, bot_id"
            select_sql = "select "+fields_list+" from " + schema + ".v_d_transfers where id=" + str(transfer_id)
            cursor1.execute(select_sql)
            data = cursor1.fetchone()
            cursor1.close()

            self.id = data[0]
            self.status = data[1]
            self.start_ts = data[2]
            self.end_ts = data[3]
            self.amount = data[4]
            self.bot_commission = data[5]
            self.owner_user_id = data[6]
            self.owner_wallet = data[7]
            self.owner_fullname = data[8]
            self.owner_lang = data[9]
            self.buyer_user_id = data[10]
            self.buyer_wallet = data[11]
            self.buyer_fullname = data[12]
            self.buyer_lang = data[13]
            self.nft_id = data[14]
            self.nft_address = data[15]
            self.nft_name = data[16]
            self.nft_description = data[17]
            self.nft_image = data[18]
            self.collection_id = data[19]
            self.collection_name = data[20]
            self.collection_address = data[21]
            self.bot_id = data[22]

        except Exception as err:
            print(err)
        finally:
            connect1.close()

    def add_to_db(self, param):
        try:
            connect1 = psycopg2.connect(host=param[0], port=param[1], dbname=param[2], user=param[3], password=param[4])
            schema = param[5]
            cursor1 = connect1.cursor()
            insert_sql = "insert into " + schema + ".d_transfers(owner_user_id, status, bot_id, collection_id) values (" \
                + str(self.owner_user_id) + ", 'new', " +str(self.bot_id)+ ", " +str(self.collection_id)+ ")"
            cursor1.execute(insert_sql)
            connect1.commit()
            cursor1.close()

            cursor2 = connect1.cursor()
            select_sql = "select max(id) as transfer_id from " + schema + ".d_transfers where owner_user_id=" + str(self.owner_user_id)
            cursor2.execute(select_sql)
            data = cursor2.fetchone()
            cursor2.close()

            #возвращаем ID сохранённого трансфера
            if data is not None:
                print("created new transfer #" + str(data[0]))
                return data[0]
            else:
                return 0

        except Exception as err:
            print(err)
        finally:
            connect1.close()

    def update_db(self, param):
        try:
            connect1 = psycopg2.connect(host=param[0], port=param[1], dbname=param[2], user=param[3], password=param[4])
            schema = param[5]
            cursor1 = connect1.cursor()
            owner_wallet = 'null' if self.owner_wallet is None else "'" + str(self.owner_wallet) + "'"
            nft_id = 'null' if self.nft_id is None else str(self.nft_id)
            amount = 'null' if self.amount is None else str(self.amount)
            bot_commission = 'null' if self.bot_commission is None else str(self.bot_commission)
            buyer_user_id = 'null' if self.buyer_user_id is None else str(self.buyer_user_id)
            buyer_wallet = 'null' if self.buyer_wallet is None else "'"+str(self.buyer_wallet)+"'"
            end_ts = 'null' if self.end_ts is None else "'" + str(self.end_ts) + "'"
            collection_id = '0' if self.collection_id is None else str(self.collection_id)

            update_sql = "update " + schema + ".d_transfers set " \
            + " owner_user_id=" + str(self.owner_user_id) + ", "\
            + " bot_id=" + str(self.bot_id) + ", "\
            + " owner_wallet=" + owner_wallet + ", " \
            + " nft_id=" + nft_id + ", "\
            + " amount=" + amount + ", "\
            + " bot_commission=" + bot_commission + ", "\
            + " buyer_user_id=" + buyer_user_id + ", "\
            + " buyer_wallet=" + buyer_wallet + ", " \
            + " status='" + str(self.status) + "', " \
            + " start_ts='" + str(self.start_ts) + "', " \
            + " end_ts=" + end_ts + ", "\
            + " collection_id=" + collection_id \
            + " where id="+str(self.id)
            cursor1.execute(update_sql)
            connect1.commit()
            cursor1.close()

        except Exception as err:
            print(err)
        finally:
            connect1.close()


#############################################################################################
# поиск и проверка аккаунта покупателя
def check_buyer_account (bot_id, buyer, param):
    try:
        connect1 = psycopg2.connect(host=param[0], port=param[1], dbname=param[2], user=param[3],  password=param[4])
        schema = param[5]
        select_sql = "select usr.user_id, usr.username, "\
            + "(case when black.user_id is not null then true else false end) as is_blacklist, "\
            + "(case when bots.bot_id is null then true else false end) as not_entered_in_bot " \
            + " from nft_auction_bot.d_users usr "\
            + " left join "+schema+".d_users_blacklist black on (usr.user_id=black.user_id) "\
            + " left join "+schema+".f_users_bots bots on (bots.user_id=usr.user_id and bots.bot_id="+str(bot_id)+")"\
            + " where (usr.user_id::text='"+str(buyer)+"' or usr.username='"+str(buyer)+"')"
        cursor1 = connect1.cursor()
        cursor1.execute(select_sql)
        data = cursor1.fetchone()
        cursor1.close()

        if data is None: #такой пользователь не найден в базе
            return 0
        elif data is not None and len(data)>0:
            if data[2] == True: #пользователь в чёрном списке
                return -1
            elif data[3] == True: #пользователь есть в базе, но ещё не заходил в этого бота
                return 0
            else: #пользователь найден и не в чёрном списке
                return data[0]

    except Exception as err:
        print(err)
    finally:
        connect1.close()



########################################################################################################
def show_main_transfers_menu(bot, user, bot_id, guarantor_start_logo):
    try:
        btn_row1 = [
            types.InlineKeyboardButton(text=translate_txt('btn_new_transfer', user.lang), callback_data='new_transfer'),
            types.InlineKeyboardButton(text=translate_txt('btn_my_transfers', user.lang), callback_data='my_transfers')]
        btn_row2 = [types.InlineKeyboardButton(text=translate_txt('btn_back', user.lang), callback_data='main_menu')]
        keyboard = types.InlineKeyboardMarkup([btn_row1, btn_row2])

        bot.send_photo(user.user_id, photo=open(guarantor_start_logo, 'rb'),
                        caption=translate_txt("msg_about_transfer_" + str(bot_id), user.lang).format(guarantor_wallet, transfer_commission ),
                        reply_markup=keyboard, parse_mode='html')

    except Exception as err:
        print(err)

########################################################################################################
# Трансферы - Твои сделки
def show_user_transfers(bot_id, bot, user, param, limit=5):
    try:
        connect1 = psycopg2.connect(host=param[0], port=param[1], dbname=param[2], user=param[3],  password=param[4])
        schema = param[5]
        cursor1 = connect1.cursor()

        select_sql = "select id, nft_name, status " \
            + " from " + schema + ".v_d_transfers where bot_id=" + str(bot_id) \
            + " and status not in ('new') " \
            + " and buyer_wallet is not null " \
            + " and (owner_user_id="+str(user.user_id)+" or buyer_user_id="+str(user.user_id)+")" \
            + " order by start_ts limit "+ str(limit)
        cursor1.execute(select_sql)
        data = cursor1.fetchall()
        cursor1.close()

        keyboard = types.InlineKeyboardMarkup()
        if data is None or len(data)==0: #нет ни одной сделки
            text_to_send = translate_txt("msg_no_my_transfers", user.lang)
        else:
            text_to_send = translate_txt("msg_your_transfers_list", user.lang)
            for transfer in data:
                statuses = {"active": "🟡", "cancelled": "❌", "finished": "✅", "payment": "💵", "NFT transfer": "🖼"}
                label = "🤝№" + str(transfer[0]) + " (" + str(transfer[1]) + ") - " + statuses.get(transfer[2]) + str(transfer[2])
                keyboard.add(types.InlineKeyboardButton(text=label, callback_data='show_transfer;'+str(transfer[0])))

        keyboard.add(types.InlineKeyboardButton(text=translate_txt('btn_back', user.lang), callback_data='menu_transfers'))
        bot.send_message(user.user_id, text_to_send, reply_markup=keyboard)

    except Exception as err:
        print(err)
    finally:
        connect1.close()

########################################################################################################
# Трансферы - Инфа о новом трансфере для подтверждения
def show_new_transfer_to_confirm(transfer_id, user_type, bot, param):
    try:
        transfer = Transfer()
        transfer.fill_by_id(transfer_id, param)

        user_id = transfer.owner_user_id if user_type == 'owner' else transfer.buyer_user_id
        user_lang = transfer.owner_lang if user_type == 'owner' else transfer.buyer_lang
        message_code = "msg_owner_confirm_new_transfer" if user_type == 'owner' else "msg_buyer_confirm_new_transfer"
        confirm_callback = "confirm_transfer_owner;" if user_type == 'owner' else "confirm_transfer_buyer;"
        cancel_callback = "cancel_transfer_owner;" if user_type == 'owner' else "cancel_transfer_buyer;"

        nft_name = "<a href='" + explorer_api_link + transfer.nft_address + "'>" + transfer.nft_name + "</a>"
        info = translate_txt("msg_new_transfer_info", user_lang).format(transfer.id, transfer.owner_fullname,
            f'<code>{transfer.owner_wallet}</code>', transfer.buyer_fullname, nft_name, str(transfer.amount), str(transfer.bot_commission)) \
            + "\n__________________________________\n" + translate_txt(message_code, user_lang)

        btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_confirm', user_lang),
                                               callback_data=confirm_callback + str(transfer.id)),
                    types.InlineKeyboardButton(text=translate_txt('btn_cancel', user_lang),
                                               callback_data=cancel_callback + str(transfer.id))]
        keyboard = types.InlineKeyboardMarkup([btn_row1])
        bot.send_photo(user_id, photo=open(transfer.nft_image, 'rb'), caption=info, reply_markup=keyboard,parse_mode='html')

    except Exception as err:
        print(err)

########################################################################################################
# Трансферы - карточка сделки
def show_transfer_info(transfer_id, user, bot, param):
    try:
        transfer = Transfer()
        transfer.fill_by_id(transfer_id, param)

        statuses = {"active": "🟡", "cancelled": "❌", "finished": "✅", "payment": "💵", "NFT transfer": "🖼"}
        nft_name = "<a href='" + explorer_api_link + transfer.nft_address + "'>" + transfer.nft_name + "</a>"
        start_ts = (transfer.start_ts).strftime("%d.%m.%y %H:%M:%S")
        end_ts = '' if transfer.end_ts is None else (transfer.end_ts).strftime("%d.%m.%y %H:%M:%S")
        info = translate_txt("msg_transfer_full_info", user.lang).format(
            transfer.id, statuses.get(transfer.status) + str(transfer.status),
            transfer.owner_fullname, f'<code>{transfer.owner_wallet}</code>',
            transfer.buyer_fullname, f'<code>{transfer.buyer_wallet}</code>',
            nft_name, str(transfer.amount), str(transfer.bot_commission),
            start_ts, end_ts
        )

        btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_back', user.lang), callback_data='my_transfers')]
        keyboard = types.InlineKeyboardMarkup([btn_row1])
        bot.send_photo(user.user_id, photo=open(transfer.nft_image, 'rb'), caption=info, reply_markup=keyboard,parse_mode='html')

    except Exception as err:
        print(err)