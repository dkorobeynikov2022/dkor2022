import psycopg2
import json
import math
import requests
from telebot import types
from datetime import datetime, timezone, timedelta
from messages import translate_txt
from main_config import check_nft_api_link, explorer_api_link, admin_users, donate_wallet, donation_logo, cryptobot_donation
from wallets_funclib import address_to_bounceable
import hashlib

class BotUser:
    def __init__(self):
        self.user_id = None
        self.username = None
        self.first_name = None
        self.last_name = None
        self.full_name = None
        self.lang = None
        self.wallet = None
        self.type = None

    def show_info_array(self):
        return [self.user_id, self.username, self.lang]

    def fill_by_id(self, user_id, param):
        try:
            connect1 = psycopg2.connect(host=param[0], port=param[1], dbname=param[2], user=param[3], password=param[4])
            schema = param[5]

            cursor1 = connect1.cursor()
            select_sql = "select user_id, username, first_name,last_name,language_code,wallet,type from " + schema + ".v_d_users where user_id=" + str(user_id)
            cursor1.execute(select_sql)
            data = cursor1.fetchone()
            print(data)
            cursor1.close()

            self.user_id = data[0]
            self.username = data[1]
            self.first_name = data[2]
            self.last_name = data[3]
            self.full_name = (self.first_name + " " + self.last_name).strip() + (" [@"+self.username+"]" if self.username != "" else "")
            self.lang = data[4]
            self.wallet = data[5]
            self.type = data[6]

        except Exception as err:
            print(err)
        finally:
            connect1.close()

##################################################################################
# текущее время по часовому поясу MSK
def get_now():
    return str(datetime.now(timezone.utc)+timedelta(hours=3))[0:19]

def string_to_array(str, delimiter):
    return str.replace("[", "").replace("]", "").replace(" ","").split(delimiter)

def hashmd5(message):
    return str(hashlib.md5(str(message).encode('utf-8')).hexdigest())

##################################################################################
# считываем токен бота, привязанного к данной коллекции
def get_bot_info(collection_id, param):
    try:
        connect1 = psycopg2.connect(host=param[0], port=param[1], dbname=param[2], user=param[3],  password=param[4])
        schema = param[5]
        cursor1 = connect1.cursor()

        select_sql = "select token, name, channel_ids, entity_id, access_hash, collection_id, start_logo " \
            + "from "+schema+".d_bots where id=" + str(collection_id)
        cursor1.execute(select_sql)
        data = cursor1.fetchone()
        cursor1.close()

        if data is not None and len(data)>0:
            bot_token = data[0]
            bot_name = data[1]
            channel_ids =  data[2]
            bot_entity_id = data[3]
            bot_access_hash = data[4]
            collection_id = data[5]
            start_logo = data[6]

            return bot_token, bot_name, channel_ids, bot_entity_id, bot_access_hash, collection_id, start_logo
        else:
            return None, None, None, None, None, None, None

    except Exception as err:
        print(err)
    finally:
        connect1.close()


########################################################################################################
# считывание информации о пользователе из сообщения + глобальных массивов скрипта.
def get_user_info(msg):
    try:
        user = BotUser()
        user.user_id = msg.from_user.id
        user.username = '' if msg.from_user.username is None else msg.from_user.username
        user.first_name = '' if msg.from_user.first_name is None else msg.from_user.first_name
        user.last_name = '' if msg.from_user.last_name is None else msg.from_user.last_name
        user.lang = 'ru' if msg.from_user.language_code is None else msg.from_user.language_code
        user.full_name = (user.first_name + " " + user.last_name).strip() + (" [@"+user.username+"]" if user.username != "" else "")

        return user

    except Exception as err:
        print(err)
########################################################################################################
# Считывание из БД вспомогательной информации - последний кошелёк и признак блэклиста
def get_user_db_info(user, param):
    try:
        connect1 = psycopg2.connect(host=param[0], port=param[1], dbname=param[2], user=param[3],  password=param[4])
        schema = param[5]
        cursor1 = connect1.cursor()
        select_sql = "select user_id, wallet, type from "+schema+".v_d_users where user_id="+str(user.user_id)
        cursor1.execute(select_sql)
        data = cursor1.fetchone()
        cursor1.close()

        user.wallet = data[1]
        user.type = data[2]

        print("get user ["+str(user.user_id)+"] info from db successfully")

    except Exception as err:
        print(err)
    finally:
        connect1.close()

