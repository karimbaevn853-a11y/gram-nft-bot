import asyncio
import logging
import os
import aiohttp
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

logging.basicConfig(level=logging.INFO)

# Render Environment Variables -> BOT_TOKEN sifatida kiriting
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = 7074089722
ADMIN_USERNAME = "@Skzpx"
CHANNEL_USERNAME = "@tonfermsale"

# To'lov kartalari va TON manzil (Visa keyingi safarga qoldirildi)
UZCARD_NUMBER = "5614681401815257"
VISA_CARD_NUMBER = ""
TON_WALLET = "UQA4qQ6E8Kf0vHXXCti_PzO71qXi7KiEeN5d71UO7xWiTL-w"

# TONAPI GRAM rate manzili (kalitsiz ishlaydi)
TONAPI_GRAM_RATES_URL = "https://tonapi.io/v2/rates?tokens=gram&currencies=usd,uzs"

# Standart va ustama sozlamalari
DEFAULT_GRAM_UZS = 12_300.0
DEFAULT_GRAM_USD = 0.96
DEFAULT_USD_UZS = 12_800.0
BUY_MARKUP_USD = 0.17
BUY_MARKUP_UZS = 2_000.0

# 134 ta NFT gift (qizil bo'yalgan gift olib tashlangan)
NFT_GIFTS = [
    "☕️ Coffee cup",
    "🔥 Torch",
    "🗽 Statue of Liberty",
    "🎭 Hockey mask",
    "🐶 Cool dog",
    "🏮 Lantern",
    "🍜 Noodles",
    "🍭 Lollipop",
    "🍨 Ice cream",
    "🛟 Pool float",
    "🛍 Bag",
    "🎒 Backpack",
    "🧁 Cupcake",
    "💩 Poop",
    "⛄️ Snowman 2025",
    "🧦 Christmas stocking",
    "🍬 Candy cane",
    "🎁 Gift box",
    "📌 Brooch",
    "🎂 Happy Birthday",
    "🧦 Socks",
    "🐍 Snake",
    "🍰 Cake",
    "⚔️ Light saber",
    "🌙 Crescent moon",
    "🍪 Heart cookie",
    "🃏 Jester hat",
    "🧺 Easter basket",
    "💐 Money bouquet",
    "🚬 Cigar / joint",
    "💌 Heart box",
    "✨ Sparkler",
    "🏅 Medal",
    "🌷 Flower vase",
    "📖 Magic book",
    "🐒 Monkey",
    "🚀 Rocket",
    "🫙 Jar",
    "👾 Tamagotchi",
    "🍄 Mushroom",
    "🍪 Gingerbread man",
    "🌙 Moon necklace",
    "🥧 Pie",
    "🐱 Love cats",
    "👁 Eye",
    "🥊 UFC",
    "📅 Calendar",
    "🍡 Mochi",
    "💝 Love You box",
    "🍷 Mulled wine",
    "🖋 Fountain pen",
    "🪙 Pot of gold",
    "☕️ Hot chocolate",
    "🍭 Swirl lollipop",
    "🌸 Sakura",
    "🥚 Easter egg",
    "🎉 2025",
    "🏄 Surfboard",
    "🤡 Jack-in-the-box",
    "📓 Notebook",
    "🏄 Surfboard",
    "🤡 Jack-in-the-box",
    "📓 Notebook",
    "🎀 Bow tie",
    "🎄 Wreath",
    "🍓 Strawberry box",
    "🎅 Santa hat",
    "🔮 Snow globe",
    "🪄 Cauldron",
    "🧁 Cupcake",
    "🎩 Witch hat",
    "🍫 Chocolate heart",
    "⭐️ Star",
    "🕯 Candle",
    "👠 High heels",
    "🧢 Fur hat",
    "🎩 Top hat",
    "🔔 Bells",
    "🔮 Crystal ball",
    "🧤 Mittens",
    "🌹 Rose",
    "🔐 Heart lock",
    "💍 Ring box",
    "🧪 Potion",
    "🧸 Teddy bear",
    "🕸 Spider heart",
    "🌺 Skull flower",
    "💨 Hair dryer",
    "🚬 Cigar",
    "🕯 Heart candle",
    "🎃 Pumpkin",
    "💿 Turntable",
    "🦅 Eagle",
    "💍 Signet ring",
    "🧸 Voodoo doll",
    "🧹 Broom",
    "🔔 Bell",
    "⌚️ Gold watch",
    "🚗 Vintage car",
    "🪖 Helmet",
    "👶 Pacifier",
    "💍 Gold ring",
    "💋 Vampire lips",
    "💀 Skull",
    "💎 Crystals",
    "💍 Diamond ring",
    "🐸 Frog",
    "🧴 Perfume",
    "✋ Golden hand",
    "💎 Diamond crystal",
    "👜 Handbag",
    "🏆 Oscar",
    "🐈‍⬛ Black cat",
    "📿 Nail bracelet",
    "🪔 Magic lamp",
    "🧱 Brick",
    "🧪 Poison bottle",
    "🧸 Plush bear",
    "🕶 Sunglasses",
    "🛡 Spartan helmet",
    "🪔 Magic lamp",
    "🧱 Brick",
    "🧪 Poison bottle",
    "🧸 Plush bear",
    "🕶 Sunglasses",
    "🛡 Spartan helmet",
    "💪 Muscle trophy",
    "🧢 Cap",
    "🫐 Plum",
    "🐸 Pepe",
    "🏆 Ice trophy",
    "🏆 Gold trophy",
    "💖 Heart locket",
    "⚰️ Coffin",
]

# Admin bot ichidan qo'sha oladigan username'lar ro'yxati
# Har bir element: {"name": str, "price": str}
username_listings: list[dict[str, str]] = [
    {"name": "@tonferm", "price": "Kelishuv asosida"},
    {"name": "@gramshop", "price": "Kelishuv asosida"},
]

dp = Dispatcher()

user_lang: dict[int, str] = {}
user_balance_uzs: dict[int, float] = {}
user_state: dict[int, dict] = {}
pending_topups: dict[int, dict] = {}

market_state = {
    "gram_uzs": DEFAULT_GRAM_UZS,
    "gram_usd": DEFAULT_GRAM_USD,
    "usd_uzs": DEFAULT_USD_UZS,
}


async def fetch_live_gram_rates() -> tuple[float, float, float]:
    timeout = aiohttp.ClientTimeout(total=6)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(TONAPI_GRAM_RATES_URL) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    rates = data.get("rates") or {}
                    gram_data = rates.get("GRAM") or rates.get("gram") or {}
                    prices = gram_data.get("prices") or {}

                    uzs_raw = prices.get("UZS") if "UZS" in prices else prices.get("uzs")
                    usd_raw = prices.get("USD") if "USD" in prices else prices.get("usd")

                    gram_uzs = float(uzs_raw) if uzs_raw is not None else None
                    gram_usd = float(usd_raw) if usd_raw is not None else None

                    if gram_uzs and gram_uzs > 0:
                        market_state["gram_uzs"] = gram_uzs
                    if gram_usd and gram_usd > 0:
                        market_state["gram_usd"] = gram_usd

                    if gram_uzs and gram_usd and gram_usd > 0:
                        market_state["usd_uzs"] = gram_uzs / gram_usd
                    elif gram_uzs and gram_uzs > 0:
                        market_state["gram_usd"] = gram_uzs / market_state["usd_uzs"]
                    elif gram_usd and gram_usd > 0:
                        market_state["gram_uzs"] = gram_usd * market_state["usd_uzs"]
    except Exception as exc:
        logging.warning("TonAPI GRAM narx xatosi: %s", exc)

    return (
        market_state["gram_uzs"],
        market_state["gram_usd"],
        market_state["usd_uzs"],
    )


