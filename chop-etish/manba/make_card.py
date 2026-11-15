import os
import sys
import tempfile
import qrcode

DOMAIN = sys.argv[1] if len(sys.argv) > 1 else "milliytaomlar.hanustoz.tech"   # faqat shu qatorni almashtiring
URL = "https://" + DOMAIN + "/"
WORK = os.environ.get("WORK") or tempfile.gettempdir()   # card2.html shu yerga yoziladi, render2.js shu yerdan o'qiydi

q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=0)
q.add_data(URL); q.make(fit=True)
m = q.get_matrix(); n = len(m)
path = "".join(f"M{x},{y}h1v1h-1z" for y, r in enumerate(m) for x, v in enumerate(r) if v)
QR = f'<svg viewBox="0 0 {n} {n}" shape-rendering="crispEdges"><path d="{path}" fill="#0A3D33"/></svg>'

EMBLEM = '''<svg class="logo" viewBox="0 0 48 48"><g transform="translate(24 24)">
<rect x="-16.5" y="-16.5" width="33" height="33" rx="4" fill="#C9A14A"/><rect x="-16.5" y="-16.5" width="33" height="33" rx="4" fill="#C9A14A" transform="rotate(45)"/>
<circle r="13.6" fill="#0F5B4B"/><circle r="11.4" fill="none" stroke="#EBCF85" stroke-width=".8" stroke-dasharray="1.4 1.9"/>
<path d="M0-6.6 1.9-1.9 6.6 0 1.9 1.9 0 6.6-1.9 1.9-6.6 0-1.9-1.9Z" fill="#EBCF85"/><circle r="1.6" fill="#0F5B4B"/></g></svg>'''
PHONE = '''<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
<rect x="7" y="9" width="10" height="13.5" rx="2"/><path d="M11 19.6h2"/><path d="M9.2 6.4a4 4 0 0 1 5.6 0"/><path d="M6.9 4a7.3 7.3 0 0 1 10.2 0"/></svg>'''


def qr_way(device, caption_html):
    return f'''<div class="way"><span class="device">{device}</span>
      <div class="qrbox">{QR}</div><div class="cap">{caption_html}</div></div>'''


def nfc_way(device, caption_html):
    return f'''<div class="way"><span class="device">{device}</span>
      <div class="nfcwrap"><div class="nfc">{PHONE}<span>NFC</span></div></div><div class="cap">{caption_html}</div></div>'''


def page(side, sub, ways, orword, guide_title, steps, foot_note=""):
    w = "".join(ways)
    st = "".join(f'<li><i>{i+1}</i><div>{s}</div></li>' for i, s in enumerate(steps))
    note = f"<span>{foot_note}</span>" if foot_note else ""
    return f'''<section class="page {side}">
  <header>{EMBLEM}<h1>Milliy Taomlar</h1><div class="sub">{sub}</div></header>
  <div class="ways">{w}<span class="or">{orword}</span></div>
  <div class="guide"><h2>{guide_title}</h2><ol>{st}</ol></div>
  <footer><b>{DOMAIN}</b>{note}</footer>
</section>'''


def ko(s):
    return f'<span lang="ko">{s}</span>'


def multi(uz, ru, k, en):
    """O'zbekcha — asosiy (qalin), keyin ruscha, koreyscha, inglizcha."""
    return f"<b>{uz}</b><br>{ru}<br>{ko(k)}<br>{en}"


# Ikkala tomon bir xil: o'zbekcha birinchi (yirik), keyin ru / ko / en.
# Orqa tomon ko'zgu: NFC chapda, QR o'ngda — bitta stiker ikkala tomonga xizmat qiladi.
# Har bir usul tepasida qaysi telefon uchunligi: Samsung/Android'da NFC ko'pincha o'chiq -> QR,
# iPhone'da (XS va yangilari) NFC doim yoqiq -> tekkizish.
SUB = "MENYU · МЕНЮ · " + ko("메뉴") + " · MENU"
OR = "yoki · или · " + ko("또는") + " · or"
TITLE = "Qanday foydalaniladi? · How to use"
QR_WAY = qr_way("Samsung · Android", multi("Kamerani QR kodga qarating", "Наведите камеру на QR-код", "카메라로 QR 코드를 스캔하세요", "Point your camera at the QR code"))
NFC_WAY = nfc_way("iPhone", multi("Telefon <em>tepasini</em> tekkizing<br><em>1–2 soniya</em> ushlab turing<br>Ekran yoniq bo’lsin",
                                   "Приложите <em>верхом телефона</em><br>на <em>1–2 сек.</em>, экран включён",
                                   "화면 켜고 <em>윗부분</em>을 <em>1~2초</em> 대세요",
                                   "Screen on · <em>top</em> of phone · <em>1–2 sec</em>"))
