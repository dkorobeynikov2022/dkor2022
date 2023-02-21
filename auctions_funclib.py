import psycopg2
import requests
import asyncio
from datetime import datetime, timezone, timedelta
from telebot import types
from messages import translate_txt
from main_config import admin_users, guarantor_wallet, explorer_api_link, balance_api_link, payment_link, send_notif_to_channel
from main_funclib import BotUser, get_now, get_nft_info
from blockchain_funclib import get_balance_async
from telethon.sync import TelegramClient
from telethon.tl.types import PeerUser, InputPeerUser
from telethon.sessions import StringSession
from main_config import connect_par, phone, api_id, api_hash, session_id
from main_funclib import get_bot_info, get_comission_amount



class Auction:
    def __init__(self):
        self.id = None
        self.collection_id = None
        self.status = None
        self.owner_user_id = None
        self.owner_wallet = None
        self.start_price = None
        self.price_step = None
        self.start_ts = None
        self.end_ts = None
        self.comment = None
        self.leader_user_id = None
        self.leader_wallet = None
        self.leader_price = None
        self.channel_id = None
        self.nft_id = None
        self.nft_address = None
        self.nft_name = None
        self.nft_description = None
        self.image_path = None
        self.owner_username = None
        self.owner_first_name = None
        self.owner_last_name = None
        self.owner_fullname = None
        self.participants = None
        self.owner_auctions_total = None
        self.owner_auctions_cancelled = None
        self.owner_auctions_with_winner = None
        self.owner_auctions_wo_winner = None
        self.owner_lang = None
        self.leader_lang = None
        self.collection_address = None
        self.leader_fullname = None
        self.bot_id = None
        self.bot_commission = None

    def get_auction_info_array(self):
        return [self.id, self.collection_id, self.nft_id, self.owner_user_id, self.owner_wallet, self.start_price, self.price_step,
                self.end_ts, self.comment]

    def fill_by_array(self, array):
        self.id = array[0]
        self.collection_id = array[1]
        self.status = array[2]
        self.owner_user_id = array[3]
        self.owner_wallet = array[4]
        self.start_price = array[5]
        self.price_step = array[6]
        self.start_ts = array[7]
        self.end_ts = array[8]
        self.comment = array[9]
        self.leader_user_id = array[10]
        self.leader_wallet = array[11]
        self.leader_price = array[12]
        self.channel_id = array[13]
        self.nft_id = array[14]
        self.nft_address = array[15]
        self.nft_name = array[16]
        self.nft_description = array[17]
        self.image_path = array[18]
        self.owner_username = array[19]
        self.owner_first_name = array[20]
        self.owner_last_name = array[21]

        self.owner_fullname = (self.owner_first_name + " " + self.owner_last_name).strip() + (
            " [@" + self.owner_username + "]" if self.owner_username != "" else "")
        self.participants = array[22]
        self.owner_auctions_total = array[23]
        self.owner_auctions_cancelled = array[24]
        self.owner_auctions_with_winner = array[25]
        self.owner_auctions_wo_winner = array[26]
        self.owner_lang = array[27]
        self.leader_lang = array[28]
        self.collection_address = array[29]
        self.leader_fullname = array[30]
        self.bot_id = array[31]
        self.bot_commission = array[32]


    def fill_by_temp_table(self, owner_user_id, param):
        try:
            connect1 = psycopg2.connect(host=param[0], port=param[1], dbname=param[2], user=param[3], password=param[4])
            schema = param[5]
            cursor1 = connect1.cursor()
            select_sql = "select collection_id, nft_id, owner_user_id, owner_wallet, start_price, price_step, end_ts, comment, owner_lang, bot_id from " \
                + schema + ".d_auctions_temp where owner_user_id=" + str(owner_user_id)
            cursor1.execute(select_sql)
            data = cursor1.fetchone()

            self.collection_id = data[0]
            self.nft_id = data[1]
            self.owner_user_id = data[2]
            self.owner_wallet = data[3]
            self.start_price = data[4]
            self.price_step = data[5]
            self.end_ts = data[6]
            self.comment = data[7]
            self.owner_lang = data[8]
            self.bot_id = data[9]

        except Exception as err:
            print(err)
        finally:
            connect1.close()

    def fill_by_id(self, auction_id, param):
        try:
            connect1 = psycopg2.connect(host=param[0], port=param[1], dbname=param[2], user=param[3], password=param[4])
            schema = param[5]

            cursor1 = connect1.cursor()
            select_sql = "select auction_id, collection_id, status, owner_user_id, owner_wallet, start_price, price_step, start_ts, end_ts, comment, " \
                + " leader_user_id, leader_wallet, leader_price, channel_id, nft_id, nft_address, nft_name, nft_description, image_path, owner_username, " \
                + " owner_first_name, owner_last_name, participants, owner_auctions_total, owner_auctions_cancelled, owner_auctions_with_winner, "\
                + " owner_auctions_wo_winner, owner_lang, leader_lang, collection_address, leader_fullname, bot_id, bot_commission " \
                + " from " + schema + ".v_d_auctions where auction_id=" + str(auction_id)
            cursor1.execute(select_sql)
            data = cursor1.fetchone()
            cursor1.close()
            self.fill_by_array(data)

        except Exception as err:
            print(err)
        finally:
            connect1.close()

########################################################################################################
def show_main_auctions_menu(bot, user):
    try:
        btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_my_auctions', user.lang), callback_data='menu_my_auctions'),
            types.InlineKeyboardButton(text=translate_txt('btn_now_participating', user.lang), callback_data='menu_now_participating')]
        btn_row2 = [types.InlineKeyboardButton(text=translate_txt('btn_participate', user.lang),callback_data='menu_participate'),
                    types.InlineKeyboardButton(text=translate_txt('btn_back', user.lang),callback_data='main_menu')]

        keyboard = types.InlineKeyboardMarkup([btn_row1, btn_row2])
        bot.send_message(user.user_id, translate_txt('msg_main_menu', user.lang), reply_markup=keyboard)

    except Exception as err:
        print(err)