########################################################################################################
# функция добавления или обновления информации о пользователе в БД
def insert_update_user_info(user, bot_id, param):
    try:
        connect1 = psycopg2.connect(host=param[0], port=param[1], dbname=param[2], user=param[3],  password=param[4])
        schema = param[5]
        cursor1 = connect1.cursor()

        user_id = str(user.user_id)
        username = "null" if user.username is None else "'"+user.username.replace("\'", "")+"'"
        first_name = "null" if user.first_name is None else "'"+user.first_name.replace("\'", "")+"'"
        last_name = "null" if user.last_name is None else "'"+user.last_name.replace("\'", "")+"'"
        language_code = "null" if user.lang is None else "'"+user.lang+"'"

        merge_sql = " INSERT INTO "+schema+".d_users (user_id, username, first_name, last_name, start_ts, language_code, last_activity_ts) " \
            " VALUES ("+user_id+", "+username+", "+first_name+", "+last_name+", now(), "+language_code+", now()) " \
            " ON CONFLICT(user_id) DO UPDATE SET "\
            " username = "+username+", first_name="+first_name+", last_name="+last_name+", language_code="+language_code+", last_activity_ts=now(); "
        cursor1.execute(merge_sql)

        insert_sql = "insert into "+schema+".f_users_bots(user_id, bot_id) values ("+user_id+","+str(bot_id)+") " \
        + " on conflict (user_id, bot_id) DO NOTHING"
        cursor1.execute(insert_sql)

        connect1.commit()
        cursor1.close()

        print(get_now() + " User ["+str(user.user_id)+ " ("+ str(user.username) + ")]"+ " info updated successfully!")

    except Exception as err:
        print(err)
    finally:
        connect1.close()


########################################################################################################
# функция добавления или обновления информации о пользователе в БД
def insert_user_log(user, bot_id, param):
    try:
        connect1 = psycopg2.connect(host=param[0], port=param[1], dbname=param[2], user=param[3],  password=param[4])
        schema = param[5]
        cursor1 = connect1.cursor()

        user_id = str(user.user_id)
        username = "null" if user.username is None else "'"+user.username.replace("\'", "")+"'"
        first_name = "null" if user.first_name is None else "'"+user.first_name.replace("\'", "")+"'"
        last_name = "null" if user.last_name is None else "'"+user.last_name.replace("\'", "")+"'"
        language_code = "null" if user.lang is None else "'"+user.lang+"'"

        insert_sql = "insert into "+schema+".f_users_log (user_id, username, first_name, last_name, language_code, bot_id) " \
            " VALUES ("+user_id+", "+username+", "+first_name+", "+last_name+", "+language_code+ ", " +str(bot_id)+  ")"
        cursor1.execute(insert_sql)
        connect1.commit()
        cursor1.close()


    except Exception as err:
        print(err)
    finally:
        connect1.close()


########################################################################################################
# Функция отображения стартовой информации о пользователе
def show_user_start_info(bot, user, bot_id, start_logo, param):
    try:
        # загружаем из БД вспомогательную информацию о пользователе
        get_user_db_info(user, param)
        name = (user.first_name + " " + user.last_name).strip()

        text_to_send = translate_txt('msg_start_'+str(bot_id), user.lang).format(f'<code>{str(user.user_id)}</code>',
            user.username, name, f'<code>{user.wallet}</code>', user.type)

        #bot.send_message(user.user_id, text_to_send, parse_mode='html')  # сообщение с инфо о пользователе
        bot.send_photo(user.user_id, photo=open(start_logo, 'rb'), caption=text_to_send, parse_mode='html')

    except Exception as err:
        print(err)