STEPS = [multi("Skanerlang yoki tekkizing", "Сканируйте или приложите", "스캔하거나 휴대폰을 대세요", "Scan or tap your phone"),
         multi("Havolani bosing", "Нажмите на ссылку", "링크를 누르세요", "Tap the link"),
         multi("Tilni tanlang", "Выберите язык", "언어를 선택하세요", "Choose your language"),
         multi("Buyurtma bering", "Закажите у официанта", "직원에게 주문하세요", "Order from your waiter")]

front = page("front", SUB, [QR_WAY, NFC_WAY], OR, TITLE, STEPS)
back = page("back", SUB, [NFC_WAY, QR_WAY], OR, TITLE, STEPS)

CSS = r'''
@page{size:105mm 148mm;margin:0}
:root{--b:0mm}
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:#0A3D33}   /* Chrome PDF sahifani ~0.2 mm kattaroq qiladi: chet kulrang emas, yashil chiqsin */
body{font-family:Manrope,"Noto Sans KR",sans-serif;-webkit-print-color-adjust:exact;print-color-adjust:exact}
[lang=ko]{font-family:"Noto Sans KR",Manrope,sans-serif}
.page{
  width:calc(105mm + 2*var(--b));height:calc(148mm + 2*var(--b));position:relative;overflow:hidden;color:#fff;
  display:flex;flex-direction:column;align-items:center;padding:calc(6mm + var(--b)) calc(6.5mm + var(--b)) calc(5mm + var(--b));
  page-break-after:always;break-after:page;
  background:
    radial-gradient(120% 60% at 50% 0%,rgba(22,119,95,.95),transparent 65%),
    url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='56' height='56' viewBox='0 0 56 56'%3E%3Cg fill='none' stroke='%23EBCF85' stroke-opacity='.12' stroke-width='1'%3E%3Cpath d='M28 12l4.6 11.4L44 28l-11.4 4.6L28 44l-4.6-11.4L12 28l11.4-4.6z'/%3E%3Ccircle cx='0' cy='0' r='7'/%3E%3Ccircle cx='56' cy='0' r='7'/%3E%3Ccircle cx='0' cy='56' r='7'/%3E%3Ccircle cx='56' cy='56' r='7'/%3E%3C/g%3E%3C/svg%3E"),
    #0A3D33;
}
.page::after{content:"";position:absolute;inset:calc(3mm + var(--b));border:.35mm solid rgba(235,207,133,.55);border-radius:4mm;pointer-events:none}
header{display:flex;flex-direction:column;align-items:center}
.logo{width:8mm;height:8mm}
h1{font:700 19.5pt/1 "Playfair Display",serif;margin-top:1.6mm}
.sub{margin-top:1.6mm;font-size:6.8pt;line-height:3mm;height:3mm;font-weight:800;letter-spacing:.24em;color:#EBCF85}
.sub [lang=ko]{letter-spacing:.06em}

.ways{position:relative;display:grid;grid-template-columns:1fr 1fr;gap:3.2mm;width:100%;margin-top:3.3mm}
.way{display:flex;flex-direction:column;align-items:center;padding:3.8mm 1.8mm 2.4mm;border-radius:4mm;
  background:rgba(255,255,255,.06);border:.3mm solid rgba(235,207,133,.45)}
.device{font-size:7.4pt;line-height:4.4mm;height:4.4mm;padding:0 3mm;border-radius:99mm;font-weight:800;letter-spacing:.04em;white-space:nowrap;
  color:#0A3D33;background:linear-gradient(#F3DE9F,#D9B55E);box-shadow:0 0 0 .3mm rgba(255,255,255,.25);margin-bottom:1.9mm}
.qrbox{background:#fff;border-radius:2.6mm;padding:3.3mm;box-shadow:0 0 0 .6mm rgba(235,207,133,.7)}
.qrbox svg{display:block;width:23.8mm;height:23.8mm}
.nfcwrap{width:30.4mm;height:30.4mm;display:grid;place-items:center;border-radius:50%;border:.45mm dashed rgba(235,207,133,.75)}
.nfc{width:25.6mm;height:25.6mm;border-radius:50%;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:.6mm;
  background:radial-gradient(circle at 35% 30%,#F8E7B4,#C9A14A 60%,#A87F2C);color:#2D2108;
  box-shadow:0 0 0 1.2mm rgba(235,207,133,.18),inset 0 .6mm 0 rgba(255,255,255,.5)}
.nfc svg{width:11.6mm;height:11.6mm}
.nfc span{font-size:8.5pt;font-weight:800;letter-spacing:.2em}
.cap{margin-top:2.2mm;text-align:center;font-size:6pt;line-height:1.32;color:rgba(255,255,255,.86)}
.cap b{color:#fff;font-weight:800;font-size:7.3pt;line-height:1.42}
.cap em{font-style:normal;font-weight:800;color:#EBCF85;white-space:nowrap}
.or{position:absolute;left:50%;top:2.2mm;transform:translateX(-50%);padding:.9mm 2.4mm;line-height:1.2;border-radius:99mm;white-space:nowrap;
  background:#0A3D33;border:.35mm solid #C9A14A;color:#EBCF85;font-size:6.6pt;font-weight:800}
.or{font-size:6pt;padding:.9mm 2mm;top:0;transform:translate(-50%,-50%)}

.guide{width:100%;margin-top:4mm;padding:3.2mm 3.4mm 3.4mm;border-radius:4mm;background:#FBF7F0;color:#1B2724}
.guide h2{font:700 10.5pt/1.1 "Playfair Display",serif;color:#0A3D33;text-align:center;margin-bottom:2.6mm}
.guide ol{list-style:none;display:grid;grid-template-columns:1fr 1fr;gap:2.4mm 3mm}
.guide li{display:flex;gap:1.8mm;align-items:flex-start;font-size:7.4pt;line-height:1.32;color:#36433E}
.guide li b{color:#0A3D33;font-weight:800}
.guide i{flex:none;width:5.2mm;height:5.2mm;border-radius:50%;display:grid;place-items:center;font-style:normal;font-weight:800;font-size:7.4pt;
  color:#fff;background:#0F5B4B;box-shadow:0 0 0 .5mm #EBCF85}
.guide{margin-top:3mm;padding:2.6mm 3.2mm 2.6mm}
.guide h2{font-size:9.6pt;margin-bottom:2.2mm}
.guide ol{gap:2.2mm 2.6mm}
.guide li{font-size:5.9pt;line-height:1.32}
.guide li b{font-size:7.2pt;line-height:1.4}
.guide i{width:5mm;height:5mm;font-size:7pt}

footer{margin-top:auto;display:flex;flex-direction:column;align-items:center;gap:.8mm}
footer b{font-size:8.6pt;color:#EBCF85;letter-spacing:.02em}
footer span{font-size:6.3pt;color:rgba(255,255,255,.66)}
'''
html = f'''<!doctype html><html lang="uz"><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Manrope:wght@500;600;700;800&family=Noto+Sans+KR:wght@500;700;800&family=Playfair+Display:wght@700&display=swap">
<style>{CSS}</style></head><body>{front}{back}</body></html>'''
open(os.path.join(WORK, "card2.html"), "w", encoding="utf-8").write(html)
# Bosmaxona uchun: har tomondan 2 mm fon (bleed) qo'shilgan, kesish o'lchami baribir 105x148
open(os.path.join(WORK, "card2-bleed.html"), "w", encoding="utf-8").write(html.replace("<body>", '<body style="--b:2mm">', 1))
print("domain", DOMAIN, "qr modules", n)
