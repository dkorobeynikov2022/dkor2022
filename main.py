import telebot #pytelegrambotapi
from telebot import types
from datetime import datetime, timezone, timedelta
import logging

from messages import translate_txt
from main_config import connect_par, admin_users, guarantor_wallet, donate_wallet, payment_link, transfer_deal_amount_limit, transfer_commission, \
    explorer_api_link, guarantor_start_logo, auction_start_price_limit, transfer_nft_service_link, cryptobot_donation, monkey_fund_wallet

from main_funclib import BotUser, get_bot_info, get_user_info, get_user_db_info, insert_update_user_info, insert_user_log, show_user_start_info, \
    update_users_wallets, save_wallet_verification,  show_nft_info, get_nft_owner, check_nft, check_black_list, \
    check_wallet, show_main_menu, show_help_menu, string_to_array, get_collections_list, hashmd5, show_donation_menu, get_comission_amount, \
    get_royalty_info, find_nft_by_address

from blockchain_funclib import check_wallet_payment, send_payment_to_queue

from auctions_funclib import Auction, get_now,  save_auction_temp_data, send_new_auction_notif_ru, send_cancel_auction_notif_ru, \
    get_owner_active_auction, update_cancelled_auction, \
    show_active_auctions, check_auction_id_correct, show_selected_auction_menu, show_auction_info, add_new_participant, raise_auction_price, \
    send_bid_raise_notif_ru, show_user_participations,  autoclose_auction, \
    set_auction_status, blacklist_notif_ru, \
    check_balance_for_auction, show_main_auctions_menu, show_owner_auctions_menu, show_auction_info_before_save, save_new_auction_to_db

from airdrop_funclib import get_airdrop_info, save_airdrop_participant
from transfers_funclib import Transfer, check_buyer_account, show_main_transfers_menu, show_user_transfers, show_new_transfer_to_confirm, \
    show_transfer_info

from monkeys_verificator_funclib import check_user_is_monkeys, check_monkeys_nft, update_monkeys_new_verification