########################################################################################################
# поиск последних Х аукционов пользователя
def show_last_user_auctions(bot_id, user, param, count_limit):
    try:
        connect1 = psycopg2.connect(host=param[0], port=param[1], dbname=param[2], user=param[3],  password=param[4])
        schema = param[5]
        cursor1 = connect1.cursor()

        select_sql = "select auction_id, status, start_ts, end_ts, start_price, price_step, leader_price, comment, " \
            + " nft_name, nft_address, participants, row_number() over (order by auction_id desc) as rn " \
            + " from "+schema+".v_f_user_auctions " \
            + " where user_id="+str(user.user_id)+ " and bot_id="+str(bot_id) + " order by auction_id desc limit " + str(count_limit)
        cursor1.execute(select_sql)
        data0 = cursor1.fetchall()
        data = data0[::-1] #обратная сортировка массива
        cursor1.close()

        info = ""
        last_auction_status = ""
        last_auction_id = None
        if data is None or len(data) == 0:
            info = translate_txt('msg_no_auctions', user.lang)
        else:
            for auction in data:
                start_ts = (auction[2] + timedelta(hours=3)).strftime("%d.%m.%y %H:%M")
                end_ts = (auction[3] + timedelta(hours=3)).strftime("%d.%m.%y %H:%M")
                leader_price = '-' if auction[10] == 0 else str(auction[6]) + "💎" #если участников 0, цена не показывается
                statuses = {"active":"🟡", "cancelled":"❌", "finished":"✅", "payment":"💵", "NFT transfer":"🖼"}

                info = info + translate_txt('msg_my_auctions_info', user.lang).format(str(auction[0]), str(auction[8]), start_ts, end_ts,
                    str(auction[4]), str(auction[10]), str(leader_price), statuses.get(auction[1]) + auction[1]) \
                    + "__________________________________\n"

                if auction[11] == 1: #последний аукцион
                    last_auction_status = auction[1]
                    last_auction_id = auction[0]

        return info, last_auction_status, last_auction_id

    except Exception as err:
        print(err)
    finally:
        connect1.close()


########################################################################################################
# Показываем пользователю информацию об Х последних активных аукционах
# 1) Аукцион в статусе active; 2) Пользователь не является его создателем; 3) Пользователь не является его участником
def show_active_auctions(bot_id, user, bot, param, count_limit):
    try:
        connect1 = psycopg2.connect(host=param[0], port=param[1], dbname=param[2], user=param[3],  password=param[4])
        schema = param[5]
        cursor1 = connect1.cursor()

        select_sql = "select auc.auction_id, auc.status, auc.start_ts, auc.end_ts, auc.start_price, auc.price_step, " \
            + " auc.leader_price, auc.comment, auc.nft_name, auc.nft_address, auc.participants, " \
            + " row_number() over (order by auc.auction_id desc) as rn_desc, auc.owner_user_id, auc.nft_short_info " \
            + " from "+schema+".v_f_user_auctions auc" \
            + " left join "+schema+".f_auction_participants part on (auc.auction_id=part.auction_id and part.user_id="+str(user.user_id)+") " \
            + " where auc.status='active' and auc.bot_id="+str(bot_id) \
            + " and auc.owner_user_id<>"+str(user.user_id)+" and part.user_id is null " \
            + " order by 1 desc limit " + str(count_limit)
        cursor1.execute(select_sql)
        data = cursor1.fetchall()
        cursor1.close()

        keyboard = types.InlineKeyboardMarkup()
        info = ""
        if data is None or len(data) == 0:
            info = translate_txt('msg_no_active_auctions', user.lang)
            keyboard.add(types.InlineKeyboardButton(text=translate_txt('btn_back', user.lang), callback_data='participate_back'))
            bot.send_message(user.user_id, info, reply_markup=keyboard, parse_mode='html')
            return 0
        else:
            for auction in data:
                end_ts = (auction[3] + timedelta(hours=3)).strftime("%d.%m.%y %H:%M")
                leader_price = '-' if auction[6] is None else str(auction[6])+"💎"
                nft_name = str(auction[8])
                nft_short_info = str(auction[13])

                info = info + translate_txt('msg_active_auctions_info', user.lang).format(str(auction[0]), nft_name, nft_short_info, end_ts,
                    str(auction[4]), str(auction[5]), leader_price, str(auction[10])) + "\n"\
                    + "__________________________________\n"

                keyboard.add(types.InlineKeyboardButton(text="🔨№"+str(auction[0])+" (" + str(auction[8])+")", callback_data='auction_refresh;'+str(auction[0])))

            keyboard.add(types.InlineKeyboardButton(text=translate_txt('btn_back', user.lang), callback_data='participate_back'))
            bot.send_message(user.user_id, info + "\n" + translate_txt("msg_input_auction_id", user.lang), reply_markup=keyboard, parse_mode='html')
            return len(data)

    except Exception as err:
        print(err)
    finally:
        connect1.close()


########################################################################################################
# Показываем пользователю информацию об активных аукционах, в которых он участвует
def show_user_participations(bot_id, user, bot, param):
    try:
        connect1 = psycopg2.connect(host=param[0], port=param[1], dbname=param[2], user=param[3],  password=param[4])
        schema = param[5]
        cursor1 = connect1.cursor()

        select_sql = "select auction_id, end_ts, start_price, price_step, leader_price, participants, nft_name, leader_user_id, nft_short_info " \
            + " from " + schema + ".v_f_auction_participants " \
            + " where status='active' and user_id="+str(user.user_id) + " and bot_id="+str(bot_id)
        cursor1.execute(select_sql)
        data = cursor1.fetchall()
        cursor1.close()

        keyboard = types.InlineKeyboardMarkup()
        info = ""
        if data is None or len(data) == 0:
            info = translate_txt('msg_no_participations', user.lang)
            keyboard.add(types.InlineKeyboardButton(text=translate_txt('btn_back', user.lang), callback_data='now_participating_back'))
            bot.send_message(user.user_id, info, reply_markup=keyboard, parse_mode='html')
            return 0
        else:
            for auction in data:
                end_ts = (auction[1] + timedelta(hours=3)).strftime("%d.%m.%y %H:%M")
                nft_short_info = str(auction[8])
                user_status = '' if auction[7]!=user.user_id else '🏆'
                leader_price = '-' if auction[4] is None else str(auction[4]) + "💎"
                info = info + user_status + translate_txt('msg_active_auctions_info', user.lang).format(str(auction[0]), str(auction[6]),
                    nft_short_info ,end_ts, str(auction[2]), str(auction[3]), leader_price, str(auction[5])) + "\n"\
                    + "__________________________________\n"

                keyboard.add(types.InlineKeyboardButton(text="🔨№"+str(auction[0])+" (" + str(auction[6])+")", callback_data='auction_refresh;'+str(auction[0])))

            keyboard.add(types.InlineKeyboardButton(text=translate_txt('btn_back', user.lang), callback_data='now_participating_back'))
            bot.send_message(user.user_id, info + "\n" + translate_txt("msg_input_auction_id", user.lang), reply_markup=keyboard, parse_mode='html')
            return len(data)

    except Exception as err:
        print(err)
    finally:
        connect1.close()