########################################################################################################
def show_main_menu(bot, user, bot_id=1):
    try:

        if bot_id == 1: # arl_auction_bot

            btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_auctions', user.lang), callback_data='menu_auctions'),
                        types.InlineKeyboardButton(text=translate_txt('btn_transfers', user.lang),callback_data='menu_transfers')]
            btn_row2 = [types.InlineKeyboardButton(text=translate_txt('btn_iucn_info', user.lang), callback_data='menu_iucn_info'),
                        types.InlineKeyboardButton(text=translate_txt('btn_help', user.lang),callback_data='menu_help')]
            btn_row3 = [types.InlineKeyboardButton(text=translate_txt('btn_airdrop', user.lang), callback_data='menu_airdrop')]
            btn_row_test = [types.InlineKeyboardButton(text="Test payment", callback_data='test_payment')]

            if user.user_id in admin_users and 1==0:
                keyboard = types.InlineKeyboardMarkup([btn_row1, btn_row2, btn_row_test])
            else:
                keyboard = types.InlineKeyboardMarkup([btn_row1, btn_row2])
            bot.send_message(user.user_id, translate_txt('msg_main_menu', user.lang), reply_markup=keyboard)

        elif bot_id in [2,4]: # monkeys_guarantor_bot

            btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_transfers', user.lang),callback_data='menu_transfers'),
                        types.InlineKeyboardButton(text=translate_txt('btn_auctions', user.lang), callback_data='menu_auctions')]
            btn_row2 = [types.InlineKeyboardButton(text=translate_txt('btn_check_nft', user.lang),callback_data='menu_check_nft')]
            btn_row3 = [types.InlineKeyboardButton(text=translate_txt('btn_monkeys_verif', user.lang), callback_data='monkeys_verif')]
            #btn_row4 = [types.InlineKeyboardButton(text=translate_txt('btn_frogs_verif', user.lang), callback_data='frogs_verif')]
            btn_row5 = [types.InlineKeyboardButton(text=translate_txt('btn_help', user.lang),callback_data='menu_help'),
                        types.InlineKeyboardButton(text=translate_txt('btn_donate', user.lang),callback_data='menu_donation')]
            keyboard = types.InlineKeyboardMarkup([btn_row1, btn_row2, btn_row3, btn_row5])
            bot.send_message(user.user_id, translate_txt('msg_main_menu', user.lang), reply_markup=keyboard)

    except Exception as err:
        print(err)

########################################################################################################
def show_help_menu(bot, user, bot_id):
    try:
        btn_row1 = [
            types.InlineKeyboardButton(text=translate_txt('btn_back', user.lang), callback_data='main_menu')]

        keyboard = types.InlineKeyboardMarkup([btn_row1])
        text_to_send = translate_txt('msg_help_menu_'+str(bot_id), user.lang).format(f'<code>{donate_wallet}</code>',donate_wallet, donate_wallet, cryptobot_donation)
        bot.send_message(user.user_id, text_to_send, reply_markup=keyboard, parse_mode='html')

    except Exception as err:
        print(err)

########################################################################################################
def show_donation_menu(bot, user):
    try:
        btn_row1 = [
            types.InlineKeyboardButton(text=translate_txt('btn_back', user.lang), callback_data='main_menu')]

        keyboard = types.InlineKeyboardMarkup([btn_row1])
        text_to_send = translate_txt('msg_donation', user.lang).format(f'<code>{donate_wallet}</code>',donate_wallet, donate_wallet, cryptobot_donation)
        bot.send_photo(user.user_id, photo=open(donation_logo, 'rb'), caption=text_to_send, reply_markup=keyboard, parse_mode='html')

    except Exception as err:
        print(err)
########################################################################################################
# проверка введённого TON-кошелька на корректность, присутствие в чёрном списке и верификацию
def check_wallet(wallet, user_id, param):
    try:
        wallet = (wallet.replace("https://tonhub.com/transfer/","").replace("ton://transfer/","")).strip()

        connect1 = psycopg2.connect(host=param[0], port=param[1], dbname=param[2], user=param[3],  password=param[4])
        schema = param[5]

        # проверяем корректность формата кошелька
        if len(wallet) != 48 or wallet[0:2] not in ['EQ', 'UQ']:
            result = 1 #некорректный формат
        else:
            # если пользователь передал кошелёк в формате Non-bounceable, преобразуем в bounceable
            if wallet[0:2] == 'UQ':
                bounceable = address_to_bounceable(wallet)
                print("Convert non-bounceable wallet " + str(wallet) + " to bounceable " + str(bounceable))
                wallet = bounceable

            select_sql = "select count(1) from "+schema+".d_users_blacklist where wallet = '"+str(wallet)+"'"
            cursor1 = connect1.cursor()
            cursor1.execute(select_sql)
            is_blacklist = cursor1.fetchone()[0]
            cursor1.close()
            if is_blacklist !=0:
                result = 2 #кошелёк в чёрном списке

            else:
                select_sql = "select count(1) from "+schema+".d_wallets_verifications where wallet = '"+str(wallet)+"' and user_id="+str(user_id)
                cursor2 = connect1.cursor()
                cursor2.execute(select_sql)
                is_verified = cursor2.fetchone()[0]
                cursor2.close()
                if is_verified == 0:
                    result = 3 #кошелёк неверифицирован
                else:
                    result = 0 # кошелёк корректный, не в чёрном списке, верифицирован

        return wallet, result

    except Exception as err:
        print(err)
    finally:
        connect1.close()