TEXTS = {
    "uz": {
        "choose_lang": "🌐 Tilni tanlang / Выберите язык / Choose language:",
        "lang_set": "O‘zbekcha tanlandi",
        "sub_req": "⚠️ Davom etish uchun <b>{ch}</b> kanaliga obuna bo‘ling!",
        "btn_sub_channel": "📢 Kanalga obuna bo‘lish",
        "btn_check_sub": "✅ Obunani tekshirish",
        "not_sub_yet": "❌ Hali {ch} kanaliga obuna bo‘lmadingiz!",
        "main_menu": (
            "⭐️ <b>Asosiy menyu</b>\n\n"
            "🆔 ID: <code>{uid}</code>\n"
            "💰 Balans: <b>{bal}</b>\n"
            "📊 1 GRAM birja narxi (1:1): <b>{gram_p}</b>\n"
            "🟢 Gramm sotib olish narxi (1g): <b>{buy_p}</b> (+2 000 so‘m / +$0.17)"
        ),
        "btn_nft": "💎 NFT Gift olish",
        "btn_username": "🔗 Username savdosi",
        "btn_buy_gram": "🟢 Gramm sotib olish",
        "btn_sell_gram": "🔴 Gramm sotish",
        "btn_topup": "💳 Hisob to‘ldirish",
        "btn_profile": "👤 Profil",
        "btn_rules": "📜 Qoidalar bilan tanishish",
        "btn_lang": "🌐 Til",
        "btn_admin_add_uname": "➕ Username qo‘shish (Admin)",
        "rules_text": (
            "📜 <b>Qoidalar bilan tanishish</b>\n\n"
            "1️⃣ Savdo <b>avtomatik emas</b> — barcha buyurtmalar, o‘tkazmalar va kelishuvlar <b>admin ({admin})</b> bilan kelishilgan holda amalga oshiriladi.\n"
            "2️⃣ Majburiy kanal: <b>{ch}</b>.\n"
            "3️⃣ <b>GRAM</b> sotish birja narxida (1:1), sotib olish esa +2 000 so‘m / +$0.17 ustama bilan hisoblanadi.\n"
            "4️⃣ <b>NFT Gift</b> savdosi faqat <b>TON</b> orqali va <b>{admin}</b> bilan kelishuv asosida o‘tadi.\n"
            "5️⃣ <b>Username savdosi</b> <b>TON</b> yoki <b>valyuta</b> (so‘m / dollar) orqali <b>{admin}</b> bilan kelishiladi."
        ),
        "username_catalog_title": (
            "🔗 <b>Username savdosi</b>\n"
            "💰 To‘lov usuli: <b>TON</b> yoki <b>Valyuta</b>\n"
            "🤝 Savdo: <b>{admin}</b> bilan kelishilgan holda\n"
            "📬 TON manzil: <code>{ton}</code>"
        ),
        "username_empty": "📭 Hozircha ro‘yxatda username yo‘q.",
        "username_detail": (
            "🔗 Username: <b>{uname}</b>\n"
            "💵 Narx / izoh: <b>{price}</b>\n"
            "💳 To‘lov: <b>TON</b> yoki <b>Valyuta</b>\n"
            "📬 TON manzil: <code>{ton}</code>\n"
            "🤝 Savdo: <b>{admin}</b> bilan kelishilgan holda"
        ),
        "btn_pay_ton": "💎 TON orqali olish",
        "btn_pay_currency": "💵 Valyuta orqali olish",
        "username_ordered": (
            "📩 <b>Admin siz bilan bog‘lanadi</b>\n\n"
            "✅ <b>{uname}</b> username bo‘yicha buyurtma (<b>{method}</b>) qabul qilindi.\n"
            "🤝 Admin ({admin}) siz bilan bog‘lanadi."
        ),
        "ask_admin_uname": (
            "➕ <b>Yangi username qo‘shish</b>\n\n"
            "Format: <code>@username | Narx yoki izoh</code>\n"
            "Masalan: <code>@fermton | 25 TON yoki 300 000 so'm</code>\n"
            "(Narx yozmasangiz ham bo‘ladi: <code>@fermton</code>)"
        ),
        "admin_uname_added": "✅ Username qo‘shildi: <b>{uname}</b> ({price})",
        "profile_text": (
            "👤 <b>Profil</b>\n\n"
            "🆔 ID: <code>{uid}</code>\n"
            "💰 Balans: <b>{bal}</b>"
        ),
        "ask_topup": "💳 Necha so‘m hisob to‘ldirmoqchisiz? (Masalan: <code>50000</code>)",
        "invalid_num": "❌ 0 dan katta son kiriting (masalan: <code>1</code> yoki <code>50000</code>).",
        "topup_card_info": (
            "💳 <b>Hisob to‘ldirish</b>\n\n"
            "💵 Summa: <b>{amt:,.0f} so‘m</b>\n"
            "{cards_block}\n\n"
            "To‘lov qilgach, <b>chek rasmini</b> yuboring. Admin tasdiqlagach hisobingiz to‘ladi."
        ),
        "topup_wait_receipt": "📸 To‘lov chekining rasmini yuboring.",
        "topup_sent": "✅ Chek {admin} ga yuborildi. Tasdiqlangach hisobingiz to‘ladi.",
        "topup_approved": "✅ Hisobingiz <b>{amt:,.0f} so‘m</b> ga to‘ldirildi!",
        "topup_rejected": "❌ To‘lov cheki rad etildi.",
        "ask_gram_buy": (
            "🟢 <b>Gramm sotib olish</b>\n"
            "💰 Balansingiz: <b>{bal}</b>\n"
            "💵 1 GRAM narxi: <b>{buy_p}</b> (birja narxidan +2 000 so‘m / +$0.17 ko‘p)\n"
            "Nechta GRAM olmoqchisiz? (Masalan: <code>1</code> yoki <code>0.5</code>)"
        ),
        "insufficient_bal": (
            "❌ Hisobingizda mablag‘ yetarli emas!\n"
            "Kerakli summa: <b>{need}</b>\n"
            "Sizning balansingiz: <b>{bal}</b>\n"
            "Avval hisobni to‘ldiring yoki balansingiz yetadigan miqdor kiriting."
        ),
        "admin_will_contact_buy": (
            "📩 <b>Admin siz bilan bog‘lanadi</b>\n\n"
            "✅ Buyurtma qabul qilindi: <b>{grams} GRAM</b>\n"
            "💳 Hisobdan yechildi: <b>{spent}</b>\n"
            "🤝 Admin ({admin}) siz bilan bog‘lanib, GRAM ni beradi."
        ),
        "ask_gram_sell": (
            "🔴 <b>Gramm sotish (Birja narxi 1:1)</b>\n"
            "📊 1 GRAM birja narxi: <b>{gram_p}</b>\n"
            "Nechta GRAM sotmoqchisiz? (Masalan: <code>1</code> yoki <code>0.5</code>)"
        ),
        "ask_sell_wallet": (
            "📬 <b>TON manzilingizni yozib keting</b>\n"
            "⚖️ Miqdor: <b>{grams} GRAM</b>\n"
            "💵 Birja narxi (1:1) bo‘yicha summa: <b>{got}</b>"
        ),
        "invalid_wallet": "❌ To‘g‘ri TON manzil kiriting.",
        "admin_will_contact_sell": (
            "📩 <b>Admin siz bilan bog‘lanadi</b>\n\n"
            "✅ Ariza yuborildi: <b>{grams} GRAM</b> sotish\n"
            "📬 TON manzil: <code>{wallet}</code>\n"
            "💵 Summa (1:1): <b>{got}</b>\n"
            "🤝 Admin ({admin}) siz bilan bog‘lanadi."
        ),
        "nft_title": (
            "💎 <b>NFT Gift katalogi ({count} ta)</b>\n"
            "⚠️ Faqat <b>TON</b> orqali va <b>{admin}</b> bilan kelishilgan holda.\n"
            "TON manzil: <code>{ton}</code>"
        ),
        "nft_selected": (
            "💎 Gift: <b>{gift}</b>\n"
            "💰 To‘lov: <b>Faqat TON</b>\n"
            "📬 TON manzil: <code>{ton}</code>\n"
            "🤝 Savdo: <b>{admin}</b> bilan kelishilgan holda"
        ),
        "btn_order_nft": "📩 NFT buyurtma berish",
        "btn_back": "⬅️ Ortga",
        "nft_ordered": (
            "📩 <b>Admin siz bilan bog‘lanadi</b>\n\n"
            "✅ <b>{gift}</b> bo‘yicha buyurtma {admin} ga yuborildi."
        ),
    },
    "ru": {
        "choose_lang": "🌐 Выберите язык / Tilni tanlang / Choose language:",
        "lang_set": "Выбран русский язык",
        "sub_req": "⚠️ Для продолжения подпишитесь на канал <b>{ch}</b>!",
        "btn_sub_channel": "📢 Подписаться на канал",
        "btn_check_sub": "✅ Проверить подписку",
        "not_sub_yet": "❌ Вы ещё не подписались на {ch}!",
        "main_menu": (
            "⭐️ <b>Главное меню</b>\n\n"
            "🆔 ID: <code>{uid}</code>\n"
            "💰 Баланс: <b>{bal}</b>\n"
            "📊 Биржевая цена 1 GRAM (1:1): <b>{gram_p}</b>\n"
            "🟢 Цена покупки грамм (1г): <b>{buy_p}</b> (+2 000 сум / +$0.17)"
        ),
        "btn_nft": "💎 Купить NFT Gift",
        "btn_username": "🔗 Продажа Username",
        "btn_buy_gram": "🟢 Купить грамм",
        "btn_sell_gram": "🔴 Продать грамм",
        "btn_topup": "💳 Пополнить счёт",
        "btn_profile": "👤 Профиль",
        "btn_rules": "📜 Ознакомиться с правилами",
        "btn_lang": "🌐 Язык",
        "btn_admin_add_uname": "➕ Добавить Username (Админ)",
        "rules_text": (
            "📜 <b>Правила сервиса</b>\n\n"
            "1️⃣ Сделки <b>не автоматические</b> — все заявки, переводы и условия согласуются с <b>админом ({admin})</b>.\n"
            "2️⃣ Обязательный канал: <b>{ch}</b>.\n"
            "3️⃣ Продажа <b>GRAM</b> по биржевой цене (1:1), покупка с наценкой +2 000 сум / +$0.17.\n"
            "4️⃣ <b>NFT Gift</b> — только за <b>TON</b> по договорённости с <b>{admin}</b>.\n"
            "5️⃣ <b>Username</b> — за <b>TON</b> или <b>валюту</b> (сум / доллар) по согласованию с <b>{admin}</b>."
        ),
        "username_catalog_title": (
            "🔗 <b>Продажа Username</b>\n"
            "💰 Оплата: <b>TON</b> или <b>Валюта</b>\n"
            "🤝 Сделка: <b>по договорённости с {admin}</b>\n"
            "📬 TON адрес: <code>{ton}</code>"
        ),
        "username_empty": "📭 Пока в списке нет ни одного username.",
        "username_detail": (
            "🔗 Username: <b>{uname}</b>\n"
            "💵 Цена / описание: <b>{price}</b>\n"
            "💳 Оплата: <b>TON</b> или <b>Валюта</b>\n"
            "📬 TON адрес: <code>{ton}</code>\n"
            "🤝 Сделка: <b>по договорённости с {admin}</b>"
        ),
        "btn_pay_ton": "💎 Оплатить в TON",
        "btn_pay_currency": "💵 Оплатить в валюте",
        "username_ordered": (
            "📩 <b>Админ с вами свяжется</b>\n\n"
            "✅ Заявка на <b>{uname}</b> (<b>{method}</b>) принята.\n"
            "🤝 Админ ({admin}) свяжется с вами."
        ),
        "ask_admin_uname": (
            "➕ <b>Добавление username</b>\n\n"
            "Формат: <code>@username | Цена или описание</code>\n"
            "Пример: <code>@fermton | 25 TON или 300 000 сум</code>\n"
            "(Можно без цены: <code>@fermton</code>)"
        ),
        "admin_uname_added": "✅ Username добавлен: <b>{uname}</b> ({price})",
        "profile_text": (
            "👤 <b>Профиль</b>\n\n"
            "🆔 ID: <code>{uid}</code>\n"
            "💰 Баланс: <b>{bal}</b>"
        ),
        "ask_topup": "💳 На какую сумму (в сум) хотите пополнить счёт? (Например: <code>50000</code>)",
        "invalid_num": "❌ Введите положительное число (например: <code>1</code> или <code>50000</code>).",
        "topup_card_info": (
            "💳 <b>Пополнение счёта</b>\n\n"
            "💵 Сумма: <b>{amt:,.0f} сум</b>\n"
            "{cards_block}\n\n"
            "После оплаты отправьте <b>фото чека</b>. После подтверждения админом баланс пополнится."
        ),
        "topup_wait_receipt": "📸 Отправьте фото чека об оплате.",
        "topup_sent": "✅ Чек отправлен {admin}. После подтверждения баланс пополнится.",
        "topup_approved": "✅ Ваш счёт пополнен на <b>{amt:,.0f} сум</b>!",
        "topup_rejected": "❌ Чек отклонён.",
        "ask_gram_buy": (
            "🟢 <b>Покупка грамм</b>\n"
            "💰 Ваш баланс: <b>{bal}</b>\n"
            "💵 Цена 1 GRAM: <b>{buy_p}</b> (+2 000 сум / +$0.17 выше биржи)\n"
            "Сколько GRAM хотите купить? (Например: <code>1</code> или <code>0.5</code>)"
        ),
        "insufficient_bal": (
            "❌ Недостаточно средств на балансе!\n"
            "Нужно: <b>{need}</b>\n"
            "Ваш баланс: <b>{bal}</b>\n"
            "Пополните счёт или введите объём в пределах баланса."
        ),
        "admin_will_contact_buy": (
            "📩 <b>Админ с вами свяжется</b>\n\n"
            "✅ Заявка принята: <b>{grams} GRAM</b>\n"
            "💳 Списано с баланса: <b>{spent}</b>\n"
            "🤝 Админ ({admin}) свяжется с вами и выдаст GRAM."
        ),
        "ask_gram_sell": (
            "🔴 <b>Продажа грамм (Биржа 1:1)</b>\n"
            "📊 Биржевая цена 1 GRAM: <b>{gram_p}</b>\n"
            "Сколько GRAM хотите продать? (Например: <code>1</code> или <code>0.5</code>)"
        ),
        "ask_sell_wallet": (
            "📬 <b>Оставьте ваш TON адрес</b>\n"
            "⚖️ Объём: <b>{grams} GRAM</b>\n"
            "💵 Сумма по бирже (1:1): <b>{got}</b>"
        ),
        "invalid_wallet": "❌ Введите корректный TON адрес.",
        "admin_will_contact_sell": (
            "📩 <b>Админ с вами свяжется</b>\n\n"
            "✅ Заявка отправлена: продажа <b>{grams} GRAM</b>\n"
            "📬 TON адрес: <code>{wallet}</code>\n"
            "💵 Сумма (1:1): <b>{got}</b>\n"
            "🤝 Админ ({admin}) свяжется с вами."
        ),
        "nft_title": (
            "💎 <b>Каталог NFT Gift ({count} шт.)</b>\n"
            "⚠️ Только за <b>TON</b> и по договорённости с <b>{admin}</b>.\n"
            "TON адрес: <code>{ton}</code>"
        ),
        "nft_selected": (
            "💎 Подарок: <b>{gift}</b>\n"
            "💰 Оплата: <b>Только TON</b>\n"
            "📬 TON адрес: <code>{ton}</code>\n"
            "🤝 Сделка: <b>по договорённости с {admin}</b>"
        ),
        "btn_order_nft": "📩 Заказать NFT",
        "btn_back": "⬅️ Назад",
        "nft_ordered": (
            "📩 <b>Админ с вами свяжется</b>\n\n"
            "✅ Заявка на <b>{gift}</b> отправлена {admin}."
        ),
    },
    "en": {
        "choose_lang": "🌐 Choose language / Tilni tanlang / Выберите язык:",
        "lang_set": "English selected",
        "sub_req": "⚠️ Subscribe to <b>{ch}</b> to continue!",
        "btn_sub_channel": "📢 Subscribe to channel",
        "btn_check_sub": "✅ Check subscription",
        "not_sub_yet": "❌ You haven't subscribed to {ch} yet!",
        "main_menu": (
            "⭐️ <b>Main Menu</b>\n\n"
            "🆔 ID: <code>{uid}</code>\n"
            "💰 Balance: <b>{bal}</b>\n"
            "📊 1 GRAM market price (1:1): <b>{gram_p}</b>\n"
            "🟢 Buy GRAM price (1g): <b>{buy_p}</b> (+2,000 UZS / +$0.17)"
        ),
        "btn_nft": "💎 Get NFT Gift",
        "btn_username": "🔗 Username Trading",
        "btn_buy_gram": "🟢 Buy Gram",
        "btn_sell_gram": "🔴 Sell Gram",
        "btn_topup": "💳 Top up balance",
        "btn_profile": "👤 Profile",
        "btn_rules": "📜 Read the Rules",
        "btn_lang": "🌐 Language",
        "btn_admin_add_uname": "➕ Add Username (Admin)",
        "rules_text": (
            "📜 <b>Service Rules</b>\n\n"
            "1️⃣ Deals are <b>not automatic</b> — all orders, transfers, and terms are handled <b>by agreement with admin ({admin})</b>.\n"
            "2️⃣ Required channel: <b>{ch}</b>.\n"
            "3️⃣ <b>GRAM</b> sell is 1:1 market price; buy includes +2,000 UZS / +$0.17 markup.\n"
            "4️⃣ <b>NFT Gift</b> deals are <b>TON only</b> by agreement with <b>{admin}</b>.\n"
            "5️⃣ <b>Username trading</b> is available in <b>TON</b> or <b>currency</b> (UZS / USD) by agreement with <b>{admin}</b>."
        ),
        "username_catalog_title": (
            "🔗 <b>Username Trading</b>\n"
            "💰 Payment: <b>TON</b> or <b>Currency</b>\n"
            "🤝 Deal: <b>by agreement with {admin}</b>\n"
            "📬 TON address: <code>{ton}</code>"
        ),
        "username_empty": "📭 No usernames listed yet.",
        "username_detail": (
            "🔗 Username: <b>{uname}</b>\n"
            "💵 Price / info: <b>{price}</b>\n"
            "💳 Payment: <b>TON</b> or <b>Currency</b>\n"
            "📬 TON address: <code>{ton}</code>\n"
            "🤝 Deal: <b>by agreement with {admin}</b>"
        ),
        "btn_pay_ton": "💎 Pay with TON",
        "btn_pay_currency": "💵 Pay with Currency",
        "username_ordered": (
            "📩 <b>Admin will contact you</b>\n\n"
            "✅ Order for <b>{uname}</b> (<b>{method}</b>) received.\n"
            "🤝 Admin ({admin}) will contact you."
        ),
        "ask_admin_uname": (
            "➕ <b>Add a new username</b>\n\n"
            "Format: <code>@username | Price or note</code>\n"
            "Example: <code>@fermton | 25 TON or 300,000 UZS</code>\n"
            "(Price is optional: <code>@fermton</code>)"
        ),
        "admin_uname_added": "✅ Username added: <b>{uname}</b> ({price})",
        "profile_text": (
            "👤 <b>Profile</b>\n\n"
            "🆔 ID: <code>{uid}</code>\n"
            "💰 Balance: <b>{bal}</b>"
        ),
        "ask_topup": "💳 How much (in UZS) do you want to top up? (Example: <code>50000</code>)",
        "invalid_num": "❌ Enter a positive number (example: <code>1</code> or <code>50000</code>).",
        "topup_card_info": (
            "💳 <b>Top Up Balance</b>\n\n"
            "💵 Amount: <b>{amt:,.0f} UZS</b>\n"
            "{cards_block}\n\n"
            "After payment, send a <b>receipt photo</b>. Balance updates after admin approval."
        ),
        "topup_wait_receipt": "📸 Send a photo of your payment receipt.",
        "topup_sent": "✅ Receipt sent to {admin}. Balance updates after approval.",
        "topup_approved": "✅ Your balance has been topped up by <b>{amt:,.0f} UZS</b>!",
        "topup_rejected": "❌ Receipt rejected.",
        "ask_gram_buy": (
            "🟢 <b>Buy Gram</b>\n"
            "💰 Your balance: <b>{bal}</b>\n"
            "💵 1 GRAM price: <b>{buy_p}</b> (+2,000 UZS / +$0.17 above market)\n"
            "How many GRAM do you want to buy? (Example: <code>1</code> or <code>0.5</code>)"
        ),
        "insufficient_bal": (
            "❌ Insufficient balance!\n"
            "Required: <b>{need}</b>\n"
            "Your balance: <b>{bal}</b>\n"
            "Top up your balance or enter a lower amount."
        ),
        "admin_will_contact_buy": (
            "📩 <b>Admin will contact you</b>\n\n"
            "✅ Order received: <b>{grams} GRAM</b>\n"
            "💳 Deducted: <b>{spent}</b>\n"
            "🤝 Admin ({admin}) will contact you and deliver GRAM."
        ),
        "ask_gram_sell": (
            "🔴 <b>Sell Gram (1:1 Market)</b>\n"
            "📊 1 GRAM market price: <b>{gram_p}</b>\n"
            "How many GRAM do you want to sell? (Example: <code>1</code> or <code>0.5</code>)"
        ),
        "ask_sell_wallet": (
            "📬 <b>Leave your TON address</b>\n"
            "⚖️ Amount: <b>{grams} GRAM</b>\n"
            "💵 Market amount (1:1): <b>{got}</b>"
        ),
        "invalid_wallet": "❌ Enter a valid TON wallet address.",
        "admin_will_contact_sell": (
            "📩 <b>Admin will contact you</b>\n\n"
            "✅ Request sent: sell <b>{grams} GRAM</b>\n"
            "📬 TON address: <code>{wallet}</code>\n"
            "💵 Amount (1:1): <b>{got}</b>\n"
            "🤝 Admin ({admin}) will contact you."
        ),
        "nft_title": (
            "💎 <b>NFT Gift Catalog ({count} items)</b>\n"
            "⚠️ <b>TON only</b> and by agreement with <b>{admin}</b>.\n"
            "TON address: <code>{ton}</code>"
        ),
        "nft_selected": (
            "💎 Gift: <b>{gift}</b>\n"
            "💰 Payment: <b>TON only</b>\n"
            "📬 TON address: <code>{ton}</code>\n"
            "🤝 Deal: <b>by agreement with {admin}</b>"
        ),
        "btn_order_nft": "📩 Order NFT",
        "btn_back": "⬅️ Back",
        "nft_ordered": (
            "📩 <b>Admin will contact you</b>\n\n"
            "✅ Order for <b>{gift}</b> sent to {admin}."
        ),
    },
}


