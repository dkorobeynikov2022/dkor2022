create schema nft_auction_bot;

/***********************************************************************/
--Коллекции NFT
drop table if exists nft_auction_bot.d_collections;
create table nft_auction_bot.d_collections (
    id serial not null primary key,
    address text not null,
    name text not null,
    description text,
    content text,
    items_count int8,
    owner_address text,
    royalty float8,
    dwh_dt timestamptz not null default now(),
    order_num int8,
    icon_symbol text,
    royalty_address text
)
;

grant all on nft_auction_bot.d_collections to nft_auction_bot;
grant all on nft_auction_bot.d_collections_id_seq to nft_auction_bot;
    

/***********************************************************************/
-- NFT из коллекций для продажи
drop table if exists nft_auction_bot.d_nft;
create table nft_auction_bot.d_nft (
    id serial not null primary key,
    collection_id int8 not null,
    address text not null unique,
    name text not null,
    description text,
    short_info text,
    image_path text not null,
    dwh_dt timestamptz not null default now()
)
;

create index d_nft_ind1 on nft_auction_bot.d_nft(collection_id);
create index d_nft_ind2 on nft_auction_bot.d_nft(address);
create index d_nft_ind3 on nft_auction_bot.d_nft(name);

grant all on nft_auction_bot.d_nft to nft_auction_bot;
grant all on nft_auction_bot.d_nft_id_seq to nft_auction_bot;    


/***********************************************************************/
drop view if exists nft_auction_bot.v_d_nft;
create view nft_auction_bot.v_d_nft as
select 
nft.id as nft_id,
coll.id as collection_id,
nft.address as nft_address,
coll.address as collection_address,
nft.name as nft_name,
coll.name as collection_name
from nft_auction_bot.d_nft nft 
inner join nft_auction_bot.d_collections coll on (nft.collection_id=coll.id)
;

grant all on nft_auction_bot.v_d_nft to nft_auction_bot;

/***********************************************************************/
-- Справочник ботов 
drop table if exists nft_auction_bot.d_bots;
create table nft_auction_bot.d_bots (
    id serial not null primary key,
    collection_id int8 not null,
    name text not null,
    address text not null unique,
    token text not null unique,
    description text,
    channel_ids text, #список каналов, в которые нужно отправлять оповещение,
    entity_id int8,
    access_hash int8,
    dwh_dt timestamptz not null default now(),

    commission_min float8 not null default 0,
    commission_perc float8 not null default 0,
    vip_commission_perc float8 not null default 0

)
;

grant all on nft_auction_bot.d_bots to nft_auction_bot;
grant all on nft_auction_bot.d_bots_id_seq to nft_auction_bot;


/***********************************************************************/
drop table if exists nft_auction_bot.d_users;
create table nft_auction_bot.d_users (
    user_id int8 not null primary key,
    username text,
    first_name text,
    last_name text,
    start_ts timestamptz,
    language_code text,
    last_activity_ts timestamptz,
    cancel_limit int8 not null default 3,
    auctions_total int8 not null default 0,
    auctions_cancelled int8 not null default 0,
    auctions_with_winner int8 not null default 0,
    auctions_wo_winner int8 not null default 0
)
;
grant all on nft_auction_bot.d_users to nft_auction_bot;

create index d_users_ind1 on nft_auction_bot.d_users(user_id);


/***********************************************************************/
drop table if exists nft_auction_bot.f_users_bots;
create table nft_auction_bot.f_users_bots (
    id serial not null primary key,
    user_id int8 not null,
    bot_id int8 not null,
    dwh_dt timestamptz not null default now(),

    UNIQUE(user_id, bot_id)
)
;
grant all on nft_auction_bot.f_users_bots to nft_auction_bot;

create index f_users_bots_ind1 on nft_auction_bot.f_users_bots(user_id, bot_id);

grant all on nft_auction_bot.f_users_bots to nft_auction_bot;
grant all on nft_auction_bot.f_users_bots_id_seq to nft_auction_bot;