########################################################################################################
# просмотр владельца NFT
def get_nft_owner(nft_address):
    nft_url = check_nft_api_link + nft_address
    print(get_now() + " NFT check link: " + nft_url)
    try:
        resp = requests.get(nft_url).json()
        #print(resp)
        blockchain_owner = resp["nft_item"]["owner_address"]
        return blockchain_owner

    except Exception as err:  # ошибка проверки владельца по API
        print(err)
        return None


########################################################################################################
# комплексная проверка NFT на чёрный список, активные аукционы, принадлежность владельцу
# возвращается код ошибки, текст ошибки и NFT_ID
def check_nft(collection_id, nft_info, owner_wallet, lang, param):
    try:
        connect1 = psycopg2.connect(host=param[0], port=param[1], dbname=param[2], user=param[3],  password=param[4])
        schema = param[5]
        cursor1 = connect1.cursor()
        nft_info = str(nft_info).strip()

        if len(nft_info) == 48 and nft_info[0:2] == 'EQ': #передан адрес NFT в bounceable формате
            filter = " nft.address = '" + nft_info + "'"
        elif len(nft_info) == 48 and nft_info[0:2] == 'UQ': #передан адрес NFT в non-bounceable формате
            print("non-bounceable NFT address: " + nft_info)
            bounceable_address = address_to_bounceable(nft_info)
            print("bounceable NFT address: " + bounceable_address)
            filter = " nft.address = '" + str(bounceable_address) + "'"
        else:
            filter = " (lower(nft.name)=lower('"+nft_info+"') or lower(replace(nft.name, 'ARL ',''))=lower('"+nft_info+ "'))"

        select_sql = "select nft.id, nft.address, nft.name, " \
            + "(case when bl.nft_id is not null then true else false end) as is_blacklist, " \
            + "(case when auc.nft_id is not null then true else false end) as is_active_auction " \
            + " from "+schema+".d_nft nft " \
            + " left join nft_auction_bot.d_users_blacklist bl on (nft.id=bl.nft_id) " \
            + " left join nft_auction_bot.d_auctions auc on (nft.id=auc.nft_id and auc.status not in ('finished', 'cancelled')) " \
            + " where nft.collection_id="+str(collection_id)+" and " + filter
        cursor1.execute(select_sql)
        data = cursor1.fetchone()
        cursor1.close()

        if data is None or len(data) == 0: #нет NFT с таким адресом или названием в коллекции
            return 1, translate_txt('msg_nft_incorrect', lang), None

        elif data[3] == True: #NFT в чёрном списке
            return 2, translate_txt('msg_nft_blacklist', lang), data[0]

        elif data[4] == True: #NFT участвует в другом незакрытом аукционе
            return 3, translate_txt('msg_nft_another_auction', lang), data[0]

        else:
            blockchain_owner = get_nft_owner(data[1])
            if blockchain_owner is None:
                return 4, translate_txt('msg_nft_api_error', lang), data[0]
            elif owner_wallet != blockchain_owner: #владелец NFT по блокчейну не совпадает с создателем аукциона
                return 5, translate_txt('msg_nft_wrong_owner', lang), data[0]
            else:
                return 0, None, data[0] # всё в порядке

    except Exception as err:
        print(err)
    finally:
        connect1.close()



########################################################################################################
# проверка введённого TON-кошелька, user_id или NFT на присутствие в чёрном списке
def check_black_list(type, input, param):
    try:
        connect1 = psycopg2.connect(host=param[0], port=param[1], dbname=param[2], user=param[3],  password=param[4])
        schema = param[5]
        cursor1 = connect1.cursor()

        if type == "wallet":
            filter = " wallet='" + str(input) + "'"
        elif type == "nft":
            filter = " nft_id::text='" + str(input) + "'"
        else:
            filter = " user_id::text='"+str(input)+"'"

        select_sql = "select reason, user_id, wallet, nft_id, auction_id from "+schema+".d_users_blacklist where " + str(filter)
        cursor1.execute(select_sql)
        data = cursor1.fetchone()
        cursor1.close()

        if data is not None:
            return data[0]
        else:
            return None

    except Exception as err:
        print(err)
    finally:
        connect1.close()