def get_lang(uid: int) -> str:
    return user_lang.get(uid, "uz")


def get_bal(uid: int) -> float:
    return user_balance_uzs.get(uid, 0.0)


def calc_buy_uzs(grams: float, gram_uzs: float, usd_uzs: float) -> float:
    markup_uzs = max(BUY_MARKUP_UZS, BUY_MARKUP_USD * usd_uzs)
    return grams * (gram_uzs + markup_uzs)


def fmt_money(uzs_amount: float, usd_uzs: float) -> str:
    rate = usd_uzs if usd_uzs > 0 else DEFAULT_USD_UZS
    return f"{uzs_amount:,.0f} so'm (${uzs_amount / rate:,.2f})"


def build_cards_block() -> str:
    lines = []
    if UZCARD_NUMBER:
        lines.append(f"🏦 Uzcard: <code>{UZCARD_NUMBER}</code>")
    if VISA_CARD_NUMBER:
        lines.append(f"💳 Visa: <code>{VISA_CARD_NUMBER}</code>")
    return "\n".join(lines) if lines else "🏦 Karta ma'lumoti sozlanmoqda"


async def is_subscribed(bot: Bot, uid: int) -> bool:
    if uid == ADMIN_ID:
        return True
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=uid)
        return member.status in {"member", "administrator", "creator"}
    except Exception as exc:
        logging.warning("Obuna tekshirishda xato: %s", exc)
        return False


