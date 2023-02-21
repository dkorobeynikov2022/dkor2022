def translate_txt(message_code, lang):
	languages = ['ru', 'en']
	if lang is None or lang not in languages:
		lang = 'en'

	messages = {
		'msg_start_1': [
			"Добро пожаловать в бот для аукционов и продаж NFT из коллекции <b>Animals Red List</b> на блокчейне TON, \n" \
			+ "посвящённой редким и исчезающим видам животных из Международной Красной Книги.\n\n" \
			+ "Канал с подробной информацией о проводимых аукционах - @arl_nft_auctions \n" \
			+ "Группа с отзывами пользователей о работе бота - @arl_auction_bot_feedback \n\n"
			+ "Вот что мне удалось о тебе узнать:\n<b>ID: </b>{}\n" \
			+ "<b>Логин: </b>{}\n<b>Имя: </b>{}\n<b>Кошелёк: </b>{}\n<b>Тип: </b>{}\n\n" \
			+ "Нажми 👉/menu👈, чтобы начать.",

			"Welcome to the bot that helps to proceed auctions and sales for NFT from collection <b>Animals Red List</b> on blockchain TON.\n" \
			+ "The collection dedicated to rare animals from International Red Book. \n\n" \
			+ "The channel with all information about auctions - @arl_nft_auctions\n"
			+ "The group for users feedback about bot - @arl_auction_bot_feedback\n\n"
			+ "That is what I know about you:\n<b>ID: </b>{}\n" \
			+ "<b>Login: </b>{}\n<b>Name: </b>{}\n<b>Wallet: </b>{}\n<b>User type: </b>{}\n\n" \
			+ "Press 👉/menu👈 to start."
		],

		'msg_start_2': [
			"Добро пожаловать в <b>бот-гарант от сообщества Monkeys</b> для проведения аукционов и P2P-продаж NFT из основных коллекций на блокчейне TON.\n\n" \
			+ "Канал с подробной информацией о проводимых аукционах - @monkeys_guarantor_bot_channel \n" \
			+ "Группа с отзывами пользователей о работе бота - @arl_auction_bot_feedback \n\n"
			+ "Вот что мне удалось о тебе узнать:\n<b>ID: </b>{}\n" \
			+ "<b>Логин: </b>{}\n<b>Имя: </b>{}\n<b>Кошелёк: </b>{}\n<b>Тип: </b>{}\n\n" \
			+ "Нажми 👉/menu👈, чтобы начать.",

			"Welcome to <b>the guarantor bot from Monkeys community</b> that helps to proceed auctions and P2P NFT sales from the collections on blockchain TON.\n\n" \
			+ "The channel with all information about deals - @monkeys_guarantor_bot_channel\n" \
			+ "The group for users feedback about bot - @arl_auction_bot_feedback\n\n"
			+ "That is what I know about you:\n<b>ID: </b>{}\n" \
			+ "<b>Login: </b>{}\n<b>Name: </b>{}\n<b>Wallet: </b>{}\n<b>User type: </b>{}\n\n" \
			+ "Press 👉/menu👈 to start."
		],

		'msg_start_4': [
			"Добро пожаловать в <b>бот-гарант от сообщества Monkeys</b> для проведения аукционов и P2P-продаж NFT из основных коллекций на блокчейне TON.\n\n" \
			+ "Канал с подробной информацией о проводимых аукционах - @monkeys_guarantor_bot_channel \n" \
			+ "Группа с отзывами пользователей о работе бота - @arl_auction_bot_feedback \n\n"
			+ "Вот что мне удалось о тебе узнать:\n<b>ID: </b>{}\n" \
			+ "<b>Логин: </b>{}\n<b>Имя: </b>{}\n<b>Кошелёк: </b>{}\n<b>Тип: </b>{}\n\n" \
			+ "Нажми 👉/menu👈, чтобы начать.",

			"Welcome to <b>the guarantor bot from Monkeys community</b> that helps to proceed auctions and P2P NFT sales from the collections on blockchain TON.\n\n" \
			+ "The channel with all information about deals - @monkeys_guarantor_bot_channel\n" \
			+ "The group for users feedback about bot - @arl_auction_bot_feedback\n\n"
			+ "That is what I know about you:\n<b>ID: </b>{}\n" \
			+ "<b>Login: </b>{}\n<b>Name: </b>{}\n<b>Wallet: </b>{}\n<b>User type: </b>{}\n\n" \
			+ "Press 👉/menu👈 to start."
		],
		#ARL
		'nft_info_1': [
			"{} | {} | {}\n\n" \
			+ "<b>Царство: </b>{}\n" \
			+ "<b>Тип: </b>{}\n" \
			+ "<b>Класс: </b>{}\n" \
			+ "<b>Отряд: </b>{}\n" \
			+ "<b>Семейство: </b>{}\n" \
			+ "<b>Род: </b>{}\n" \
			+ "<b>Классификация ARL: </b>{}\n\n" \
			+ "<b>Общее название: </b><a href='https://apiv3.iucnredlist.org/api/v3/taxonredirect/{}'>{}</a>\n" \
			+ "<b>Год открытия: </b>{}\n" \
			+ "<b>Среда обитания: </b>{}\n" \
			+ "<b>Тренд популяции: </b>{}\n" \
			+ "<b>Миграция: </b>{}",

			"{} | {} | {}\n\n" \
			+ "<b>Kingdom: </b>{}\n" \
			+ "<b>Phylum: </b>{}\n" \
			+ "<b>Class: </b>{}\n" \
			+ "<b>Order: </b>{}\n" \
			+ "<b>Family: </b>{}\n" \
			+ "<b>Genus: </b>{}\n" \
			+ "<b>ARL group: </b>{}\n\n" \
			+ "<b>Common name: </b><a href='https://apiv3.iucnredlist.org/api/v3/taxonredirect/{}'>{}</a>\n" \
			+ "<b>Discovery year: </b>{}\n" \
			+ "<b>System: </b>{}\n" \
			+ "<b>Population trend: </b>{}\n" \
			+ "<b>Migration: </b>{}"
		],

		# RichCats
		'nft_info_2': [
			"\n<b>Тело: </b>{}\n┖ {}\n\n" \
			+ "<b>Глаза: </b>{}\n┖ {}\n\n" \
			+ "<b>Зубы: </b>{}\n┖ {}\n\n" \
			+ "<b>Усы: </b>{}\n┖ {}\n\n" \
			+ "<b>Фон: </b>{}\n┖ {}",

			"\n<b>Body: </b>{}\n┖ {}\n\n" \
			+ "<b>Eyes: </b>{}\n┖ {}\n\n" \
			+ "<b>Teeth: </b>{}\n┖ {}\n\n" \
			+ "<b>Whiskers: </b>{}\n┖ {}\n\n" \
			+ "<b>Background: </b>{}\n┖ {}"
		],

		# TON Earth Land
		'nft_info_3': [
			"\n<b>Тип: </b>{}\n┖ {}\n\n" \
			+ "<b>Биом: </b>{}\n┖ {}\n\n" \
			+ "<b>Доступ к озеру: </b>{}\n┖ {}\n\n" \
			+ "<b>Доступ к океану: </b>{}\n┖ {}",

			"\n<b>Type: </b>{}\n┖ {}\n\n" \
			+ "<b>Biome: </b>{}\n┖ {}\n\n" \
			+ "<b>Lake access: </b>{}\n┖ {}\n\n" \
			+ "<b>Ocean access: </b>{}\n┖ {}"
		],

		# Annihilation
		'nft_info_4': [
			"{}\n\n"\
			+ "<b>Тип: </b>{}\n┖ {}\n\n" \
			+ "<b>Генезис: </b>{}\n┖ {}\n\n" \
			+ "<b>Статус: </b>{}\n┖ {}\n\n" \
			+ "<b>Душа: </b>{}\n┖ {}\n\n" \
			+ "<b>Раса: </b>{}\n┖ {}\n\n" \
			+ "<b>Эволюция: </b>{}\n┖ {}\n\n" \
			+ "<b>Суперсила: </b>{}"
			,
			"{}\n\n"\
			+ "<b>Type: </b>{}\n┖ {}\n\n" \
			+ "<b>Genesis: </b>{}\n┖ {}\n\n" \
			+ "<b>Status: </b>{}\n┖ {}\n\n" \
			+ "<b>Soul: </b>{}\n┖ {}\n\n" \
			+ "<b>Race: </b>{}\n┖ {}\n\n" \
			+ "<b>Evolution: </b>{}\n┖ {}\n\n" \
			+ "<b>Superpower: </b>{}"
		],

		# TON Earth Houses
		'nft_info_5': [
			"\n<b>База: </b>{}\n┖ {}\n\n" \
			+ "<b>Крыша: </b>{}\n┖ {}\n\n" \
			+ "<b>Окна: </b>{}\n┖ {}\n\n" \
			+ "<b>Дверь: </b>{}\n┖ {}\n\n" \
			+ "<b>Этажи: </b>{}\n┖ {}",

			"\n<b>Base: </b>{}\n┖ {}\n\n" \
			+ "<b>Roof: </b>{}\n┖ {}\n\n" \
			+ "<b>Windows: </b>{}\n┖ {}\n\n" \
			+ "<b>Door: </b>{}\n┖ {}\n\n" \
			+ "<b>Floors: </b>{}\n┖ {}"
		],

		# TON Earth Houses
		'nft_info_6': [
			"\n<b>База: </b>{}\n┖ {}\n\n" \
			+ "<b>Крыша: </b>{}\n┖ {}\n\n" \
			+ "<b>Окна: </b>{}\n┖ {}\n\n" \
			+ "<b>Дверь: </b>{}\n┖ {}",

			"\n<b>Base: </b>{}\n┖ {}\n\n" \
			+ "<b>Roof: </b>{}\n┖ {}\n\n" \
			+ "<b>Windows: </b>{}\n┖ {}\n\n" \
			+ "<b>Door: </b>{}\n┖ {}"
		],

		# GBOTS
		'nft_info_7': [
			"\n<b>Тип элементов: </b>{}\n┖ {}\n\n" \
			+ "<b>Голова: </b>{}\n┖ {}\n\n" \
			+ "<b>Глаза: </b>{}\n┖ {}\n\n" \
			+ "<b>Туловище: </b>{}\n┖ {}\n\n" \
			+ "<b>Внутренний тип тела: </b>{}\n┖ {}\n\n" \
			+ "<b>Внешний тип тела: </b>{}\n┖ {}\n\n" \
			+ "<b>Верх рук: </b>{}\n┖ {}\n\n" \
			+ "<b>Низ рук: </b>{}\n┖ {}\n\n" \
			+ "<b>Верх ног: </b>{}\n┖ {}\n\n" \
			+ "<b>Низ ног: </b>{}\n┖ {}\n\n" \
			+ "<b>Броня: </b>{}\n┖ {}\n\n" \
			+ "<b>Цвета: </b>{}\n┖ {}",

			"\n<b>Elements Type: </b>{}\n┖ {}\n\n" \
			+ "<b>Head: </b>{}\n┖ {}\n\n" \
			+ "<b>Eyes: </b>{}\n┖ {}\n\n" \
			+ "<b>Torso: </b>{}\n┖ {}\n\n" \
			+ "<b>Inner Body Type: </b>{}\n┖ {}\n\n" \
			+ "<b>Outer Body Type: </b>{}\n┖ {}\n\n" \
			+ "<b>Arms Top: </b>{}\n┖ {}\n\n" \
			+ "<b>Arms Bottom: </b>{}\n┖ {}\n\n" \
			+ "<b>Legs Top: </b>{}\n┖ {}\n\n" \
			+ "<b>Legs Bottom: </b>{}\n┖ {}\n\n" \
			+ "<b>Armor Set: </b>{}\n┖ {}\n\n" \
			+ "<b>Colors: </b>{}\n┖ {}"
		],

		# Punks
		'nft_info_9': [
			"\n<b>Тип: </b>{}\n┖ {}\n\n" \
			+ "<b>Фон: </b>{}\n┖ {}\n\n" \
			+ "<b>Владелец: </b>{}\n┖ {}\n\n" \
			+ "<b>Количество атрибутов: </b>{}\n┖ {}\n\n" \
			+ "<b>Аттрибут 1: </b>{}\n┖ {}\n\n" \
			+ "<b>Аттрибут 2: </b>{}\n┖ {}\n\n" \
			+ "<b>Аттрибут 3: </b>{}\n┖ {}\n\n" \
			+ "<b>Аттрибут 4: </b>{}\n┖ {}\n\n" \
			+ "<b>Аттрибут 5: </b>{}\n┖ {}\n\n" \
			+ "<b>Аттрибут 6: </b>{}\n┖ {}\n\n" \
			+ "<b>Аттрибут 7: </b>{}\n┖ {}",

			"\n<b>Type: </b>{}\n┖ {}\n\n" \
			+ "<b>Background: </b>{}\n┖ {}\n\n" \
			+ "<b>Owner: </b>{}\n┖ {}\n\n" \
			+ "<b>Attributes count: </b>{}\n┖ {}\n\n" \
			+ "<b>Attribute 1: </b>{}\n┖ {}\n\n" \
			+ "<b>Attribute 2: </b>{}\n┖ {}\n\n" \
			+ "<b>Attribute 3: </b>{}\n┖ {}\n\n" \
			+ "<b>Attribute 4: </b>{}\n┖ {}\n\n" \
			+ "<b>Attribute 5: </b>{}\n┖ {}\n\n" \
			+ "<b>Attribute 6: </b>{}\n┖ {}\n\n" \
			+ "<b>Attribute 7: </b>{}\n┖ {}"
		],


		# Deversee
		'nft_info_8': [
			"\n<b>Город: </b>{}\n┖ {}\n\n" \
			+ "<b>Размер: </b>{}\n┖ {}\n\n"
			+ "<b>Вода: </b>{}\n┖ {}"
			,
			"\n<b>City: </b>{}\n┖ {}\n\n" \
			+ "<b>Size: </b>{}\n┖ {}\n\n"
			+ "<b>Water: </b>{}\n┖ {}"
		],

		# RichCats Glasses
		'nft_info_10': [
			"\n<b>Тип: </b>{}\n┖ {}" ,

			"\n<b>Type: </b>{}\n┖ {}"
		],
		# RichCats Hair
		'nft_info_11': [
			"\n<b>Тип: </b>{}\n┖ {}",

			"\n<b>Type: </b>{}\n┖ {}"
		],

		# RichCats Piercing
		'nft_info_12': [
			"\n<b>Тип: </b>{}\n┖ {}",

			"\n<b>Type: </b>{}\n┖ {}"
		],

		# RichCats Outfits
		'nft_info_13': [
			"\n<b>Тип: </b>{}\n┖ {}",

			"\n<b>Type: </b>{}\n┖ {}"
		],

		# Diamonds
		'nft_info_14': [
			"\n<b>Размер: </b>{}\n┖ {}\n\n" \
			+ "<b>Цвет: </b>{}\n┖ {}\n\n" \
			+ "<b>Форма: </b>{}\n┖ {}\n\n" \
			+ "<b>Фон: </b>{}\n┖ {}\n\n" \
			+ "<b>Огранка: </b>{}\n┖ {}\n\n" \
			+ "<b>Отблеск: </b>{}\n┖ {}\n\n" \
			+ "<b>Сияние: </b>{}\n┖ {}",

			"\n<b>Size: </b>{}\n┖ {}\n\n" \
			+ "<b>Color: </b>{}\n┖ {}\n\n" \
			+ "<b>Shape: </b>{}\n┖ {}\n\n" \
			+ "<b>Backgroup: </b>{}\n┖ {}\n\n" \
			+ "<b>Cut: </b>{}\n┖ {}\n\n" \
			+ "<b>Glow: </b>{}\n┖ {}\n\n" \
			+ "<b>Shine: </b>{}\n┖ {}\n\n" \
			+ "<b>Shine: </b>{}\n┖ {}"
		],


		# Doodles
		'nft_info_16': [
			"\n<b>Бриллиант: </b>{}\n┖ {}\n\n" \
			+ "<b>Волосы: </b>{}\n┖ {}\n\n" \
			+ "<b>Глаза: </b>{}\n┖ {}\n\n" \
			+ "<b>Уши: </b>{}\n┖ {}\n\n" \
			+ "<b>Рот: </b>{}\n┖ {}\n\n" \
			+ "<b>Одежда: </b>{}\n┖ {}\n\n" \
			+ "<b>Фон: </b>{}\n┖ {}",

			"\n<b>Diamond: </b>{}\n┖ {}\n\n" \
			+ "<b>Hair: </b>{}\n┖ {}\n\n" \
			+ "<b>Eyes: </b>{}\n┖ {}\n\n" \
			+ "<b>Ears: </b>{}\n┖ {}\n\n" \
			+ "<b>Mouth: </b>{}\n┖ {}\n\n" \
			+ "<b>Clothes: </b>{}\n┖ {}\n\n" \
			+ "<b>Background: </b>{}\n┖ {}"
		],

		# Dark Doodles
		'nft_info_17': [
			"\n<b>Статус: </b>{}\n┖ {}\n\n" \
			+ "<b>Голова: </b>{}\n┖ {}\n\n" \
			+ "<b>Глаза: </b>{}\n┖ {}\n\n" \
			+ "<b>Уши: </b>{}\n┖ {}\n\n" \
			+ "<b>Рот: </b>{}\n┖ {}\n\n" \
			+ "<b>Одежда: </b>{}\n┖ {}\n\n" \
			+ "<b>Фон: </b>{}\n┖ {}",

			"\n<b>Status: </b>{}\n┖ {}\n\n" \
			+ "<b>Head: </b>{}\n┖ {}\n\n" \
			+ "<b>Eyes: </b>{}\n┖ {}\n\n" \
			+ "<b>Ears: </b>{}\n┖ {}\n\n" \
			+ "<b>Mouth: </b>{}\n┖ {}\n\n" \
			+ "<b>Clothes: </b>{}\n┖ {}\n\n" \
			+ "<b>Background: </b>{}\n┖ {}"
		],

		# TON Ducks
		'nft_info_18': [
			"\n<b>Кожа: </b>{}\n┖ {}\n\n" \
			+ "<b>Глаза: </b>{}\n┖ {}\n\n" \
			+ "<b>Шляпа: </b>{}\n┖ {}\n\n" \
			+ "<b>Бриллиант: </b>{}\n┖ {}\n\n" \
			+ "<b>Курение: </b>{}\n┖ {}\n\n" \
			+ "<b>Фон: </b>{}\n┖ {}",

			"\n<b>Skin: </b>{}\n┖ {}\n\n" \
			+ "<b>Eyes: </b>{}\n┖ {}\n\n" \
			+ "<b>Hat: </b>{}\n┖ {}\n\n" \
			+ "<b>Diamond: </b>{}\n┖ {}\n\n" \
			+ "<b>Smoking: </b>{}\n┖ {}\n\n" \
			+ "<b>Background: </b>{}\n┖ {}"
		],

		# Chuwee Boys
		'nft_info_20': [
			"\n<b>Редкость: </b>{}\n┖ {}\n\n" \
			+ "<b>Класс: </b>{}\n┖ {}\n\n" \
			+ "<b>Голова: </b>{}\n┖ {}\n\n" \
			+ "<b>Цвет кожи: </b>{}\n┖ {}\n\n" \
			+ "<b>Волосы на лице: </b>{}\n┖ {}\n\n" \
			+ "<b>Рисунок на коже: </b>{}\n┖ {}\n\n" \
			+ "<b>Аксессуар: </b>{}\n┖ {}",

			"\n<b>Class: </b>{}\n┖ {}\n\n" \
			+ "<b>Grade: </b>{}\n┖ {}\n\n" \
			+ "<b>Head: </b>{}\n┖ {}\n\n" \
			+ "<b>Skin Color: </b>{}\n┖ {}\n\n" \
			+ "<b>Facial Hair: </b>{}\n┖ {}\n\n" \
			+ "<b>Skin Painting: </b>{}\n┖ {}\n\n" \
			+ "<b>Accessory: </b>{}\n┖ {}"
		],

		# BBT
		'nft_info_21': [
			"\n<b>Категория: </b>{}\n┖ {}\n\n" \
			+ "<b>Коллаборация: </b>{}\n┖ {}",

			"\n<b>Category: </b>{}\n┖ {}\n\n" \
			+ "<b>Collaboration: </b>{}\n┖ {}"
		],
		# TAC
		'nft_info_22': [
			"\n<b>Тело: </b>{}\n┖ {}\n\n" \
			+ "<b>Глаза: </b>{}\n┖ {}\n\n" \
			+ "<b>Рот: </b>{}\n┖ {}\n\n" \
			+ "<b>Правое ухо: </b>{}\n┖ {}\n\n" \
			+ "<b>Левое ухо: </b>{}\n┖ {}\n\n" \
			+ "<b>Одежда: </b>{}\n┖ {}\n\n" \
			+ "<b>Шляпа: </b>{}\n┖ {}\n\n" \
			+ "<b>Бриллиант: </b>{}\n┖ {}\n\n" \
			+ "<b>Аксессуар 1 (ногти): </b>{}\n┖ {}\n\n" \
			+ "<b>Аксессуар 2 (рука): </b>{}\n┖ {}\n\n" \
			+ "<b>Аксессуар 3 (кольца): </b>{}\n┖ {}\n\n" \
			+ "<b>Фон: </b>{}\n┖ {}",

			"\n<b>Body: </b>{}\n┖ {}\n\n" \
			+ "<b>Eyes: </b>{}\n┖ {}\n\n" \
			+ "<b>Mouth: </b>{}\n┖ {}\n\n" \
			+ "<b>Ear right: </b>{}\n┖ {}\n\n" \
			+ "<b>Ear left: </b>{}\n┖ {}\n\n" \
			+ "<b>Dress: </b>{}\n┖ {}\n\n" \
			+ "<b>Hat: </b>{}\n┖ {}\n\n" \
			+ "<b>Diamond: </b>{}\n┖ {}\n\n" \
			+ "<b>Accessory 1 (nails): </b>{}\n┖ {}\n\n" \
			+ "<b>Accessory 2 (hand): </b>{}\n┖ {}\n\n" \
			+ "<b>Accessory 3 (rings): </b>{}\n┖ {}\n\n" \
			+ "<b>Background: </b>{}\n┖ {}"
		],

		# TON Frogs
		'nft_info_23': [
			"\n<b>Статус: </b>{}\n┖ {}",

			"\n<b>Status: </b>{}\n┖ {}"
		],
		# Dolphy Money Team
		'nft_info_24': [
			"\n<b>Статус: </b>{}\n┖ {}",

			"\n<b>Status: </b>{}\n┖ {}"
		],
		# Bombasters
		'nft_info_25': [
			"\n<b>Тело: </b>{}\n┖ {}\n\n" \
			+ "<b>Элемент: </b>{}\n┖ {}\n\n" \
			+ "<b>Лицо: </b>{}\n┖ {}\n\n" \
			+ "<b>Фитиль: </b>{}\n┖ {}\n\n" \
			+ "<b>Обувь: </b>{}\n┖ {}\n\n" \
			+ "<b>Предмет: </b>{}\n┖ {}\n\n" \
			+ "<b>Бриллиант: </b>{}\n┖ {}\n\n" \
			+ "<b>Фон: </b>{}\n┖ {}",

			"\n<b>Body: </b>{}\n┖ {}\n\n" \
			+ "<b>Element: </b>{}\n┖ {}\n\n" \
			+ "<b>Face: </b>{}\n┖ {}\n\n" \
			+ "<b>Wick: </b>{}\n┖ {}\n\n" \
			+ "<b>Shoes: </b>{}\n┖ {}\n\n" \
			+ "<b>Main element: </b>{}\n┖ {}\n\n" \
			+ "<b>Gem: </b>{}\n┖ {}\n\n" \
			+ "<b>Background: </b>{}\n┖ {}"
		],

		# TON Mason
		'nft_info_26': [
			"\n<b>Лого: </b>{}\n┖ {}\n\n" \
			+ "<b>Материал: </b>{}\n┖ {}\n\n" \
			+ "<b>Украшения: </b>{}\n┖ {}\n\n" \
			+ "<b>Заполнение: </b>{}\n┖ {}\n\n" \
			+ "<b>Орнамент: </b>{}\n┖ {}\n\n" \
			+ "<b>Фон: </b>{}\n┖ {}",

			"\n<b>Logo: </b>{}\n┖ {}\n\n" \
			+ "<b>Material: </b>{}\n┖ {}\n\n" \
			+ "<b>Gems: </b>{}\n┖ {}\n\n" \
			+ "<b>Filling: </b>{}\n┖ {}\n\n" \
			+ "<b>Ornament: </b>{}\n┖ {}\n\n" \
			+ "<b>Background: </b>{}\n┖ {}"
		],

		# Web3TON
		'nft_info_27': [
			"\n<b>Категория: </b>{}\n┖ {}\n\n" \
			+ "<b>Пол: </b>{}\n┖ {}\n\n" \
			+ "<b>Раса: </b>{}\n┖ {}\n\n" \
			+ "<b>Уровень: </b>{}\n┖ {}",

			"\n<b>Category: </b>{}\n┖ {}\n\n" \
			+ "<b>Gender: </b>{}\n┖ {}\n\n" \
			+ "<b>Race: </b>{}\n┖ {}\n\n" \
			+ "<b>Level: </b>{}\n┖ {}"
		],

		# Фантон
		'nft_info_28': [
			"\n<b>Тир: </b>{}\n┖ {}\n\n" \
			+ "<b>Редкость: </b>{}\n┖ {}",

			"\n<b>Tier: </b>{}\n┖ {}\n\n" \
			+ "<b>Rarity: </b>{}\n┖ {}"
		],


		# Круги на Полях
		'nft_info_29': [
			"\n<b>Статус: </b>{}\n┖ {}\n\n" \
			+ "<b>Цвет: </b>{}\n┖ {}\n\n" \
			+ "<b>Видео: </b>{}\n┖ {}\n\n" \
			+ "<b>Персона: </b>{}\n┖ {}",

			"\n<b>Status: </b>{}\n┖ {}\n\n" \
			+ "<b>Color: </b>{}\n┖ {}\n\n" \
			+ "<b>Video: </b>{}\n┖ {}\n\n" \
			+ "<b>Person: </b>{}\n┖ {}"
		],



		'msg_owner_auctions_rules_1': [
			"Пользователи бота, создавая новый аукцион, автоматически соглашаются с <a href='https://telegra.ph/Pravila-ispolzovaniya-bota-arl-auction-bot-06-28'>правилами проведения аукционов</a>. Ты подтвержаешь, что прочитал правила и согласен с ними?",
			"When user creates new auction he confirm that he agree with <a href='https://telegra.ph/Rules-for-using-the-arl-auction-bot-07-12'>auction rules</a>. Do you confirm that you read the rules and agree with them?"],

		'msg_participant_auctions_rules_1': [
			"Пользователи бота, участвуя в аукционе, автоматически соглашаются с <a href='https://telegra.ph/Pravila-ispolzovaniya-bota-arl-auction-bot-06-28'>правилами проведения аукционов</a>. Ты подтвержаешь, что прочитал правила и согласен с ними?",
			"When user participates in the auction he confirm that he agree with <a href='https://telegra.ph/Rules-for-using-the-arl-auction-bot-07-12'>auction rules</a>. Do you confirm that you read the rules and agree with them?"],

		'msg_owner_auctions_rules_2': [
			"Пользователи бота, создавая новый аукцион, автоматически соглашаются с <a href='https://telegra.ph/Pravila-ispolzovaniya-bota-monkeys-guarantor-bot-07-18'>правилами проведения аукционов</a>. Ты подтвержаешь, что прочитал правила и согласен с ними?",
			"When user creates new auction he confirm that he agree with <a href='https://telegra.ph/Rules-for-using-the-monkeys-guarantor-bot-07-18'>auction rules</a>. Do you confirm that you read the rules and agree with them?"],

		'msg_participant_auctions_rules_2': [
			"Пользователи бота, участвуя в аукционе, автоматически соглашаются с <a href='https://telegra.ph/Pravila-ispolzovaniya-bota-monkeys-guarantor-bot-07-18'>правилами проведения аукционов</a>. Ты подтвержаешь, что прочитал правила и согласен с ними?",
			"When user participates in the auction he confirm that he agree with <a href='https://telegra.ph/Rules-for-using-the-monkeys-guarantor-bot-07-18'>auction rules</a>. Do you confirm that you read the rules and agree with them?"],

		'msg_about_transfer_1': [
			"Продажа NFT из коллекции " \
			 + "<a href='https://explorer.tonnft.tools/collection/EQAA1yvDaDwEK5vHGOXRdtS2MbOVd1-TNy01L1S_t2HF4oLu'>Animals Red List</a> " \
			 + "через бота-гаранта позволяет <b>повысить безопасность</b> совершаемых сделок. \n\n" \
			 + "<b>Схема сделки:</b>\n1. Владелец NFT создаёт новую сделку, назначает цену и приглашает покупателя.\n2. Покупатель переводит сумму сделки на <a href='https://tonscan.org/address/{}'>кошелёк бота-гаранта</a>.\n" \
			 + "3. Владелец переводит NFT на кошелёк покупателя.\n4. Бот-гарант переводит сумму сделки на кошелёк инициатора сделки.\n\n" \
			 + "Если владелец не перевёл NFT в течение 1 часа, сделка отменяется и бот автоматически возвращает сумму сделки на кошелёк покупателя.\n\n" \
			 + "Для покрытия транзакционных расходов бота взимается комиссия <b>{} TON</b>.",

			 "Sale NFT from collection " \
			 + "<a href='https://explorer.tonnft.tools/collection/EQAA1yvDaDwEK5vHGOXRdtS2MbOVd1-TNy01L1S_t2HF4oLu'>Animals Red List</a> " \
			 + "via the guarantor bot helps <b>to increase safety</b> of deals.\n\n" \
			 + "<b>Schema of the deal:</b>\n1. The owner of the NFT creates a new deal, sets a price and invites a buyer.\n2. The buyer transfers deal amount to <a href='https://tonscan.org/address/{}'>the guarantor bot's wallet</a>.\n" \
			 + "3. The owner transfers NFT to the buyer's wallet.\n4. The guarant bot transfers deal amount to the wallet of the deal initiator.\n\n" \
			 + " If the owner does not transfer NFT within 1 hour, the deal is canceled and the bot automatically returns deal amount to the buyer's wallet.\n\n" \
			 + "To cover the network fee, a commission of <b>{} TON</b> is charged."
		],

		'msg_about_transfer_2': [
			"P2P продажа NFT через бота-гаранта позволяет <b>повысить безопасность</b> совершаемых сделок. \n\n" \
			+ "<b>Схема сделки:</b>\n1. Владелец NFT создаёт новую сделку, назначает цену и приглашает покупателя.\n2. Покупатель переводит сумму сделки на <a href='https://tonscan.org/address/{}'>кошелёк бота-гаранта</a>.\n" \
			+ "3. Владелец переводит NFT на кошелёк покупателя.\n4. Бот-гарант переводит сумму сделки на кошелёк инициатора сделки.\n\n" \
			+ "Если владелец не перевёл NFT в течение 1 часа, сделка отменяется и бот автоматически возвращает сумму сделки на кошелёк покупателя."
			,

			"P2P sale NFT via the guarantor bot helps <b>to increase safety</b> of deals.\n\n" \
			+ "<b>Schema of the deal:</b>\n1. The owner of the NFT creates a new deal, sets a price and invites a buyer.\n2. The buyer transfers deal amount to <a href='https://tonscan.org/address/{}'>the guarantor bot's wallet</a>.\n" \
			+ "3. The owner transfers NFT to the buyer's wallet.\n4. The guarant bot transfers deal amount to the wallet of the deal initiator.\n\n" \
			+ " If the owner does not transfer NFT within 1 hour, the deal is canceled and the bot automatically returns deal amount to the buyer's wallet."

		],

		'msg_main_menu': ["Выбери пункт меню:", "Select option from menu:"],
		'msg_help_menu_1': [
			"В случае возникновения неполадок или предложений по развитию бота обращайся по адресу @dkor2022.\n\n" \
			+ "Рекомендую также прочитать инструкцию вот по этой <a href='https://telegra.ph/Telegram-bot-ARL-NFT-auctions-bot-06-20'>ссылке</a>.\n\n" \
			+ "Если тебе понравился бот, ты можешь порадовать разработчика <b>донатом на кофе и булочку</b> 😉 - {}\n\n" \
			+ "<a href='https://app.tonkeeper.com/transfer/{}'>💎TON Keeper</a> | "
			+ "<a href='https://tonhub.com/transfer/{}'>💰TON Hub</a> | "
			+ "<a href='{}'>💸CryptoBot</a>\n\n" \
			+ "__________________________________\n",

			"For support or for any suggestions please contact @dkor2022.\n\n" \
			#+ "It's strongly recommended to read <a href='https://telegra.ph/'>manual</a>.\n\n" \
			+ "If you liked this bot you can please the developer by making <b>a donation for coffee and a donut</b> 😉 - {}\n\n" \
			+ "<a href='https://app.tonkeeper.com/transfer/{}'>💎TON Keeper</a> | "
			+ "<a href='https://tonhub.com/transfer/{}'>💰TON Hub</a> | "
			+ "<a href='{}'>💸CryptoBot</a>\n\n" \
			+ "__________________________________\n"
		],

		'msg_help_menu_2': [
			"В случае возникновения неполадок или предложений по развитию бота обращайся по адресу @dkor2022.\n\n" \
			+ "Если тебе понравился бот, ты можешь порадовать разработчика <b>донатом на кофе и булочку</b> 😉 - {}\n\n" \
			+ "<a href='https://app.tonkeeper.com/transfer/{}'>💎TON Keeper</a> | "
			+ "<a href='https://tonhub.com/transfer/{}'>💰TON Hub</a> | "
			+ "<a href='{}'>💸CryptoBot</a>\n\n" \
			+ "__________________________________\n",

			"For support or for any suggestions please contact @dkor2022.\n\n" \
			+ "If you liked this bot you can please the developer by making <b>a donation for coffee and a donut</b> 😉 - {}\n\n" \
			+ "<a href='https://app.tonkeeper.com/transfer/{}'>💎TON Keeper</a> | "
			+ "<a href='https://tonhub.com/transfer/{}'>💰TON Hub</a> | "
			+ "<a href='{}'>💸CryptoBot</a>\n\n" \
			+ "__________________________________\n"
		],

		'msg_auction_menu': ['Выбери пункт меню:', 'Select menu option:'],

		'msg_input_wallet': ["Введи свой TON-кошелёк (текущий известный кошелёк {}):",
							 'Please input your TON wallet (current known wallet is {}):'],
		'msg_input_collection': ["Выбери NFT коллекцию:", "Please select NFT collection:"],
		'msg_input_nft': ["Введи адрес или название NFT:", 'Please input NFT address or name:'],
		'msg_input_nft_check': ["Бот позволяет найти информацию об NFT из коллекций, перечисленных <a href='https://telegra.ph/Pravila-ispolzovaniya-bota-monkeys-guarantor-bot-07-18'>на этой странице</a>.\n\n" \
			+ "<b>Введи адрес NFT</b> (в формате EQAy1zPQ5e66T0lClaTOgHgKbojDC6aG0lMPMHLsRa2xhwSE):",
								"The bot can find info about NFT from the collections that listed <a href='https://telegra.ph/Rules-for-using-the-monkeys-guarantor-bot-07-18'>on this page</a>.\n\n" \
			+ "<b>Please input NFT address</b> (like EQAy1zPQ5e66T0lClaTOgHgKbojDC6aG0lMPMHLsRa2xhwSE):"],
		'msg_input_start_price': ["Введи стартовую цену лота (💎):", 'Please input start price (💎):'],
		'msg_input_price_step': ["Введи шаг ставок (💎):", 'Please input price step (💎):'],
		'msg_input_duration_type': ["Выбери вариант длительности аукциона:", "Please select option to set auction duration:"],
		'msg_input_fix_end_time': [
			"Введи фиксированное время окончания аукциона (MSK) в формате ДД.MM.ГГ ЧЧ24:00. Минимальное время окончания - <b>{}</b>",
			"Please input fix end auction time (MSK) in format DD.MM.YY HH24:00. Minimal end datetime is <b>{}</b>"],
		'msg_input_comment': ["Введи комментарий к аукциону (до 150 символов):", 'Please input comment for auction (up to 150 symbols):'],


		'msg_wallet_incorrect': ['Это некорректный кошелёк TON! Попробуй ввести другой.', 'This TON wallet is incorrect! Please try another one.'],
		'msg_nft_incorrect': ['NFT с таким адресом или названием нет в данной коллекции! Попробуй ввести другой.',
								 'There is no NFT with address or name like this. Pleasy try another one.'],

		'msg_nft_format_incorrect': ['Неверный формат адреса NFT! Попробуй ввести другой, похожий на этот - EQAy1zPQ5e66T0lClaTOgHgKbojDC6aG0lMPMHLsRa2xhwSE:',
							  'This is incorrect NT address format! Please try another one like this - EQAy1zPQ5e66T0lClaTOgHgKbojDC6aG0lMPMHLsRa2xhwSE:'],

		'msg_nft_address_not_found': ['NFT с таким адресом не найден в проверенных коллекциях бота! Попробуй ввести другой:',
			'This is not NFT with such address in verified collections. Please try another one:'],

		'msg_start_price_incorrect':['Введено некорректное значение цены. Попробуй ввести другое.',
									'There is incorrect price value. Please try another one.'],
		'msg_price_step_incorrect': ['Введено некорректное значение шага цены. Попробуй ввести другое.',
									  'There is incorrect price step value. Please try another one.'],
		'msg_user_blacklist': ["Ранее ты был добавлен в чёрный список как <b>недобросовестный участник</b>{}. Мы не рады таким людям в нашем сообществе!🤬",
			"Earlier you was added to blacklist as a <b>unreliable user</b>{}! We don't like such people in our community!🤬"],

		'msg_user_no_username': [
			"Для успешного взаимодействия все участники должны иметь корректно заполненный username в Telegram (больше 3 символов). Заполни и попробуй ещё раз.",
			"You must have correct Telegram login (more than 3 symbols) for successfull comunication with other participants. Please fill your login and try again."],

		'msg_wallet_blacklist': ['Этот кошелёк использовался ранее <b>недобросовестным участником</b>🤬! Попробуй ввести другой.',
								 'This TON wallet was used by <b>unreliable user</b>🤬! Pleasy try another one.'],
		'msg_nft_blacklist': ['Этот NFT внесён в чёрный список из-за <b>недобросовестного участника</b>{}🤬! Попробуй ввести другой.',
			'This NFT is in blacklist because of <b>unreliable user</b>{}🤬! Pleasy try another one.'],
		'msg_nft_another_auction': [
			'Этот NFT сейчас участвует в незакрытом аукционе! Попробуй ввести другой.',
			'This NFT is in unfinished auction! Please try another one.'],

		'msg_nft_api_error': ['Ошибка при проверке владельца данного NFT через API. Пожалуйста, попробуй позже.',
			'Owner check API is unavailable. Please try later.'],
		'msg_nft_wrong_owner': ['По данным в блокчейне, этот NFT принадлежит <b>другому владельцу</b>. Ты должен снять его с продажи на всех маркетах перед отправкой на аукцион или P2P сделкой через гаранта. Попробуй ещё раз:',
			'According to blockchain info this NFT has <b>another owner</b>. You must cancel any sales on other marketplaces before using on auction or P2P deal via guarantor. Try again:'],

		'msg_incorrect_endtime_format': ["Введён неверный формат даты! Попробуй ещё раз.", "This is incorrect date format! Please try again."],
		'msg_short_duration': ["Указанные дата/время окончания ({}) меньше минимально допустимого! Минимальное время окончания (GMT+3) аукциона - <b>{}</b>. Попробуй ещё раз.",
										 "Entered end time ({}) is less than limit! Minimal end time (GMT+3) of auction is <b>{}</b>. Please try again."],
		'msg_long_duration': [
			"Длительность аукциона не может превышать 3 дня (<b>{}</b>). Попробуй ещё раз.",
			"The duration of an auction cannot be more than 3 days (<b>{}</b>). Please try again."],

		'msg_confirm_new_auction': ["Ты подтверждаешь, что указанная выше информация корректна?",
			"Do you confirm that information above is correct?"],

		'msg_confirm_auction_info':["<b>Стартовая цена: </b>{}💎\n"\
			+ "<b>Шаг цены: </b>{}💎\n<b>Время окончания (GMT+3): </b>{}\n\n"\
			+ "<b>Владелец: </b>{}\n<b>ID владельца: </b>{}\n<b>Кошелёк владельца: </b>{}\n<b>Комментарий: </b>{}",
									"<b>Start price: </b>{}💎\n"\
			+ "<b>Price step: </b>{}💎\n<b>End datetime (GMT+3): </b>{}\n\n"\
			+ "<b>Owner: </b>{}\n<b>Owner ID: </b>{}\n<b>Owner wallet: </b>{}\n<b>Comment: </b>{}"],

		'msg_new_auction_success': ["Новый аукцион создан успешно! ID={}", "New auction has been created successfully! ID={}"],

		'msg_my_auctions_info': ["<b>🔨Аукцион №</b>{}\n<b>Лот: </b>{}\n<b>Период: </b>{} - {}\n<b>Стартовая цена: </b>{}💎\n" \
            + "<b>Участники: </b>{}\n<b>Ставка лидера: </b>{}\n<b>Статус: </b>{}\n",
			 "<b>🔨Auction №</b>{}\n<b>Lot: </b>{}\n<b>Period: </b>{} - {}\n<b>Start price: </b>{}💎\n" \
			 + "<b>Participants: </b>{}\n<b>Leader's bid: </b>{}\n<b>Status: </b>{}\n"],

		'msg_active_auctions_info': [
			"<b>🔨Аукцион №</b>{}\n<b>Лот: </b>{} ({})\n<b>Окончание: </b>{}\n<b>Стартовая цена: </b>{}💎 (шаг +{})\n<b>Ставка лидера: </b>{}\n<b>Участники: </b>{}",
			"<b>🔨Auction №</b>{}\n<b>Lot: </b>{} ({})\n<b>Finish: </b>{}\n<b>Start price: </b>{}💎 (step +{})\n<b>Leader's bid: </b>{}\n<b>Participants: </b>{}"],

		'msg_auction_full_info': [
			"<b>🔨Аукцион №</b>{}\n{}\n<b>Период: </b>{} - {}\n<b>Стартовая цена: </b>{}💎 (шаг +{})\n" \
			+ "<b>Ставка лидера: </b>{}\n" \
			+ "<b>Участники: </b>{}\n" \
			+"__________________________________\n"\
			+"<b>Доп.информация о лоте: </b>\n{}\n" \
			+ "__________________________________\n"
			+ "<b>Владелец: </b>{}\n<b>Кошелёк владельца: </b>{}\n<b>Статистика: </b>{}\n<b>Комментарий: </b>{}",

			"<b>🔨Auction №</b>{}\n{}\n<b>Period: </b>{} - {}\n<b>Start price: </b>{}💎 (step +{})\n" \
			+ "<b>Leader's bid: </b>{}\n" \
			+ "<b>Participants: </b>{}\n" \
			+ "__________________________________\n"
			+ "<b>Additional info about lot: </b>\n{}\n" \
			+ "__________________________________\n"
			+ "<b>Owner: </b>{}\n<b>Owner wallet: </b>{}\n<b>Statistics: </b>{}\n<b>Comment: </b>{}"
		],

		'msg_auction_short_info': [
			"<b>🔨Аукцион №</b>{} ({}) \n\n" \
			+ "<b>Владелец: </b>{}\n" \
			+ "<b>Кошелёк владельца: </b>{}\n\n" \
			+ "<b>Лидер: </b>{}\n" \
			+ "<b>Кошелёк лидера: </b>{}\n\n" \
			+ "<b>NFT: </b>{}\n\n" \
			+ "<b>Стартовая цена: </b>{}💎 (шаг +{})\n" \
			+ "<b>Ставка лидера: </b>{}\n" \
			+ "<b>Начало: </b>{}\n" \
			+ "<b>Окончание: </b>{}"
			,
			  "<b>🔨Auction №</b>{} ({}) \n\n" \
			+ "<b>Owner: </b>{}\n" \
			+ "<b>Owner's wallet: </b>{}\n\n" \
			+ "<b>Leader: </b>{}\n" \
			+ "<b>Leader's wallet: </b>{}\n\n" \
			+ "<b>NFT: </b>{}\n\n" \
			+ "<b>Start price: </b>{}💎 (step +{})\n" \
			+ "<b>Leader's bid: </b>{}\n" \
			+ "<b>Start: </b>{}\n" \
			+ "<b>End: </b>{}"

		],

		'msg_last_active_auctions': [
			"Ниже представлены TOP-3 самых свежих аукционов. Можно выбрать один из них или найти любой другой по его номеру.",
			"There are TOP-3 the most recent auctions below. You can choose one of them or you can find another by it's number."],


		'msg_no_auctions': ["Пока ты не организовал ни одного аукциона.\n","You have not created auctions yet.\n"],
		'msg_no_active_auctions': ["Подходящих для тебя аукционов не найдено.\n", "There is no auctions for you right now.\n"],
		'msg_no_participations': ["Ты не участвуешь ни в одном активном аукционе.\n",
								   "You are not participating in any active auctions right now.\n"],
		'msg_cancel_warning': ["Можно отменить только ограниченное число аукционов. Количество оставшихся у тебя отмен - <b>{}</b>. Ты подтверждаешь, отмену аукциона №<b>{}</b>?",
							   "Users can cancel auctions only limited times. You have only <b>{}</b> cancels. Do you confirm the cancellation of auction №<b>{}</b>?"],
		'msg_cancel_limit': ["Ты исчерпал свой лимит по отменам аукционов. Обратись в поддержку.",
							 "You are out of your cancellation limit. Please contact support."],

		'msg_input_auction_id':["Нажми на кнопку ниже или введи номер для открытия карточки аукциона:", "Press the button below or input number to open auction profile:"],
		'msg_auction_id_incorrect': ["Введено некорректное значение номера. Попробуй ещё раз.", "This is incorrect number value. Please try again."],
		'msg_auction_id_not_found': ["Аукцион с таким номером не найден. Попробуй другой.", "There is no auction with this number. Please try another one."],
		'msg_auction_id_not_active': ["Этот аукцион уже закончился. Попробуй другой.",
									 "This auction is not active. Please try another one."],
		'msg_auction_id_owner': ["Пользователи не могут участвовать в своих же аукционах. Попробуй другой.",
									 "Users cannot participate in their own auctions. Please try another one."],
		'msg_auction_id_participant': ["Ты уже участвуешь в данном аукционе. Попробуй другой.",
								 "You are participating in this auction already. Please try another one."],

		'msg_balance_not_enough': ["Не хватает баланса для участия в аукционе. Требуется <b>{}</b> TON, твой текущий баланс <b>{}</b> TON. Пополни кошелёк или используй другой.",
									   "You don't have enough money on your wallet. It's required <b>{}</b> TON and you have only <b>{}</b> TON. Please fill up your wallet or use another."],
		'msg_balance_not_enough2': [
			"Не хватает баланса для повышения ставки. Требуется <b>{}</b> TON, твой текущий баланс <b>{}</b> TON. Пополни кошелёк и попробуй снова.",
			"You don't have enough money on your wallet. It's required <b>{}</b> TON and you have only <b>{}</b> TON. Please fill up your wallet and try again."],

		'msg_owner': ["Ты являешься владельцем этого аукциона! Владельцы аукционов не могут участвовать в них.", "You are the owner of this auction! Owners can't participate in their own auctions."],
		'msg_leader': ["Ты являешься лидером данного аукциона! Не имеет смысла поднимать ставку ещё выше.","You are the leader of this auction! There is no need to raise the bid at this moment!"],

		'msg_confirm_raise1': ["Ты подтверждаешь, что хочешь поднять ставку на <b>{} TON</b>? Итоговая ставка составит <b>{} TON</b> " \
			+ "(твой текущий баланс - <b>{} TON</b>). Напоминаю, что участник аукциона не может отказаться от подтверждённой ставки, " \
			+ "а недобросовестные участники автоматически попадают в <b>чёрный список</b>.",
			"Do you confirm that you want to raise the bid on <b>{} TON</b>? The value of the bid will be <b>{} TON</b> " \
			+ "(your current balace in <b>{} TON</b>). I remind you that participant cannot refuse confirmed bid, " \
			+ "and all unscrupulous users will be automatically addred to <b>the black list</b>."],
		'msg_confirm_raise2': [
			"Ты подтверждаешь, что хочешь принять начальную ставку <b>{} TON</b> " \
			+ "(твой текущий баланс - <b>{} TON</b>)? Напоминаю, что участник аукциона не может отказаться от подтверждённой ставки, " \
			+ "а недобросовестные участники автоматически попадают в <b>чёрный список</b>.",
			"Do you confirm that you want to accept start bid <b>{} TON</b> " \
			+ "(your current balace in <b>{} TON</b>)? I remind you that participant cannot refuse confirmed bid, " \
			+ "and all unscrupulous users will be automatically addred to <b>the black list</b>."],

		'msg_auction_finished_owner1': ["Аукцион <b>№{}</b> завершён!🎉 \n\n<b>Победитель: </b>{}\n<b>Кошелёк: </b>{}\n<b>Ставка победителя: </b>{}💎.\n\n" \
			+ "Дождись информации от бота о том, что победитель перевёл сумму ставки на кошелёк бота (гаранта), после чего выполни перевод NFT на кошелёк победителя в течение 1 часа.",
			"Auction <b>№{}</b> has finished!🎉 \n\n<b>Winner: </b>{}\n<b>Wallet: </b>{}\n<b>Winner's bid: </b>{}💎.\n\n" \
		  	+ "Please wait message from bot that winner has paid amount to the bot's (guarantee's) wallet. After that you must transfer NFT to the winner's wallet during 1 hour.\n\n"],

		'msg_auction_finished_owner2': ["Аукцион <b>№{}</b> завершён без победителя.", "Auction <b>№{}</b> has finished without winner."],

		'msg_auction_finished_leader1': ["Аукцион <b>№{}</b> завершён и ты победил!🎉\n\n" \
			+ "<a href='{}'>Переведи</a> сумму <b>{} TON</b> на кошелёк бота-гаранта - {} ({} TON ставка + {} TON комиссия бота) " \
			+ "с <b>обязательным комментарием</b> {}.\n\n" \
			+ "<b>Внимание!</b> Если оплата не будет совершена в течение 1 часа, будут применены <b>административные меры</b>."
			,
			"Auction <b>№{}</b> has finished and you are the winner!🎉\n\n" \
			+ "Please <a href='{}'>transfer</a> <b>{} TON</b> to the guarantor bot's wallet - {} ({} TON the bid + {} TON the bot commission) " \
			+ "with <b>obligatory comment<b> {}.\n\n" \
			+ "<b>Attention!</b> If you not pay during 1 hour there will be <b>administrative punishment</b>."],

		'msg_nft_not_transfered': ["По данным блокчейна, NFT {} <b>не была передана</b> на нужный кошелёк!\n\nАдрес NFT - {}, кошелёк для перевода - {}.",
										"According blockchain data NFT {} <b>wasn't transfered</b> to the right wallet!\n\nNFT address is {}, the wallet for transfer is {}."],

		'msg_confirm_payment': ["Победитель аукциона №{} подтвердил, что он совершил платёж в размере {}💎. Подтверди получение средств на кошелёк бота (гаранта).",
			"The winner of auction №{} confirmed that the payment was done ({}💎). Confirm that you received payment on the bot's (guarantee's) wallet."],

		'msg_payment_confirmed': [
			"Платёж на кошелёк бота-гаранта <b>подтверждён</b>. Теперь владелец ({}) должен перевести NFT на твой кошелёк в течение 1 часа. Если этого не произошло, свяжись с техподдержкой - @dkor2022.",
			"The payment to the guarantor bot's wallet is <b>confirmed</b>. Now the owner ({}) must transfer the NFT to your wallet within 1 hour. If he will not do please contact support - @dkor2022."],

		'msg_nft_transfer_confirmed': [
			"Перевод NFT подтверждён, сделка успешно завершена. Если остались какие-то вопросы, свяжись с техподдержкой - @dkor2022.\n\n" \
			+ "Если тебе понравился бот, ты можешь порадовать разработчика донатом на кофе и булочку 😉 - {}\n\n" \
			+ "<a href='https://app.tonkeeper.com/transfer/{}'>💎TON Keeper</a> | "
			+ "<a href='https://tonhub.com/transfer/{}'>💰TON Hub</a> | "
			+ "<a href='{}'>💸CryptoBot</a>",
			"The NFT transfer is confirmed, the deal has finished successfully. If you have any questions please contact support - @dkor2022.\n\n"
			+ "If you liked this bot you can please the developer by making a donation for coffee and a donut 😉 - {}\n\n" \
			+ "<a href='https://app.tonkeeper.com/transfer/{}'>💎TON Keeper</a> | "
			+ "<a href='https://tonhub.com/transfer/{}'>💰TON Hub</a> | "
			+ "<a href='{}'>💸CryptoBot</a>"],

		'msg_blacklist_owner': ["Ты был внесён в чёрный список. Причина - не перевёл NFT победителю аукциона №{}.\nЕсли произошла ошибка, обратись в техподдержку.",
								"You was added to the blacklist. Reason - did not transfer NFT to the winner of auction №{}.\nIf there is mistake please contact support."],
		'msg_blacklist_leader': [
			"Ты был внесён в чёрный список. Причина - не оплатил ставку после победы в аукционе №{}.\nЕсли произошла ошибка, обратись в техподдержку.",
			"You was added to the blacklist. Reason - did not pay a bid after win in auction №{}.\nIf there is mistake please contact support."],

		'msg_wallet_not_verif': ["Кошелёк <b>не верифицирован</b>. Для верификации <a href='{}'>переведи</a> 0.01 TON на адрес {} с обязательным комментарием {}.",
			"The wallet <b> is not verified</b>. For verification <a href='{}'>send</a> 0.01 TON to wallet {} with comment {}."],

		'msg_wallet_verif_success': ["Кошелёк успешно <b>верифицирован</b>!", "The wallet was <b>verified</b> successfully!"],
		'msg_wallet_already_verif': ["Кошелёк был успешно <b>верифицирован</b> ранее. Больше ничего делать не нужно.",
									 "The wallet has been <b>verified</b> already. You don't need to do anything."],
		'msg_wallet_verif_unsuccess': ["Информация о транзации для верификации не найдена. Попробуй немного подождать и проверить снова.",
									   "Information about verification transaction was not found. Please wait a little bit and check again."],

		'msg_payment_unsuccess': [
			"Информация о платеже не найдена. Попробуй немного подождать и проверить снова.",
			"Information about payment transaction was not found. Please wait a little bit and check again."],

		'msg_transaction_check_api_err': [
			"Ошибка API при проверке транзакции. Попробуй немного подождать и проверить снова.",
			"API Error during transaction check. Please wait a little bit and check again."],

		'msg_transfer_after_payment': ["На кошелёк бота-гаранта была переведена необходимая сумма ({} TON). \n\nВ течение <b>1 часа</b> ты должен перевести NFT на кошелёк покупателя {}. Это можно сделать через сервис переводов, например, на <a href='{}'>Getgems</a>.\n\n" \
			+ "Внимание! Если перевод NFT не будет осуществлён вовремя, будут применены <b>административные меры</b>.",

			"The amount ({} TON) was transfered to the guatantor bot's wallet. \n\nDuring <b>1 hour</b> you must transfer NFT to the buyer's wallet - {}. You can do this via transfer service, for example <a href='{}'>Getgems</a>.\n\n" \
			+ "Attention! If you will not transfer NFT during this time there will be <b>administrative punishment.</b>"],

		'msg_wait_bot_payment': [
			"Сделка успешно завершена, платёж от бота-гаранта поступит в ближайшее время. Если этого не произошло, свяжись с техподдержкой - @dkor2022.\n\n" \
			+"Если тебе понравился бот, ты можешь порадовать разработчика донатом на кофе и булочку 😉 - {}\n\n" \
			+ "<a href='https://app.tonkeeper.com/transfer/{}'>💎TON Keeper</a> | "
			+ "<a href='https://tonhub.com/transfer/{}'>💰TON Hub</a> | "
			+ "<a href='{}'>💸CryptoBot</a>",

			"The deal has finished successfully. The payment from the guarantor bot will be done shortly. If it will not happen, please contact support - @dkor2022.\n\n" \
			+"If you liked this bot you can please the developer by making a donation for coffee and a donut 😉 - {}\n\n" \
			+ "<a href='https://app.tonkeeper.com/transfer/{}'>💎TON Keeper</a> | "
			+ "<a href='https://tonhub.com/transfer/{}'>💰TON Hub</a> | "
			+ "<a href='{}'>💸CryptoBot</a>"
		],

		'msg_airdrop_already': ["Ты уже участвуешь в розыгрыше TON. Для получения NFT активно участвуй в аукционах!",
								"You've already participated in the airdrop of TON. You can take a part in auctions and get free NFT!"],

		'msg_airdrop_input_wallet': ["❗<b>Для участия в розыгрыше</b>❗ введи свой TON-кошелёк (TON Keeper или TON Hub, в формате EQAxiQYJEm18naGei5BiaxclXZDFcbgR9Si-1PkgZZD9UBh1):",
								"❗<b>For participate in the airdrop</b>❗ input your TON wallet (TON Keeper или TON Hub, in the format like EQAxiQYJEm18naGei5BiaxclXZDFcbgR9Si-1PkgZZD9UBh1):"],

		'msg_airdrop_success_participate': [
			"Теперь ты участвуешь в розыгрыше TON. Для получения NFT активно участвуй в аукционах!",
			"Now you are participating in the airdrop of TON. You can take a part in auctions and get free NFT!"],

		'msg_input_deal_amount': ["Введи сумму сделки (в TON):", "Input deal amount (TON):"],
		'msg_deal_amount_out_of_limits': ["Сумма сделки должна лежать в диапазоне от 1 до {} TON. Введи корректную сумму:",
			"Deal amount must be between 1 and {} TON. Please input correct amount:"],

		'msg_start_price_out_of_limits': [
			"Стартовая цена должна лежать в диапазоне от 1 до {} TON. Введи корректную сумму:",
			"Start price must be between 1 and {} TON. Please input correct amount:"],

		'msg_deal_amount_incorrect': ['Введено некорректное значение суммы сделки. Попробуй ввести другое.',
									  'There is incorrect deal amount. Please try another one.'],

		'msg_input_buyer_login': ["Введи логин или User ID покупателя:", "Input buyer's login or user ID:"],
		'msg_buyer_not_find': ["Такой пользователь не найден в базе. Попроси покупателя зайти в бота и нажать команду /start, после чего попробуй снова.",
							   "There is not such user in database. Please ask him enter the bot and press /start, and try again after."],
		'msg_buyer_blacklist': [
			"Пользователь внесён <b>в чёрный список</b> как неблагонадёжный участник. Попробуй выбрать другого.",
			"The user is <b>in blacklist</b> as unreliable participant. Please try another one."],

		'msg_wait_buyer_answer': [
			"Предложение по сделке №{} отправлено покупателю - {}. Дождись его ответа.",
			"The deal №{} info was sent to buyer - {}. Please wait for his answer."],

		'msg_buyer_cancel_transfer': ["Покупатель {} отказался от сделки №{}.",
									  "The buyer {} has cancelled the deal №{}."],

		'msg_buyer_confirm_transfer': ["Покупатель {} подтвердил участие в сделке №{}. Жди его дальнейших действий.",
									  "The buyer {} has confirmed the deal №{}. Wait for his further actions."],

		'msg_new_transfer_info': [
			"<b>🤝№{}</b>\n\n" \
			+ "<b>Владелец: </b>{}\n" \
			+ "<b>Кошелёк владельца: </b>{}\n" \
			+ "<b>Покупатель: </b>{}\n" \
			+ "<b>NFT: </b>{}\n" \
			+ "<b>Сумма сделки: </b>{}💎\n" \
			+ "<b>Комиссия бота: </b>{}💎",

			"<b>🤝№{}</b>\n\n" \
			+ "<b>Owner: </b>{}\n" \
			+ "<b>Owner's wallet: </b>{}\n" \
			+ "<b>Buyer: </b>{}\n" \
			+ "<b>NFT: </b>{}\n" \
			+ "<b>Amount: </b>{}💎\n" \
			+ "<b>Bot commission: </b>{}💎"	],

		'msg_transfer_full_info': [
			"<b>🤝№{}</b> ({})\n\n" \
			+ "<b>Владелец: </b>{}\n" \
			+ "<b>Кошелёк владельца: </b>{}\n\n" \
			+ "<b>Покупатель: </b>{}\n" \
			+ "<b>Кошелёк покупателя: </b>{}\n\n" \
			+ "<b>NFT: </b>{}\n" \
			+ "<b>Сумма сделки: </b>{}💎\n" \
			+ "<b>Комиссия бота: </b>{}💎\n" \
			+ "<b>Начало: </b>{}\n" \
			+ "<b>Окончание: </b>{}"
			,

			"<b>🤝№{}</b> ({})\n\n" \
			+ "<b>Owner: </b>{}\n" \
			+ "<b>Owner's wallet: </b>{}\n\n" \
			+ "<b>Buyer: </b>{}\n" \
			+ "<b>Buyer's wallet: </b>{}\n\n" \
			+ "<b>NFT: </b>{}\n" \
			+ "<b>Amount: </b>{}💎\n" \
			+ "<b>Bot commission: </b>{}💎" \
			+ "<b>Start: </b>{}" \
			+ "<b>End: </b>{}"
		],

		'msg_owner_confirm_new_transfer': [
			"Ты подтверждаешь, что информация выше корректна и ты хочешь отправить покупателю предложение сделки?",
			"Do you confirm that information above is correct and you want to send the offer to the buyer?"],

		'msg_buyer_confirm_new_transfer': [
			"Ты подтверждаешь, что информация выше тебя устраивает и ты хочешь принять участие в этой сделке?",
			"Do you confirm that information above is OK for you and you want to take a part in this deal?"],

		"msg_transfer_amount": ["<a href='{}'>Переведи</a> <b>{} TON</b> ({} TON сумма сделки + {} TON комиссия бота) на кошелёк бота-гаранта {} с обязательным комментарием {}.",
								"<a href='{}'>Transfer</a> <b>{} TON</b> ({} TON deal amount + {} TON the bot commission) to the guarantor bot {} with mandatory comment {}."],

		"msg_press_button_below": [
			"После отправки нажми кнопку ниже:",
			"After payment press button below:"],

		"msg_no_my_transfers": ["У тебя ещё не было ни одной сделки.", "You haven't had any deals yet."],
		"msg_your_transfers_list": ["Ниже представлены твои сделки. Нажми на кнопку, чтобы получить подробную информацию",
									"There are your deals below. Press the button to get more information about the deal."],

		"msg_iucn_input_nft": ["Чтобы получить детальную информацию по NFT с сайта Красной Книги, введи название или адрес NFT:",
			"To get additional NFT info from IUCN (Red List) input name or addres of the NFT:"],

		"msg_technical_break": [
			"🚧 Этот бот очень много работал, и сейчас у него небольшой перерыв :) Просьба отнестись с пониманием и подождать пару часов. 🚧",
			"🚧 This bot worked hard and now he is resting a little :) Please be patient and wait a couple of hours. 🚧"],

		"msg_user_is_monkeys": [
			"Ты уже являешься членом сообщества 🐒Monkeys и можешь получать все бонусы!",
			"You are a member of the 🐒Monkeys Community and you can get all bonuses!"],
		"msg_user_is_monkeys_new": [
			"Поздравляю! 🎉 Теперь ты являешься членом сообщества 🐒Monkeys и можешь получать все бонусы! \n" \
			+ "Для получения доступа к закрытому чату обратись к администратору - @ApeRLadmin",
			"Congratulations! 🎉 Now you a member of the 🐒Monkeys Community and you can get all bonuses!\n" \
			+ "To get access to the private chat please contact to the administrator - @ApeRLadmin"
		],
		"msg_monkeys_verif_info": [
			"<b>Monkeys</b> - это сообщество криптоэнтузиастов, объединённых общими интересами и целями, одной из которых является продвижение" \
			+ " блокчейна TON и NFT-проектов на этом блокчейне. Для доступа в сообщество нужно являться владельцем NFT из коллекции"\
			+ " <a href='https://getgems.io/collection/EQAA1yvDaDwEK5vHGOXRdtS2MbOVd1-TNy01L1S_t2HF4oLu'>Animal Red List</a> с животным из <b>отряда приматов (обезьяны, лемуры, лори)</b>.",

			"<b>Monkeys</b> is a community of crypto enthusiasts united by common interests and goals, one of which is the promotion of blockchain TON\n" \
			+ " and NFT collections on it. To access the community, you must be the owner of the NFT from the collection "\
			+ " <a href='https://getgems.io/collection/EQAA1yvDaDwEK5vHGOXRdtS2MbOVd1-TNy01L1S_t2HF4oLu'>Animal Red List</a> with an animal from <b>the order of primates (monkeys, lemurs, loris)</b>."
		],

		'msg_monkeys_nft_incorrect': ["NFT с таким адресом или названием нет в данной коллекции, либо животное не относится к <b>отряду приматов</b>! "\
			+ "Попробуй ввести другой:",
			"There is no NFT with address or name like this or the animal does not belongs to <b>the order of primates</b>. "\
			+ "Please try another one:"],
		'msg_monkeys_nft_wrong_owner': [
			"По данным в блокчейне, этот NFT принадлежит <b>другому владельцу</b>, либо выставлена на продажу в маркетплейсе. Попробуй ещё раз:",
			"According to blockchain info this NFT has <b>another owner</b> or it's on sale. Try again:"],

		'msg_donation': [
			"Если тебе понравился бот, ты можешь порадовать разработчика донатом на кофе и булочку 😉: {}\n\n" \
			+ "<a href='https://app.tonkeeper.com/transfer/{}'>💎TON Keeper</a> | "
			+ "<a href='https://tonhub.com/transfer/{}'>💰TON Hub</a> | "
			+ "<a href='{}'>💸CryptoBot</a>",

			"If you liked this bot you can please the developer by making a donation for coffee and a donut 😉: {}\n\n" \
			+ "<a href='https://app.tonkeeper.com/transfer/{}'>💎TON Keeper</a> | "
			+ "<a href='https://tonhub.com/transfer/{}'>💰TON Hub</a> | "
			+ "<a href='{}'>💸CryptoBot</a>"
		],

		'btn_auctions': ["🔨Аукционы", "🔨Auctions"],
		'btn_transfers': ["🤝P2P продажи", "🤝P2P sales"],
		'btn_help': ["🆘Помощь", "🆘Help"],
		'btn_iucn_info': ["📕Красная Книга", "📕Red List info"],
		'btn_airdrop': ["🎁Розыгрыш", "🎁Airdrop"],

		'btn_participate': ["🔎Найти новый", "🔎Find new"],
		'btn_now_participating': ["👌Ты - участник", "👌You're participant"],
		'btn_my_auctions': ["📜Ты - организатор", "📜You're owner"],
		'btn_my_transfers': ["📜Твои сделки", "📜Your deals"],
		'btn_back': ["↩Назад", "↩Back"],
		'btn_new_auction': ["🔨Новый аукцион", "🔨New auction"],
		'btn_cancel_auction': ["❌Отменить аукцион", "❌Cancel auction"],
		'btn_payment_received': ["💸Оплата получена", "💸Payment received"],
		'btn_nft_transfered': ["🖼NFT передан", "🖼NFT transfered"],
		'btn_cancel': ["🚫Отмена", "🚫Cancel"],
		'btn_duration_types': ["⏰Задать вручную;1 час;2 часа;3 часа;6 часов;12 часов;24 часа",
							   "⏰Manual input;1 hour;2 hours;3 hours;6 hours;12 hours;24 hours"],
		'btn_confirm': ["✅Подтвердить", "✅Confirm"],
		'btn_join': ["➕Присоединиться", "➕Join"],
		'btn_raise_first': ["💵Принять ставку", "💵Accept the bid"],
		'btn_raise': ["💵Поднять ставку (+{}💎)", "💵Raise the bid (+{}💎)"],
		'btn_refresh': ["🔄Обновить", "🔄Refresh"],
		'btn_owner': ["👑Ты - владелец!", "👑You are owner!"],
		'btn_leader': ["🏆Ты - лидер", "🏆You are leader!"],
		'btn_payment_done': ["💸Я оплатил", "💸I've paid"],
		'btn_check_verif': ["💸Я отправил", "💸I've sent"],
		'btn_new_transfer': ["🤝Новая сделка", "🤝New deal"],
		'btn_monkeys_verif': ["🐒Верификация Monkeys", "🐒Monkeys verification"],
		'btn_frogs_verif': ["🐸Верификация ARL Frogs", "🐸ARL Frogs verification"],
		'btn_donate': ["☕🍩Донат", "☕🍩Donation"],
		'btn_check_nft': ["🔎Проверка NFT", "🔎Check NFT"]

	}

	lang_id = languages.index(lang)
	return messages.get(message_code)[lang_id]