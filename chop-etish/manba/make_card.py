import sys
import qrcode

DOMAIN = sys.argv[1] if len(sys.argv) > 1 else "milliytaomlar.hanustoz.tech"   # faqat shu qatorni almashtiring
URL = "https://" + DOMAIN + "/"
WORK = "/tmp/claude-0/-home-user-oshxona-menyu/3922530d-0e4c-5ed0-bb9e-ae44f109b79e/scratchpad/print/"

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
<rect x="5.5" y="3" width="9" height="16" rx="2"/><path d="M9 16h2"/><path d="M17.5 8.5a5 5 0 0 1 0 6"/><path d="M19.8 6.3a8.2 8.2 0 0 1 0 10.4"/></svg>'''


def qr_way(title, caption_html):
    return f'''<div class="way"><span class="tagline">{title}</span>
      <div class="qrbox">{QR}</div><div class="cap">{caption_html}</div></div>'''


def nfc_way(title, caption_html):
    return f'''<div class="way"><span class="tagline">{title}</span>
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
SUB = "MENYU · МЕНЮ · " + ko("메뉴") + " · MENU"
OR = "yoki · или · " + ko("또는") + " · or"
TITLE = "Qanday foydalaniladi? · How to use"
QR_WAY = qr_way("QR", multi("Kamerani QR kodga qarating", "Наведите камеру на QR-код", "카메라로 QR 코드를 스캔하세요", "Point your camera at the QR code"))
NFC_WAY = nfc_way("NFC", multi("Telefonni doiraga tekkizing", "Приложите телефон к кругу", "휴대폰을 원에 대세요", "Tap your phone on the circle"))
STEPS = [multi("Skanerlang yoki tekkizing", "Сканируйте или приложите", "스캔하거나 휴대폰을 대세요", "Scan or tap your phone"),
         multi("Havolani bosing", "Нажмите на ссылку", "링크를 누르세요", "Tap the link"),
         multi("Tilni tanlang", "Выберите язык", "언어를 선택하세요", "Choose your language"),
         multi("Buyurtma bering", "Закажите у официанта", "직원에게 주문하세요", "Order from your waiter")]

front = page("front", SUB, [QR_WAY, NFC_WAY], OR, TITLE, STEPS)
back = page("back", SUB, [NFC_WAY, QR_WAY], OR, TITLE, STEPS)

CSS = r'''
@page{size:105mm 148mm;margin:0}
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:#555}
body{font-family:Manrope,"Noto Sans KR",sans-serif;-webkit-print-color-adjust:exact;print-color-adjust:exact}
[lang=ko]{font-family:"Noto Sans KR",Manrope,sans-serif}
.page{
  width:105mm;height:148mm;position:relative;overflow:hidden;color:#fff;
  display:flex;flex-direction:column;align-items:center;padding:6.6mm 6.5mm 5.6mm;
  page-break-after:always;break-after:page;
  background:
    radial-gradient(120% 60% at 50% 0%,rgba(22,119,95,.95),transparent 65%),
    url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='56' height='56' viewBox='0 0 56 56'%3E%3Cg fill='none' stroke='%23EBCF85' stroke-opacity='.12' stroke-width='1'%3E%3Cpath d='M28 12l4.6 11.4L44 28l-11.4 4.6L28 44l-4.6-11.4L12 28l11.4-4.6z'/%3E%3Ccircle cx='0' cy='0' r='7'/%3E%3Ccircle cx='56' cy='0' r='7'/%3E%3Ccircle cx='0' cy='56' r='7'/%3E%3Ccircle cx='56' cy='56' r='7'/%3E%3C/g%3E%3C/svg%3E"),
    #0A3D33;
}
.page::after{content:"";position:absolute;inset:3mm;border:.35mm solid rgba(235,207,133,.55);border-radius:4mm;pointer-events:none}
header{display:flex;flex-direction:column;align-items:center}
.logo{width:9.5mm;height:9.5mm}
h1{font:700 19.5pt/1 "Playfair Display",serif;margin-top:1.6mm}
.sub{margin-top:1.6mm;font-size:6.8pt;line-height:3mm;height:3mm;font-weight:800;letter-spacing:.24em;color:#EBCF85}
.sub [lang=ko]{letter-spacing:.06em}

.ways{position:relative;display:grid;grid-template-columns:1fr 1fr;gap:3.2mm;width:100%;margin-top:4mm}
.way{display:flex;flex-direction:column;align-items:center;padding:3mm 1.8mm 2.4mm;border-radius:4mm;
  background:rgba(255,255,255,.06);border:.3mm solid rgba(235,207,133,.45)}
.tagline{font-size:6.6pt;line-height:3mm;height:3mm;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:#EBCF85;margin-bottom:2mm}
.qrbox{background:#fff;border-radius:2.6mm;padding:3.3mm;box-shadow:0 0 0 .6mm rgba(235,207,133,.7)}
.qrbox svg{display:block;width:28.4mm;height:28.4mm}
.nfcwrap{width:35mm;height:35mm;display:grid;place-items:center;border-radius:50%;border:.45mm dashed rgba(235,207,133,.75)}
.nfc{width:28.6mm;height:28.6mm;border-radius:50%;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:.6mm;
  background:radial-gradient(circle at 35% 30%,#F8E7B4,#C9A14A 60%,#A87F2C);color:#2D2108;
  box-shadow:0 0 0 1.2mm rgba(235,207,133,.18),inset 0 .6mm 0 rgba(255,255,255,.5)}
.nfc svg{width:12.5mm;height:12.5mm}
.nfc span{font-size:8.5pt;font-weight:800;letter-spacing:.2em}
.cap{margin-top:2.2mm;text-align:center;font-size:6pt;line-height:1.32;color:rgba(255,255,255,.86)}
.cap b{color:#fff;font-weight:800;font-size:7.3pt;line-height:1.5}
.or{position:absolute;left:50%;top:2.2mm;transform:translateX(-50%);padding:.9mm 2.4mm;line-height:1.2;border-radius:99mm;white-space:nowrap;
  background:#0A3D33;border:.35mm solid #C9A14A;color:#EBCF85;font-size:6.6pt;font-weight:800}
.or{font-size:6pt;padding:.9mm 2mm}

.guide{width:100%;margin-top:4mm;padding:3.2mm 3.4mm 3.4mm;border-radius:4mm;background:#FBF7F0;color:#1B2724}
.guide h2{font:700 10.5pt/1.1 "Playfair Display",serif;color:#0A3D33;text-align:center;margin-bottom:2.6mm}
.guide ol{list-style:none;display:grid;grid-template-columns:1fr 1fr;gap:2.4mm 3mm}
.guide li{display:flex;gap:1.8mm;align-items:flex-start;font-size:7.4pt;line-height:1.32;color:#36433E}
.guide li b{color:#0A3D33;font-weight:800}
.guide i{flex:none;width:5.2mm;height:5.2mm;border-radius:50%;display:grid;place-items:center;font-style:normal;font-weight:800;font-size:7.4pt;
  color:#fff;background:#0F5B4B;box-shadow:0 0 0 .5mm #EBCF85}
.guide{margin-top:3.4mm;padding:2.8mm 3.2mm 3mm}
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
open(WORK + "card2.html", "w", encoding="utf-8").write(html)
print("domain", DOMAIN, "qr modules", n)
