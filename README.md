# Milliy Taomlar — menyu sayti

NFC stiker va QR kod orqali telefonda ochiladigan restoran menyusi + **admin panel**.

- 4 til: **o’zbekcha** (asosiy), русский, 한국어, English. Tanlangan til eslab qolinadi
- Narxlar Koreya vonida (₩)
- Rasmlar: [Pexels](https://www.pexels.com/license/) (bepul litsenziya) yoki admin paneldan yuklangan o’z rasmlaringiz
- **Admin panel** (`/admin`): tugagan taomni bir bosishda “Tugadi” qilish va qaytarish, yangi taom qo’shish
  (telefondan rasm bilan), narx/nomni o’zgartirish, tartibini almashtirish, o’chirish

### Fayllar

| Fayl | Nima |
|---|---|
| `index.html` | Mijozlar ko’radigan menyu sahifasi |
| `admin.html` | Admin panel |
| `server.js` | Kichik Node.js server (tashqi kutubxonasiz) — sahifalar, API, rasm yuklash |
| `menu.json` | **Boshlang’ich** menyu — server birinchi marta ishga tushganda shundan nusxa oladi |
| `Dockerfile` | Dokploy shu fayl bilan yig’adi |

## Havolalar

| Qayerda | Havola |
|---|---|
| **Asosiy (Dokploy, NFC va QR shu yerga)** | https://milliytaomlar.hanustoz.tech/ |
| **Admin panel** | https://milliytaomlar.hanustoz.tech/admin |
| GitHub Pages (zaxira, admin paneldagi o’zgarishlar bu yerda ko’rinmaydi) | https://jtoxtasinov0-sys.github.io/Oshxona-menyu/ |
| Ruscha ochish | `...?lang=ru` |
| Koreyscha ochish | `...?lang=ko` |
| Inglizcha ochish | `...?lang=en` |

## Chop etish uchun fayllar (`chop-etish/`)

- `stol-kartochka-A6.pdf` — ikki tomonlama stol kartochkasi (105×148 mm, 2 sahifa), bosmaxonaga shu faylni bering
  - Ikkala tomon: QR, NFC doirasi va “Qanday foydalaniladi?” qo’llanma — o’zbekcha birinchi, keyin ruscha, koreyscha, inglizcha
  - NFC doiralari ikki tomonda aynan bir-birining orqasida: bitta stiker ikkala tomonga ishlaydi
- `stol-kartochka-old.png`, `stol-kartochka-orqa.png` — o’sha kartochka rasm ko’rinishida
- `manba/` — kartochkani boshqa domen bilan qayta yasash uchun skript
- `qr-milliytaomlar.svg` / `.png` — faqat QR kod (istalgan o’lchamda sifat yo’qotmaydi: SVG)

Hammasi `https://milliytaomlar.hanustoz.tech/` ga olib boradi.

## Admin panel — taomlarni boshqarish

Manzil: **https://milliytaomlar.hanustoz.tech/admin** → parolni kiriting (parol Dokploy’da o’rnatiladi, pastga qarang).

- **Taom tugadi** → taom yonidagi yashil tugmani bosing, u qizil “Tugadi” bo’ladi. Qaytib kelganda yana bosing.
  O’zgarish darhol saqlanadi, mijozlarning telefonida ochiq turgan menyu ham 1 daqiqa ichida yangilanadi.
- **Tugagan taom mijozga qanday ko’rinsin** — sahifa pastidagi sozlama:
  “Kulrang, Tugadi belgisi bilan” (bo’lim oxirida, oq-qora rasm) yoki “Butunlay yashirilsin”.
- **Yangi taom** → pastdagi oltin “Yangi taom qo’shish” tugmasi: kategoriya, nom, tavsif, narx, o’lchov, rasm
  (telefon galereyasi yoki kamerasidan — avtomatik kichraytiriladi). Ruscha/koreyscha/inglizcha nomlar ixtiyoriy:
  yozilmasa, o’sha tillarda ham o’zbekcha nom chiqadi.
- **Tahrirlash** → taom nomini bosing: narx, nom, rasm, belgi (Xit/Yangi/Achchiq/Mavsumiy), tavsiya kartochka,
  menyudagi o’rni (Yuqoriga/Pastga), butunlay o’chirish.
- “Rasm kesilmasin — to’liq ko’rinsin” belgisi qo’yilsa, rasm menyuda kesilmasdan butunligicha chiqadi (Osh shunday).

Admin paneldagi barcha o’zgarishlar serverdagi `/app/data/menu.json` ga, yuklangan rasmlar `/app/data/uploads/` ga
yoziladi. Shuning uchun Dokploy’da **volume** ulash shart (pastdagi 3-qadam), aks holda qayta deploy qilinganda
o’zgarishlar o’chib ketadi — admin panel buni sariq ogohlantirish bilan ko’rsatadi.

> `menu.json` (repodagi) faqat **boshlang’ich** menyu. Sayt ishga tushgandan keyin menyuni faqat admin paneldan
> o’zgartiring — repodagi `menu.json` ni tahrirlash ishlab turgan saytga ta’sir qilmaydi.

Manzil, telefon va ish vaqti `index.html` dagi `T` (matnlar) bo’limida va fayl pastidagi `tel:` havolalarida.

## Dokploy (Hostinger VPS) ga joylash

Repoda tayyor `Dockerfile` bor (Node.js 22) — Dokploy uni o’zi yig’ib ishga tushiradi. Konteyner 80-portda ishlaydi.

### Allaqachon joylangan sayt uchun (admin panelni yoqish) — 3 ta qadam

1. **Parol**: Dokploy → `milliy-taomlar` → `menyu` ilovasi → **Environment** bo’limi → quyidagini yozing → **Save**:
   ```
   ADMIN_PASSWORD=bu-yerga-murakkab-parol
   ```
   Parolni hech kimga bermang va GitHub’ga yozmang. Parolni almashtirsangiz, barcha qurilmalar admin paneldan chiqib ketadi.
2. **Volume (doimiy saqlash)**: **Advanced** bo’limi → **Volumes / Mounts** → **Add Volume**:
   - Mount type: **Volume Mount**
   - Volume Name: `milliy-taomlar-data`
   - Mount Path: `/app/data`
   - **Save**
3. Yuqoridagi **Deploy** tugmasini bosing. So’ng https://milliytaomlar.hanustoz.tech/admin ni oching.

Domen sozlamasi o’zgarmaydi (Container Port = `80`).

### Noldan joylash

1. Dokploy paneli → **Projects** → **Create Project** → nom: `milliy-taomlar`.
2. Loyiha ichida **Create Service** → **Application** → nom: `menyu`.
3. **General** bo’limi → **Provider**: `Git` (yoki GitHub ulangan bo’lsa `GitHub`):
   - Repository URL: `https://github.com/jtoxtasinov0-sys/oshxona-menyu.git`
   - Branch: `main`
   - **Save**.
4. **Build Type**: `Dockerfile` (Docker File: `Dockerfile`) → **Save**.
5. Yuqoridagi “Allaqachon joylangan sayt uchun” bo’limidagi 1- va 2-qadamlar (parol va volume).
6. **Deploy** tugmasini bosing. Holat “done” bo’lishini kuting.
7. **Domains** bo’limi → **Add Domain**:
   - Tez sinash uchun: zar (🎲) belgisini bosing — `….traefik.me` manzil beriladi.
   - O’z domeningiz uchun: Host = `menu.sizningdomen.com`, Path = `/`, Container Port = `80`,
     HTTPS = yoqilgan, Certificate = `Let's Encrypt`. Domen DNS’ida **A record** →
     VPS IP manzili (Hostinger → Domains → DNS).
8. Keyinchalik GitHub’dagi o’zgarishlar avtomatik chiqishi uchun: GitHub provider’dan foydalaning
   va **Autodeploy** ni yoqing (yoki Git provider bilan har safar **Deploy** ni bosing).
   Volume ulangan bo’lsa, qayta deploy admin paneldagi menyuga tegmaydi.

### Kompyuterda sinash

```
ADMIN_PASSWORD=test123 PORT=8080 node server.js
```
→ http://localhost:8080 (menyu) va http://localhost:8080/admin (admin). Ma’lumotlar `./data/` papkasiga yoziladi.

## NFC stikerga yozish

1. Telefonga **NFC Tools** ilovasini o’rnating (Android / iPhone).
2. **Write** → **Add a record** → **URL / URI** → havolani kiriting.
3. **Write** ni bosing va telefonni stikerga tekkizing.
4. ⚠️ “Lock tag / Make read-only” ni faqat havola **yakuniy** bo’lganda bosing — bu qaytarib bo’lmaydi.