########################################################################################################
# 1) вся информация об аукционе (цена, количество участников)
# 2) является ли пользователь владельцем или участником
# 3) статус пользователя (лидер или нет)
def show_selected_auction_menu(user, auction_id, bot, param):
    try:
        auction = Auction()
        auction.fill_by_id(auction_id, param) #загружаем данные об аукционе из базы

        connect1 = psycopg2.connect(host=param[0], port=param[1], dbname=param[2], user=param[3],  password=param[4])
        schema = param[5]
        cursor1 = connect1.cursor()

        select_sql = "select auc.id, auc.participants, " \
        + " (case when auc.owner_user_id = "+str(user.user_id)+" then true else false end) as is_owner, "\
        + " (case when part.user_id is not null then true else false end) as is_participant, " \
        + " (case when auc.leader_user_id = "+str(user.user_id)+" then true else false end) as is_leader " \
        + " from "+schema+".d_auctions auc " \
        + " left join "+schema+".f_auction_participants part on (auc.id=part.auction_id and part.user_id="+str(user.user_id)+")" \
        + " where auc.id="+ str(auction_id)
        cursor1.execute(select_sql)
        data = cursor1.fetchone()
        cursor1.close()

        participants = data[1]
        is_owner = data[2]
        is_participant = data[3]
        is_leader = data[4]

        info, image = get_auction_full_info(user.lang, auction_id, param)

        btn_row2 = [types.InlineKeyboardButton(text=translate_txt('btn_refresh', user.lang), callback_data='auction_refresh;' + str(auction_id)),
                    types.InlineKeyboardButton(text=translate_txt('btn_back', user.lang), callback_data='auction_back')]

        if is_owner == True: #владелец аукциона
            btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_owner', user.lang), callback_data='auction_owner;'+str(auction_id))]

        elif is_leader == True: # лидер аукциона
            btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_leader', user.lang), callback_data='auction_leader;'+str(auction_id))]

        elif is_participant == True: #уже участвует, но не лидер
            text_to_send = translate_txt('btn_raise_first', user.lang) if auction.leader_price is None else translate_txt('btn_raise', user.lang).format(str(auction.price_step))
            btn_row1 = [types.InlineKeyboardButton(text=text_to_send, callback_data='auction_raise;'+str(auction_id))]

        else: #elif is_participant == False: #ещё не участвует
            btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_join', user.lang), callback_data='auction_join;'+str(auction_id))]

        keyboard = types.InlineKeyboardMarkup([btn_row1, btn_row2])
        bot.send_photo(user.user_id, photo=open(image, 'rb'), caption=info, reply_markup=keyboard, parse_mode='html')

    except Exception as err:
        print(err)
    finally:
        connect1.close()

########################################################################################################
# Проверяем введённый пользователем ID аукциона.
# Варианты: 1) некорректное число 1) Такого аукциона нет 2) Аукцион не активен
def check_auction_id_correct(bot_id, auction_id, param):
    try:
        auction_id = auction_id.strip()

        connect1 = psycopg2.connect(host=param[0], port=param[1], dbname=param[2], user=param[3],  password=param[4])
        schema = param[5]
        cursor1 = connect1.cursor()

        select_sql = "select id, status from "+schema+".d_auctions where id::text='"+str(auction_id) + "' and bot_id="+str(bot_id)
        cursor1.execute(select_sql)
        data = cursor1.fetchone()
        cursor1.close()

        if data is None or len(data)==0:
            return 0 #not found
        elif data[1] != "active":
            return -1 #not active
        else:
            return 1 # OK

    except Exception as err2:
        print(err2)

    finally:
        connect1.close()


########################################################################################################
# Аукционы - Ты организатор
def show_owner_auctions_menu(bot_id, bot, user, param):
    try:
        # собираем информацию об аукционах пользователя
        info, last_auction_status, last_auction_id = show_last_user_auctions(bot_id, user, param, 3)

        if last_auction_status in ["finished", "cancelled", ""]:
            btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_new_auction', user.lang), callback_data='auction_new'),
                        types.InlineKeyboardButton(text=translate_txt('btn_back', user.lang), callback_data='menu_auctions')]

        elif last_auction_status in ["active"]:
            btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_cancel_auction', user.lang), callback_data='auction_cancel'),
                        types.InlineKeyboardButton(text=translate_txt('btn_back', user.lang), callback_data='menu_auctions')]

        elif last_auction_status in ["payment"]:
            btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_back', user.lang),callback_data='menu_auctions')]

        elif last_auction_status in ["NFT transfer"]:
            btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_nft_transfered', user.lang), callback_data='auction_nft_transfered;'+str(last_auction_id)),
                        types.InlineKeyboardButton(text=translate_txt('btn_back', user.lang),callback_data='menu_auctions')]


        keyboard = types.InlineKeyboardMarkup([btn_row1])
        bot.send_message(user.user_id, info + translate_txt('msg_auction_menu', user.lang), reply_markup=keyboard, parse_mode='html')

    except Exception as err:
        print(err)

