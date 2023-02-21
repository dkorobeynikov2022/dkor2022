import telebot #pytelegrambotapi

from main_config import connect_par
from main_funclib import get_bot_info, get_now, get_user_info, insert_update_user_info, insert_user_log
bot_id = 3
def main():
    try:
        bot_token, bot_name, channel_ids, bot_entity_id, bot_access_hash, collection_id, start_logo = get_bot_info(bot_id, connect_par) #'5363287773:AAHQ6hl2s9du747hlqA_p1WmHCJK7Xo6zp0' #   @dk_python_test_bot

        bot1 = telebot.TeleBot(bot_token)
        print(get_now() + ' - Bot connected! Token = ' + bot_token + ", bot_id="+str(bot_id) + ", collection_id="+str(collection_id))

        #обработка всех обращений бота
        @bot1.message_handler(content_types=['text', 'photo'])
        def get_user_messages(msg):
            user = get_user_info(msg)
            user_msg = str(msg.text).strip() if msg.text is not None else str(msg.caption).strip()
            print(get_now() + " [message_handler] " + str(user.show_info_array()))

            if user_msg in ['/start', '/menu']:
                # обновление/добавление пользователя в базе при вводе команд start и menu
                insert_update_user_info(user, bot_id, connect_par)
                insert_user_log(user, bot_id, connect_par)

            #######################################################################################
            if user_msg in ['/start']:
                pass
                # стартовое меню о пользователе
                #show_user_start_info(bot1, user, bot_id, start_logo, connect_par)

            elif user_msg in ['/menu']:
                pass
                # основное меню
                #show_main_menu(bot1, user, bot_id)

    except Exception as err:
        print(err)

