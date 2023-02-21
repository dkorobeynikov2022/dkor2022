# dkor2022
Repository for Python projects of Dmitry Korobeynikov


Installation of mankeys_guarantor_bot
1. Install PostgreSQL 13
2. Create database (botdb)
3. Create schemas, tables and views (SQL script from ddl folder)
4. Insert info about bot in table nft_auction_bot.d_bots (bot name, token, entity_id etc.)
5. Insert info in main_config.py (db connection parameters, admins user_id, api_id and hash to Telegram account for telethon client etc
6. Install Python 3 and libraries:
- psycopg2-binary
- pytelegrambotapi
- requests
- telethon
- ton
- tvm-valuetypes

7a. using ton library For Windows:
- use ./lib/tonlibjson.amd64.dll file (with full path to it)

7b. using ton library For Linux
- build manually libtonlibjson.so on your server from binary (https://github.com/kdimentionaltree/ton-builder )

8. Set on scheduler files autoclose_auction_monkeys.sh, blacklist_users_monkeys.sh, send_money_by_queue.sh

8. Run start_bot.py with bot_id from nft_auction_bot.d_bots table