########################################################################################################
def get_owner_active_auction(bot_id, user_id, param):
    try:
        connect1 = psycopg2.connect(host=param[0], port=param[1], dbname=param[2], user=param[3],  password=param[4])
        schema = param[5]
        cursor1 = connect1.cursor()

        select_sql = "select auc.id, usr.cancel_limit, auc.leader_price " \
            + " from "+schema+".d_auctions auc " \
            + " inner join "+schema+".d_users usr on (auc.owner_user_id=usr.user_id) " \
            + " where status='active' and auc.owner_user_id="+str(user_id) + " and auc.bot_id="+str(bot_id)
        cursor1.execute(select_sql)
        data = cursor1.fetchone()
        cursor1.close()

        auction_id = data[0]
        cancel_limit = data[1]
        leader_price = data[2]

        if data is not None:
            return auction_id, cancel_limit, leader_price
        else:
            return None, None, None

    except Exception as err:
        print(err)
    finally:
        connect1.close()



########################################################################################################
# проверка введённого TON-кошелька, user_id или NFT на присутствие в чёрном списке
def save_auction_temp_data(auction, param):
    try:
        connect1 = psycopg2.connect(host=param[0], port=param[1], dbname=param[2], user=param[3],  password=param[4])
        schema = param[5]

        #чистим старые данные
        cursor1 = connect1.cursor()
        delete_sql = "delete from "+schema+".d_auctions_temp where owner_user_id=" + str(auction.owner_user_id)
        cursor1.execute(delete_sql)
        connect1.commit()
        cursor1.close()

        cursor2 = connect1.cursor()
        nft_id = 'null' if auction.nft_id is None else str(auction.nft_id)
        start_price = 'null' if auction.start_price is None else str(auction.start_price)
        price_step = 'null' if auction.price_step is None else str(auction.price_step)
        end_ts = 'null' if auction.end_ts is None else "'" + str(auction.end_ts.strftime("%Y-%m-%d %H:%M:%S")) + "'"
        comment = 'null' if auction.comment is None else "'" + str(auction.comment) + "'"
        owner_lang = 'null' if auction.owner_lang is None else "'" + str(auction.owner_lang) + "'"

        insert_sql = "insert into "+schema+".d_auctions_temp (collection_id, nft_id, owner_user_id, owner_wallet, start_price, "\
            + "price_step, end_ts, comment, owner_lang, bot_id) " \
            + "values ("+str(auction.collection_id)+ "," + nft_id + ", "+ str(auction.owner_user_id) + ", '"\
            + str(auction.owner_wallet) + "', " + start_price + ", " + price_step + ", " \
            + end_ts + "," + comment + "," + owner_lang + "," + str(auction.bot_id) +")"
        cursor2.execute(insert_sql)
        connect1.commit()
        cursor2.close()

    except Exception as err:
        print(err)
    finally:
        connect1.close()

########################################################################################################
# Отображение итогового набора данных по аукциону
def show_auction_info_before_save(auction, user, param):
    try:
        connect1 = psycopg2.connect(host=param[0], port=param[1], dbname=param[2], user=param[3],  password=param[4])
        schema = param[5]

        cursor1 = connect1.cursor()
        select_sql = "select id, name, address, image_path from "+schema+".d_nft where id=" + str(auction.nft_id)
        cursor1.execute(select_sql)
        data = cursor1.fetchone()
        cursor1.close()

        nft_name = data[1]
        nft_url = explorer_api_link + data[2]
        image = data[3]
        end_ts = (auction.end_ts + timedelta(hours=3)).strftime("%d.%m.%Y %H:%M:%S") # показываем время в формате GMT+3

        info = "<a href='" + nft_url + "'>" + nft_name + "</a>\n\n" \
            + translate_txt("msg_confirm_auction_info", user.lang).format(str(auction.start_price), str(auction.price_step),
                end_ts, str(user.full_name), str(auction.owner_user_id),
                str(auction.owner_wallet), str(auction.comment))


        return info, image

    except Exception as err:
        print(err)
    finally:
        connect1.close()


###########################################################
# рассылка информации в канал о новом созданном аукционе
def get_auction_full_info(lang, auction_id, param):
    try:
        auc = Auction()
        auc.fill_by_id(auction_id, param) #заполняем информацию из БД

        start_ts = (auc.start_ts + timedelta(hours=3)).strftime("%d.%m.%y %H:%M") # время в GMT+3
        end_ts = (auc.end_ts + timedelta(hours=3)).strftime("%d.%m.%y %H:%M") # время в GMT+3

        nft_name = "<b><a href='" + explorer_api_link + auc.nft_address + "'>" + str(auc.nft_name) + "</a></b>\n"
        nft_info = get_nft_info(auc.collection_id, auc.nft_description, lang)
        leader_price = '-' if auc.leader_price is None else str(auc.leader_price)+'💎'
        owner_stats = "🔨:"+str(auc.owner_auctions_total)+" "+ "❌:"+str(auc.owner_auctions_cancelled)+" " \
                      +"🏆:"+str(auc.owner_auctions_with_winner)+" "+"🚮:"+str(auc.owner_auctions_wo_winner)

        info = translate_txt('msg_auction_full_info', lang).format(str(auc.id), nft_name, start_ts, end_ts, str(auc.start_price),
            str(auc.price_step), leader_price, str(auc.participants), nft_info, str(auc.owner_fullname),
            f'<code>{str(auc.owner_wallet)}</code>', owner_stats, str(auc.comment))

        return info, auc.image_path

    except Exception as err:
        print(err)



########################################################################################################
# Аукционы - карточка аукциона
def show_auction_info(auction_id, user, bot, param):
    try:
        auction = Auction()
        auction.fill_by_id(auction_id, param)

        statuses = {"active": "🟡", "cancelled": "❌", "finished": "✅", "payment": "💵", "NFT transfer": "🖼"}
        nft_name = "<a href='" + explorer_api_link + auction.nft_address + "'>" + auction.nft_name + "</a>"
        start_ts = (auction.start_ts + timedelta(hours=3)).strftime("%d.%m.%y %H:%M:%S")
        end_ts = '' if auction.end_ts is None else (auction.end_ts + timedelta(hours=3)).strftime("%d.%m.%y %H:%M:%S")
        info = translate_txt("msg_auction_short_info", user.lang).format(
            auction.id, statuses.get(auction.status) + str(auction.status),
            auction.owner_fullname, f'<code>{auction.owner_wallet}</code>',
            auction.leader_fullname, f'<code>{auction.leader_wallet}</code>',
            nft_name, str(auction.start_price), str(auction.price_step), str(auction.leader_price),
            start_ts, end_ts
        )

        btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_back', user.lang), callback_data='menu_auctions')]
        keyboard = types.InlineKeyboardMarkup([btn_row1])
        bot.send_photo(user.user_id, photo=open(auction.image_path, 'rb'), caption=info, reply_markup=keyboard,parse_mode='html')

    except Exception as err:
        print(err)


