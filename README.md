# dkor2022
Repository for Python projects of Dmitry Korobeynikov

donate_wallet = 'EQBnk2PqeZZjIya2zvPlH2pnSQYYPjNReMntiOyWYt9au_fc'

<b><a href='t.me/mankeys_guarantor_bot'>@mankeys_guarantor_bot</a> - Telegram bot for P2P deals and auctions for NFT on TON blockchain. 
It helps to decrease risks for users when they want to sell NFT without commissions via P2P deals. Also it helps to provide auctions (also without commissions).</b>

<b>Functionality of mankeys_guarantor_bot</b>
Main functionality:
1. Creation of new NFT auctions of the main TON NFT collections
2. Automatic notification of new/closed auctions (with detailed information) in a special channel(s)
3. Participation in active auctions (bid increase, bid change notifications)
4. Conducting P2P transactions for the sale of NFTs between two participants
5. Protection of participants from fraud - transfer of funds of the auction winner and P2P buyer to the wallet of the guarantor bot and automatic sending only after the transfer of NFT
6. Maintaining a blacklist of unscrupulous participants (Telegram account, TON wallet, NFT address) and a ban on further use of the bot by such participants
7. Verification of Monkeys - checking if the user has a special NFT that gives access to the closed Monkeys community group (ApeRedList) with bonuses for participants (discounts, presales, airdrops, etc.)


Additional functionality:
1. Bilingual interface (automatic language selection according to user settings)
2. Verification of wallets of auction organizers and participants
3. Verification of ownership of NFT by the organizer of the auction and the seller in the transaction
4. Checking the sufficiency of the balance of participants to participate in auctions and increase rates
5. Extended statistics on the attributes of the lot (number in the collection,%, rank, etc.)


<b>Installation of mankeys_guarantor_bot</b>
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

9. Run start_bot.py with bot_id from nft_auction_bot.d_bots table