async def post_to_channel(bot: Bot, text: str) -> None:
    try:
        await bot.send_message(chat_id=CHANNEL_USERNAME, text=text, parse_mode="HTML")
    except Exception as exc:
        logging.warning("Kanalga xabar ketmadi: %s", exc)


def lang_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇺🇿 O‘zbekcha", callback_data="lang_uz"),
                InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
                InlineKeyboardButton(text="🇺🇸 English", callback_data="lang_en"),
            ]
        ]
    )


def sub_kb(lang: str) -> InlineKeyboardMarkup:
    t = TEXTS[lang]
    clean_ch = CHANNEL_USERNAME.lstrip("@")
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t["btn_sub_channel"], url=f"https://t.me/{clean_ch}")],
            [InlineKeyboardButton(text=t["btn_check_sub"], callback_data="check_sub")],
        ]
    )


def main_kb(lang: str, uid: int) -> InlineKeyboardMarkup:
    t = TEXTS[lang]
    rows: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text=t["btn_nft"], callback_data="open_nft_0")],
        [InlineKeyboardButton(text=t["btn_username"], callback_data="open_unames")],
        [
            InlineKeyboardButton(text=t["btn_buy_gram"], callback_data="gram_buy"),
            InlineKeyboardButton(text=t["btn_sell_gram"], callback_data="gram_sell"),
        ],
        [
            InlineKeyboardButton(text=t["btn_topup"], callback_data="topup_start"),
            InlineKeyboardButton(text=t["btn_profile"], callback_data="open_profile"),
        ],
        [
            InlineKeyboardButton(text=t["btn_rules"], callback_data="open_rules"),
            InlineKeyboardButton(text=t["btn_lang"], callback_data="open_lang"),
        ],
    ]
    if uid == ADMIN_ID:
        rows.append([InlineKeyboardButton(text=t["btn_admin_add_uname"], callback_data="admin_add_uname")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def username_catalog_kb(lang: str) -> InlineKeyboardMarkup:
    t = TEXTS[lang]
    rows: list[list[InlineKeyboardButton]] = []
    for idx, item in enumerate(username_listings):
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"{item['name']} — {item['price']}",
                    callback_data=f"pick_uname_{idx}",
                )
            ]
        )
    rows.append([InlineKeyboardButton(text=t["btn_back"], callback_data="back_main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def username_pay_kb(lang: str, idx: int) -> InlineKeyboardMarkup:
    t = TEXTS[lang]
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t["btn_pay_ton"], callback_data=f"order_uname_{idx}_ton"),
                InlineKeyboardButton(text=t["btn_pay_currency"], callback_data=f"order_uname_{idx}_cur"),
            ],
            [InlineKeyboardButton(text=t["btn_back"], callback_data="open_unames")],
        ]
    )