########################################################################################################
# формирование описания NFT в зависимости от коллекции (в каждой коллекции в поле description - разная информация)
def get_nft_info(collection_id, description, lang):
    try:
        info = ""
        dj = json.loads(description)
        if collection_id==1: # ARL
            kingdom = dj["kingdom"] if lang=="ru" else dj["kingdom_en"]
            phylum = dj["phylum"] if lang=="ru" else dj["phylum_en"]
            animal_class = dj["class"] if lang=="ru" else dj["class_en"]
            filter_group = dj["filter_group"] if lang == "ru" else dj["filter_group_en"]
            system = dj["system"] if lang == "ru" else dj["system_en"]
            trend_ico = {"Increasing": "💚", "Stable": "💛", "Decreasing": "💔", "Unknown": "🤍"}
            trend = trend_ico.get(dj["trend"]) + str(dj["trend"])

            #формируем итоговое описание NFT
            info = translate_txt("nft_info_"+str(collection_id), lang).format(dj["tier"], dj["nft_subtier"], dj["nft_class"],
                kingdom, phylum, animal_class, dj["order"], dj["family"], dj["genus"], filter_group, str(dj["taxonid"]),
                dj["common_name"], str(dj["discovery_year"]), system, trend, dj["last_migration"])

        elif collection_id==2: # RichCats
            #формируем итоговое описание NFT
            info = translate_txt("nft_info_"+str(collection_id), lang).format(dj["body"], dj["body_info"],
                dj["eyes"], dj["eyes_info"], dj["teeth"], dj["teeth_info"], dj["whiskers"], dj["whiskers_info"],
                dj["background"], dj["background_info"])

        elif collection_id==3: # TON Earth Lands
            lake_access = "✅" if dj["lake_access"]=="Yes" else "❌"
            ocean_access = "✅" if dj["ocean_access"] == "Yes" else "❌"

            #формируем итоговое описание NFT
            info = translate_txt("nft_info_"+str(collection_id), lang).format(dj["type"], dj["type_info"],
                dj["biome"], dj["biome_info"], lake_access, dj["lake_access_info"], ocean_access, dj["ocean_access_info"])

        elif collection_id==4: # Annihilation
            status = "🎁"+str(dj["status"]) if dj["status"]=="closed" else "🖼"+str(dj["status"])
            type = "👑"+str(dj["type"]) if dj["type"]=="genesis" else "👼"+str(dj["type"])

            #формируем итоговое описание NFT
            info = translate_txt("nft_info_"+str(collection_id), lang).format(dj["description"],type, dj["type_info"],dj["genesis"], dj["genesis_info"],
                status, dj["status_info"], dj["soul"], dj["soul_info"], dj["race"], dj["race_info"], dj["evolution"], dj["evolution_info"],
                dj["superpower"])

        elif collection_id==5: # TON Earth Houses
            #формируем итоговое описание NFT
            info = translate_txt("nft_info_"+str(collection_id), lang).format(dj["base"], dj["base_info"],
                dj["roof"], dj["roof_info"], dj["windows"], dj["windows_info"], dj["door"], dj["door_info"], dj["floors"], dj["floors_info"])

        elif collection_id==6: # TON Earth Houseboats
            #формируем итоговое описание NFT
            info = translate_txt("nft_info_"+str(collection_id), lang).format(dj["base"], dj["base_info"],
                dj["roof"], dj["roof_info"], dj["windows"], dj["windows_info"], dj["door"], dj["door_info"])

        elif collection_id==7: # GBOTS
            #формируем итоговое описание NFT
            info = translate_txt("nft_info_"+str(collection_id), lang).format(dj["elements_type"], dj["elements_type_info"],
                dj["head"], dj["head_info"], dj["eyes"], dj["eyes_info"], dj["torso"], dj["torso_info"],
                dj["inner_body_type"], dj["inner_body_type_info"], dj["outer_body_type"],dj["outer_body_type_info"],
                dj["arms_top"],dj["arms_top_info"],dj["arms_bottom"],dj["arms_bottom_info"],dj["legs_top"],dj["legs_top_info"],
                dj["legs_bottom"], dj["legs_bottom_info"], dj["armor_set"], dj["armor_set_info"],dj["colors"], dj["colors_info"])

        elif collection_id==8: # Deversee
            #формируем итоговое описание NFT
            if dj["water_access"] == 'true':
                water_access = '✅'
            else:
                water_access = '❌'

            info = translate_txt("nft_info_"+str(collection_id), lang).format(dj["city"], dj["city_info"],
                dj["size"], dj["size_info"], water_access, dj["water_access_info"])

        elif collection_id==9: # Punks
            #формируем итоговое описание NFT
            info = translate_txt("nft_info_"+str(collection_id), lang).format(dj["type"], dj["type_info"],
                dj["background"], dj["background_info"], dj["owner"], dj["owner_info"], dj["attr_count"], dj["attr_count_info"],
                dj["attr1"], dj["attr1_info"], dj["attr2"],dj["attr2_info"],
                dj["attr3"],dj["attr3_info"],dj["attr4"],dj["attr4_info"],dj["attr5"],dj["attr5_info"],
                dj["attr6"], dj["attr6_info"], dj["attr7"], dj["attr7_info"])

        elif collection_id in [10,11,12,13]: # RichCats Glasses, Hair, Piercing, Outfits
            #формируем итоговое описание NFT
            info = translate_txt("nft_info_"+str(collection_id), lang).format(dj["type"], dj["type_info"])

        elif collection_id==14: # Diamonds
            #формируем итоговое описание NFT

            shine = '-' if dj["shine"]=='None' else dj["shine"]

            info = translate_txt("nft_info_"+str(collection_id), lang).format(dj["size"], dj["size_info"],
                dj["color"], dj["color_info"], dj["shape"], dj["shape_info"], dj["background"], dj["background_info"],
                dj["cut"], dj["cut_info"], dj["glow"],dj["glow_info"],shine,dj["shine_info"])

        elif collection_id==16: # Doodles
            info = translate_txt("nft_info_"+str(collection_id), lang).format(dj["diamond"], dj["diamond_info"],
                dj["hair"], dj["hair_info"], dj["eyes"], dj["eyes_info"], dj["ears"], dj["ears_info"],
                dj["mouth"], dj["mouth_info"], dj["clothes"],dj["clothes_info"],
                dj["bg"],dj["bg_info"])

        elif collection_id==17: # Dark Doodles
            info = translate_txt("nft_info_"+str(collection_id), lang).format(dj["status"], dj["status_info"],
                dj["head"], dj["head_info"], dj["eyes"], dj["eyes_info"], dj["ears"], dj["ears_info"],
                dj["mouth"], dj["mouth_info"], dj["clothes"],dj["clothes_info"],
                dj["bg"],dj["bg_info"])

        elif collection_id==18: # TON Ducks
            info = translate_txt("nft_info_"+str(collection_id), lang).format(dj["skin"], dj["skin_info"],
                dj["eye"], dj["eye_info"], dj["hat"], dj["hat_info"], dj["diamond"], dj["diamond_info"],
                dj["smoke"], dj["smoke_info"], dj["background"],dj["background_info"])

        elif collection_id==20: # Chuwee Boys
            info = translate_txt("nft_info_"+str(collection_id), lang).format(dj["class"], dj["class_info"],
                dj["grade"], dj["grade_info"], dj["head"], dj["head_info"], dj["skin_color"], dj["skin_color_info"],
                dj["facial_hair"], dj["facial_hair_info"], dj["skin_painting"],dj["skin_painting_info"], dj["accessory"],dj["accessory_info"])

        elif collection_id==21: # BBT
            info = translate_txt("nft_info_"+str(collection_id), lang).format(dj["category"], dj["category_info"],
                dj["collaboration"], dj["collaboration_info"])

        elif collection_id==22: # TAC
            info = translate_txt("nft_info_"+str(collection_id), lang).format(dj["body"], dj["body_info"],
                dj["eyes"], dj["eyes_info"], dj["mouth"], dj["mouth_info"], dj["ear_right"], dj["ear_right_info"],
                dj["ear_left"], dj["ear_left_info"], dj["dress"],dj["dress_info"], dj["hat"],dj["hat_info"],
                dj["diamond"], dj["diamond_info"],dj["accessory_nails"], dj["accessory_nails_info"],dj["accessory_hand"], dj["accessory_hand_info"],
                dj["accessory_rings"], dj["accessory_rings_info"], dj["background"],dj["background_info"])

        elif collection_id==23: # TON Frogs
            status = dj["status"] if lang=="ru" else dj["status_eng"]
            info = translate_txt("nft_info_"+str(collection_id), lang).format(status, dj["status_info"])

        elif collection_id==24: # Dolphy Money Team
            status = dj["status"] if lang=="ru" else dj["status_eng"]
            info = translate_txt("nft_info_"+str(collection_id), lang).format(status, dj["status_info"])

        elif collection_id==25: # Bombasters
            info = translate_txt("nft_info_"+str(collection_id), lang).format(dj["body"], dj["body_info"],
                dj["element"], dj["element_info"], dj["face"], dj["face_info"], dj["wick"], dj["wick_info"],
                dj["shoes"], dj["shoes_info"], dj["main_element"],dj["main_element_info"], dj["gem"],dj["gem_info"],
                                                                              dj["background"],dj["background_info"])
        elif collection_id==26: # Masons
            info = translate_txt("nft_info_"+str(collection_id), lang).format(dj["logo"], dj["logo_info"],
                dj["materials"], dj["materials_info"], dj["gems"], dj["gems_info"], dj["filling"], dj["filling_info"],
                dj["ornament"], dj["ornament_info"], dj["background"],dj["background_info"])

        elif collection_id==27: # Web3TON
            info = translate_txt("nft_info_"+str(collection_id), lang).format(dj["category"], dj["category_info"],
                dj["gender"], dj["gender_info"], dj["race"], dj["race_info"], dj["race_level"], dj["race_level_info"])

        elif collection_id==28: # Fanton
            info = translate_txt("nft_info_"+str(collection_id), lang).format(dj["tier"], dj["tier_info"],
                dj["rarity"], dj["rarity_info"])

        elif collection_id==29: # Круги на полях

            if dj["color"] == 'BLUE':
                color = "🔵 blue"
            elif dj["color"] == 'GREEN':
                color = "🟢 green"
            elif dj["color"] == 'RED':
                color = "🔴 red"
            elif dj["color"] == 'PURPLE':
                color = "🟣 purple"
            elif dj["color"] == 'GOLD':
                color = "🟡 gold"

            filepath = "<a href='https://cloudflare-ipfs.com/ipfs/bafybeibc4kr72r74w3p6fqohya4vp4fqrao3ky332vkl5j2ylmelmvkbgi/"+dj["filepath"]+"'>"+dj["filepath"]+"</a>"


            info = translate_txt("nft_info_"+str(collection_id), lang).format(dj["status"], dj["status_info"],
                color, dj["color_info"], filepath, dj["filepath_info"], dj["person"], dj["person_info"])


        return info

    except Exception as err:
        print(err)
        return ""