insert into nft_auction_bot.f_users_bots (user_id, bot_id, dwh_dt)
select user_id, 1 as bot_id, start_ts as dwh_dt from nft_auction_bot.d_users;

/***********************************************************************/
drop table if exists nft_auction_bot.f_users_log;
create table nft_auction_bot.f_users_log (
    id serial not null primary key,
    time_id timestamptz not null default now(),
    user_id int8 not null,
    username text,
    first_name text,
    last_name text,
    language_code text,
    bot_id int8
)
;
grant all on nft_auction_bot.f_users_log to nft_auction_bot;
grant all on nft_auction_bot.f_users_log_id_seq to nft_auction_bot;

create index f_users_log_ind1 on nft_auction_bot.f_users_log(user_id);

/***********************************************************************/
drop table if exists nft_auction_bot.d_users_blacklist;
create table nft_auction_bot.d_users_blacklist (
    id serial not null primary key,
    user_id int8,
    wallet text,
    nft_id int8,
    auction_id int8,
    reason text,
    dwh_dt timestamptz not null default now()
)
;
grant all on nft_auction_bot.d_users_blacklist to nft_auction_bot;
grant all on nft_auction_bot.d_users_blacklist_id_seq to nft_auction_bot;

/***********************************************************************/

drop view if exists nft_auction_bot.v_d_users;
create or replace view nft_auction_bot.v_d_users as 
select
usr.user_id,
usr.username,
usr.first_name,
usr.last_name,
(case 
    when black.user_id is not null then '🖤blacklist' 
    when monkeys.user_id is not null then '🐒monkey'
    else '💚good'
end) as type,
wallet.wallet,
usr.language_code
from nft_auction_bot.d_users usr
left join nft_auction_bot.d_users_blacklist black on (usr.user_id=black.user_id)
left join nft_auction_bot.v_d_user_wallets wallet on (usr.user_id=wallet.user_id and now() between wallet.fd and wallet.td)
left join nft_auction_bot.d_monkeys_users_list monkeys on (usr.user_id=monkeys.user_id)
;

grant all on nft_auction_bot.v_d_users to nft_auction_bot;

/***********************************************************************/
drop table if exists nft_auction_bot.d_auctions;
create table nft_auction_bot.d_auctions  (
    id serial not null primary key,
    status text not null default 'active',
    collection_id int8 not null,
    nft_id int8 not null,
    owner_user_id int8 not null,
    owner_wallet text not null,
    start_price numeric not null default 0,
    price_step numeric not null,
    start_ts timestamptz not null,
    end_ts timestamptz not null,
    comment text,
    leader_user_id int8,
    leader_wallet text,
    leader_price numeric,
    participants int8 not null default 0,
    dwh_dt timestamptz not null default now(),
    bot_id int8,
    bot_commission float8 not null default 0
)
;

grant all on nft_auction_bot.d_auctions to nft_auction_bot;
grant all on nft_auction_bot.d_auctions_id_seq to nft_auction_bot;

create index d_auctions_ind1 on nft_auction_bot.d_auctions(bot_id, status);
create index d_auctions_ind2 on nft_auction_bot.d_auctions(owner_user_id);



/*временная таблица, которая используется для передачи данных между register_next_step_handler и callback_query_handler*/
drop table if exists nft_auction_bot.d_auctions_temp;
create table nft_auction_bot.d_auctions_temp  (
    collection_id int8 not null,
    nft_id int8,
    owner_user_id int8,
    owner_wallet text,
    start_price numeric,
    price_step numeric,
    end_ts text,
    comment text,
    dwh_dt timestamptz not null default now()   ,
    owner_lang text,
    bot_id int8
)
;

grant all on nft_auction_bot.d_auctions_temp to nft_auction_bot;