def nft_catalog_kb(lang: str, page: int = 0, per_page: int = 12) -> InlineKeyboardMarkup:
    t = TEXTS[lang]
    total_pages = max(1, (len(NFT_GIFTS) + per_page - 1) // per_page)
    page = max(0, min(page, total_pages - 1))
    start = page * per_page
    end = start + per_page

    rows: list[list[InlineKeyboardButton]] = []
    chunk = NFT_GIFTS[start:end]
    for i in range(0, len(chunk), 2):
        row = []
        for offset in range(2):
            if i + offset < len(chunk):
                idx = start + i + offset
                row.append(
                    InlineKeyboardButton(
                        text=NFT_GIFTS[idx],
                        callback_data=f"pick_nft_{idx}_{page}",
                    )
                )
        rows.append(row)

    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton(text="◀️", callback_data=f"open_nft_{page - 1}"))
    nav_row.append(InlineKeyboardButton(text=f"{page + 1}/{total_pages}", callback_data="noop"))
    if page < total_pages - 1:
        nav_row.append(InlineKeyboardButton(text="▶️", callback_data=f"open_nft_{page + 1}"))
    rows.append(nav_row)
    rows.append([InlineKeyboardButton(text=t["btn_back"], callback_data="back_main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def nft_order_kb(lang: str, gift_idx: int, page: int) -> InlineKeyboardMarkup:
    t = TEXTS[lang]
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t["btn_order_nft"], callback_data=f"order_nft_{gift_idx}")],
            [InlineKeyboardButton(text=t["btn_back"], callback_data=f"open_nft_{page}")],
        ]
    )