########################################################################################################
# Отображение итогового набора данных по аукциону
def get_participants_list(auction_id, param):
    try:
        connect1 = psycopg2.connect(host=param[0], port=param[1], dbname=param[2], user=param[3],  password=param[4])
        schema = param[5]

        cursor1 = connect1.cursor()
        select_sql = "select distinct user_id from "+schema+".f_auction_participants where auction_id=" + str(auction_id)
        cursor1.execute(select_sql)
        participants = []
        for row in cursor1.fetchall():
            participants.append(row[0])
        cursor1.close()

        return participants

    except Exception as err:
        print(err)
    finally:
        connect1.close()

###########################################################
# рассылка информации в канал о новом созданном аукционе
def send_new_auction_notif_ru(auction_id, channel_ids, bot, bot_name, param):
    try:
        info, image = get_auction_full_info('ru', auction_id, param)
        text_to_send = info + "\n\n" + "#new #аукцион"+str(auction_id) + "\n"\
        + "/a_"+str(auction_id)+" via @"+bot_name

        if send_notif_to_channel == True:
            for channel_id in channel_ids:
                bot.send_photo(channel_id, photo=open(image, 'rb'), caption=text_to_send, parse_mode='html')

    except Exception as err:
        print(err)

###########################################################
# рассылка информации о поднятии цены
def send_bid_raise_notif_ru(auction_id, user, bot, bot_address, channel_ids, param):
    try:
        auction = Auction()
        auction.fill_by_id(auction_id, param)

        info = "💵<b>Повышение ставки в аукционе №" +str(auction.id) + "!</b>💵" \
        + "__________________________________\n" \
        + "<a href='" + explorer_api_link + auction.nft_address + "'>" + str(auction.nft_name) + "</a>\n" \
        + "<b>Лидер: </b>" + str(auction.leader_fullname) + "\n" \
        + "<b>Ставка лидера: </b>" + str(auction.leader_price) + "💎\n\n"\
        + "#аукцион"+str(auction_id) + "\n" \
        + "/a_" + str(auction_id) + " via @" + bot_address

        #оправляем сообщение каждому из участников аукциона (кроме того, кто поднял ставку) + владельцу
        receivers = get_participants_list(auction.id, param)
        receivers.append(auction.owner_user_id) #добавляем в получатели владельца

        for receiver in receivers:
            if receiver != user.user_id:
                bot.send_photo(receiver, photo=open(auction.image_path, 'rb'), caption=info, parse_mode='html')

        #отправляем сообщение админу
        admin = BotUser()
        admin.user_id = admin_users[0]
        admin.lang = "ru"
        bot.send_message(admin.user_id, "Повышена ставка в аукционе №" + str(auction.id), parse_mode='html')
        show_auction_info(auction.id, admin, bot, param)

        #отправляем сообщение в каналы
        if send_notif_to_channel == True:
            for channel_id in channel_ids:
                pass
                #bot.send_photo(channel_id, photo=open(auction.image_path, 'rb'), caption=info, parse_mode='html')

    except Exception as err:
        print(err)


###########################################################
# рассылка информации об отмене аукциона
def send_cancel_auction_notif_ru(auction_id, bot, channel_ids, param):
    try:
        auc = Auction()
        auc.fill_by_id(auction_id,param)

        info = "❌<b>Аукцион №" +str(auc.id) + " был отменён владельцем!</b>❌" \
        + "__________________________________\n" \
        + "<a href='" + explorer_api_link + auc.nft_address + "'>" + str(auc.nft_name) + "</a>\n" \
        + "<b>Владелец: </b>" + auc.owner_fullname + "\n\n" \
        + "#cancelled #аукцион"+str(auction_id)

        #оправляем сообщение каждому из участников аукциона
        receivers = get_participants_list(auc.id, param)
        for receiver in receivers:
            bot.send_photo(receiver, photo=open(auc.image_path, 'rb'), caption=info, parse_mode='html')

        #отправляем сообщение в канал
        if send_notif_to_channel == True:
            for channel_id in channel_ids:
                bot.send_photo(channel_id, photo=open(auc.image_path, 'rb'), caption=info, parse_mode='html')

    except Exception as err:
        print(err)



########################################################################################################
# Сохранение нового аукциона в БД
def save_new_auction_to_db(auction, param):
    try:
        connect1 = psycopg2.connect(host=param[0], port=param[1], dbname=param[2], user=param[3],  password=param[4])
        schema = param[5]
        cursor1 = connect1.cursor()
        comment = str(auction.comment).replace("\'","").strip()
        insert_sql = "insert into "+schema+".d_auctions (collection_id, nft_id, owner_user_id, owner_wallet, start_price, price_step, " \
            + " start_ts, end_ts, comment, bot_id) values (" \
            + str(auction.collection_id) + ","+str(auction.nft_id)+ "," + str(auction.owner_user_id) + ",'" + str(auction.owner_wallet)+"', " \
            + str(auction.start_price) + ", " + str(auction.price_step) + ", now(), '" \
            + str(auction.end_ts) + "', '"+ comment+"',"+str(auction.bot_id) +  ")"

        cursor1.execute(insert_sql)
        connect1.commit()
        cursor1.close()

        #обновляем статистику у пользователя-владельца
        cursor3 = connect1.cursor()
        update_sql = "update "+schema+".d_users set auctions_total=auctions_total+1 where user_id="+str(auction.owner_user_id)
        cursor3.execute(update_sql)
        connect1.commit()
        cursor3.close()

        #возвращаем ID созданного аукциона
        cursor2 = connect1.cursor()
        select_sql = "select max(id) from "+schema+".d_auctions where owner_user_id="+str(auction.owner_user_id)
        cursor2.execute(select_sql)
        data = cursor2.fetchone()
        cursor2.close()

        auction_id = 0
        if data is not None:
            auction_id=int(data[0])

        print(get_now() + " - New auction created, ID ="+str(auction_id))
        return auction_id

    except Exception as err:
        print(err)
    finally:
        connect1.close()