/***********************************************************************/
drop view if exists nft_auction_bot.v_d_auctions;
create or replace view nft_auction_bot.v_d_auctions as
select 
auc.id as auction_id,
auc.collection_id,
auc.status,
auc.owner_user_id,
auc.owner_wallet,
auc.start_price,
auc.price_step,
auc.start_ts,
auc.end_ts,
(case 
    when length(auc.comment)>150 then left(auc.comment,150)||'...'
    else auc.comment
end) as comment, 
auc.leader_user_id,
auc.leader_wallet,
auc.leader_price,
bot.channel_id,
nft.id as nft_id,
nft.address as nft_address,
nft.name as nft_name,
nft.description as nft_description,
nft.image_path,
owner.username as owner_username,
owner.first_name as owner_first_name,
owner.last_name as owner_last_name,
auc.participants,
owner.auctions_total as owner_auctions_total,
owner.auctions_cancelled as owner_auctions_cancelled,
owner.auctions_with_winner as owner_auctions_with_winner,
owner.auctions_wo_winner as owner_auctions_wo_winner,
owner.language_code as owner_lang,
leader.language_code as leader_lang,
collection.address as collection_address,
trim(coalesce(leader.first_name,'')||' '||coalesce(leader.last_name,'')) || (case when coalesce(leader.username,'')<>'' then ' [@'||leader.username||']' else '' end) as leader_fullname,
auc.bot_id,
auc.bot_commission

from nft_auction_bot.d_auctions auc
inner join nft_auction_bot.d_bots bot on (auc.bot_id=bot.id)
inner join nft_auction_bot.d_nft nft on (auc.nft_id=nft.id)
inner join nft_auction_bot.d_collections collection on (nft.collection_id=collection.id)
inner join nft_auction_bot.d_users owner on (auc.owner_user_id = owner.user_id)
left join nft_auction_bot.d_users leader on (auc.leader_user_id = leader.user_id)
;

grant all on nft_auction_bot.v_d_auctions to nft_auction_bot;
/***********************************************************************/


drop view if exists nft_auction_bot.v_d_closed_auctions;
create view nft_auction_bot.v_d_closed_auctions as
select
auc.id,
row_number() over (partition by auc.owner_user_id order by auc.id desc) as rn_desc
from nft_auction_bot.d_auctions auc
where auc.status='closed'
;

grant all on nft_auction_bot.v_d_closed_auctions to nft_auction_bot;
/***********************************************************************/

drop table if exists nft_auction_bot.f_auction_participants;
create table nft_auction_bot.f_auction_participants (
    id serial not null primary key,
    auction_id int8 not null,
    user_id int8 not null,
    wallet text,
    dwh_dt timestamptz not null default now(),

    UNIQUE(auction_id, user_id)
)
;
grant all on nft_auction_bot.f_auction_participants to nft_auction_bot;
grant all on nft_auction_bot.f_auction_participants_id_seq to nft_auction_bot;

create index f_auction_participants_ind1 on nft_auction_bot.f_auction_participants (auction_id, user_id);


/***********************************************************************/

drop table if exists nft_auction_bot.f_auction_user_bids;
create table nft_auction_bot.f_auction_user_bids (
    id serial not null primary key,
    auction_id int8 not null,
    user_id int8 not null,
    amount text,
    dwh_dt timestamptz not null default now()
)
;
grant all on nft_auction_bot.f_auction_user_bids to nft_auction_bot;
grant all on nft_auction_bot.f_auction_user_bids_id_seq to nft_auction_bot;

/***********************************************************************/
--все аукционы, в которых участвует конкретный пользователь
drop view if exists nft_auction_bot.v_f_auction_participants;
create or replace view nft_auction_bot.v_f_auction_participants as
select
part.auction_id,
auc.status,
auc.start_ts,
auc.end_ts,
auc.start_price,
auc.price_step,
auc.leader_price,
part.user_id,
auc.participants,
nft.name as nft_name,
auc.leader_user_id,
nft.short_info as nft_short_info,
auc.bot_id
from nft_auction_bot.f_auction_participants part
inner join nft_auction_bot.d_auctions auc on (part.auction_id=auc.id)
inner join nft_auction_bot.d_nft nft on (auc.nft_id=nft.id)
order by part.auction_id
;

grant all on nft_auction_bot.v_f_auction_participants to nft_auction_bot;

