# Milliy Taomlar — menyu sayti (demo)

NFC stiker va QR kod orqali telefonda ochiladigan restoran menyusi.

- Bitta fayl: `index.html` (CSS va JS ichida)
- 4 til: **o’zbekcha** (asosiy), русский, 한국어, English. Tanlangan til eslab qolinadi
- Narxlar Koreya vonida (₩)
- Rasmlar: [Pexels](https://www.pexels.com/license/) (bepul litsenziya)

## Havolalar

| Qayerda | Havola |
|---|---|
| **Asosiy (Dokploy, NFC va QR shu yerga)** | https://milliytaomlar.hanustoz.tech/ |
| GitHub Pages (zaxira) | https://jtoxtasinov0-sys.github.io/Oshxona-menyu/ |
| Ruscha ochish | `...?lang=ru` |
| Koreyscha ochish | `...?lang=ko` |
| Inglizcha ochish | `...?lang=en` |

## Chop etish uchun fayllar (`chop-etish/`)

- `stol-kartochka-A6.pdf` — ikki tomonlama stol kartochkasi (105×148 mm, 2 sahifa), bosmaxonaga shu faylni bering
  - Ikkala tomon: QR, NFC doirasi va “Qanday foydalaniladi?” qo’llanma — o’zbekcha birinchi, keyin ruscha, koreyscha, inglizcha
  - QR tepasida **“Samsung · Android”**, NFC tepasida **“iPhone”** yozuvi; NFC ostida “1–2 soniya tekkizib turing”
    (Android’da NFC ko’pincha o’chiq bo’ladi va uni sayt yoki stiker yoqa olmaydi, shuning uchun ularga QR)
  - NFC doiralari ikki tomonda aynan bir-birining orqasida: bitta stiker ikkala tomonga ishlaydi
- `stol-kartochka-old.png`, `stol-kartochka-orqa.png` — o’sha kartochka rasm ko’rinishida
- `manba/` — kartochkani boshqa domen bilan qayta yasash uchun skript:
  `pip install qrcode`, keyin `python3 make_card.py [domen] && node render2.js` (Playwright kerak)
- `qr-milliytaomlar.svg` / `.png` — faqat QR kod (istalgan o’lchamda sifat yo’qotmaydi: SVG)

Hammasi `https://milliytaomlar.hanustoz.tech/` ga olib boradi.

## Narx yoki taomni o’zgartirish (terminalsiz)

1. GitHub’da `index.html` faylini oching → qalam (✏️ Edit) tugmasini bosing.
2. `MENYU` deb yozilgan joyni toping. Har bir taomda:
   - `p:13000` — narx (vonda)
   - `n:{ uz:"…", ru:"…", ko:"…", en:"…" }` — nomi 4 tilda
   - `d:{ … }` — qisqa tavsif 4 tilda
   - `img:"7866189"` — Pexels rasm raqami (pexels.com/photo/…-**7866189**/)
3. Pastdagi yashil **Commit changes** tugmasini bosing. 1–2 daqiqada sayt yangilanadi.

Manzil, telefon va ish vaqti `T` (matnlar) bo’limida va fayl pastidagi `tel:` havolalarida.

## Dokploy (Hostinger VPS) ga joylash

Repoda tayyor `Dockerfile` bor — Dokploy uni o’zi yig’ib ishga tushiradi.

1. Dokploy paneli → **Projects** → **Create Project** → nom: `milliy-taomlar`.
2. Loyiha ichida **Create Service** → **Application** → nom: `menyu`.
3. **General** bo’limi → **Provider**: `Git` (yoki GitHub ulangan bo’lsa `GitHub`):
   - Repository URL: `https://github.com/jtoxtasinov0-sys/oshxona-menyu.git`
   - Branch: `main`
   - **Save**.
4. **Build Type**: `Dockerfile` (Docker File: `Dockerfile`) → **Save**.
5. Yuqoridagi **Deploy** tugmasini bosing. Holat “done” bo’lishini kuting.
6. **Domains** bo’limi → **Add Domain**:
   - Tez sinash uchun: zar (🎲) belgisini bosing — `….traefik.me` manzil beriladi.
   - O’z domeningiz uchun: Host = `menu.sizningdomen.com`, Path = `/`, Container Port = `80`,
     HTTPS = yoqilgan, Certificate = `Let's Encrypt`. Domen DNS’ida **A record** →
     VPS IP manzili (Hostinger → Domains → DNS).
7. Keyinchalik GitHub’dagi o’zgarishlar avtomatik chiqishi uchun: GitHub provider’dan foydalaning
   va **Autodeploy** ni yoqing (yoki Git provider bilan har safar **Deploy** ni bosing).

## NFC stikerga yozish

1. Telefonga **NFC Tools** ilovasini o’rnating (Android / iPhone).
2. **Write** → **Add a record** → **URL / URI** → havolani kiriting.
3. **Write** ni bosing va telefonni stikerga tekkizing.
4. ⚠️ “Lock tag / Make read-only” ni faqat havola **yakuniy** bo’lganda bosing — bu qaytarib bo’lmaydi.