########################################################################################################
# отображение информации о конкретном NFT и ссылка на его картинку
def show_nft_info(nft_id, param, lang="en"):
    try:
        connect1 = psycopg2.connect(host=param[0], port=param[1], dbname=param[2], user=param[3],  password=param[4])
        schema = param[5]
        cursor1 = connect1.cursor()

        select_sql = "select id, name, address, description, image_path, collection_id from "+schema+".d_nft where id=" + str(nft_id)
        cursor1.execute(select_sql)
        data = cursor1.fetchone()
        cursor1.close()

        if data is not None:
            name = data[1]
            collection_id = data[5]
            description = data[3]
            nft_url = explorer_api_link + data[2]
            image = data[4]
            info = "<b><a href='"+nft_url+"'>"+name+"</a></b>\n" + get_nft_info(collection_id, description, lang)

            return info, image
        else:
            return None, None

    except Exception as err:
        print(err)
    finally:
        connect1.close()


########################################################################################################
# Обновление истории изменения кошельков пользователя
def update_users_wallets0(user_id, param):
    try:
        connect1 = psycopg2.connect(host=param[0], port=param[1], dbname=param[2], user=param[3],  password=param[4])
        schema = param[5]
        cursor1 = connect1.cursor()
        delete_sql = "delete from "+schema+".d_user_wallets where user_id = " + str(user_id)
        cursor1.execute(delete_sql)
        connect1.commit()
        cursor1.close()

        cursor2 = connect1.cursor()
        insert_sql = "insert into "+schema+".d_user_wallets (user_id, fd, td, wallet) select user_id, fd, td, wallet " \
            + " from "+schema+".v_d_user_wallets where user_id = " + str(user_id)
        cursor2.execute(insert_sql)
        connect1.commit()
        cursor2.close()

        print("Updated wallet for user "+str(user_id))

    except Exception as err:
        print(err)
    finally:
        connect1.close()