########################################################################################################
# Обновление отменённого аукциона
def update_cancelled_auction(auction_id, user_id, param, decrease_limit):
    try:
        connect1 = psycopg2.connect(host=param[0], port=param[1], dbname=param[2], user=param[3],  password=param[4])
        schema = param[5]

        #обновляем статус аукциона
        cursor1 = connect1.cursor()
        update_sql = "update "+schema+".d_auctions set status='cancelled' where id="+str(auction_id)
        cursor1.execute(update_sql)
        connect1.commit()
        cursor1.close()

        #отмена со ставкой, уменьшает лимит отмен
        if decrease_limit==True:
            update_cancel_limit = "cancel_limit=cancel_limit-1, "
        else:
            update_cancel_limit = ""

        # обновляем лимит отмен и статистику пользователя-владельца
        cursor2 = connect1.cursor()
        update_sql = "update "+schema+".d_users set "+update_cancel_limit+"auctions_cancelled=auctions_cancelled+1 where user_id="+str(user_id)
        cursor2.execute(update_sql)
        connect1.commit()
        cursor2.close()

    except Exception as err:
        print(err)
    finally:
        connect1.close()


########################################################################################################
# Обновление истории изменения кошельков пользователя
def add_new_participant(auction_id, user_id, wallet, param):
    try:
        connect1 = psycopg2.connect(host=param[0], port=param[1], dbname=param[2], user=param[3],  password=param[4])
        schema = param[5]
        cursor1 = connect1.cursor()

        #добавляем нового участника
        insert_sql = "insert into "+schema+".f_auction_participants (auction_id, user_id, wallet) " \
        + " values ("+str(auction_id)+", "+str(user_id)+", '"+wallet+"')"
        cursor1.execute(insert_sql)
        connect1.commit()

        #обновляем данные о количестве участников аукциона
        update_sql = "update " +schema+ ".d_auctions set participants = participants + 1 where id="+str(auction_id)
        cursor1.execute(update_sql)
        connect1.commit()
        cursor1.close()

        print("New participant added: auction_id=" +str(auction_id) + ", user_id="+str(user_id) )
    except Exception as err:
        print(err)
    finally:
        connect1.close()

########################################################################################################
# Поднятие ставки участником
def raise_auction_price(auction_id, user, param):
    try:
        connect1 = psycopg2.connect(host=param[0], port=param[1], dbname=param[2], user=param[3],  password=param[4])
        schema = param[5]
        cursor1 = connect1.cursor()

        #обновляем ставку у аукциона
        update_sql = "update "+schema+".d_auctions set " \
        + " leader_price = coalesce(leader_price + price_step, start_price), leader_user_id="+str(user.user_id) + ", dwh_dt = now(), " \
        + " leader_wallet = (select wallet from "+schema+".v_d_user_wallets where now() between fd and td and user_id="+str(user.user_id)+"), " \
        + " end_ts = (case when now()+interval '10 minutes'>end_ts then  end_ts+interval '10 minutes' else end_ts end) " \
        + " where id="+str(auction_id)
        cursor1.execute(update_sql)
        connect1.commit()

        #сохраняем в таблицу истории повышения ставок
        insert_sql = "insert into " + schema + ".f_auction_user_bids (auction_id, user_id, amount) values (" \
            + str(auction_id) + ", " + str(user.user_id) + ", " \
            + " (select leader_price from "+schema+".d_auctions where id="+str(auction_id)+")"\
            + ")"
        cursor1.execute(insert_sql)
        connect1.commit()
        cursor1.close()

        print("Raise the bid: auction_id=" +str(auction_id) + ", user_id="+str(user.user_id)  )
    except Exception as err:
        print(err)
    finally:
        connect1.close()

###############################################################################################################
# список аукционов, у которых срок завершения истёк
def get_auctions_for_close(bot_id, param):
    try:
        connect1 = psycopg2.connect(host=param[0], port=param[1], dbname=param[2], user=param[3],  password=param[4])
        schema = param[5]
        cursor1 = connect1.cursor()
        select_sql = "select id from "+schema+".d_auctions where status='active' and bot_id = "+str(bot_id) \
        + " and now() AT TIME ZONE 'UTC' > end_ts order by end_ts"
        cursor1.execute(select_sql)
        data = cursor1.fetchall()
        cursor1.close()

        if data is not None and len(data)>0:
            return [x[0] for x in data] #массив первых элементов
        else:
            return None

    except Exception as err:
        print(err)
    finally:
        connect1.close()