async def send_sub_prompt(bot: Bot, chat_id: int, uid: int) -> None:
    lang = get_lang(uid)
    t = TEXTS[lang]
    await bot.send_message(
        chat_id,
        t["sub_req"].format(ch=CHANNEL_USERNAME),
        parse_mode="HTML",
        reply_markup=sub_kb(lang),
    )


async def send_main(bot: Bot, chat_id: int, uid: int) -> None:
    lang = get_lang(uid)
    t = TEXTS[lang]
    gram_uzs, _, usd_uzs = await fetch_live_gram_rates()
    buy_one_uzs = calc_buy_uzs(1.0, gram_uzs, usd_uzs)
    text = t["main_menu"].format(
        uid=uid,
        bal=fmt_money(get_bal(uid), usd_uzs),
        gram_p=fmt_money(gram_uzs, usd_uzs),
        buy_p=fmt_money(buy_one_uzs, usd_uzs),
    )
    await bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=main_kb(lang, uid))


@dp.message(CommandStart())
async def cmd_start(message: Message) -> None:
    uid = message.from_user.id
    user_state.pop(uid, None)
    await message.answer(TEXTS[get_lang(uid)]["choose_lang"], reply_markup=lang_kb())


@dp.callback_query(F.data == "noop")
async def on_noop(callback: CallbackQuery) -> None:
    await callback.answer()


@dp.callback_query(F.data.startswith("lang_"))
async def on_lang(callback: CallbackQuery, bot: Bot) -> None:
    uid = callback.from_user.id
    code = callback.data.split("_", 1)[1]
    if code in TEXTS:
        user_lang[uid] = code
    lang = get_lang(uid)
    await callback.answer(TEXTS[lang]["lang_set"])
    if await is_subscribed(bot, uid):
        await send_main(bot, callback.message.chat.id, uid)
    else:
        await send_sub_prompt(bot, callback.message.chat.id, uid)


@dp.callback_query(F.data == "check_sub")
async def on_check_sub(callback: CallbackQuery, bot: Bot) -> None:
    uid = callback.from_user.id
    lang = get_lang(uid)
    t = TEXTS[lang]
    if await is_subscribed(bot, uid):
        await callback.answer()
        await send_main(bot, callback.message.chat.id, uid)
    else:
        await callback.answer(t["not_sub_yet"].format(ch=CHANNEL_USERNAME), show_alert=True)


@dp.callback_query(F.data == "open_lang")
async def on_open_lang(callback: CallbackQuery) -> None:
    uid = callback.from_user.id
    await callback.answer()
    await callback.message.answer(TEXTS[get_lang(uid)]["choose_lang"], reply_markup=lang_kb())


@dp.callback_query(F.data == "open_rules")
async def on_open_rules(callback: CallbackQuery, bot: Bot) -> None:
    uid = callback.from_user.id
    if not await is_subscribed(bot, uid):
        await callback.answer(TEXTS[get_lang(uid)]["not_sub_yet"].format(ch=CHANNEL_USERNAME), show_alert=True)
        return
    lang = get_lang(uid)
    t = TEXTS[lang]
    await callback.answer()
    kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=t["btn_back"], callback_data="back_main")]]
    )
    await callback.message.answer(
        t["rules_text"].format(admin=ADMIN_USERNAME, ch=CHANNEL_USERNAME),
        parse_mode="HTML",
        reply_markup=kb,
    )


@dp.callback_query(F.data == "open_unames")
async def on_open_unames(callback: CallbackQuery, bot: Bot) -> None:
    uid = callback.from_user.id
    if not await is_subscribed(bot, uid):
        await callback.answer(TEXTS[get_lang(uid)]["not_sub_yet"].format(ch=CHANNEL_USERNAME), show_alert=True)
        return
    lang = get_lang(uid)
    t = TEXTS[lang]
    await callback.answer()
    if not username_listings:
        kb = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text=t["btn_back"], callback_data="back_main")]]
        )
        await callback.message.answer(t["username_empty"], parse_mode="HTML", reply_markup=kb)
        return
    await callback.message.answer(
        t["username_catalog_title"].format(admin=ADMIN_USERNAME, ton=TON_WALLET),
        parse_mode="HTML",
        reply_markup=username_catalog_kb(lang),
    )


@dp.callback_query(F.data.startswith("pick_uname_"))
async def on_pick_uname(callback: CallbackQuery) -> None:
    idx = int(callback.data.split("_")[-1])
    uid = callback.from_user.id
    lang = get_lang(uid)
    t = TEXTS[lang]
    if idx < 0 or idx >= len(username_listings):
        await callback.answer()
        return
    item = username_listings[idx]
    await callback.answer()
    await callback.message.answer(
        t["username_detail"].format(
            uname=item["name"],
            price=item["price"],
            ton=TON_WALLET,
            admin=ADMIN_USERNAME,
        ),
        parse_mode="HTML",
        reply_markup=username_pay_kb(lang, idx),
    )


@dp.callback_query(F.data.startswith("order_uname_"))
async def on_order_uname(callback: CallbackQuery, bot: Bot) -> None:
    parts = callback.data.split("_")
    idx = int(parts[2])
    pay_code = parts[3]
    uid = callback.from_user.id
    lang = get_lang(uid)
    t = TEXTS[lang]
    await callback.answer()
    if idx < 0 or idx >= len(username_listings):
        return

    item = username_listings[idx]
    method_label = t["btn_pay_ton"] if pay_code == "ton" else t["btn_pay_currency"]
    uname = f"@{callback.from_user.username}" if callback.from_user.username else "yo'q"

    try:
        await bot.send_message(
            ADMIN_ID,
            f"🔗 <b>Username savdosi buyurtmasi</b>\n"
            f"🏷 Username: <b>{item['name']}</b> ({item['price']})\n"
            f"💳 To‘lov usuli: <b>{method_label}</b>\n"
            f"👤 Xaridor ID: <code>{uid}</code> ({uname})\n"
            f"📬 TON manzil: <code>{TON_WALLET}</code>",
            parse_mode="HTML",
        )
    except Exception as exc:
        logging.warning("Adminga username buyurtmasi ketmadi: %s", exc)

    await post_to_channel(
        bot,
        f"🔗 <b>Username Buyurtma</b>\n🏷 Username: <b>{item['name']}</b>\n💳 To‘lov: <b>{method_label}</b>\n👤 Mijoz ID: <code>{uid}</code>\n🤝 Admin: {ADMIN_USERNAME}",
    )
    await callback.message.answer(
        t["username_ordered"].format(
            uname=item["name"],
            method=method_label,
            admin=ADMIN_USERNAME,
        ),
        parse_mode="HTML",
    )
    await send_main(bot, callback.message.chat.id, uid)


@dp.callback_query(F.data == "admin_add_uname")
async def on_admin_add_uname(callback: CallbackQuery) -> None:
    uid = callback.from_user.id
    if uid != ADMIN_ID:
        await callback.answer()
        return
    user_state[uid] = {"step": "admin_add_uname"}
    await callback.answer()
    await callback.message.answer(TEXTS[get_lang(uid)]["ask_admin_uname"], parse_mode="HTML")


@dp.callback_query(F.data == "back_main")
async def on_back_main(callback: CallbackQuery, bot: Bot) -> None:
    uid = callback.from_user.id
    if not await is_subscribed(bot, uid):
        await callback.answer(TEXTS[get_lang(uid)]["not_sub_yet"].format(ch=CHANNEL_USERNAME), show_alert=True)
        return
    await callback.answer()
    await send_main(bot, callback.message.chat.id, uid)