###############################################################################################################
# Обновление истории изменения кошельков пользователя
def update_users_wallets(user_id, wallet, source_type, param):
    try:
        if user_id is not None and wallet is not None:
            connect1 = psycopg2.connect(host=param[0], port=param[1], dbname=param[2], user=param[3],  password=param[4])
            schema = param[5]
            cursor1 = connect1.cursor()
            insert_sql = "insert into "+schema+".f_user_wallets_usage (user_id, wallet, source_type) values ("\
            + str(user_id)+", '"+str(wallet)+"', '"+str(source_type)+"')"
            cursor1.execute(insert_sql)
            connect1.commit()
            cursor1.close()

    except Exception as err:
        print(err)
    finally:
        connect1.close()

###############################################################################################################
# список пользователей, которые не выполнили платёж или перевод NFT в ходе аукциона в течение Х часов
def save_wallet_verification(user_id, wallet, param):
    try:
        connect1 = psycopg2.connect(host=param[0], port=param[1], dbname=param[2], user=param[3],  password=param[4])
        schema = param[5]

        cursor1 = connect1.cursor()
        insert_sql = "insert into "+schema+".d_wallets_verifications (user_id, wallet) values (" \
        + str(user_id) + ", '" + wallet + "')"
        cursor1.execute(insert_sql)
        connect1.commit()
        cursor1.close()

    except Exception as err:
        print(err)
    finally:
        connect1.close()