/***********************************************************************/
-- список аукционов, которые организовал данный пользователь
drop view if exists nft_auction_bot.v_f_user_auctions;
create or replace view nft_auction_bot.v_f_user_auctions as
select
auc.owner_user_id as user_id,
auc.id as auction_id,
auc.status,
auc.start_ts,
auc.end_ts,
auc.start_price,
auc.price_step,
auc.leader_price,
auc.comment,
nft.name as nft_name,
nft.address as nft_address,
nft.short_info as nft_short_info,
auc.participants,
auc.owner_user_id,
row_number() over (partition by auc.owner_user_id order by auc.start_ts desc) as rn_desc,
auc.bot_id
from nft_auction_bot.d_auctions auc
inner join  nft_auction_bot.d_nft nft on (auc.nft_id=nft.id)
;

grant all on nft_auction_bot.v_f_user_auctions to nft_auction_bot;


/***********************************************************************/
drop table if exists nft_auction_bot.f_user_wallets_usage;
create table nft_auction_bot.f_user_wallets_usage (
    id serial not null primary key,
    user_id int8 not null,
    wallet text not null,
    dwh_dt timestamptz not null default now(),
    source_type text
)
;
grant all on nft_auction_bot.f_user_wallets_usage to nft_auction_bot;
grant all on nft_auction_bot.f_user_wallets_usage_id_seq to nft_auction_bot;

create index f_user_wallets_usage_ind1 on nft_auction_bot.f_user_wallets_usage(user_id);
create index f_user_wallets_usage_ind2 on nft_auction_bot.f_user_wallets_usage(user_id, dwh_dt);



truncate table nft_auction_bot.f_user_wallets_usage ;
insert into nft_auction_bot.f_user_wallets_usage (user_id, wallet, source_type, dwh_dt)
select user_id, wallet, source_type, dwh_dt from (
    select 
    owner_user_id as user_id,
    owner_wallet as wallet,
    'auction_owner' as source_type,
    start_ts as dwh_dt
    from nft_auction_bot.d_auctions

    UNION ALL 

    select 
    user_id,
    wallet,
    'auction_participant' as source_type,
    dwh_dt
    from nft_auction_bot.f_auction_participants

    UNION ALL 

    select 
    owner_user_id as user_id,
    owner_wallet as wallet,
    'transfer_owner' as source_type,
    start_ts as dwh_dt
    from nft_auction_bot.d_transfers
    where owner_wallet is not null

    UNION ALL 

    select 
    buyer_user_id as user_id,
    buyer_wallet as wallet,
    'transfer_buyer' as source_type,
    start_ts as dwh_dt
    from nft_auction_bot.d_transfers
    where buyer_user_id is not null and buyer_wallet is not null

    UNION ALL 

    select 
    user_id,
    info as wallet,
    'airdrop' as source_type,
    dwh_dt
    from nft_auction_bot.f_airdrop_users
) t
;


create or replace view nft_auction_bot.v_d_user_wallets as
select 
user_id,
dwh_dt as fd,
coalesce(lead(dwh_dt-interval '1 sec') over (partition by user_id order by dwh_dt), '9999-01-01'::timestamptz) as td,
wallet,
source_type
from nft_auction_bot.f_user_wallets_usage
order by user_id, fd
;

grant all on nft_auction_bot.v_d_user_wallets to nft_auction_bot;



/***********************************************************************/
drop table if exists nft_auction_bot.d_wallets_verifications;
create table nft_auction_bot.d_wallets_verifications (
    id serial not null primary key,
    user_id int8 not null,
    wallet text not null,
    dwh_dt timestamptz not null default now(),

    UNIQUE (user_id, wallet)
)
;
grant all on nft_auction_bot.d_wallets_verifications to nft_auction_bot;
grant all on nft_auction_bot.d_wallets_verifications_id_seq to nft_auction_bot;



/***********************************************************************/


drop table if exists nft_auction_bot.d_transfers;
create table nft_auction_bot.d_transfers (
    id serial not null primary key,
    owner_user_id int8,
    owner_wallet text,
    nft_id int8,
    amount float8,
    bot_commission float8,
    buyer_user_id int8,
    buyer_wallet text,
    status text not null default 'active',
    start_ts timestamptz not null default now(),
    end_ts timestamptz,
    bot_id int8,
    collection_id int8
)
;
grant all on nft_auction_bot.d_transfers to nft_auction_bot;
grant all on nft_auction_bot.d_transfers_id_seq to nft_auction_bot;