@dp.callback_query(F.data == "open_profile")
async def on_open_profile(callback: CallbackQuery, bot: Bot) -> None:
    uid = callback.from_user.id
    if not await is_subscribed(bot, uid):
        await callback.answer(TEXTS[get_lang(uid)]["not_sub_yet"].format(ch=CHANNEL_USERNAME), show_alert=True)
        return
    lang = get_lang(uid)
    t = TEXTS[lang]
    _, _, usd_uzs = await fetch_live_gram_rates()
    await callback.answer()
    kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=t["btn_back"], callback_data="back_main")]]
    )
    await callback.message.answer(
        t["profile_text"].format(uid=uid, bal=fmt_money(get_bal(uid), usd_uzs)),
        parse_mode="HTML",
        reply_markup=kb,
    )


@dp.callback_query(F.data == "topup_start")
async def on_topup_start(callback: CallbackQuery, bot: Bot) -> None:
    uid = callback.from_user.id
    if not await is_subscribed(bot, uid):
        await callback.answer(TEXTS[get_lang(uid)]["not_sub_yet"].format(ch=CHANNEL_USERNAME), show_alert=True)
        return
    lang = get_lang(uid)
    user_state[uid] = {"step": "topup_amount"}
    await callback.answer()
    await callback.message.answer(TEXTS[lang]["ask_topup"], parse_mode="HTML")


@dp.callback_query(F.data.in_({"gram_buy", "gram_sell"}))
async def on_gram_action(callback: CallbackQuery, bot: Bot) -> None:
    uid = callback.from_user.id
    if not await is_subscribed(bot, uid):
        await callback.answer(TEXTS[get_lang(uid)]["not_sub_yet"].format(ch=CHANNEL_USERNAME), show_alert=True)
        return
    lang = get_lang(uid)
    t = TEXTS[lang]
    gram_uzs, _, usd_uzs = await fetch_live_gram_rates()
    await callback.answer()
    if callback.data == "gram_buy":
        user_state[uid] = {"step": "gram_buy"}
        await callback.message.answer(
            t["ask_gram_buy"].format(
                bal=fmt_money(get_bal(uid), usd_uzs),
                buy_p=fmt_money(calc_buy_uzs(1.0, gram_uzs, usd_uzs), usd_uzs),
            ),
            parse_mode="HTML",
        )
    else:
        user_state[uid] = {"step": "gram_sell"}
        await callback.message.answer(
            t["ask_gram_sell"].format(gram_p=fmt_money(gram_uzs, usd_uzs)),
            parse_mode="HTML",
        )


@dp.callback_query(F.data.startswith("open_nft_"))
async def on_open_nft(callback: CallbackQuery, bot: Bot) -> None:
    uid = callback.from_user.id
    if not await is_subscribed(bot, uid):
        await callback.answer(TEXTS[get_lang(uid)]["not_sub_yet"].format(ch=CHANNEL_USERNAME), show_alert=True)
        return
    lang = get_lang(uid)
    t = TEXTS[lang]
    page = int(callback.data.split("_")[-1])
    await callback.answer()
    await callback.message.answer(
        t["nft_title"].format(count=len(NFT_GIFTS), admin=ADMIN_USERNAME, ton=TON_WALLET),
        parse_mode="HTML",
        reply_markup=nft_catalog_kb(lang, page=page),
    )


@dp.callback_query(F.data.startswith("pick_nft_"))
async def on_pick_nft(callback: CallbackQuery) -> None:
    parts = callback.data.split("_")
    gift_idx = int(parts[2])
    page = int(parts[3])
    uid = callback.from_user.id
    lang = get_lang(uid)
    t = TEXTS[lang]
    if gift_idx < 0 or gift_idx >= len(NFT_GIFTS):
        await callback.answer()
        return
    await callback.answer()
    await callback.message.answer(
        t["nft_selected"].format(gift=NFT_GIFTS[gift_idx], admin=ADMIN_USERNAME, ton=TON_WALLET),
        parse_mode="HTML",
        reply_markup=nft_order_kb(lang, gift_idx, page),
    )


@dp.callback_query(F.data.startswith("order_nft_"))
async def on_order_nft(callback: CallbackQuery, bot: Bot) -> None:
    gift_idx = int(callback.data.split("_")[-1])
    uid = callback.from_user.id
    lang = get_lang(uid)
    t = TEXTS[lang]
    await callback.answer()
    if gift_idx < 0 or gift_idx >= len(NFT_GIFTS):
        return

    gift_name = NFT_GIFTS[gift_idx]
    uname = f"@{callback.from_user.username}" if callback.from_user.username else "yo'q"
    try:
        await bot.send_message(
            ADMIN_ID,
            f"💎 <b>NFT Gift buyurtmasi</b>\n"
            f"🎁 Gift: <b>{gift_name}</b>\n"
            f"👤 Xaridor ID: <code>{uid}</code> ({uname})\n"
            f"💰 To‘lov: <b>Faqat TON</b> (kelishuv asosida)\n"
            f"📬 TON manzil: <code>{TON_WALLET}</code>",
            parse_mode="HTML",
        )
    except Exception as exc:
        logging.warning("Adminga NFT xabari ketmadi: %s", exc)

    await post_to_channel(
        bot,
        f"💎 <b>NFT Buyurtma</b>\n🎁 Gift: <b>{gift_name}</b>\n👤 Mijoz ID: <code>{uid}</code>\n🤝 Savdo: TON ({ADMIN_USERNAME})",
    )
    await callback.message.answer(t["nft_ordered"].format(gift=gift_name, admin=ADMIN_USERNAME), parse_mode="HTML")
    await send_main(bot, callback.message.chat.id, uid)


@dp.callback_query(F.data.startswith("topup_ok_"))
async def on_topup_ok(callback: CallbackQuery, bot: Bot) -> None:
    if callback.from_user.id != ADMIN_ID:
        await callback.answer()
        return
    req_id = int(callback.data.split("_")[-1])
    req = pending_topups.pop(req_id, None)
    await callback.answer()
    if not req:
        await callback.message.answer("So‘rov topilmadi.")
        return

    target_uid = req["uid"]
    amt = req["amount"]
    user_balance_uzs[target_uid] = get_bal(target_uid) + amt

    await callback.message.answer(
        f"✅ Tasdiqlandi: ID <code>{target_uid}</code> ga <b>{amt:,.0f} so‘m</b> qo‘shildi.",
        parse_mode="HTML",
    )
    try:
        await bot.send_message(
            target_uid,
            TEXTS[get_lang(target_uid)]["topup_approved"].format(amt=amt),
            parse_mode="HTML",
        )
    except Exception:
        pass

    await post_to_channel(
        bot,
        f"💳 <b>Hisob to‘ldirildi</b>\n👤 Mijoz ID: <code>{target_uid}</code>\n💵 Summa: <b>{amt:,.0f} so‘m</b>",
    )


@dp.callback_query(F.data.startswith("topup_no_"))
async def on_topup_no(callback: CallbackQuery, bot: Bot) -> None:
    if callback.from_user.id != ADMIN_ID:
        await callback.answer()
        return
    req_id = int(callback.data.split("_")[-1])
    req = pending_topups.pop(req_id, None)
    await callback.answer()
    if not req:
        return
    target_uid = req["uid"]
    await callback.message.answer(f"❌ Rad etildi: ID <code>{target_uid}</code>", parse_mode="HTML")
    try:
        await bot.send_message(target_uid, TEXTS[get_lang(target_uid)]["topup_rejected"])
    except Exception:
        pass