###############################################################################################################
# список NFT коллекций для выбора
def get_collections_list(object_id, object_type, param):
    try:
        connect1 = psycopg2.connect(host=param[0], port=param[1], dbname=param[2], user=param[3],  password=param[4])
        schema = param[5]

        cursor1 = connect1.cursor()
        select_sql = "select id, icon_symbol, name from  "+schema+".d_collections order by order_num"
        cursor1.execute(select_sql)
        data = cursor1.fetchall()
        cursor1.close()

        btn_cols_count = 2  # количество столбцов
        btn_rows_count = math.ceil(len(data) / btn_cols_count)  # количество строк
        keyboard_buttons = [[]]
        for i in range(btn_rows_count):
            buttons_row = []

            for j in range(btn_cols_count):
                if (i * btn_cols_count + j)+1 <= len(data): #при нечётном количестве коллекций
                    row = data[i * btn_cols_count + j]
                    collection_id = str(row[0])
                    icon = str(row[1])
                    name = str(row[2])
                    buttons_row.append(types.InlineKeyboardButton(text=icon+name, callback_data="menu_"+object_type+"_collections;"+str(object_id)+";"+collection_id))
            keyboard_buttons.append(buttons_row)

        keyboard = types.InlineKeyboardMarkup(keyboard_buttons)
        return keyboard

    except Exception as err:
        print(err)
    finally:
        connect1.close()


###############################################################################################################
# Расчёт комиссии бота в зависимости от суммы и типа участников
def get_comission_amount(amount, user1, user2, bot_id, param):
    try:
        connect1 = psycopg2.connect(host=param[0], port=param[1], dbname=param[2], user=param[3],  password=param[4])
        schema = param[5]

        cursor1 = connect1.cursor()
        select_sql = "select greatest(commission_min, "+str(amount)+" * ((case when vip.cnt=0 then commission_perc else vip_commission_perc end)/100.0) ) as commission_amount "\
            + " from "+schema+".d_bots bot "\
            + " left join (select count(1) as cnt from "+schema+".d_monkeys_users_list where user_id in ( "+str(user1)+"," +str(user2)+ " ) ) vip on (1=1) " \
            + " where bot.id=" +str(bot_id)

        cursor1.execute(select_sql)
        data = cursor1.fetchone()
        cursor1.close()

        if data is not None and len(data)>0:
            return data[0]
        else:
            return None

    except Exception as err:
        print(err)
    finally:
        connect1.close()



###############################################################################################################
# Расчёт комиссии бота в зависимости от суммы и типа участников
def get_royalty_info(bot_id, collection_id, param):
    try:
        connect1 = psycopg2.connect(host=param[0], port=param[1], dbname=param[2], user=param[3],  password=param[4])
        schema = param[5]

        cursor1 = connect1.cursor()
        select_sql = "select royalty_address, royalty/100.0 from " +schema+".d_collections where id=" + str(collection_id)
        cursor1.execute(select_sql)
        data = cursor1.fetchone()
        cursor1.close()

        if bot_id in [1]: #бот ARL - нет выплат
            return donate_wallet, 0
        elif data is not None and len(data)>0:
            return data[0], float(data[1])
        else:
            return None, None

    except Exception as err:
        print(err)
    finally:
        connect1.close()


###############################################################################################################
# Расчёт комиссии бота в зависимости от суммы и типа участников
def find_nft_by_address (address, param):
    try:

        # проверяем корректность формата кошелька
        if len(address) != 48 or address[0:2] not in ['EQ', 'UQ']:
            return -1
        else:
            # если пользователь передал адрес в формате Non-bounceable, преобразуем в bounceable
            if address[0:2] == 'UQ':
                address = address_to_bounceable(address)

            connect1 = psycopg2.connect(host=param[0], port=param[1], dbname=param[2], user=param[3],  password=param[4])
            schema = param[5]

            cursor1 = connect1.cursor()
            select_sql = "select id from " +schema+".d_nft where address='" + str(address) + "'"
            cursor1.execute(select_sql)
            data = cursor1.fetchone()
            cursor1.close()
            connect1.close()

            if data is None or len(data)==0:
                return 0
            else:
                return int(data[0])

    except Exception as err:
        print(err)