###############################################################################################################
# список пользователей, которые не выполнили платёж или перевод NFT в ходе аукциона в течение Х часов
def add_users_for_blacklist(bot_id, param, hours_limit=2):
    try:
        connect1 = psycopg2.connect(host=param[0], port=param[1], dbname=param[2], user=param[3],  password=param[4])
        schema = param[5]

        # добавляем пользователей в чёрный список
        cursor2 = connect1.cursor()
        insert_sql = "insert into "+schema+".d_users_blacklist (user_id, wallet, nft_id, auction_id, reason) " \
        + "select leader_user_id, leader_wallet, null, auction_id, 'leader did not pay' " \
        + " from "+schema+".v_d_auctions where bot_id="+str(bot_id)+" and status in ('payment') and now() AT TIME ZONE 'UTC' > (end_ts AT TIME ZONE 'UTC') + interval '"+str(hours_limit)+" hours'" \
        + " union all " \
        + " select owner_user_id, owner_wallet, nft_id, auction_id, 'owner did not transfer the NFT' " \
        + " from "+schema+".v_d_auctions where bot_id="+str(bot_id)+" and status in ('NFT transfer') and now() AT TIME ZONE 'UTC' > (end_ts AT TIME ZONE 'UTC') + interval '"+str(hours_limit)+" hours'"
        cursor2.execute(insert_sql)
        connect1.commit()
        cursor2.close()

        # делаем выборку всех просроченных аукционов
        cursor1 = connect1.cursor()
        select_sql = "select auction_id, status, owner_user_id, owner_wallet, leader_user_id, leader_wallet, nft_id " \
        + " from "+schema+".v_d_auctions where status in ('payment','NFT transfer') " \
        + " and bot_id="+str(bot_id) \
        + " and now() AT TIME ZONE 'UTC' > (end_ts AT TIME ZONE 'UTC') + interval '"+str(hours_limit)+" hours'"
        cursor1.execute(select_sql)
        data = cursor1.fetchall()
        cursor1.close()

        result = []
        for row in data:
            if row[1] == 'payment': #лидер не перевёл платёж
                result.append([row[4], row[0], "leader"])
            elif row[1] == 'NFT transfer': # владелец не перевёл NFT
                result.append([row[2], row[0], "owner"])

        # отменяем все просроченные аукционы
        cursor2 = connect1.cursor()
        update_sql = "update "+schema+".d_auctions set status='cancelled' " \
        + " where status in ('payment','NFT transfer') and bot_id="+str(bot_id) \
        + " and now() AT TIME ZONE 'UTC' > (end_ts AT TIME ZONE 'UTC') + interval '"+str(hours_limit)+" hours'"
        cursor2.execute(update_sql)
        connect1.commit()
        cursor2.close()

        return result

    except Exception as err:
        print(err)
    finally:
        connect1.close()

###############################################################################################################
# уведомление пользователей о попадании в чёрный список
def blacklist_notif_ru(blacklist_user_id, blacklist_auction_id, blacklist_type, channel_ids, bot, param):
    try:
        blacklist_user = BotUser()
        blacklist_user.fill_by_id(blacklist_user_id, param)

        # отправляем сообщение заблокированному пользователю
        if blacklist_type == "owner":
            text_to_send = translate_txt("msg_blacklist_owner", blacklist_user.lang).format(str(blacklist_auction_id))
            bot.send_message(blacklist_user_id, text_to_send, parse_mode='html')
        elif blacklist_type == "leader":
            text_to_send = translate_txt("msg_blacklist_leader", blacklist_user.lang).format(str(blacklist_auction_id))
            bot.send_message(blacklist_user_id, text_to_send, parse_mode='html')

        # отправляем сообщение в канал
        text_to_send2 = "☠Пользователь " + str(blacklist_user.full_name) + " добавлен в чёрный список!☠\n" \
                                                                           "Причина - {}\n\n#blacklist"
        if blacklist_type == "owner":
            text_to_send2 = text_to_send2.format(
                "не перевёл NFT победителю аукциона №" + str(blacklist_auction_id) + " после оплаты.")
        elif blacklist_type == "leader":
            text_to_send2 = text_to_send2.format(
                "не оплатил ставку в аукционе №" + str(blacklist_auction_id) + " после победы.")

        if send_notif_to_channel == True:
            for channel_id in channel_ids:
                bot.send_message(channel_id, text_to_send2, parse_mode='html')

    except Exception as err:
        print(err)

###############################################################################################################
# обновление статуса аукциона в БД
def set_auction_status(auction, status, param, bot_commission=None):
    try:
        connect1 = psycopg2.connect(host=param[0], port=param[1], dbname=param[2], user=param[3],  password=param[4])
        schema = param[5]
        cursor1 = connect1.cursor()

        #комиссия после завершения аукциона с победителем
        if bot_commission is not None:
            update_sql = "update " + schema + ".d_auctions set status='" + status + "', bot_commission="+str(bot_commission)+" where id=" + str(auction.id)
        else:
            update_sql = "update "+schema+".d_auctions set status='"+status+"' where id=" + str(auction.id)

        cursor1.execute(update_sql)
        connect1.commit()
        cursor1.close()

        #обновляем статистику пользователей-владельцев
        if status =='finished':
            field_name = None
            if auction.participants>0 and auction.leader_user_id is not None:
                field_name = 'auctions_with_winner'
            elif auction.leader_user_id is None:
                field_name = 'auctions_wo_winner'

            if field_name is not None:
                cursor2 = connect1.cursor()
                update_sql2 = "update " + schema + ".d_users set "+field_name+"="+field_name+"+1 where user_id=" + str(auction.owner_user_id)
                cursor2.execute(update_sql2)
                connect1.commit()
                cursor2.close()

    except Exception as err:
        print(err)
    finally:
        connect1.close()