drop view if exists nft_auction_bot.v_d_transfers;
create or replace view nft_auction_bot.v_d_transfers as 
select
trans.id,
trans.status,
trans.start_ts,
trans.end_ts,
trans.amount,
trans.bot_commission,
trans.owner_user_id,
trans.owner_wallet,
trim(coalesce(owner.first_name,'')||' '||coalesce(owner.last_name,'')) || (case when coalesce(owner.username,'')<>'' then ' [@'||owner.username||']' else '' end) as owner_fullname,
owner.language_code as owner_lang,
trans.buyer_user_id,
trans.buyer_wallet,
trim(coalesce(buyer.first_name,'')||' '||coalesce(buyer.last_name,'')) || (case when coalesce(buyer.username,'')<>'' then ' [@'||buyer.username||']' else '' end) as buyer_fullname,
buyer.language_code as buyer_lang,
trans.nft_id,
nft.address as nft_address,
nft.name as nft_name,
nft.description as nft_description,
nft.image_path as nft_image,
coalesce(nft.collection_id, trans.collection_id) as collection_id,
collection.name as collection_name,
collection.address as collection_address,
trans.bot_id
from nft_auction_bot.d_transfers trans 
left join nft_auction_bot.d_users owner on (trans.owner_user_id=owner.user_id)
left join nft_auction_bot.d_users buyer on (trans.buyer_user_id=buyer.user_id)
left join nft_auction_bot.d_nft nft on (trans.nft_id=nft.id)
left join nft_auction_bot.d_collections collection on (nft.collection_id=collection.id)
;
grant all on nft_auction_bot.v_d_transfers to nft_auction_bot;


/***********************************************************************/

drop table if exists nft_auction_bot.f_airdrop_users_membership;
create table nft_auction_bot.f_airdrop_users_membership (
    id serial not null primary key,
    airdrop_id int8 not null,
    user_id int8 not null,
    channel_id int8 not null,
    is_member bool not null,
    dwh_dt timestamptz not null default now()
)
;
grant all on nft_auction_bot.f_airdrop_users_membership to nft_auction_bot;
grant all on nft_auction_bot.f_airdrop_users_membership_id_seq to nft_auction_bot;


/***********************************************************************/
drop table if exists nft_auction_bot.d_monkeys_nft;
create table nft_auction_bot.d_monkeys_nft (
    id serial not null primary key,
    collection_address text not null,
    nft_address text not null unique,
    name text,
    owner text not null,
    description text,
    dwh_dt timestamptz not null default now(),
    status text,
    price float8,
    market text
)
;
grant all on nft_auction_bot.d_monkeys_nft to nft_auction_bot;
grant all on nft_auction_bot.d_monkeys_nft_id_seq to nft_auction_bot;

insert into nft_auction_bot.d_monkeys_nft (collection_address, nft_address, name, owner, description)
select 
collection_address,
nft_address,
nft_name as name,
owner,
nft_tier||'-'||nft_subtier||'-'||filter_group as description
from nft_collections.d_nft_arl 
where animal_order='Primates'
;




/***********************************************************************/
drop table if exists nft_auction_bot.f_send_money_queue;
create table nft_auction_bot.f_send_money_queue (
    id serial not null primary key,
    from_wallet text not null,    
    to_wallet text not null,
    amount float8 not null,
    comment text not null,    
    payment_type text not null, /*buyer, royalty, fund*/
    queue_ts timestamptz not null default now(),    
    status text not null default 'queued', /*queued, sent, checked*/
    from_wallet_balance float8,
    send_ts timestamptz,
    check_ts timestamptz
)
;
grant all on nft_auction_bot.f_send_money_queue to nft_auction_bot;
grant all on nft_auction_bot.f_send_money_queue_id_seq to nft_auction_bot;
