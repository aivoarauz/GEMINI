# Gemini Pro / AI Video Kanal Sotuvchi Bot

Aiogram 3 (async) asosida yozilgan to'liq funksional Telegram bot.

## Imkoniyatlari

- 🧠 Gemini Pro obunasini sotish (miqdor 1–10 tagacha, narx admin panelda o'zgartiriladi)
- 🎬 Yopiq (AI video) kanal linkini sotish
- 💳 Chek (skrinshot) orqali to'lovni tasdiqlash — admin ✅/❌ tugmalar bilan javob beradi
- 🔗 Gemini linkini admin qo'lda yuboradi, kanal linki avtomatik yuboriladi
- 👥 Majburiy obuna (kanalga a'zo bo'lmaganlar botdan foydalana olmaydi)
- 🎁 Referal tizimi (N ta do'st taklif qilinganda adminga murojaat qilish haqida xabar)
- 💬 Izohlar bo'limi (foydalanuvchilar yozadi, hammasi ko'ra oladi)
- 📖 Yo'riqnoma, 🆘 Yordam (admin username)
- ⚙️ To'liq admin panel: karta raqami/egasi, narxlar, matnlar, majburiy kanal, referal sozlamalari — barchasi botning o'zidan o'zgartiriladi
- 📣 Reklama (barcha foydalanuvchilarga xabar yuborish)
- 📊 Statistika

## 1. Tayyorgarlik

1. **Bot yaratish** — [@BotFather](https://t.me/BotFather) ga `/newbot` yuboring, tokenni saqlab qo'ying.
2. **O'z ID'ingizni bilish** — [@userinfobot](https://t.me/userinfobot) ga `/start` yozing, u sizning raqamli ID'ingizni beradi. Shu ID `ADMIN_IDS` bo'ladi.
3. **Botni kanalga admin qilib qo'shish** — `@aivora_uz` kanaliga botni **admin** sifatida qo'shing. Bu shart, aks holda bot foydalanuvchilarning kanalga a'zoligini tekshira olmaydi.

## 2. Lokal ishga tushirish (test uchun)

```bash
git clone <repo>
cd gemini_bot
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# .env faylini oching va BOT_TOKEN, ADMIN_IDS qiymatlarini kiriting
python main.py
```

Botga Telegram'da `/start` yozing.

## 3. Render.com'ga 24/7 deploy qilish

1. Kodni GitHub repositoryga yuklang.
2. [Render.com](https://render.com) da **New +** → **Web Service** tanlang.
3. Repository'ni ulang.
4. Sozlamalar:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python main.py`
   - **Instance Type:** Free yoki istalgan tarif
5. **Environment** bo'limida quyidagilarni qo'shing:
   - `BOT_TOKEN` — bot tokeningiz
   - `ADMIN_IDS` — sizning Telegram ID'ingiz (bir nechta bo'lsa vergul bilan: `111,222`)
   - `DB_PATH` — `/data/bot_database.db` (pastdagi eslatmaga qarang)
6. **Deploy** tugmasini bosing.

Render avtomatik `PORT` environment o'zgaruvchisini beradi — kod buni o'zi o'qiydi, qo'shimcha sozlash shart emas. `main.py` ichida oddiy health-check web-server ishga tushiriladi, shu sababli Render buni "Web Service" sifatida to'g'ri tan oladi va bot polling rejimida 24/7 ishlaydi.

### ⚠️ Muhim: ma'lumotlar bazasi haqida

Render'ning bepul "Web Service"ida fayl tizimi **disk qayta yaratilganda** (masalan yangi deploy) tozalanadi. Ya'ni SQLite fayldagi foydalanuvchilar/buyurtmalar tarixi yo'qolib qolishi mumkin.

Buning oldini olish uchun:

1. Render dashboard'da **Disks** bo'limidan **Add Disk** qiling (masalan 1GB, `/data` yo'liga ulang).
2. Environment Variables'ga `DB_PATH=/data/bot_database.db` deb qo'shing.

Shunda baza doimiy diskda saqlanadi va deploy qilinganda ham yo'qolmaydi.

## 4. Admin paneldan boshqarish

Botga `/admin` buyrug'ini yozing yoki asosiy menyudagi **⚙️ Admin panel** tugmasini bosing. U yerdan quyidagilarni o'zgartirishingiz mumkin:

- 💳 Karta raqami / 👤 Karta egasi
- 💰 Gemini narxi / 💰 Kanal narxi
- 🔗 Yopiq kanal linki
- ℹ️ "Gemini nima?" matni
- 📖 Yo'riqnoma matni
- 👥 Referal chegarasi (nechta taklifda xabar yuboriladi) / 💬 Referal xabari matni
- 🆘 Admin username (Yordam tugmasi uchun)
- 📢 Majburiy obuna kanali
- 📣 Reklama yuborish (barcha foydalanuvchilarga)
- 📊 Statistika

## Fayllar tuzilishi

```
gemini_bot/
├── main.py             # Kirish nuqtasi, bot va web-server ishga tushiriladi
├── config.py           # Environment o'zgaruvchilar
├── database.py         # SQLite bilan ishlash
├── texts.py            # Standart matnlar/sozlamalar
├── states.py            # FSM holatlari
├── keyboards.py         # Barcha inline klaviaturalar
├── utils.py             # Obunani tekshirish funksiyasi
├── middleware.py        # Majburiy obuna middleware
├── handlers_user.py     # Oddiy foydalanuvchi handlerlari
├── handlers_admin.py    # Admin panel va buyurtmalarni boshqarish
├── requirements.txt
├── .env.example
└── .gitignore
```
