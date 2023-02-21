import psycopg2
import telebot #pytelegrambotapi
from telebot import types

from main_config import connect_par
from messages import translate_txt

###############################################################################################################
# информация об эйрдропе
def get_airdrop_info(user, param):
    try:
        connect1 = psycopg2.connect(host=param[0], port=param[1], dbname=param[2], user=param[3],  password=param[4])
        schema = param[5]

        cursor1 = connect1.cursor()
        select_sql = "select air.info_rus, air.info_eng, " \
        + " (case when usr.user_id is not null then true else false end) as is_participant, bot_id from "+schema+".d_airdrops air " \
        + " left join nft_auction_bot.f_airdrop_users usr on (air.id=usr.airdrop_id and usr.user_id="+str(user.user_id)+") " \
        + " where now() between air.start_ts and air.end_ts"
        cursor1.execute(select_sql)
        data = cursor1.fetchone()
        cursor1.close()

        if data is not None and len(data)>0:
            if user.lang == 'ru':
                return data[2], data[0].replace("#", '\n')
            else:
                return data[2], data[1].replace("#", '\n')

    except Exception as err:
        print(err)
    finally:
        connect1.close()

###############################################################################################################
# сохраняем нового участника эйрдропа
def save_airdrop_participant(user_id, wallet, param):
    try:
        connect1 = psycopg2.connect(host=param[0], port=param[1], dbname=param[2], user=param[3],  password=param[4])
        schema = param[5]

        cursor1 = connect1.cursor()
        insert_sql = "insert into "+schema+".f_airdrop_users (airdrop_id, user_id, info) values (" \
        "(select id from "+schema+".d_airdrops where now() between start_ts and end_ts), "+str(user_id)+", '"+str(wallet)+"')"
        cursor1.execute(insert_sql)
        connect1.commit()
        cursor1.close()

    except Exception as err:
        print(err)
    finally:
        connect1.close()


def save_channel_membership_airdrop (bot_token, channel_id, airdrop_id, param):
    try:
        connect1 = psycopg2.connect(host=param[0], port=param[1], dbname=param[2], user=param[3],  password=param[4])
        schema = param[5]

        cursor1 = connect1.cursor()
        select_sql = "select user_id from "+schema+".f_airdrop_users where airdrop_id="+str(airdrop_id)
        cursor1.execute(select_sql)
        users = cursor1.fetchall()
        cursor1.close()

        print("Airdrop users count: " + str(len(users)))

        result = []
        if users is not None and len(users)>0:
            bot = telebot.TeleBot(bot_token)

            for usr in users:
                user_id = usr[0]
                print("check user_id="+str(user_id))
                try:
                    status = bot.get_chat_member(channel_id, user_id).status
                    if status in ['member', 'creator']:
                        result.append([user_id, True])
                    else:
                        result.append([user_id, False])
                except Exception as err0:
                    print(err0)

        print("Result users count: " + str(len(users)))

        cursor2 = connect1.cursor()
        for row in result:
            insert_sql = "insert into "+schema+".f_airdrop_users_membership (airdrop_id, user_id, channel_id, is_member)  values (" \
                + str(airdrop_id) + "," + str(row[0]) + "," + str(channel_id) + "," + str(row[1]) + ")"
            cursor2.execute(insert_sql)

        connect1.commit()
        cursor2.close()
        bot.close()

        print("The End")

    except Exception as err:
        print(err)
    finally:
        connect1.close()


#save_channel_membership_airdrop("5289795131:AAHaSSuxA4c1iM8-Mp9AO0W5UtAcagTZKzI", -1001703115531, 1, connect_par)