@dp.message(F.photo)
async def on_photo(message: Message, bot: Bot) -> None:
    uid = message.from_user.id
    st = user_state.get(uid)
    if not st or st.get("step") != "topup_receipt":
        return

    lang = get_lang(uid)
    t = TEXTS[lang]
    amt = st["amount"]
    user_state.pop(uid, None)

    req_id = message.message_id
    pending_topups[req_id] = {"uid": uid, "amount": amt}

    uname = f"@{message.from_user.username}" if message.from_user.username else "yo'q"
    admin_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"topup_ok_{req_id}"),
                InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"topup_no_{req_id}"),
            ]
        ]
    )
    try:
        await bot.send_photo(
            chat_id=ADMIN_ID,
            photo=message.photo[-1].file_id,
            caption=(
                f"💳 <b>Hisob to‘ldirish cheki</b>\n"
                f"👤 Foydalanuvchi ID: <code>{uid}</code> ({uname})\n"
                f"💵 Summa: <b>{amt:,.0f} so‘m</b>\n"
                f"{build_cards_block()}"
            ),
            parse_mode="HTML",
            reply_markup=admin_kb,
        )
    except Exception as exc:
        logging.warning("Adminga chek ketmadi: %s", exc)

    await message.answer(t["topup_sent"].format(admin=ADMIN_USERNAME), parse_mode="HTML")
    await send_main(bot, message.chat.id, uid)


@dp.message(F.text)
async def on_text(message: Message, bot: Bot) -> None:
    uid = message.from_user.id
    st = user_state.get(uid)
    if not st:
        return

    lang = get_lang(uid)
    t = TEXTS[lang]
    step = st.get("step")
    raw_text = message.text.strip()

    if step == "admin_add_uname" and uid == ADMIN_ID:
        user_state.pop(uid, None)
        if "|" in raw_text:
            left, right = raw_text.split("|", 1)
            uname_clean = left.strip()
            price_clean = right.strip() or "Kelishuv asosida"
        else:
            uname_clean = raw_text
            price_clean = "Kelishuv asosida"

        if not uname_clean.startswith("@"):
            uname_clean = f"@{uname_clean}"

        username_listings.append({"name": uname_clean, "price": price_clean})
        await message.answer(
            t["admin_uname_added"].format(uname=uname_clean, price=price_clean),
            parse_mode="HTML",
        )
        await send_main(bot, message.chat.id, uid)
        return

    if step == "topup_receipt":
        await message.answer(t["topup_wait_receipt"])
        return

    if step == "gram_sell_wallet":
        if len(raw_text) < 10 or " " in raw_text:
            await message.answer(t["invalid_wallet"])
            return

        grams = st["grams"]
        got_uzs = st["got_uzs"]
        _, _, usd_uzs = await fetch_live_gram_rates()
        user_state.pop(uid, None)

        uname = f"@{message.from_user.username}" if message.from_user.username else "yo'q"
        got_fmt = fmt_money(got_uzs, usd_uzs)

        try:
            await bot.send_message(
                ADMIN_ID,
                f"🔴 <b>GRAM Sotish arizasi (1:1 birja)</b>\n"
                f"👤 Mijoz ID: <code>{uid}</code> ({uname})\n"
                f"📬 Mijoz TON manzili: <code>{raw_text}</code>\n"
                f"⚖️ Miqdor: <b>{grams} GRAM</b>\n"
                f"💵 Summa (1:1): <b>{got_fmt}</b>",
                parse_mode="HTML",
            )
        except Exception as exc:
            logging.warning("Adminga sotuv xabari ketmadi: %s", exc)

        await post_to_channel(
            bot,
            f"🔴 <b>GRAM Sotildi</b>\n⚖️ Miqdor: <b>{grams} GRAM</b>\n👤 Mijoz ID: <code>{uid}</code>\n💵 Summa: <b>{got_fmt}</b>",
        )
        await message.answer(
            t["admin_will_contact_sell"].format(
                grams=grams,
                wallet=raw_text,
                got=got_fmt,
                admin=ADMIN_USERNAME,
            ),
            parse_mode="HTML",
        )
        await send_main(bot, message.chat.id, uid)
        return

    try:
        val = float(raw_text.replace(",", "."))
        if val <= 0:
            raise ValueError
    except ValueError:
        await message.answer(t["invalid_num"], parse_mode="HTML")
        return

    if step == "topup_amount":
        user_state[uid] = {"step": "topup_receipt", "amount": val}
        await message.answer(
            t["topup_card_info"].format(amt=val, cards_block=build_cards_block()),
            parse_mode="HTML",
        )
        return

    gram_uzs, _, usd_uzs = await fetch_live_gram_rates()

    if step == "gram_buy":
        total_uzs = calc_buy_uzs(val, gram_uzs, usd_uzs)
        bal = get_bal(uid)

        if total_uzs > bal:
            await message.answer(
                t["insufficient_bal"].format(
                    need=fmt_money(total_uzs, usd_uzs),
                    bal=fmt_money(bal, usd_uzs),
                ),
                parse_mode="HTML",
            )
            return

        user_state.pop(uid, None)
        user_balance_uzs[uid] = bal - total_uzs
        spent_fmt = fmt_money(total_uzs, usd_uzs)
        uname = f"@{message.from_user.username}" if message.from_user.username else "yo'q"

        try:
            await bot.send_message(
                ADMIN_ID,
                f"🟢 <b>GRAM Sotib olish buyurtmasi</b>\n"
                f"👤 Xaridor ID: <code>{uid}</code> ({uname})\n"
                f"⚖️ Miqdor: <b>{val} GRAM</b>\n"
                f"💳 To‘langan summa: <b>{spent_fmt}</b>\n"
                f"🤝 Admin grammini berishi kerak.",
                parse_mode="HTML",
            )
        except Exception as exc:
            logging.warning("Adminga xarid xabari ketmadi: %s", exc)

        await post_to_channel(
            bot,
            f"🟢 <b>GRAM Sotib olindi</b>\n⚖️ Miqdor: <b>{val} GRAM</b>\n👤 Mijoz ID: <code>{uid}</code>\n💵 Summa: <b>{spent_fmt}</b>",
        )
        await message.answer(
            t["admin_will_contact_buy"].format(
                grams=val,
                spent=spent_fmt,
                admin=ADMIN_USERNAME,
            ),
            parse_mode="HTML",
        )
        await send_main(bot, message.chat.id, uid)
        return

    if step == "gram_sell":
        got_uzs = val * gram_uzs
        user_state[uid] = {
            "step": "gram_sell_wallet",
            "grams": val,
            "got_uzs": got_uzs,
        }
        await message.answer(
            t["ask_sell_wallet"].format(
                grams=val,
                got=fmt_money(got_uzs, usd_uzs),
            ),
            parse_mode="HTML",
        )


async def healthcheck(request: web.Request) -> web.Response:
    return web.Response(text="OK")


async def start_web_server() -> None:
    app = web.Application()
    app.router.add_get("/", healthcheck)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()


async def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN muhit o'zgaruvchisi (Render Environment) o'rnatilmagan!")
    await start_web_server()
    bot = Bot(token=BOT_TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
