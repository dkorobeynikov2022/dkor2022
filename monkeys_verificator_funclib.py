import psycopg2
from main_config import  connect_par
from messages import  translate_txt
from wallets_funclib import  address_to_bounceable
from main_funclib import get_nft_owner

#################################################################
# проверяем, входит ли пользователь в сообщество Monkeys
def check_user_is_monkeys(user, param):
    try:
        connect1 = psycopg2.connect(host=param[0], port=param[1], dbname=param[2], user=param[3],  password=param[4])
        schema = param[5]

        select_sql = "select user_id from "+schema+".d_monkeys_users_list where user_id ="+str(user.user_id)
        cursor1 = connect1.cursor()
        cursor1.execute(select_sql)
        data = cursor1.fetchone()
        cursor1.close()

        if data is not None and len(data)>0:
            return True
        else:
            return False

        return wallet, result

    except Exception as err:
        print(err)
    finally:
        connect1.close()

#################################################################
# обновляем справочники после новой верификации
def update_monkeys_new_verification (user, nft_id, param):
    try:
        connect1 = psycopg2.connect(host=param[0], port=param[1], dbname=param[2], user=param[3],  password=param[4])
        schema = param[5]
        cursor1 = connect1.cursor()

        update_sql = "update "+schema+".d_monkeys_nft set owner='"+user.wallet+"' where id ="+str(nft_id)
        cursor1.execute(update_sql)

        script_sql = "drop table if exists tmp_d_monkeys_users_list; " \
            + " create local temporary table tmp_d_monkeys_users_list (user_id int8 primary key, type text) on commit preserve rows; " \
            + " insert into tmp_d_monkeys_users_list select distinct user_id, 'nft' as type from nft_auction_bot.v_d_monkeys_nft where user_id is not null; "\
            + " insert into tmp_d_monkeys_users_list select distinct user_id, 'vip' as type from nft_auction_bot.d_monkeys_users_vip on conflict (user_id) do nothing; " \
            + " delete from nft_auction_bot.d_monkeys_users_list; " \
            + " insert into nft_auction_bot.d_monkeys_users_list  select user_id, now(), type from tmp_d_monkeys_users_list;"
        cursor1.execute(script_sql)
        connect1.commit()
        cursor1.close()

    except Exception as err:
        print(err)
    finally:
        connect1.close()

########################################################################################################
# комплексная проверка NFT на чёрный список и принадлежность к категории NFT для Monkeys,принадлежность владельцу
# возвращается код ошибки, текст ошибки и NFT_ID
def check_monkeys_nft(nft_info, owner_wallet, lang, param):
    try:
        connect1 = psycopg2.connect(host=param[0], port=param[1], dbname=param[2], user=param[3],  password=param[4])
        schema = param[5]
        cursor1 = connect1.cursor()
        nft_info = str(nft_info).strip()

        if len(nft_info) == 48 and nft_info[0:2] == 'EQ': #передан адрес NFT в bounceable формате
            filter = " nft.nft_address = '" + nft_info + "'"
        elif len(nft_info) == 48 and nft_info[0:2] == 'UQ': #передан адрес NFT в non-bounceable формате
            print("non-bounceable NFT address: " + nft_info)
            bounceable_address = address_to_bounceable(nft_info)
            print("bounceable NFT address: " + bounceable_address)
            filter = " nft.nft_address = '" + str(bounceable_address) + "'"
        else:
            filter = " (lower(nft.name)=lower('"+nft_info+"') or lower(replace(nft.name, 'ARL ',''))=lower('"+nft_info+ "'))"

        select_sql = "select nft.id, nft.nft_address, nft.name," \
            + "(case when bl.nft_id is not null then true else false end) as is_blacklist " \
            + " from "+schema+".d_monkeys_nft nft " \
            + " left join "+schema+".d_users_blacklist bl on (nft.id=bl.nft_id) " \
            + " where " + filter
        cursor1.execute(select_sql)
        data = cursor1.fetchone()
        cursor1.close()

        if data is None or len(data) == 0: #нет NFT с таким адресом или названием в коллекции
            return 1, translate_txt('msg_monkeys_nft_incorrect', lang), None

        elif data[3] == True: #NFT в чёрном списке
            return 2, translate_txt('msg_nft_blacklist', lang), data[0]

        else:
            blockchain_owner = get_nft_owner(data[1])
            if blockchain_owner is None:
                return 4, translate_txt('msg_nft_api_error', lang), data[0]
            elif owner_wallet != blockchain_owner: #владелец NFT по блокчейну не совпадает с создателем аукциона
                return 5, translate_txt('msg_monkeys_nft_wrong_owner', lang), data[0]
            else:
                return 0, None, data[0] # всё в порядке

    except Exception as err:
        print(err)
    finally:
        connect1.close()