######################################################################################################################
def start_bot(bot_id):
    try:
        logging.getLogger("urllib3").setLevel(logging.WARNING) #отключаем лишние сообщения

        bot_token, bot_name, channel_ids, bot_entity_id, bot_access_hash, collection_id, start_logo = get_bot_info(bot_id, connect_par)
        channel_ids = string_to_array(channel_ids, ",")
        bot1 = None
        if bot_token is not None:
            bot1 = telebot.TeleBot(bot_token)
            print(get_now() + ' - Bot connected! Token = ' + bot_token + ", bot_id="+str(bot_id) + ", collection_id="+str(collection_id))


        ########################################################################################
        #обработка всех обращений бота
        @bot1.message_handler(content_types=['text', 'photo'])
        def get_user_messages(msg):
            user = get_user_info(msg)
            user_msg = str(msg.text).strip() if msg.text is not None else str(msg.caption).strip()
            print(get_now() + " [message_handler] " + str(user.show_info_array()))

            if user_msg in ['/start', '/menu']:
                # обновление/добавление пользователя в базе при вводе команд start и menu
                insert_update_user_info(user, bot_id, connect_par)
                #insert_user_log(user, bot_id, connect_par)

            #######################################################################################
            if user_msg in ['/start']:
                # стартовое меню о пользователе
                show_user_start_info(bot1, user, bot_id, start_logo, connect_par)

            elif user_msg in ['/menu']:
                # основное меню
                show_main_menu(bot1, user, bot_id)

            elif user_msg in ['/help']:
                # основное меню
                show_help_menu(bot1, user, bot_id)

            # передан номер аукциона через ключевую команду /a_
            elif user_msg[0:3] == '/a_':
                auction_id = user_msg.split("_")[1]
                check_result = check_auction_id_correct(bot_id, auction_id, connect_par)
                if check_result == 1:  # аукцион найден и он активен
                    show_selected_auction_menu(user, auction_id, bot1, connect_par)# показываем меню для выбранного аукциона
                else:
                    if check_result == 0:  # аукцион не найден
                        text_to_send = translate_txt('msg_auction_id_not_found', user.lang)
                    elif check_result == -1:  # аукцион не активен
                        text_to_send = translate_txt('msg_auction_id_not_active', user.lang)
                    else:
                        text_to_send = "Error"
                    bot1.send_message(user.user_id, text_to_send, parse_mode='html')

            # команда автозакрытия аукциона по завершению времени
            elif user_msg[0:11] == '/autoclose_' and user.user_id in admin_users:
                auction_id = user_msg.split("_")[1]
                autoclose_auction(auction_id, bot1, channel_ids, bot_name, connect_par)

            # команда рассылки информации о попадании в чёрный список
            elif user_msg[0:11] == '/blacklist_' and user.user_id in admin_users:
                blacklist_user_id = user_msg.split("_")[1]
                blacklist_auction_id = user_msg.split("_")[2]
                blacklist_type = user_msg.split("_")[3]

                blacklist_notif_ru(blacklist_user_id, blacklist_auction_id, blacklist_type, channel_ids, bot1, connect_par)



        ##################################################################################################################
        # обработка нажатий клавиш inline меню
        @bot1.callback_query_handler(func=lambda callback: True)
        def callback_query(callback):
            user = get_user_info(callback)
            action = callback.data.split(';')[0]
            print(get_now() + " [callback_query_handler], action=" + action + ", " + str(user.show_info_array()))

            # удаляем нажатую кнопку
            try:
                bot1.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.id)

                #очищаем инфорацию обо всех message_handler, инициированных на шагах ранее
                bot1.clear_step_handler_by_chat_id(chat_id=callback.message.chat.id)
            except Exception as err:
                print(get_now() + " Error while delete InlineButton message "+str(callback.message.id) + " for user " + str(user.user_id))
            # --------------------------------------------------------------------------------

            # Возврат в основное меню
            if action in ['main_menu']:
                show_main_menu(bot1, user, bot_id)

            # Основное меню -> Аукционы
            elif action == 'menu_auctions':
                show_main_auctions_menu(bot1, user)

            #Основное меню - Продажа через гаранта
            elif action == 'menu_transfers':
                show_main_transfers_menu(bot1, user, bot_id, guarantor_start_logo)

            # Основное меню -> Красная Книга
            elif action == 'menu_iucn_info':
                btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_back', user.lang), callback_data='main_menu')]
                keyboard = types.InlineKeyboardMarkup([btn_row1])
                text_to_send = translate_txt("msg_iucn_input_nft", user.lang)
                bot1.send_message(user.user_id, text_to_send, reply_markup=keyboard, parse_mode='html')
                bot1.register_next_step_handler(callback.message, input_iucn_nft_info)  # шаг для проверки введённого НФТ

            # Основное меню -> Помощь
            elif action == 'menu_help':
                show_help_menu(bot1, user, bot_id)

            # Основное меню -> Помощь
            elif action == 'menu_donation':
                show_donation_menu(bot1, user)


            # Основное меню - Розыгрыш
            elif action == 'menu_airdrop':
                pass
                #btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_back', user.lang), callback_data='main_menu')]
                #keyboard = types.InlineKeyboardMarkup([btn_row1])

                #is_participant, airdrop_info = get_airdrop_info(user, connect_par)
                #if is_participant == True: # уже участвует
                    #bot1.send_message(user.user_id, translate_txt("msg_airdrop_already", user.lang), reply_markup=keyboard, parse_mode='html')
                #else:
                    #text_to_send = airdrop_info + "\n\n" + translate_txt("msg_airdrop_input_wallet", user.lang)
                    #bot1.send_photo(user.user_id, photo=open("images/airdrop_logo.png", 'rb'), caption=text_to_send,reply_markup=keyboard,  parse_mode='html')
                    #bot1.register_next_step_handler(callback.message, input_airdrop_wallet)  # шаг для проверки введённого кошелька

            # Основное меню -> Мои аукционы
            elif action == 'menu_my_auctions':
                show_owner_auctions_menu(bot_id, bot1, user, connect_par)

            # Основное меню -> Мои трансферы
            elif action == 'my_transfers':
                show_user_transfers(bot_id, bot1, user, connect_par)

            # Основное меню -> Мои аукционы -> Новый
            elif action == 'auction_new':
                blacklist_check = check_black_list("user_id", user.user_id, connect_par)
                if blacklist_check is not None: #пользователь в чёрном списке
                    text_to_send = translate_txt('msg_user_blacklist', user.lang).format(" (" + str(blacklist_check) + ")")
                    bot1.send_message(user.user_id, text_to_send, parse_mode='html')

                elif user.username is None or len(user.username)<3: #пользователь с пустым логином
                    bot1.send_message(user.user_id, translate_txt('msg_user_no_username', user.lang), parse_mode='html')
                    show_main_auctions_menu(bot1, user)

                else: #пользователь не в чёрном списке
                    #уведомление о соглашении с правилами аукционов
                    btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_confirm', user.lang), callback_data='owner_confirm_rules'),
                                types.InlineKeyboardButton(text=translate_txt('btn_cancel', user.lang), callback_data='main_menu')]
                    keyboard = types.InlineKeyboardMarkup([btn_row1])
                    bot1.send_message(user.user_id, translate_txt('msg_owner_auctions_rules_'+str(bot_id), user.lang), reply_markup=keyboard, parse_mode='html')

            # Основное меню -> Мои аукционы -> Новый -> Согласен с правилами
            elif action == 'owner_confirm_rules':
                auction = Auction()  # создаём объект нового аукциона
                auction.bot_id = bot_id
                auction.collection_id = collection_id
                auction.owner_user_id = user.user_id
                auction.owner_lang = user.lang

                get_user_db_info(user, connect_par) #считываем кошелёк пользователя
                text_to_send = translate_txt('msg_input_wallet', auction.owner_lang).format(f'<code>{user.wallet}</code>')
                btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_cancel', auction.owner_lang), callback_data='menu_my_auctions')]
                keyboard = types.InlineKeyboardMarkup([btn_row1])
                bot1.send_message(auction.owner_user_id, text_to_send, reply_markup=keyboard, parse_mode='html')
                bot1.register_next_step_handler(callback.message, input_owner_wallet, auction)  # шаг для проверки введённого кошелька

            # Основное меню -> Мои аукционы -> Новый -> Проверка верификации (Владелец)
            elif action == 'auction_owner_verif':
                auction = Auction()
                auction.fill_by_temp_table(user.user_id, connect_par)

                #проверяем, что с кошелька владельца на кошелёк верификации была транзакция с комментарием
                verif_check = check_wallet_payment(auction.owner_wallet, guarantor_wallet, hashmd5("verif"+str(user.user_id)), 0.01)
                if verif_check == 1: #верификация подтверждена
                    # сохраняем информацию об успешной верификации
                    save_wallet_verification(auction.owner_user_id, auction.owner_wallet, connect_par)

                    if collection_id !=0: # бот для одной коллекции (ARL)
                        btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_cancel', user.lang), callback_data='menu_my_auctions')]
                        keyboard = types.InlineKeyboardMarkup([btn_row1])
                        text_to_send = translate_txt("msg_wallet_verif_success", user.lang) + "\n\n" \
                                       + translate_txt('msg_input_nft', user.lang)
                        bot1.send_message(auction.owner_user_id, text_to_send, reply_markup=keyboard, parse_mode='html')
                        bot1.register_next_step_handler(callback.message, input_auction_nft_info, auction)  # шаг для проверки введённого NFT

                    else: #меню выбора коллекции из списка
                        text_to_send = translate_txt("msg_wallet_verif_success", user.lang) + "\n\n" \
                                       + translate_txt('msg_input_collection', user.lang)
                        keyboard = get_collections_list(0, "auction", connect_par)
                        keyboard.add(types.InlineKeyboardButton(text=translate_txt('btn_cancel', user.lang),callback_data='menu_my_auctions'))
                        bot1.send_message(user.user_id, text_to_send, reply_markup=keyboard, parse_mode='html')

                elif verif_check in [-1, 0]: # ошибка API или верификация не подтверждена
                    btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_check_verif', user.lang),callback_data='auction_owner_verif'),
                                types.InlineKeyboardButton(text=translate_txt('btn_cancel', user.lang), callback_data='menu_my_auctions')]
                    keyboard = types.InlineKeyboardMarkup([btn_row1])
                    msg_code = "msg_transaction_check_api_err" if verif_check==-1 else "msg_wallet_verif_unsuccess"
                    bot1.send_message(user.user_id, translate_txt(msg_code, user.lang), reply_markup=keyboard, parse_mode='html')

            #-----------------------------------------------------
            # Основное меню - Новый аукцион - Выбрана коллекция
            elif action == 'menu_auction_collections':
                auction = Auction()
                auction.fill_by_temp_table(user.user_id, connect_par)
                auction.collection_id = str(callback.data.split(';')[2])

                btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_cancel', user.lang),callback_data='menu_my_auctions')]
                keyboard = types.InlineKeyboardMarkup([btn_row1])
                bot1.send_message(user.user_id, translate_txt('msg_input_nft', user.lang), reply_markup=keyboard, parse_mode='html')
                bot1.register_next_step_handler(callback.message, input_auction_nft_info, auction)  # шаг для проверки введённого NFT


            #---------------------------------------------------------------------------
            # Основное меню -> Мои аукционы -> Новый -> Выбери тип длительности аукциона
            elif action == 'duration_type':
                duration_type = callback.data.split(';')[1]
                auction = Auction()
                auction.fill_by_temp_table(user.user_id, connect_par)

                btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_cancel', user.lang), callback_data='menu_my_auctions')]
                keyboard = types.InlineKeyboardMarkup([btn_row1])

                if duration_type == '0': # введите фиксированное время (минимально = текущее время GMT+3 + 2 часа)
                    min_time = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)+timedelta(hours=3)+timedelta(hours=2)
                    min_time_string = min_time.strftime("%d.%m.%Y %H:%M:%S")

                    bot1.send_message(user.user_id, translate_txt('msg_input_fix_end_time', user.lang).format(min_time_string), reply_markup=keyboard, parse_mode='html')
                    bot1.register_next_step_handler(callback.message, input_fix_end_time, auction)  # шаг для проверки введённого фиксированного времени
                else:
                    action_durations = [0, 1,2,3,6,12,24]

                    #округляем текущий час до следующего часа и прибавляем выбранную длительность аукциона
                    auction.end_ts = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0) + timedelta(hours=1) \
                        + timedelta(hours=action_durations[int(duration_type)])

                    bot1.send_message(user.user_id, translate_txt('msg_input_comment', user.lang), reply_markup=keyboard, parse_mode='html')
                    bot1.register_next_step_handler(callback.message, input_auction_comment, auction)  # ввод комментария

            # Основное меню -> Мои аукционы -> Новый -> Подтверди информацию о новом аукционе
            elif action == 'confirm_new_auction':
                auction = Auction()
                auction.fill_by_temp_table(user.user_id, connect_par)

                #сохраняем в базу новый
                auction.id = save_new_auction_to_db(auction, connect_par)

                #отправляем подтверждение владельцу
                bot1.send_message(user.user_id, translate_txt('msg_new_auction_success', user.lang).format(str(auction.id)), parse_mode='html')
                show_main_auctions_menu(bot1, user)

                # отправляем сообщение в канал аукционов
                send_new_auction_notif_ru(auction.id, channel_ids, bot1, bot_name, connect_par)

            # Основное меню -> Мои аукционы -> Отменить активный аукцион
            elif action == "auction_cancel":
                auction_id, cancel_limit, leader_price = get_owner_active_auction(bot_id, user.user_id, connect_par)

                if leader_price is not None and cancel_limit == 0: #есть ставка и лимит отмен исчерпан
                    btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_back', user.lang), callback_data='menu_my_auctions')]
                    keyboard = types.InlineKeyboardMarkup([btn_row1])
                    bot1.send_message(user.user_id, translate_txt('msg_cancel_limit', user.lang),reply_markup=keyboard, parse_mode='html')

                elif leader_price is not None and cancel_limit>0: # есть ставка и лимит отмен не исчерпан
                    btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_confirm', user.lang), callback_data='auction_cancel_confirm;' + str(auction_id)),
                                types.InlineKeyboardButton(text=translate_txt('btn_back', user.lang), callback_data='menu_my_auctions')]
                    keyboard = types.InlineKeyboardMarkup([btn_row1])
                    text_to_send = translate_txt('msg_cancel_warning', user.lang).format(cancel_limit, auction_id)
                    bot1.send_message(user.user_id, text_to_send, reply_markup=keyboard, parse_mode='html')

                else: #не было ставок в аукционе
                    # обновляем статус аукциона и статистику пользователя
                    update_cancelled_auction(auction_id, user.user_id, connect_par, False)
                    show_owner_auctions_menu(bot_id, bot1, user, connect_par)

                    # рассылка об отмене в основном канале
                    send_cancel_auction_notif_ru(auction_id, bot1, channel_ids, connect_par)

            # Основное меню -> Мои аукционы -> Отменить активный аукцион -> Подтвердить
            elif action == 'auction_cancel_confirm':
                auction_id = callback.data.split(';')[1]

                #обновляем статус аукциона и лимит отмен
                update_cancelled_auction(auction_id, user.user_id, connect_par, True)
                show_owner_auctions_menu(bot_id, bot1, user, connect_par)

                #рассылка об отмене в основном канале
                send_cancel_auction_notif_ru(auction_id, bot1, channel_ids, connect_par)

            # Основное меню -> Участвовать
            elif action == 'menu_participate':
                auctions_count = show_active_auctions(bot_id, user, bot1, connect_par, count_limit=5)
                if auctions_count>0:
                    bot1.register_next_step_handler(callback.message, input_auction_id)  # шаг для проверки введённого номера аукциона

            # Основное меню -> Участвовать -> Назад
            elif action == 'participate_back':
                show_main_auctions_menu(bot1, user)

            # Основное меню -> Ты-участник -> Назад
            elif action == 'now_participating_back':
                show_main_auctions_menu(bot1, user)

            # Основное меню -> Информация об аукционе -> Назад
            elif action == 'auction_back':
                show_main_auctions_menu(bot1, user)

            # Основное меню -> Информация об аукционе -> Обновить
            elif action == 'auction_refresh':
                auction_id = str(callback.data.split(';')[1])
                show_selected_auction_menu(user, auction_id, bot1, connect_par)

            # Основное меню -> Информация об аукционе -> Участвовать
            elif action == 'auction_join':
                auction_id = str(callback.data.split(';')[1])
                blacklist_check = check_black_list("user_id", user.user_id, connect_par)
                if blacklist_check is not None: #пользователь в чёрном списке
                    text_to_send = translate_txt('msg_user_blacklist', user.lang).format(" (" + str(blacklist_check) + ")")
                    bot1.send_message(user.user_id, text_to_send, parse_mode='html')

                elif user.username is None or len(user.username)<3: #пользователь с пустым или коротким логином
                    bot1.send_message(user.user_id, translate_txt('msg_user_no_username', user.lang), parse_mode='html')
                    show_main_auctions_menu(bot1, user)

                else: #не в чёрном списке и заполнен логин
                    # уведомление о соглашении с правилами аукционов
                    btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_confirm', user.lang), callback_data='participate_confirm_rules;'+str(auction_id)),
                                types.InlineKeyboardButton(text=translate_txt('btn_back', user.lang), callback_data='auction_back')]
                    keyboard = types.InlineKeyboardMarkup([btn_row1])
                    bot1.send_message(user.user_id, translate_txt('msg_participant_auctions_rules_'+str(bot_id), user.lang), reply_markup=keyboard, parse_mode='html')

            # Основное меню -> Мои аукционы -> Новый -> Согласен с правилами
            elif action == 'participate_confirm_rules':
                auction_id = str(callback.data.split(';')[1])

                get_user_db_info(user, connect_par)  # считываем кошелёк пользователя
                text_to_send = translate_txt('msg_input_wallet', user.lang).format(f'<code>{user.wallet}</code>')
                btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_back', user.lang), callback_data='auction_back')]
                keyboard = types.InlineKeyboardMarkup([btn_row1])
                bot1.send_message(user.user_id, text_to_send, reply_markup=keyboard, parse_mode='html')
                bot1.register_next_step_handler(callback.message, input_participant_wallet, auction_id)  # шаг для проверки введённого кошелька

            # ---------------------------------------------------------------
            # Основное меню -> Участвовать! -> Проверить верификцию (Участник)
            elif action == 'vrf2': #верификация кошелька нового участника аукциона
                wallet = callback.data.split(';')[1]
                auction_id = callback.data.split(';')[2]

                # проверяем, что с кошелька участника на кошелёк верификации была транзакция с комментарием
                verif_check = check_wallet_payment(wallet, guarantor_wallet, hashmd5("verif" + str(user.user_id)), 0.01)
                if verif_check == 1:  # верификация подтверждена
                    # сохраняем информацию об успешной верификации
                    save_wallet_verification(user.user_id, wallet, connect_par)

                    # добавляем нового участника
                    add_new_participant(auction_id, user.user_id, wallet, connect_par)

                    # сообщаем об успешности верификации и показываем карточку аукциона
                    bot1.send_message(user.user_id, translate_txt("msg_wallet_verif_success", user.lang), parse_mode='html')
                    show_selected_auction_menu(user, auction_id, bot1, connect_par)

                elif verif_check in [-1, 0]:  # ошибка API или верификация не подтверждена
                    btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_check_verif', user.lang),
                                                           callback_data="vrf2;"+str(wallet)+";"+str(auction_id)),
                                types.InlineKeyboardButton(text=translate_txt('btn_back', user.lang), callback_data='auction_back')]
                    keyboard = types.InlineKeyboardMarkup([btn_row1])
                    msg_code = "msg_transaction_check_api_err" if verif_check == -1 else "msg_wallet_verif_unsuccess"
                    bot1.send_message(user.user_id, translate_txt(msg_code, user.lang), reply_markup=keyboard,parse_mode='html')


            # ---------------------------------------------------------------
            # Основное меню -> Верификация Monkeys -> Проверить верификцию
            elif action == 'mnkverif': #верификация кошелька Monkeys
                wallet = callback.data.split(';')[1]

                # проверяем, что с кошелька участника на кошелёк верификации была транзакция с комментарием
                verif_check = check_wallet_payment(wallet, guarantor_wallet, hashmd5("verif" + str(user.user_id)), 0.01)
                if verif_check == 1:  # верификация подтверждена
                    # сохраняем информацию об успешной верификации
                    save_wallet_verification(user.user_id, wallet, connect_par)

                    # сообщаем об успешности верификации и просим ввести название NFT
                    btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_back', user.lang), callback_data='main_menu')]
                    keyboard = types.InlineKeyboardMarkup([btn_row1])
                    text_to_send = translate_txt("msg_wallet_verif_success", user.lang) + "\n\n" + translate_txt('msg_input_nft', user.lang)
                    bot1.send_message(user.user_id, text_to_send, reply_markup=keyboard, parse_mode='html')

                    bot1.register_next_step_handler(callback.message, input_monkeys_verif_nft)  # шаг для проверки введённого NFT

                elif verif_check in [-1, 0]:  # ошибка API или верификация не подтверждена
                    btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_check_verif', user.lang),
                                                           callback_data="mnkverif;"+str(wallet)),
                                types.InlineKeyboardButton(text=translate_txt('btn_back', user.lang), callback_data='main_menu')]
                    keyboard = types.InlineKeyboardMarkup([btn_row1])
                    msg_code = "msg_transaction_check_api_err" if verif_check == -1 else "msg_wallet_verif_unsuccess"
                    bot1.send_message(user.user_id, translate_txt(msg_code, user.lang), reply_markup=keyboard,parse_mode='html')

            # ---------------------------------------------------------------
            # Основное меню -> Верификация Frogs -> Проверить верификцию
            elif action == 'frgverif':  # верификация кошелька Frogs
                wallet = callback.data.split(';')[1]

                # проверяем, что с кошелька участника на кошелёк верификации была транзакция с комментарием
                verif_check = check_wallet_payment(wallet, guarantor_wallet, hashmd5("verif" + str(user.user_id)), 0.01)
                if verif_check == 1:  # верификация подтверждена
                    # сохраняем информацию об успешной верификации
                    save_wallet_verification(user.user_id, wallet, connect_par)

                    # сообщаем об успешности верификации
                    btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_back', user.lang),
                                                           callback_data='main_menu')]
                    keyboard = types.InlineKeyboardMarkup([btn_row1])
                    text_to_send = translate_txt("msg_wallet_verif_success", user.lang)
                    bot1.send_message(user.user_id, text_to_send, reply_markup=keyboard, parse_mode='html')

                elif verif_check in [-1, 0]:  # ошибка API или верификация не подтверждена
                    btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_check_verif', user.lang),
                                                           callback_data="frgverif;" + str(wallet)),
                                types.InlineKeyboardButton(text=translate_txt('btn_back', user.lang),
                                                           callback_data='main_menu')]
                    keyboard = types.InlineKeyboardMarkup([btn_row1])
                    msg_code = "msg_transaction_check_api_err" if verif_check == -1 else "msg_wallet_verif_unsuccess"
                    bot1.send_message(user.user_id, translate_txt(msg_code, user.lang), reply_markup=keyboard,
                                      parse_mode='html')

            # Основное меню -> Информация об аукционе -> Ты-владелец
            elif action == 'auction_owner':
                btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_back', user.lang), callback_data='auction_back')]
                keyboard = types.InlineKeyboardMarkup([btn_row1])
                text_to_send = translate_txt('msg_owner', user.lang)
                bot1.send_message(user.user_id, text_to_send, reply_markup=keyboard, parse_mode='html')

            # Основное меню -> Информация об аукционе -> Ты-лидер
            elif action == 'auction_leader':
                btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_back', user.lang), callback_data='auction_back')]
                keyboard = types.InlineKeyboardMarkup([btn_row1])
                text_to_send = translate_txt('msg_leader', user.lang)
                bot1.send_message(user.user_id, text_to_send, reply_markup=keyboard, parse_mode='html')


            # Основное меню -> Информация об аукционе -> Поднять ставку
            elif action == 'auction_raise':
                auction_id = str(callback.data.split(';')[1])
                get_user_db_info(user, connect_par)

                btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_back', user.lang), callback_data='auction_back')]
                keyboard = types.InlineKeyboardMarkup([btn_row1])

                auction_state = check_auction_id_correct(bot_id, auction_id, connect_par)
                if auction_state == -1: #аукцион завершён
                    text_to_send = translate_txt('msg_auction_id_not_active', user.lang)
                    bot1.send_message(user.user_id, text_to_send, reply_markup=keyboard, parse_mode='html')

                else:
                    minimum_balance, user_balance = check_balance_for_auction(user.wallet, auction_id, connect_par)
                    if user_balance < minimum_balance:  # недостаточно средств на счёте для повышения ставки
                        text_to_send = translate_txt('msg_balance_not_enough2', user.lang).format(str(minimum_balance), str(user_balance))
                        bot1.send_message(user.user_id, text_to_send, reply_markup=keyboard, parse_mode='html')

                    else:
                        btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_confirm', user.lang),callback_data='confirm_raise;'+str(auction_id)),
                                    types.InlineKeyboardButton(text=translate_txt('btn_cancel', user.lang),callback_data='auction_back')]
                        keyboard = types.InlineKeyboardMarkup([btn_row1])

                        auction = Auction()
                        auction.fill_by_id(auction_id, connect_par) #считываем самую актуальную последнюю цену аукциона
                        price_step = auction.price_step
                        raise_value = (auction.start_price if auction.leader_price is None else auction.leader_price + auction.price_step)

                        if auction.leader_price is None: #первая ставка аукциона
                            text_to_send = translate_txt('msg_confirm_raise2', user.lang).format(str(raise_value),str(user_balance))
                        else: # поднятие уже существующей ставки
                            text_to_send = translate_txt('msg_confirm_raise1', user.lang).format(str(price_step),str(raise_value),str(user_balance))
                        bot1.send_message(user.user_id, text_to_send, reply_markup=keyboard, parse_mode='html')

            # --------------------------------------------------------------------------------
            # Основное меню -> Информация об аукционе -> Поднять ставку -> Подтвердить повышение ставки
            elif action == 'confirm_raise':
                # изменяем ставку текущего аукциона
                auction_id = str(callback.data.split(';')[1])
                raise_auction_price(auction_id, user, connect_par)
                show_selected_auction_menu(user, auction_id, bot1, connect_par)

                #делаем рассылку о повышении ставки в общий канал и всем участникам аукциона
                send_bid_raise_notif_ru(auction_id, user, bot1, bot_name, channel_ids, connect_par)

            # --------------------------------------------------------------------------------
            # Основное меню -> Ты - участник
            elif action == 'menu_now_participating':
                # показываем пользователю активные аукционы, в которых он участвует
                auctions_count = show_user_participations(bot_id, user, bot1, connect_par)
                if auctions_count > 0:
                    bot1.register_next_step_handler(callback.message, input_auction_id)  # шаг для проверки введённого номера аукциона

            # --------------------------------------------------------------------------------
            # Лидер аукциона - я оплатил ставку (перевёл на кошелёк гаранта)
            elif action == 'auction_leader_paid':
                auction_id = str(callback.data.split(';')[1])
                auction = Auction()
                auction.fill_by_id(auction_id, connect_par)

                # проверяем, что с кошелька победителя на кошелёк гаранта была транзакция с комментарием
                payment_check = check_wallet_payment(auction.leader_wallet, guarantor_wallet, "auction" + str(auction_id), auction.leader_price)
                if payment_check == 1:  # платёж подтверждён

                    # отправляем сообщение победителю аукциона (бот проверяет оплату, владелец переводит NFT)
                    text_to_send = translate_txt("msg_payment_confirmed", auction.leader_lang).format(str(auction.owner_fullname))
                    bot1.send_message(auction.leader_user_id, text_to_send, parse_mode='html')

                    # сообщение владельцу о необходимости перевести NFT победителю (с кнопкой Я перевёл)
                    btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_nft_transfered', auction.owner_lang),
                                                           callback_data='auction_nft_transfered;'+str(auction.id))]
                    keyboard = types.InlineKeyboardMarkup([btn_row1])
                    text_to_send = translate_txt("msg_transfer_after_payment", auction.owner_lang).format(str(auction.leader_price),
                        f'<code>{str(auction.leader_wallet)}</code>', transfer_nft_service_link + str(auction.collection_address)+"/"+ str(auction.nft_address))
                    bot1.send_message(auction.owner_user_id, text_to_send, reply_markup=keyboard, parse_mode='html')

                    #обновляем статус аукциона
                    set_auction_status(auction, 'NFT transfer', connect_par)

                elif payment_check in [-1, 0]:  # ошибка API или платёж не подтверждён
                    btn_row1 = [types.InlineKeyboardButton(text=translate_txt("btn_payment_done", auction.leader_lang),
                                                             callback_data = 'auction_leader_paid;' + str(auction_id))]
                    keyboard = types.InlineKeyboardMarkup([btn_row1])
                    msg_code = "msg_transaction_check_api_err" if payment_check == -1 else "msg_payment_unsuccess"
                    bot1.send_message(auction.leader_user_id, translate_txt(msg_code, auction.leader_lang), reply_markup=keyboard, parse_mode='html')

            #--------------------------------------------------------------------------------
            # Владелец аукциона - NFT передана
            elif action == 'auction_nft_transfered':
                auction_id = str(callback.data.split(';')[1])
                auction = Auction()
                auction.fill_by_id(auction_id, connect_par)

                # проверяем текущего владельца NFT и убеждаемся, что это - победитель аукциона
                blockchain_owner = get_nft_owner(auction.nft_address)

                if blockchain_owner != auction.leader_wallet: #Владелец NFT не изменился
                    nft_href = "<a href='"+explorer_api_link+auction.nft_address+"'>"+auction.nft_name+"</a>"
                    text_to_send = translate_txt("msg_nft_not_transfered", auction.owner_lang).format(nft_href,
                    f'<code>{auction.nft_address}</code>', f'<code>{auction.leader_wallet}</code>')

                    btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_nft_transfered', auction.owner_lang), callback_data='auction_nft_transfered;'+str(auction_id))]
                    keyboard = types.InlineKeyboardMarkup([btn_row1])
                    bot1.send_message(auction.owner_user_id, text_to_send, reply_markup=keyboard, parse_mode='html')

                else: #NFT успешно передана
                    # сообщение владельцу NFT - дождись платежа от бота
                    text_to_send = translate_txt("msg_wait_bot_payment", auction.owner_lang).format(f'<code>{donate_wallet}</code>',donate_wallet, donate_wallet, cryptobot_donation)
                    bot1.send_message(auction.owner_user_id, text_to_send, parse_mode='html')

                    # отправляем сообщение победителю аукциона об успешной передаче NFT
                    text_to_send = translate_txt("msg_nft_transfer_confirmed", auction.leader_lang).format(f'<code>{donate_wallet}</code>',donate_wallet, donate_wallet, cryptobot_donation)
                    bot1.send_message(auction.leader_user_id, text_to_send, parse_mode='html')

                    #ставим в очередь отправку платежа покупателю
                    send_payment_to_queue(guarantor_wallet, auction.owner_wallet, auction.leader_price,
                                          "Auction #" + str(auction.id) + " via " + str(bot_name), 'buyer', connect_par)

                    # меняем статус аукциона
                    set_auction_status(auction, 'finished', connect_par)

                    #отправляем сообщение админу
                    admin = BotUser()
                    admin.user_id = admin_users[0]
                    admin.lang = "ru"
                    bot1.send_message(admin.user_id, "Успешно закрыт аукцион с победителем №" + str(auction.id), parse_mode='html')
                    show_auction_info(auction.id, admin, bot1, connect_par)

                    # ставим в очередь  платёж в royalty-кошелёк коллекции
                    royalty_wallet, royalty_size = get_royalty_info(bot_id, auction.collection_id, connect_par)
                    royalty_amount = float(auction.leader_price) * float(royalty_size)
                    if royalty_amount > 0.01: #выплата роялти только в боте с множеством коллекций
                        send_payment_to_queue(guarantor_wallet, royalty_wallet, royalty_amount,
                                              "royalty for Auction #" + str(auction.id), 'royalty',connect_par)

                    # ставим в очередь  платёж в фонд Monkeys
                    monkey_fund_amount = min(float(auction.bot_commission) - royalty_amount, royalty_amount)
                    if monkey_fund_amount > 0.01:
                        send_payment_to_queue(guarantor_wallet, monkey_fund_wallet, monkey_fund_amount,
                                              "commission for Auction #" + str(auction.id), 'fund', connect_par)



            ####################################################################################################################
            # Основное меню - Продажа через гаранта - Отмена (Владелец или покупатель)
            # -----------------------------------------------------
            elif action in ['cancel_transfer_owner', 'cancel_transfer_buyer']:
                show_main_menu(bot1, user, bot_id)

                transfer_id = str(callback.data.split(';')[1])
                transfer = Transfer()
                transfer.fill_by_id(transfer_id, connect_par)
                transfer.status = 'cancelled'
                transfer.end_ts = datetime.now(timezone.utc)
                transfer.update_db(connect_par)

                if action == "cancel_transfer_owner": #отменил владелец
                    pass

                elif action == "cancel_transfer_buyer": #отменил покупатель
                    # отправляем владельцу информацию "Покупатель отменил сделку"
                    bot1.send_message(transfer.owner_user_id, text=translate_txt('msg_buyer_cancel_transfer', transfer.owner_lang).format(
                                          transfer.buyer_fullname, transfer.id), parse_mode='html')


            #-----------------------------------------------------
            # Основное меню - Продажа через гаранта - Новая сделка
            elif action == 'new_transfer':
                blacklist_check = check_black_list("user_id", user.user_id, connect_par)
                if blacklist_check is not None: #пользователь в чёрном списке
                    text_to_send = translate_txt('msg_user_blacklist', user.lang).format(" (" + str(blacklist_check) + ")")
                    bot1.send_message(user.user_id, text_to_send, parse_mode='html')

                elif user.username is None or len(user.username)<3: #пользователь с пустым логином
                    bot1.send_message(user.user_id, translate_txt('msg_user_no_username', user.lang), parse_mode='html')
                    show_main_menu(bot1, user, bot_id)

                else: #пользователь не в чёрном списке
                    transfer = Transfer()
                    transfer.bot_id = bot_id
                    transfer.owner_user_id = user.user_id
                    transfer.collection_id = collection_id
                    transfer_id = transfer.add_to_db(connect_par) #добавляем новую запись в базу
                    transfer.fill_by_id(transfer_id, connect_par)

                    get_user_db_info(user, connect_par)  # считываем кошелёк пользователя
                    text_to_send = translate_txt('msg_input_wallet', user.lang).format(f'<code>{user.wallet}</code>')
                    btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_cancel', user.lang), callback_data='cancel_transfer_owner;'+str(transfer.id))]
                    keyboard = types.InlineKeyboardMarkup([btn_row1])
                    bot1.send_message(user.user_id, text_to_send, reply_markup=keyboard, parse_mode='html')
                    bot1.register_next_step_handler(callback.message, input_transfer_owner_wallet, transfer)  # шаг для проверки введённого кошелька


            #-----------------------------------------------------
            # Основное меню - Продажа через гаранта - Выбрана коллекция
            elif action == 'menu_transfer_collections':
                transfer = Transfer()
                transfer.fill_by_id(str(callback.data.split(';')[1]), connect_par)
                transfer.collection_id = str(callback.data.split(';')[2])
                transfer.update_db(connect_par)

                btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_cancel', user.lang),
                                                       callback_data='cancel_transfer_owner;' + str(transfer.id))]
                keyboard = types.InlineKeyboardMarkup([btn_row1])
                bot1.send_message(user.user_id, translate_txt('msg_input_nft', user.lang), reply_markup=keyboard, parse_mode='html')
                bot1.register_next_step_handler(callback.message, input_transfer_nft_info, transfer)  # шаг для проверки введённого NFT

            #-----------------------------------------------------
            # Основное меню - Продажа через гаранта - Твои сделки - Карточка сделки
            elif action == 'show_transfer':
                transfer_id = str(callback.data.split(';')[1])

                #показываем карточку сделки
                show_transfer_info(transfer_id, user,bot1, connect_par)

            # ---------------------------------------------------------------------------------
            # Основное меню -> Продажа через гаранта -> Новая сделка -> Проверка верификации (Владелец или покупатель)
            elif action in ['transfer_owner_wallet_verif', 'transfer_buyer_wallet_verif']:
                transfer_id = str(callback.data.split(';')[1])
                transfer = Transfer()
                transfer.fill_by_id(transfer_id, connect_par) #заполняем все данные сделки из базы

                cancel_callback = ('cancel_transfer_owner;' if action == 'transfer_owner_wallet_verif' else 'cancel_transfer_buyer;')+str(transfer.id)

                #проверяем, что с кошелька пользователя на кошелёк верификации была транзакция с комментарием
                wallet = transfer.owner_wallet if action == 'transfer_owner_wallet_verif' else transfer.buyer_wallet
                verif_check = check_wallet_payment(wallet, guarantor_wallet, hashmd5("verif"+str(user.user_id)), 0.01)

                if verif_check in [-1, 0]: # ошибка API или верификация не подтверждена
                    btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_check_verif', user.lang), callback_data=action+";"+str(transfer.id)),
                                types.InlineKeyboardButton(text=translate_txt('btn_cancel', user.lang), callback_data=cancel_callback)]
                    keyboard = types.InlineKeyboardMarkup([btn_row1])
                    msg_code = "msg_transaction_check_api_err" if verif_check == -1 else "msg_wallet_verif_unsuccess"
                    bot1.send_message(user.user_id, translate_txt(msg_code, user.lang), reply_markup=keyboard, parse_mode='html')

                elif verif_check == 1: #верификация подтверждена
                    # сохраняем информацию об успешной верификации
                    save_wallet_verification(user.user_id, wallet, connect_par)

                    # Успешная верификация кошелька владельца
                    if action == "transfer_owner_wallet_verif":
                        btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_cancel', user.lang), callback_data=cancel_callback)]
                        keyboard = types.InlineKeyboardMarkup([btn_row1])

                        if collection_id !=0: #бот с одной коллекцией (ARL)
                            text_to_send = translate_txt("msg_wallet_verif_success", user.lang) + "\n\n" + translate_txt(
                                'msg_input_nft', user.lang)
                            bot1.send_message(user.user_id, text_to_send, reply_markup=keyboard, parse_mode='html')
                            bot1.register_next_step_handler(callback.message, input_transfer_nft_info, transfer)  # шаг для проверки введённого NFT

                        else: # меню с выбором коллекций
                            text_to_send = translate_txt("msg_wallet_verif_success", user.lang) + "\n\n" \
                                           + translate_txt('msg_input_collection', user.lang)
                            keyboard = get_collections_list(transfer.id, "transfer", connect_par)
                            keyboard.add(types.InlineKeyboardButton(text=translate_txt('btn_cancel', user.lang),
                                                                    callback_data='cancel_transfer_owner;'+str(transfer.id)))
                            bot1.send_message(user.user_id, text_to_send,reply_markup=keyboard, parse_mode='html')


                    # Успешная верификация кошелька покупателя
                    elif action == "transfer_buyer_wallet_verif":
                        transfer.buyer_wallet = wallet  # сохраняем введённый buyer_wallet
                        transfer.update_db(connect_par)

                        # посылаем сообщение с реквизитами
                        amount_nano = int((transfer.amount+transfer.bot_commission) * (10**9))
                        fast_pay_link = payment_link.format(guarantor_wallet, str(amount_nano), "sale"+str(transfer.id))
                        text_to_send = translate_txt("msg_wallet_verif_success", user.lang) + "\n\n" \
                                       + translate_txt("msg_transfer_amount", user.lang).format(fast_pay_link,
                            str(transfer.amount + transfer.bot_commission), str(transfer.amount), str(transfer.bot_commission),
                            f'<code>{guarantor_wallet}</code>',f'<code>{"sale"+str(transfer.id)}</code>')
                        bot1.send_message(user.user_id, text_to_send, parse_mode='html')

                        btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_payment_done', user.lang),
                                                               callback_data='transfer_buyer_paid;' + str(transfer.id))]
                        keyboard = types.InlineKeyboardMarkup([btn_row1])
                        bot1.send_message(user.user_id, translate_txt("msg_press_button_below", user.lang), reply_markup=keyboard, parse_mode='html')

            # -----------------------------------------------------
            # Основное меню - Продажа через гаранта - Владелец подтвердил новый трансфер
            elif action == 'confirm_transfer_owner':
                transfer_id = str(callback.data.split(';')[1])
                transfer = Transfer()
                transfer.fill_by_id(transfer_id, connect_par) #заполняем все данные сделки из базы

                # отправляем покупателю предложение о сделке для подтверждения
                show_new_transfer_to_confirm(transfer_id, "buyer", bot1, connect_par)

                #отправляем владельцу информацию "Подожди ответа покупателя"
                bot1.send_message(transfer.owner_user_id, text=translate_txt('msg_wait_buyer_answer', transfer.owner_lang).format(
                    transfer.id, transfer.buyer_fullname), parse_mode='html')

                #обновляем статус у трансфера
                transfer.status = 'invite_buyer'
                transfer.update_db(connect_par)


            # -----------------------------------------------------
            # Основное меню - Продажа через гаранта - Покупатель соглашается принять участие в трансфере
            elif action == 'confirm_transfer_buyer':
                transfer_id = str(callback.data.split(';')[1])
                transfer = Transfer()
                transfer.fill_by_id(transfer_id, connect_par) #заполняем все данные сделки из базы
                transfer.status = "active"
                transfer.update_db(connect_par)

                get_user_db_info(user, connect_par)  # считываем кошелёк пользователя
                text_to_send = translate_txt('msg_input_wallet', user.lang).format(f'<code>{user.wallet}</code>')
                btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_cancel', user.lang),
                                                       callback_data='cancel_transfer_buyer;'+str(transfer_id))]
                keyboard = types.InlineKeyboardMarkup([btn_row1])
                bot1.send_message(user.user_id, text_to_send, reply_markup=keyboard, parse_mode='html')
                bot1.register_next_step_handler(callback.message, input_transfer_buyer_wallet, transfer)  # шаг для проверки введённого кошелька

                #отправляем владельцу информацию "Покупатель согласился на сделку"
                bot1.send_message(transfer.owner_user_id, text=translate_txt('msg_buyer_confirm_transfer', transfer.owner_lang).format(
                    transfer.buyer_fullname, transfer.id), parse_mode='html')

                # отправляем сообщение админу
                admin = BotUser()
                admin.user_id = admin_users[0]
                admin.lang = "ru"
                bot1.send_message(admin.user_id, "Новая подтверждённая продажа №" + str(transfer.id), parse_mode='html')
                show_transfer_info(transfer.id, admin, bot1, connect_par)

            # -----------------------------------------------------
            # Основное меню - Продажа через гаранта - Покупатель - Я оплатил
            elif action == 'transfer_buyer_paid':
                transfer_id = str(callback.data.split(';')[1])
                transfer = Transfer()
                transfer.fill_by_id(transfer_id, connect_par)

                # проверяем, что с кошелька владельца на кошелёк гаранта была транзакция с комментарием
                payment_check = check_wallet_payment(transfer.buyer_wallet, guarantor_wallet, "sale" + str(transfer.id), transfer.amount+transfer.bot_commission)
                if payment_check in [-1, 0]:  # ошибка API или транзакция не найдена
                    btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_payment_done', transfer.buyer_lang), callback_data='transfer_buyer_paid;' + str(transfer.id))]
                    keyboard = types.InlineKeyboardMarkup([btn_row1])
                    msg_code = "msg_transaction_check_api_err" if payment_check == -1 else "msg_payment_unsuccess"
                    bot1.send_message(user.user_id, translate_txt(msg_code, transfer.buyer_lang), reply_markup=keyboard, parse_mode='html')

                elif payment_check == 1:  # транзакция найдена
                    # отправляем сообщение покупателю
                    text_to_send = translate_txt("msg_payment_confirmed", transfer.buyer_lang).format(transfer.owner_fullname)
                    bot1.send_message(transfer.buyer_user_id, text_to_send, parse_mode='html')

                    # сообщение владельцу о необходимости перевести NFT победителю
                    btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_nft_transfered', transfer.owner_lang),
                                                           callback_data='sale_nft_transfered;'+str(transfer.id))]
                    keyboard = types.InlineKeyboardMarkup([btn_row1])
                    text_to_send = translate_txt("msg_transfer_after_payment", transfer.owner_lang).format(
                        str(transfer.amount), f'<code>{str(transfer.buyer_wallet)}</code>',transfer_nft_service_link + str(transfer.collection_address)+"/" + str(transfer.nft_address))
                    bot1.send_message(transfer.owner_user_id, text_to_send, reply_markup=keyboard, parse_mode='html')

                    transfer.status = "NFT transfer"
                    transfer.update_db(connect_par)

            # -----------------------------------------------------
            # Основное меню - Продажа через гаранта - Владелец - Я перевёл NFT
            elif action == 'sale_nft_transfered':
                transfer_id = str(callback.data.split(';')[1])
                transfer = Transfer()
                transfer.fill_by_id(transfer_id, connect_par)

                # проверяем текущего владельца NFT и убеждаемся, что это - победитель аукциона
                blockchain_owner = get_nft_owner(transfer.nft_address)

                if blockchain_owner != transfer.buyer_wallet: # Владелец NFT не изменился
                    nft_href = "<a href='"+explorer_api_link+transfer.nft_address+"'>"+transfer.nft_name+"</a>"
                    text_to_send = translate_txt("msg_nft_not_transfered", transfer.owner_lang).format(nft_href,
                        f'<code>{transfer.nft_address}</code>', f'<code>{transfer.buyer_wallet}</code>')

                    btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_nft_transfered', transfer.owner_lang), callback_data='sale_nft_transfered;'+str(transfer.id))]
                    keyboard = types.InlineKeyboardMarkup([btn_row1])
                    bot1.send_message(user.user_id, text_to_send, reply_markup=keyboard, parse_mode='html')

                else: # NFT успешно передана
                    # сообщение владельцу NFT - дождись платежа от бота
                    text_to_send = translate_txt("msg_wait_bot_payment", transfer.owner_lang).format(f'<code>{donate_wallet}</code>',donate_wallet, donate_wallet, cryptobot_donation)
                    bot1.send_message(transfer.owner_user_id, text_to_send, parse_mode='html')

                    # отправляем сообщение покупателю об успешной передаче NFT
                    text_to_send = translate_txt("msg_nft_transfer_confirmed", transfer.buyer_lang).format(f'<code>{donate_wallet}</code>',donate_wallet, donate_wallet, cryptobot_donation)
                    bot1.send_message(transfer.buyer_user_id, text_to_send, parse_mode='html')

                    #ставим в очередь платёж на кошелёк владельца
                    send_payment_to_queue(guarantor_wallet, transfer.owner_wallet, transfer.amount,
                                          "Sale #"+str(transfer.id)+" via "+bot_name, 'buyer', connect_par)
                    transfer.status = "finished"
                    transfer.end_ts = datetime.now(timezone.utc)
                    transfer.update_db(connect_par)

                    #отправляем сообщение админу
                    admin = BotUser()
                    admin.user_id = admin_users[0]
                    admin.lang = "ru"
                    bot1.send_message(admin.user_id, "Успешно закрыта продажа №" + str(transfer.id), parse_mode='html')
                    show_transfer_info(transfer.id, admin, bot1, connect_par)

                    # ставим в очередь платёж на royalty-кошелёк коллекции
                    royalty_wallet, royalty_size = get_royalty_info(bot_id, transfer.collection_id, connect_par)
                    royalty_amount = float(transfer.amount) * float(royalty_size)
                    if royalty_amount > 0.01:
                        send_payment_to_queue(guarantor_wallet, royalty_wallet, royalty_amount,
                                              "royalty for Sale #" + str(transfer.id), 'royalty', connect_par)


                    # ставим в очередь платёж в фонд Monkeys
                    monkey_fund_amount = min(float(transfer.bot_commission) - royalty_amount, royalty_amount)
                    if monkey_fund_amount> 0.01:
                        send_payment_to_queue(guarantor_wallet, monkey_fund_wallet, monkey_fund_amount,
                                              "commission for Sale #" + str(transfer.id), 'fund', connect_par)

            #-----------------------------------------------------------------------------------------------------------------

            # -----------------------------------------------------
            # Основное меню - Верификация Monkeys
            elif action == "monkeys_verif":

                btn_back = [types.InlineKeyboardButton(text=translate_txt('btn_back', user.lang), callback_data='main_menu')]
                keyboard = types.InlineKeyboardMarkup([btn_back])

                is_monkeys = check_user_is_monkeys(user, connect_par)
                if is_monkeys == True:
                    text_to_send = translate_txt("msg_monkeys_verif_info", user.lang) + "\n\n" + translate_txt("msg_user_is_monkeys", user.lang)
                    bot1.send_photo(user.user_id, photo=open(start_logo, 'rb'), caption=text_to_send, reply_markup=keyboard, parse_mode='html')
                else:
                    get_user_db_info(user, connect_par)  # считываем кошелёк пользователя
                    text_to_send =  translate_txt("msg_monkeys_verif_info", user.lang) + "\n\n" + translate_txt('msg_input_wallet', user.lang).format(f'<code>{user.wallet}</code>')
                    bot1.send_photo(user.user_id, photo=open(start_logo, 'rb'), caption=text_to_send, reply_markup=keyboard, parse_mode='html')
                    bot1.register_next_step_handler(callback.message, input_monkeys_verif_wallet)  # шаг для проверки введённого кошелька

            # Основное меню - Верификация Frogs
            elif action == "frogs_verif":

                btn_back = [types.InlineKeyboardButton(text=translate_txt('btn_back', user.lang), callback_data='main_menu')]
                keyboard = types.InlineKeyboardMarkup([btn_back])

                get_user_db_info(user, connect_par)  # считываем кошелёк пользователя
                text_to_send =  translate_txt('msg_input_wallet', user.lang).format(f'<code>{user.wallet}</code>')
                bot1.send_photo(user.user_id, photo=open("images/frogs_verif_logo.jpg", 'rb'), caption=text_to_send, reply_markup=keyboard, parse_mode='html')
                bot1.register_next_step_handler(callback.message, input_frogs_verif_wallet)  # шаг для проверки введённого кошелька

            # Основное меню - Проверка NFT
            elif action == "menu_check_nft":

                btn_back = [types.InlineKeyboardButton(text=translate_txt('btn_back', user.lang), callback_data='main_menu')]
                keyboard = types.InlineKeyboardMarkup([btn_back])

                bot1.send_message(user.user_id, text=translate_txt('msg_input_nft_check', user.lang), reply_markup=keyboard, parse_mode='html')
                bot1.register_next_step_handler(callback.message, input_nft_to_check)  # шаг для проверки введённого НФТ


        #Основное меню - Проверка NFT -> Введи адрес NFT
        # ----------------------------------------------------------
        def input_nft_to_check(msg):
            user = get_user_info(msg)
            btn_back = [types.InlineKeyboardButton(text=translate_txt('btn_back', user.lang), callback_data='main_menu')]
            keyboard = types.InlineKeyboardMarkup([btn_back])

            nft_id = find_nft_by_address(msg.text, connect_par)
            if nft_id == -1: #некорректный формат
                bot1.send_message(user.user_id, text=translate_txt('msg_nft_format_incorrect', user.lang), reply_markup=keyboard, parse_mode='html')

            elif nft_id == 0: #не найдено
                bot1.send_message(user.user_id, text=translate_txt('msg_nft_address_not_found', user.lang), reply_markup=keyboard, parse_mode='html')

            else: #всё ОК
                info, image = show_nft_info(nft_id, connect_par, user.lang)
                bot1.send_photo(user.user_id, photo=open(image, 'rb'), caption=info, reply_markup=keyboard, parse_mode='html')

            #даём возможность ввести адрес ещё раз
            bot1.register_next_step_handler(msg, input_nft_to_check)



        #Основное меню - Верификация Frogs -> Введи кошелёк
        # ----------------------------------------------------------
        def input_frogs_verif_wallet(msg):
            user = get_user_info(msg)
            btn_cancel = [types.InlineKeyboardButton(text=translate_txt('btn_back', user.lang), callback_data='main_menu')]

            wallet, check_result = check_wallet(msg.text, user.user_id, connect_par)
            if check_result in [1, 2]:  #введён некорректный TON кошелёк или кошелёк в чёрном списке
                keyboard = types.InlineKeyboardMarkup([btn_cancel])
                text_code = 'msg_wallet_incorrect' if check_result == 1 else 'msg_wallet_blacklist'
                bot1.send_message(user.user_id, translate_txt(text_code, user.lang), reply_markup=keyboard, parse_mode='html')
                bot1.register_next_step_handler(msg, input_frogs_verif_wallet) #повторный запуск

            elif check_result == 3: #кошелёк неверифицирован
                update_users_wallets(user.user_id, wallet, "frogs_verification", connect_par)  # сохраняем кошелёк в БД

                #отправляем сообщение с реквизитами для верификации
                amount_nano = int((0.01) * (10 ** 9))
                fast_pay_link = payment_link.format(guarantor_wallet, str(amount_nano), hashmd5("verif"+str(user.user_id)))
                text_to_send = translate_txt("msg_wallet_not_verif", user.lang).format(fast_pay_link,
                    f'<code>{guarantor_wallet}</code>', f'<code>{hashmd5("verif"+str(user.user_id))}</code>')
                bot1.send_message(user.user_id, text_to_send, parse_mode='html')

                btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_check_verif', user.lang), callback_data='frgverif;'+str(wallet)),
                            types.InlineKeyboardButton(text=translate_txt('btn_back', user.lang), callback_data='main_menu')]
                keyboard = types.InlineKeyboardMarkup([btn_row1])
                bot1.send_message(user.user_id, translate_txt('msg_press_button_below', user.lang), reply_markup=keyboard, parse_mode='html')

            elif check_result == 0: #кошелёк верифицирован
                update_users_wallets(user.user_id, wallet, "frogs_verification", connect_par)  # сохраняем кошелёк в БД

                keyboard = types.InlineKeyboardMarkup([btn_cancel])
                bot1.send_message(user.user_id, translate_txt('msg_wallet_already_verif', user.lang), reply_markup=keyboard, parse_mode='html')


        #Основное меню - Верификация Monkeys -> Введи кошелёк
        # ----------------------------------------------------------
        def input_monkeys_verif_wallet(msg):
            user = get_user_info(msg)
            btn_cancel = [types.InlineKeyboardButton(text=translate_txt('btn_back', user.lang), callback_data='main_menu')]

            wallet, check_result = check_wallet(msg.text, user.user_id, connect_par)
            if check_result in [1, 2]:  #введён некорректный TON кошелёк или кошелёк в чёрном списке
                keyboard = types.InlineKeyboardMarkup([btn_cancel])
                text_code = 'msg_wallet_incorrect' if check_result == 1 else 'msg_wallet_blacklist'
                bot1.send_message(user.user_id, translate_txt(text_code, user.lang), reply_markup=keyboard, parse_mode='html')
                bot1.register_next_step_handler(msg, input_monkeys_verif_wallet) #повторный запуск

            elif check_result == 3: #кошелёк неверифицирован
                update_users_wallets(user.user_id, wallet, "monkeys_verification", connect_par)  # сохраняем кошелёк в БД

                #отправляем сообщение с реквизитами для верификации
                amount_nano = int((0.01) * (10 ** 9))
                fast_pay_link = payment_link.format(guarantor_wallet, str(amount_nano), hashmd5("verif"+str(user.user_id)))
                text_to_send = translate_txt("msg_wallet_not_verif", user.lang).format(fast_pay_link,
                    f'<code>{guarantor_wallet}</code>', f'<code>{hashmd5("verif"+str(user.user_id))}</code>')
                bot1.send_message(user.user_id, text_to_send, parse_mode='html')

                btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_check_verif', user.lang), callback_data='mnkverif;'+str(wallet)),
                            types.InlineKeyboardButton(text=translate_txt('btn_back', user.lang), callback_data='main_menu')]
                keyboard = types.InlineKeyboardMarkup([btn_row1])
                bot1.send_message(user.user_id, translate_txt('msg_press_button_below', user.lang), reply_markup=keyboard, parse_mode='html')

            elif check_result == 0: #кошелёк верифицирован
                update_users_wallets(user.user_id, wallet, "monkeys_verification", connect_par)  # сохраняем кошелёк в БД

                keyboard = types.InlineKeyboardMarkup([btn_cancel])
                bot1.send_message(user.user_id, translate_txt('msg_input_nft', user.lang), reply_markup=keyboard)
                bot1.register_next_step_handler(msg, input_monkeys_verif_nft) # шаг для проверки введённого NFT


        # Основное меню - Верификация Monkeys -> Введи NFT
        # ----------------------------------------------------------
        def input_monkeys_verif_nft(msg):
            user = get_user_info(msg)
            get_user_db_info(user, connect_par)
            btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_back', user.lang), callback_data='main_menu')]
            keyboard = types.InlineKeyboardMarkup([btn_row1])

            #проверяем введённое название или адрес NFT
            error_code, error_text, nft_id = check_monkeys_nft(msg.text, user.wallet, user.lang, connect_par)
            #проверяем введённое название или адрес NFT
            if error_code != 0:
                if error_code == 1: #нет такого NFT в коллекции
                    bot1.send_message(user.user_id, error_text, reply_markup=keyboard, parse_mode='html')
                else: # выдаём ошибку, но показываем информацию об NFT
                    info, image = show_nft_info(nft_id, connect_par, user.lang)
                    info = info + "\n__________________________________\n\n"+error_text
                    bot1.send_photo(user.user_id, photo=open(image, 'rb'), caption=info, reply_markup=keyboard, parse_mode='html')

                bot1.register_next_step_handler(msg, input_monkeys_verif_nft)  # повторный запуск

            else:
                # отправляем пользователю картинку и информацию по выбранному NFT
                info, image = show_nft_info(nft_id, connect_par, user.lang)
                bot1.send_photo(user.user_id, photo=open(image, 'rb'), caption=info, parse_mode='html')

                #обновляем данные по верификации Monkeys и сообщаем пользователю, что всё успешно
                update_monkeys_new_verification(user, nft_id, connect_par)
                bot1.send_message(user.user_id, translate_txt("msg_user_is_monkeys_new", user.lang), reply_markup=keyboard, parse_mode='html')


        #Основное меню - Продажа через гаранта - Новая сделка -> Введи кошелёк (Владелец)
        # ----------------------------------------------------------
        def input_transfer_owner_wallet(msg, transfer):
            user = get_user_info(msg)
            btn_cancel = [types.InlineKeyboardButton(text=translate_txt('btn_cancel', user.lang), callback_data='cancel_transfer_owner;'+str(transfer.id))]

            wallet, check_result = check_wallet(msg.text, user.user_id, connect_par)
            if check_result in [1, 2]:  #введён некорректный TON кошелёк или кошелёк в чёрном списке
                keyboard = types.InlineKeyboardMarkup([btn_cancel])
                text_code = 'msg_wallet_incorrect' if check_result == 1 else 'msg_wallet_blacklist'
                bot1.send_message(user.user_id, translate_txt(text_code, user.lang), reply_markup=keyboard, parse_mode='html')
                bot1.register_next_step_handler(msg, input_transfer_owner_wallet, transfer) #повторный запуск

            elif check_result == 3: #кошелёк неверифицирован
                transfer.owner_wallet = wallet #сохраняем введённый owner_wallet
                transfer.update_db(connect_par)
                update_users_wallets(user.user_id, wallet, "transfer_owner", connect_par)  # сохраняем кошелёк в БД

                #отправляем сообщение с реквизитами для верификации
                amount_nano = int((0.01) * (10 ** 9))
                fast_pay_link = payment_link.format(guarantor_wallet, str(amount_nano), hashmd5("verif"+str(user.user_id)))
                text_to_send = translate_txt("msg_wallet_not_verif", user.lang).format(fast_pay_link,
                    f'<code>{guarantor_wallet}</code>', f'<code>{hashmd5("verif"+str(user.user_id))}</code>')
                bot1.send_message(user.user_id, text_to_send, parse_mode='html')

                btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_check_verif', user.lang), callback_data='transfer_owner_wallet_verif;'+str(transfer.id)),
                            types.InlineKeyboardButton(text=translate_txt('btn_cancel', user.lang), callback_data='cancel_transfer_owner;'+str(transfer.id))]
                keyboard = types.InlineKeyboardMarkup([btn_row1])
                bot1.send_message(user.user_id, translate_txt('msg_press_button_below', user.lang), reply_markup=keyboard, parse_mode='html')

            elif check_result == 0: #кошелёк верифицирован
                transfer.owner_wallet = wallet #сохраняем введённый owner_wallet
                transfer.update_db(connect_par)
                update_users_wallets(user.user_id, wallet, "transfer_owner", connect_par)  # сохраняем кошелёк в БД

                keyboard = types.InlineKeyboardMarkup([btn_cancel])

                if collection_id !=0: # бот с одной коллекцией (ARL)
                    bot1.send_message(user.user_id, translate_txt('msg_input_nft', user.lang), reply_markup=keyboard)
                    bot1.register_next_step_handler(msg, input_transfer_nft_info, transfer) # шаг для проверки введённого NFT

                else: #меню с кнопками для выбора коллекции
                    keyboard = get_collections_list(transfer.id, "transfer", connect_par)
                    keyboard.add(types.InlineKeyboardButton(text=translate_txt('btn_cancel', user.lang), callback_data='cancel_transfer_owner;' + str(transfer.id)))
                    bot1.send_message(user.user_id, translate_txt("msg_input_collection", user.lang),reply_markup=keyboard)


        # Основное меню - Красная Книга -> Введи NFT
        # ----------------------------------------------------------
        def input_iucn_nft_info(msg):
            user = get_user_info(msg)
            btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_back', user.lang), callback_data='main_menu')]
            keyboard = types.InlineKeyboardMarkup([btn_row1])

            #проверяем введённое название или адрес NFT
            error_code, error_text, nft_id = check_nft(collection_id, msg.text, "none_wallet", user.lang, connect_par)
            if error_code == 1:  # нет такого NFT в коллекции
                bot1.send_message(user.user_id, error_text, reply_markup=keyboard, parse_mode='html')

            else: # показываем информацию об NFT
                info, image = show_nft_info(nft_id, connect_par, user.lang)
                bot1.send_photo(user.user_id, photo=open(image, 'rb'), caption=info, reply_markup=keyboard, parse_mode='html')

            bot1.register_next_step_handler(msg, input_iucn_nft_info)  # повторный запуск


        #Основное меню - Продажа через гаранта - Новая сделка -> Введи кошелёк (Покупатель)
        # ----------------------------------------------------------
        def input_transfer_buyer_wallet(msg, transfer):
            user = get_user_info(msg)

            wallet, check_result = check_wallet(msg.text, user.user_id, connect_par)
            if check_result in [1, 2]:  #введён некорректный TON кошелёк или кошелёк в чёрном списке
                text_code = 'msg_wallet_incorrect' if check_result == 1 else 'msg_wallet_blacklist'
                btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_cancel', user.lang), callback_data='cancel_transfer_buyer;'+str(transfer.id))]
                keyboard = types.InlineKeyboardMarkup([btn_row1])
                bot1.send_message(user.user_id, translate_txt(text_code, user.lang), reply_markup=keyboard, parse_mode='html')
                bot1.register_next_step_handler(msg, input_transfer_buyer_wallet, transfer) #повторный запуск

            elif check_result == 3: #кошелёк неверифицирован
                transfer.buyer_wallet = wallet #сохраняем введённый owner_wallet
                transfer.update_db(connect_par)
                update_users_wallets(user.user_id, wallet, "transfer_buyer", connect_par)  # сохраняем кошелёк в БД

                # отправляем сообщение с реквизитами для верификации
                amount_nano = int((0.01) * (10 ** 9))
                fast_pay_link = payment_link.format(guarantor_wallet, str(amount_nano), hashmd5("verif"+str(user.user_id)))
                text_to_send = translate_txt("msg_wallet_not_verif", user.lang).format(fast_pay_link,
                    f'<code>{guarantor_wallet}</code>', f'<code>{hashmd5("verif"+str(user.user_id))}</code>')
                bot1.send_message(user.user_id, text_to_send, parse_mode='html')

                btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_check_verif', user.lang), callback_data='transfer_buyer_wallet_verif;'+str(transfer.id)),
                            types.InlineKeyboardButton(text=translate_txt('btn_cancel', user.lang), callback_data='cancel_transfer_buyer;'+str(transfer.id))]
                keyboard = types.InlineKeyboardMarkup([btn_row1])
                bot1.send_message(user.user_id, translate_txt('msg_press_button_below', user.lang), reply_markup=keyboard, parse_mode='html')


            elif check_result == 0: #кошелёк верифицирован
                transfer.buyer_wallet = wallet #сохраняем введённый buyer_wallet и обновляем статус
                transfer.status = "payment"
                transfer.update_db(connect_par)
                update_users_wallets(user.user_id, wallet, "transfer_buyer", connect_par)  # сохраняем кошелёк в БД

                #отправляем информацию для платежа
                amount_nano = int((transfer.amount + transfer.bot_commission) * (10 ** 9))
                fast_pay_link = payment_link.format(guarantor_wallet, str(amount_nano), "sale"+str(transfer.id))
                text_to_send = translate_txt("msg_transfer_amount", user.lang).format(fast_pay_link,
                    str(transfer.amount+transfer.bot_commission), str(transfer.amount), str(transfer.bot_commission),
                    f'<code>{guarantor_wallet}</code>', f'<code>{"sale"+str(transfer.id)}</code>')
                bot1.send_message(user.user_id, text_to_send, parse_mode='html')

                btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_payment_done', user.lang), callback_data='transfer_buyer_paid;'+str(transfer.id))]
                keyboard = types.InlineKeyboardMarkup([btn_row1])
                bot1.send_message(user.user_id, translate_txt("msg_press_button_below", user.lang), reply_markup=keyboard, parse_mode='html')



        # Основное меню - Продажа через гаранта - Новая сделка -> Введи NFT
        # ----------------------------------------------------------
        def input_transfer_nft_info(msg, transfer):
            user = get_user_info(msg)
            btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_cancel', user.lang), callback_data='cancel_transfer_owner;'+str(transfer.id))]
            keyboard = types.InlineKeyboardMarkup([btn_row1])

            #проверяем введённое название или адрес NFT
            error_code, error_text, nft_id = check_nft(transfer.collection_id,  msg.text, transfer.owner_wallet, user.lang, connect_par)
            if error_code != 0:
                if error_code == 1: #нет такого NFT в коллекции
                    bot1.send_message(user.user_id, error_text, reply_markup=keyboard, parse_mode='html')
                else: # выдаём ошибку, но показываем информацию об NFT
                    info, image = show_nft_info(nft_id, connect_par, user.lang)
                    info = info + "\n__________________________________\n\n"+error_text
                    bot1.send_photo(user.user_id, photo=open(image, 'rb'), caption=info, reply_markup=keyboard, parse_mode='html')

                bot1.register_next_step_handler(msg, input_transfer_nft_info, transfer)  # повторный запуск
            else:
                transfer.nft_id = nft_id  # сохраняем введённый nft_id
                transfer.update_db(connect_par)

                # отправляем пользователю картинку и информацию по выбранному NFT
                info, image = show_nft_info(nft_id, connect_par, user.lang)
                bot1.send_photo(user.user_id, photo=open(image, 'rb'), caption=info, parse_mode='html')

                bot1.send_message(user.user_id, translate_txt('msg_input_deal_amount', user.lang), reply_markup=keyboard)
                bot1.register_next_step_handler(msg, input_sale_amount, transfer)  # шаг для проверки суммы сделки


        # Основное меню -> Продажа через гаранта -> Новый-> Введи сумму сделки
        # ----------------------------------------------------------
        def input_sale_amount(msg, transfer):
            user = get_user_info(msg)
            btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_cancel', user.lang), callback_data='cancel_transfer_owner;'+str(transfer.id))]
            keyboard = types.InlineKeyboardMarkup([btn_row1])

            try:
                amount = float(msg.text.strip())

                # Сумма не попадает в диапазон
                if amount < 1 or amount > transfer_deal_amount_limit:
                    bot1.send_message(user.user_id, translate_txt('msg_deal_amount_out_of_limits', user.lang).format(
                        str(transfer_deal_amount_limit)),
                                      reply_markup=keyboard, parse_mode='html')
                    bot1.register_next_step_handler(msg, input_sale_amount, transfer)  # повторный запуск
                else:
                    transfer.amount = amount #сохраняем сумму сделки
                    #transfer.bot_commission = transfer_commission #сохраняем комиссию бота
                    transfer.update_db(connect_par)

                    bot1.send_message(user.user_id, translate_txt('msg_input_buyer_login', user.lang), reply_markup=keyboard)
                    bot1.register_next_step_handler(msg, input_transfer_buyer_login, transfer)  # шаг для проверки логина второго участника

            except ValueError as err:
                print(err)
                # введены ошибочные данные
                bot1.send_message(user.user_id, translate_txt('msg_deal_amount_incorrect', user.lang), reply_markup=keyboard,parse_mode='html')
                bot1.register_next_step_handler(msg, input_sale_amount, transfer)  # повторный запуск

        # Основное меню -> Передача через гаранта -> Новый-> Введи логин покупателя
        # ----------------------------------------------------------
        def input_transfer_buyer_login(msg, transfer):
            user = get_user_info(msg)

            buyer = msg.text.replace("@","").strip()
            buyer_check = check_buyer_account(bot_id, buyer, connect_par)
            if buyer_check in [0,-1]: #не найден или в чёрном списке
                btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_cancel', user.lang), callback_data='cancel_transfer_owner;'+str(transfer.id))]
                keyboard = types.InlineKeyboardMarkup([btn_row1])
                message_code = "msg_buyer_not_find" if buyer_check == 0 else "msg_buyer_blacklist"
                bot1.send_message(user.user_id, translate_txt(message_code, user.lang), reply_markup=keyboard, parse_mode='html')
                bot1.register_next_step_handler(msg, input_transfer_buyer_login, transfer)  # повторный запуск

            else: #покупатель найден в базе и он не в чёрном списке
                transfer.buyer_user_id = buyer_check
                transfer.bot_commission = get_comission_amount(transfer.amount, transfer.owner_user_id, transfer.buyer_user_id, bot_id, connect_par)
                transfer.update_db(connect_par)

                #отправляем владельцу инфорацию для подтверждения
                show_new_transfer_to_confirm(transfer.id, "owner", bot1, connect_par)

        # Основное меню -> Я-участник -> Участвовать -> Введи кошелёк
        # ----------------------------------------------------------
        def input_airdrop_wallet(msg):
            user = get_user_info(msg)
            btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_back', user.lang), callback_data='main_menu')]
            keyboard = types.InlineKeyboardMarkup([btn_row1])

            wallet = (msg.text.replace("https://tonhub.com/transfer/", "").replace("ton://transfer/", "")).strip()

            # проверяем корректность формата кошелька
            if len(wallet) != 48 or wallet[0:2] not in ['EQ', 'UQ']:
                bot1.send_message(user.user_id, translate_txt('msg_wallet_incorrect', user.lang), reply_markup=keyboard, parse_mode='html')
                bot1.register_next_step_handler(msg, input_airdrop_wallet) #повторный запуск
            else:
                #сохраняем участника розыгрыша и его кошелёк
                save_airdrop_participant(user.user_id, wallet, connect_par)
                update_users_wallets(user.user_id, wallet, "airdrop", connect_par)
                bot1.send_message(user.user_id, translate_txt('msg_airdrop_success_participate', user.lang), reply_markup=keyboard,parse_mode='html')


        # Основное меню -> Найти аукцион->Введи номер аукциона
        # ----------------------------------------------------------
        def input_auction_id (msg):
            user = get_user_info(msg)
            btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_back', user.lang), callback_data='participate_back')]
            keyboard = types.InlineKeyboardMarkup([btn_row1])

            #проверяем корректность введённого ID
            auction_id = msg.text.strip()
            check_result = check_auction_id_correct(bot_id, auction_id, connect_par)
            if check_result == 1: #аукцион найден и он активен
                # показываем меню для выбранного аукциона
                show_selected_auction_menu(user, auction_id, bot1, connect_par)

            else:
                if check_result == 0: # аукцион не найден
                    text_to_send = translate_txt('msg_auction_id_not_found', user.lang)
                elif check_result == -1: #аукцион не активен
                    text_to_send = translate_txt('msg_auction_id_not_active', user.lang)
                else:
                    text_to_send = "Error"

                bot1.send_message(user.user_id, text_to_send, reply_markup=keyboard, parse_mode='html')
                bot1.register_next_step_handler(msg, input_auction_id)  # повторный запуск

        # Основное меню -> Я-участник -> Участвовать -> Введи кошелёк
        # ----------------------------------------------------------
        def input_participant_wallet(msg, auction_id):
            user = get_user_info(msg)

            wallet, wallet_check_result = check_wallet(msg.text, user.user_id, connect_par)
            if wallet_check_result == 1: #введён некорректный TON кошелёк
                btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_back', user.lang), callback_data='auction_back')]
                keyboard = types.InlineKeyboardMarkup([btn_row1])
                bot1.send_message(user.user_id, translate_txt('msg_wallet_incorrect', user.lang), reply_markup=keyboard, parse_mode='html')
                bot1.register_next_step_handler(msg, input_participant_wallet) #повторный запуск

            elif wallet_check_result == 2: #кошелёк в чёрном списке
                btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_back', user.lang), callback_data='auction_back')]
                keyboard = types.InlineKeyboardMarkup([btn_row1])
                bot1.send_message(user.user_id, translate_txt('msg_wallet_blacklist', user.lang), reply_markup=keyboard, parse_mode='html')
                bot1.register_next_step_handler(msg, input_participant_wallet)  # повторный запуск

            else:
                update_users_wallets(user.user_id, wallet, "auction_participant", connect_par) #сохраняем кошелёк в БД

                minimum_balance, user_balance = check_balance_for_auction(wallet, auction_id, connect_par)
                if user_balance < minimum_balance: #недостаточно средств на счёте
                    btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_back', user.lang), callback_data='auction_back')]
                    keyboard = types.InlineKeyboardMarkup([btn_row1])
                    text_to_send = translate_txt('msg_balance_not_enough', user.lang).format(str(minimum_balance), str(user_balance))
                    bot1.send_message(user.user_id, text_to_send, reply_markup=keyboard, parse_mode='html')
                    bot1.register_next_step_handler(msg, input_participant_wallet)  # повторный запуск
                else:

                    if wallet_check_result == 3: #кошелёк неверифицирован
                        # отправляем сообщение с реквизитами для верификации
                        amount_nano = int((0.01) * (10 ** 9))
                        fast_pay_link = payment_link.format(guarantor_wallet, str(amount_nano), hashmd5("verif"+str(user.user_id)))
                        text_to_send = translate_txt("msg_wallet_not_verif", user.lang).format(fast_pay_link,
                            f'<code>{guarantor_wallet}</code>', f'<code>{hashmd5("verif" + str(user.user_id))}</code>')
                        bot1.send_message(user.user_id, text_to_send, parse_mode='html')

                        btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_check_verif', user.lang),
                                                               callback_data="vrf2;"+str(wallet)+";"+str(auction_id)),
                                    types.InlineKeyboardButton(text=translate_txt('btn_back', user.lang),
                                                               callback_data='auction_back')]
                        keyboard = types.InlineKeyboardMarkup([btn_row1])
                        bot1.send_message(user.user_id, translate_txt('msg_press_button_below', user.lang), reply_markup=keyboard, parse_mode='html')

                    elif wallet_check_result == 0: #кошелёк верифицирован
                        #добавляем нового участника
                        add_new_participant(auction_id, user.user_id, wallet, connect_par)

                        # показываем карточку аукциона
                        show_selected_auction_menu(user, auction_id, bot1, connect_par)


        # Основное меню -> Мои аукционы -> Новый-> Введи кошелёк
        # ----------------------------------------------------------
        def input_owner_wallet(msg, auction):
            user = get_user_info(msg)

            wallet, check_result = check_wallet(msg.text, user.user_id, connect_par)
            if check_result in [1,2]:  #введён некорректный TON кошелёк или кошелёк в чёрном списке
                message_code = "msg_wallet_incorrect" if check_result == 1 else "msg_wallet_blacklist"
                btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_cancel', user.lang),callback_data='menu_my_auctions')]
                keyboard = types.InlineKeyboardMarkup([btn_row1])
                bot1.send_message(user.user_id, translate_txt(message_code, user.lang), reply_markup=keyboard, parse_mode='html')
                bot1.register_next_step_handler(msg, input_owner_wallet, auction) #повторный запуск

            elif check_result == 3: #кошелёк неверифицирован
                auction.owner_wallet = wallet  # сохраняем введённый owner_wallet
                update_users_wallets(user.user_id, wallet, "auction_owner", connect_par) # сохраняем кошелёк в БД
                save_auction_temp_data(auction, connect_par)  # сохраняем промежуточные данные по аукциону

                # отправляем сообщение с реквизитами для верификации
                amount_nano = int((0.01) * (10 ** 9))
                fast_pay_link = payment_link.format(guarantor_wallet, str(amount_nano), hashmd5("verif"+str(user.user_id)))
                text_to_send = translate_txt("msg_wallet_not_verif", user.lang).format(fast_pay_link,
                    f'<code>{guarantor_wallet}</code>', f'<code>{hashmd5("verif"+str(user.user_id))}</code>')
                bot1.send_message(user.user_id, text_to_send, parse_mode='html')

                btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_check_verif', user.lang), callback_data='auction_owner_verif'),
                            types.InlineKeyboardButton(text=translate_txt('btn_cancel', user.lang),callback_data='menu_my_auctions')]
                keyboard = types.InlineKeyboardMarkup([btn_row1])
                bot1.send_message(user.user_id, translate_txt('msg_press_button_below', user.lang), reply_markup=keyboard,parse_mode='html')

            elif check_result == 0: #кошелёк верифицирован
                auction.owner_wallet = wallet #сохраняем введённый owner_wallet
                update_users_wallets(user.user_id, wallet, "auction_owner", connect_par)  # сохраняем кошелёк в БД

                if collection_id !=0: #бот для конкретной коллекции (ARL)
                    btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_cancel', user.lang), callback_data='menu_my_auctions')]
                    keyboard = types.InlineKeyboardMarkup([btn_row1])
                    bot1.send_message(user.user_id, translate_txt('msg_input_nft', user.lang), reply_markup=keyboard)
                    bot1.register_next_step_handler(msg, input_auction_nft_info, auction) # шаг для проверки введённого NFT
                else:
                    save_auction_temp_data(auction, connect_par)  # сохраняем промежуточные данные по аукциону

                    keyboard = get_collections_list(0, "auction", connect_par) #при создании аукциона ID неизвестен
                    keyboard.add(types.InlineKeyboardButton(text=translate_txt('btn_cancel', user.lang), callback_data='menu_my_auctions'))
                    bot1.send_message(user.user_id, translate_txt("msg_input_collection", user.lang),reply_markup=keyboard)

        # Основное меню -> Мои аукционы -> Новый-> Введи NFT
        # ----------------------------------------------------------
        def input_auction_nft_info(msg, auction):
            user = get_user_info(msg)
            btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_cancel', user.lang), callback_data='menu_my_auctions')]
            keyboard = types.InlineKeyboardMarkup([btn_row1])

            #проверяем введённое название или адрес NFT
            error_code, error_text, nft_id = check_nft(auction.collection_id,  msg.text, auction.owner_wallet, user.lang, connect_par)
            if error_code != 0:
                if error_code == 1: #нет такого NFT в коллекции
                    bot1.send_message(user.user_id, error_text, reply_markup=keyboard, parse_mode='html')
                else: # выдаём ошибку, но показываем информацию об NFT
                    info, image = show_nft_info(nft_id, connect_par, user.lang)
                    info = info + "\n__________________________________\n\n"+error_text
                    bot1.send_photo(user.user_id, photo=open(image, 'rb'), caption=info, reply_markup=keyboard, parse_mode='html')

                bot1.register_next_step_handler(msg, input_auction_nft_info, auction)  # повторный запуск

            else:
                auction.nft_id = nft_id  # сохраняем введённый nft_id

                # отправляем пользователю картинку и информацию по выбранному NFT
                info, image = show_nft_info(nft_id, connect_par, user.lang)
                bot1.send_photo(user.user_id, photo=open(image, 'rb'), caption=info, parse_mode='html')

                bot1.send_message(user.user_id, translate_txt('msg_input_start_price', user.lang), reply_markup=keyboard)
                bot1.register_next_step_handler(msg, input_start_price, auction)  # шаг для проверки стартовой цены


        # Основное меню -> Мои аукционы -> Новый-> Введи стартовую цену
        # ----------------------------------------------------------
        def input_start_price(msg, auction):
            user = get_user_info(msg)
            btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_cancel', user.lang), callback_data='menu_my_auctions')]
            keyboard = types.InlineKeyboardMarkup([btn_row1])

            try:
                start_price = float(msg.text.strip())

                #сумма не попадает в диапазон
                if start_price < 1 or start_price > auction_start_price_limit:
                    bot1.send_message(user.user_id, translate_txt('msg_start_price_out_of_limits', user.lang).format(
                        str(auction_start_price_limit)),
                                      reply_markup=keyboard, parse_mode='html')
                    bot1.register_next_step_handler(msg, input_start_price, auction)  # повторный запуск

                else:
                    auction.start_price = start_price
                    bot1.send_message(user.user_id, translate_txt('msg_input_price_step', user.lang), reply_markup=keyboard)
                    bot1.register_next_step_handler(msg, input_price_step, auction)  # шаг для проверки шага цены

            except ValueError as err:
                print(err)
                # введены ошибочные данные
                bot1.send_message(user.user_id, translate_txt('msg_start_price_incorrect', user.lang), reply_markup=keyboard,parse_mode='html')
                bot1.register_next_step_handler(msg, input_start_price, auction)  # повторный запуск


        # Основное меню -> Мои аукционы -> Новый-> Введи шаг цены
        # ----------------------------------------------------------
        def input_price_step(msg, auction):
            user = get_user_info(msg)

            try: # пробуем преобразовать введённый пользователем текст в число
                price_step = float(msg.text.strip())
                auction.price_step = (0 if price_step < 0 else price_step) # 0, если введено меньше 0

                #отображаем варианты длительности аукциона
                select_duration_type(msg, auction)

            except ValueError as err:
                print(err)
                # введены ошибочные данные
                btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_cancel', user.lang),callback_data='menu_my_auctions')]
                keyboard = types.InlineKeyboardMarkup([btn_row1])
                bot1.send_message(user.user_id, translate_txt('msg_price_step_incorrect', user.lang), reply_markup=keyboard,parse_mode='html')
                bot1.register_next_step_handler(msg, input_price_step, auction)  # повторный запуск

        # Основное меню -> Мои аукционы -> Новый-> Выбери тип длительности
        # ----------------------------------------------------------
        def select_duration_type(msg, auction):
            user = get_user_info(msg)
            labels = translate_txt('btn_duration_types', user.lang).split(";")

            btn_row1 = [types.InlineKeyboardButton(text=labels[1], callback_data="duration_type;1"),
                        types.InlineKeyboardButton(text=labels[2], callback_data="duration_type;2")]

            btn_row2 = [types.InlineKeyboardButton(text=labels[3], callback_data="duration_type;3"),
                        types.InlineKeyboardButton(text=labels[4], callback_data="duration_type;4")]

            btn_row3 = [types.InlineKeyboardButton(text=labels[5], callback_data="duration_type;5"),
                        types.InlineKeyboardButton(text=labels[6], callback_data="duration_type;6")]

            btn_row4 = [types.InlineKeyboardButton(text=labels[0], callback_data="duration_type;0"),
                        types.InlineKeyboardButton(text=translate_txt('btn_cancel', user.lang), callback_data='menu_my_auctions')]
            keyboard = types.InlineKeyboardMarkup([btn_row1, btn_row2, btn_row3, btn_row4])

            # сохраняем все введённые пользователем ранее данные в промежуточную таблицу в БД, чтобы не потерять при переходе на callback_handler
            save_auction_temp_data(auction, connect_par)
            bot1.send_message(user.user_id, translate_txt('msg_input_duration_type', user.lang), reply_markup=keyboard, parse_mode='html')

        # Основное меню -> Мои аукционы -> Новый-> Введи фиксированное время окончания
        # ----------------------------------------------------------
        def input_fix_end_time(msg, auction):
            user = get_user_info(msg)
            btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_cancel', user.lang), callback_data='menu_my_auctions')]
            keyboard = types.InlineKeyboardMarkup([btn_row1])

            try:
                date_string = msg.text.strip().split(" ")[0]
                day = int(date_string.split(".")[0])
                month = int(date_string.split(".")[1])
                year_str = date_string.split(".")[2]
                year = int(year_str) if len(year_str)==4 else 2000+int(year_str)


                time_string = msg.text.strip().split(" ")[1]
                hour = int(time_string.split(":")[0])
                minutes = 0 #int(time_string.split(":")[1])
                seconds = 0 #int(time_string.split(":")[2])
                microseconds = 0

                end_time = datetime(year, month, day, hour, 0, 0, 0, timezone.utc)  # округляем введённое время GMT+3
                end_time_string = (end_time).strftime("%d.%m.%Y %H:%M:%S")


                min_end_time = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0) + timedelta(hours=3) + timedelta(hours=2)
                min_time_string = min_end_time.strftime("%d.%m.%Y %H:%M:%S")
                max_end_time = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0) + timedelta(hours=3) + timedelta(hours=72)
                max_time_string = max_end_time.strftime("%d.%m.%Y %H:%M:%S")

                if end_time < min_end_time:
                    bot1.send_message(user.user_id, translate_txt('msg_short_duration', user.lang).format(end_time_string, min_time_string), reply_markup=keyboard, parse_mode='html')
                    bot1.register_next_step_handler(msg, input_fix_end_time, auction)  # повторный запуск

                elif end_time > max_end_time:
                    bot1.send_message(user.user_id, translate_txt('msg_long_duration', user.lang).format(max_time_string), reply_markup=keyboard, parse_mode='html')
                    bot1.register_next_step_handler(msg, input_fix_end_time, auction)  # повторный запуск

                else: #введённое время корректно
                    auction.end_ts = end_time - timedelta(hours=3)  #сохраняем время в формате GMT-0
                    bot1.send_message(user.user_id, translate_txt('msg_input_comment', user.lang), reply_markup=keyboard, parse_mode='html')
                    bot1.register_next_step_handler(msg, input_auction_comment, auction)  # ввод комментария

            except Exception as err:
                print(err)
                bot1.send_message(user.user_id, translate_txt('msg_incorrect_endtime_format', user.lang), reply_markup=keyboard, parse_mode='html')
                bot1.register_next_step_handler(msg, input_fix_end_time, auction)  # повторный запуск

        # Основное меню -> Мои аукционы -> Новый-> Введи комментарий
        # ----------------------------------------------------------
        def input_auction_comment(msg, auction):
            try:
                user = get_user_info(msg)
                auction.comment = msg.text.strip()

                btn_row1 = [types.InlineKeyboardButton(text=translate_txt('btn_confirm', user.lang), callback_data='confirm_new_auction'),
                            types.InlineKeyboardButton(text=translate_txt('btn_cancel', user.lang), callback_data='menu_my_auctions')]
                keyboard = types.InlineKeyboardMarkup([btn_row1])

                # сохраняем во временную таблицу для обработки callback_handler
                save_auction_temp_data(auction, connect_par)

                # отображаем пользователю инфу для финального подтверждения
                info, image = show_auction_info_before_save(auction, user, connect_par)
                # bot1.send_photo(user.user_id, photo=open(image, 'rb'), caption=info, parse_mode='html')
                # bot1.send_message(user.user_id, translate_txt('msg_confirm_new_auction', user.lang), reply_markup=keyboard, parse_mode='html')

                text_to_send = info + "\n\n" + translate_txt('msg_confirm_new_auction', user.lang)
                bot1.send_photo(user.user_id, photo=open(image, 'rb'), caption=text_to_send, reply_markup=keyboard,parse_mode='html')

            except Exception as err:
                print(err)



    ###########################################################
        # запускаем бот на непрерывное ожидание сообщений
        bot1.infinity_polling()

    ###########################################################
    except Exception as err:
        print(err)
        if bot1 is not None:
            bot1.close()