###############################################################################################################
# автоматическое закрытие аукциона по истечению времени
# список аукционов, у которых срок завершения истёк
def autoclose_auction(auction_id, bot, channel_ids, bot_name, param):
    try:
        auction = Auction()
        auction.fill_by_id(auction_id, param)

        if auction.leader_user_id is not None: #если у аукциона есть победитель

            #комиссия
            auction.bot_commission = get_comission_amount(auction.leader_price, auction.owner_user_id, auction.leader_user_id, auction.bot_id, param)

            # обновляем информацию по аукциону + размер комиссии
            set_auction_status(auction, 'payment', param, auction.bot_commission)

            # отправляем сообщение владельцу аукциона (дождаться сообщения о переводе на кошелёк гаранта)
            text_to_send = translate_txt('msg_auction_finished_owner1', auction.owner_lang).format(
                str(auction_id), auction.leader_fullname, f'<code>{auction.leader_wallet}</code>', str(auction.leader_price))
            bot.send_message(auction.owner_user_id, text_to_send, parse_mode='html')

            # отправляем сообщение победителю аукциона (перевести ставку на кошелёк гаранта)
            full_amount = float(auction.leader_price) + float(auction.bot_commission)
            amount_nano = int(full_amount * (10**9))
            fast_pay_link = payment_link.format(guarantor_wallet, str(amount_nano), "auction" + str(auction.id))
            text_to_send = translate_txt('msg_auction_finished_leader1', auction.leader_lang).format(str(auction_id), fast_pay_link,
            str(full_amount), f'<code>{guarantor_wallet}</code>', str(auction.leader_price), str(auction.bot_commission),  f'<code>{"auction"+str(auction_id)}</code>')
            bot.send_message(auction.leader_user_id, text_to_send, parse_mode='html')

            keyboard2 = types.InlineKeyboardMarkup()
            keyboard2.add(types.InlineKeyboardButton(text=translate_txt("btn_payment_done", auction.leader_lang), callback_data='auction_leader_paid;'+str(auction_id)))
            bot.send_message(auction.leader_user_id, translate_txt("msg_press_button_below", auction.leader_lang), reply_markup=keyboard2, parse_mode='html')

            # отправляем сообщение в канал о завершении аукциона и о победителе
            info = "⏱<b>Аукцион №" +str(auction_id) + "</b> завершён!⏱" \
            + "__________________________________\n" \
            + "<a href='" + explorer_api_link + auction.nft_address + "'>" + str(auction.nft_name) + "</a>\n" \
            + "<b>Победитель: </b>" + auction.leader_fullname + "\n"\
            + "<b>Ставка победителя,💎: </b>" + str(auction.leader_price) + "\n\n"\
            + "#closed #аукцион"+str(auction_id) + " on @" + str(bot_name)

        else: # если нет победителя - сразу завершаем аукцион
            # обновляем информацию по аукциону
            set_auction_status(auction, 'finished', param)

            # отправляем сообщение владельцу аукциона
            text_to_send = translate_txt('msg_auction_finished_owner2', auction.owner_lang).format(str(auction_id))
            bot.send_message(auction.owner_user_id, text_to_send, parse_mode='html')

            # отправляем сообщение в канал о завершении аукциона и о победителе
            info = "⏱<b>Аукцион №" +str(auction_id) + "</b> завершён без победителя!⏱" \
            + "__________________________________\n" \
            + "<a href='" + explorer_api_link + auction.nft_address + "'>" + str(auction.nft_name) + "</a>\n" \
            + "#closed #аукцион"+str(auction_id)+ " on @" + str(bot_name)

        #отправляем сообщение каждому из участников аукциона (кроме того, кто победил)
        receivers = get_participants_list(auction_id, param)
        for receiver in receivers:
            if receiver != auction.leader_user_id:
                bot.send_photo(receiver, photo=open(auction.image_path, 'rb'), caption=info, parse_mode='html')

        #отправляем сообщение в каналы
        if send_notif_to_channel == True:
            for channel_id in channel_ids:
                bot.send_photo(channel_id, photo=open(auction.image_path, 'rb'), caption=info, parse_mode='html')

    except Exception as err:
        print(err)

########################################################################################################
# проверка баланса кошелька для участия в аукционе или для поднятия ставки
def check_balance_for_auction(wallet, auction_id, param):
    try:
        #получаем информацию о балансе кошелька
        user_balance = asyncio.run(get_balance_async(wallet))
        print("Balance of wallet "+str(wallet) + ": " + str(user_balance))

        auc = Auction()
        auc.fill_by_id(auction_id, param)  # заполняем информацию из БД
        minimum_balance = (auc.start_price if auc.leader_price is None else auc.leader_price + auc.price_step)

        return minimum_balance, round(user_balance, 2)
    except Exception as err:
        print(err)


########################################################################################################
# Отправка команды на закрытие просроченного аукциона
def send_auction_close_message(bot_id):
    try:
        # tg_client1 = TelegramClient(StringSession(), api_id, api_hash).start(phone=phone)
        # print(tg_client1.session.save())
        bot_token, bot_name, channel_ids, bot_entity_id, bot_access_hash, collection_id, start_logo = get_bot_info(
            bot_id, connect_par)

        tg_client1 = TelegramClient(StringSession(session_id), api_id, api_hash)
        tg_client1.start()
        print('Telegram session started successfully!')

        # bot_entity = tg_client1.get_entity(bot_name) #вызывает ошибку A wait of 13606 seconds is required (caused by ResolveUsernameRequest)
        bot_entity = tg_client1.get_input_entity(
            InputPeerUser(user_id=int(bot_entity_id), access_hash=int(bot_access_hash)))
        print("bot_name: " + str(bot_name) + "; entity_id=" + str(bot_entity.user_id) + "; access_hash=" + str(
            bot_entity.access_hash))

        auctions = get_auctions_for_close(bot_id, connect_par)
        print("Auctions for close: " + str(auctions))
        if auctions is not None:
            for auction_id in auctions:
                tg_client1.send_message(bot_entity, "/autoclose_" + str(auction_id))

    except Exception as err:
        print(err)
    finally:
        tg_client1.disconnect()

########################################################################################################
# Отправка команды на добавление пользователя в чёрный список
def send_blacklist_message(bot_id):
    try:
        # tg_client1 = TelegramClient(StringSession(), api_id, api_hash).start(phone=phone)
        # print(tg_client1.session.save())
        bot_token, bot_name, channel_ids, bot_entity_id, bot_access_hash, collection_id, start_logo = get_bot_info(
            bot_id, connect_par)

        tg_client1 = TelegramClient(StringSession(session_id), api_id, api_hash)
        tg_client1.start()
        print('Telegram session started successfully!')

        # bot_entity = tg_client1.get_entity(bot_name) #вызывает ошибку A wait of 13606 seconds is required (caused by ResolveUsernameRequest)
        bot_entity = tg_client1.get_input_entity(InputPeerUser(user_id=int(bot_entity_id), access_hash=int(bot_access_hash)))
        print("bot_name: " + str(bot_name) + "; entity_id=" + str(bot_entity.user_id) + "; access_hash=" + str(
            bot_entity.access_hash))

        black_list = add_users_for_blacklist(collection_id, connect_par, hours_limit=2)
        print(black_list)
        if black_list is not None:
            for row in black_list:
                tg_client1.send_message(bot_entity, "/blacklist_" + str(row[0]) + "_" + str(row[1]) + "_" + str(row[2]))


    except Exception as err:
        print(err)
    finally:
        tg_client1.disconnect()

