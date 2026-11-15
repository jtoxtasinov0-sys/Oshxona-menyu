/* =====================================================================
   Milliy Taomlar — menyu sayti va admin panel serveri
   Tashqi kutubxonalarsiz: faqat Node.js (22+) ning o'zi yetarli.

   Sozlamalar (muhit o'zgaruvchilari):
     ADMIN_PASSWORD  — admin panel paroli (majburiy, aks holda admin yopiq)
     PORT            — port (standart: 80)
     DATA_DIR        — menyu va rasmlar saqlanadigan papka (standart: ./data)
   ===================================================================== */
"use strict";
const http = require("http");
const fs = require("fs");
const fsp = fs.promises;
const path = require("path");
const crypto = require("crypto");
const zlib = require("zlib");

const PORT = Number(process.env.PORT) || 80;
const ROOT = __dirname;
const DATA_DIR = path.resolve(process.env.DATA_DIR || path.join(ROOT, "data"));
const UPLOAD_DIR = path.join(DATA_DIR, "uploads");
const MENU_FILE = path.join(DATA_DIR, "menu.json");
const SEED_FILE = path.join(ROOT, "menu.json");
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || "";
const TOKEN_TTL = 30 * 24 * 3600 * 1000;      // 30 kun
const MAX_BODY = 12 * 1024 * 1024;            // so'rov hajmi (rasm bilan)
const MAX_IMAGE = 6 * 1024 * 1024;            // bitta rasm

const LANGS = ["uz", "ru", "ko", "en"];
const UNITS = ["portion", "skewer", "piece", "bowl", "pot", "liter", "half", "glass", "kg", "g100"];
const TAGS = ["hit", "new", "hot", "season"];

/* ---------- Ma'lumotlarni tozalash (faqat to'g'ri maydonlar saqlanadi) ---------- */
class BadInput extends Error {}
const str = (v, max) => typeof v === "string" ? v.replace(/[\u0000-\u0008\u000B-\u001F\u007F]/g, "").trim().slice(0, max) : "";
function i18n(o, max) {
  const out = {};
  if (o && typeof o === "object") for (const l of LANGS) { const s = str(o[l], max); if (s) out[l] = s; }
  return out;
}
const UPLOAD_RE = /^\/uploads\/[a-f0-9]{16,40}\.(?:jpg|png|webp)$/;
function cleanImg(v) {
  if (typeof v === "string") {
    if (/^\d{1,12}$/.test(v) || UPLOAD_RE.test(v)) return v;
    return null;
  }
  if (v && typeof v === "object" && /^\d{1,12}$/.test(String(v.id))) {
    const o = { id: String(v.id) };
    if (typeof v.pos === "string" && /^\d{1,3}% \d{1,3}%$/.test(v.pos)) o.pos = v.pos;
    if (typeof v.z === "number" && v.z >= 1 && v.z <= 4) o.z = v.z;
    if (typeof v.o === "string" && /^\d{1,3}% \d{1,3}%$/.test(v.o)) o.o = v.o;
    return o;
  }
  return null;
}
const newId = () => "t" + Date.now().toString(36) + crypto.randomBytes(2).toString("hex");
function cleanItem(it, seen) {
  if (!it || typeof it !== "object") throw new BadInput("Taom ma'lumoti noto'g'ri");
  const n = i18n(it.n, 80);
  if (!n.uz) throw new BadInput("Taom nomi (o'zbekcha) yozilishi shart");
  let id = typeof it.id === "string" && /^[a-z0-9-]{1,40}$/i.test(it.id) ? it.id : newId();
  while (seen.has(id)) id = newId();
  seen.add(id);
  const p = Math.round(Number(it.p));
  const o = { id, n, d: i18n(it.d, 300), p: Number.isFinite(p) ? Math.min(Math.max(p, 0), 100000000) : 0,
    u: UNITS.includes(it.u) ? it.u : "portion" };
  const img = cleanImg(it.img);
  if (img) o.img = img;
  if (it.full === true) o.full = true;
  if (TAGS.includes(it.tag)) o.tag = it.tag;
  if (it.feat === true) o.feat = true;
  const ribbon = i18n(it.ribbon, 40);
  if (o.feat && ribbon.uz) o.ribbon = ribbon;
  if (it.off === true) o.off = true;
  return o;
}
function cleanMenu(m) {
  if (!m || typeof m !== "object" || !Array.isArray(m.categories)) throw new BadInput("Menyu tuzilishi noto'g'ri");
  if (m.categories.length > 40) throw new BadInput("Kategoriyalar juda ko'p");
  const seenCat = new Set(), seenItem = new Set();
  const categories = m.categories.map(c => {
    if (!c || typeof c !== "object" || typeof c.id !== "string" || !/^[a-z0-9-]{1,40}$/.test(c.id) || seenCat.has(c.id))
      throw new BadInput("Kategoriya nomi noto'g'ri");
    seenCat.add(c.id);
    const title = i18n(c.title, 60);
    if (!title.uz) throw new BadInput("Kategoriya nomi (o'zbekcha) yozilishi shart");
    const items = Array.isArray(c.items) ? c.items : [];
    if (items.length > 300) throw new BadInput("Taomlar juda ko'p");
    const o = { id: c.id };
    if (c.list === true) o.list = true;
    o.title = title;
    o.chip = Object.keys(i18n(c.chip, 40)).length ? i18n(c.chip, 40) : title;
    o.sub = i18n(c.sub, 200);
    const thumb = cleanImg(c.thumb);
    if (thumb) o.thumb = thumb;
    o.items = items.map(it => cleanItem(it, seenItem));
    return o;
  });
  const soldOut = m.settings && m.settings.soldOut === "hide" ? "hide" : "show";
  return { settings: { soldOut }, categories };
}

/* ---------- Saqlash ---------- */
let menu = null;                 // joriy menyu (xotirada)
let indexTpl = "", adminHtml = "";
let pageCache = null;            // { version, html, gz }

async function writeAtomic(file, data) {
  const tmp = file + "." + process.pid + ".tmp";
  await fsp.writeFile(tmp, data);
  await fsp.rename(tmp, file);
}
let saving = Promise.resolve();
function saveMenu() {
  const data = JSON.stringify(menu, null, 2) + "\n";
  saving = saving.then(() => writeAtomic(MENU_FILE, data));
  return saving;
}

function isPersistent() {
  // Docker ichida data papkasi alohida "volume" bo'lmasa, qayta deploy qilinganda o'zgarishlar yo'qoladi
  if (process.env.DATA_PERSISTENT === "1") return true;
  if (!fs.existsSync("/.dockerenv")) return true;
  try {
    const mounts = fs.readFileSync("/proc/self/mountinfo", "utf8").split("\n").map(l => l.split(" ")[4]).filter(Boolean);
    return mounts.some(mp => mp !== "/" && (DATA_DIR === mp || DATA_DIR.startsWith(mp + "/")));
  } catch (e) { return null; }
}

async function init() {
  await fsp.mkdir(UPLOAD_DIR, { recursive: true });
  try {
    menu = JSON.parse(await fsp.readFile(MENU_FILE, "utf8"));
    if (!menu || !Array.isArray(menu.categories)) throw new Error("buzuq fayl");
  } catch (e) {
    if (e.code !== "ENOENT") {
      console.error("menu.json o'qilmadi (" + e.message + "), zaxira nusxa olinib, boshlang'ich menyu tiklanadi");
      try { await fsp.copyFile(MENU_FILE, MENU_FILE + ".buzuq-" + Date.now()); } catch (_) {}
    }
    const seed = JSON.parse(await fsp.readFile(SEED_FILE, "utf8"));
    menu = Object.assign({ version: 1, updatedAt: new Date().toISOString() }, cleanMenu(seed));
    await saveMenu();
  }
  indexTpl = await fsp.readFile(path.join(ROOT, "index.html"), "utf8");
  adminHtml = await fsp.readFile(path.join(ROOT, "admin.html"), "utf8");
}

/* ---------- Kirish (token) ---------- */
let secret = null;
async function getKey() {
  if (!secret) {
    const f = path.join(DATA_DIR, ".secret");
    try { secret = (await fsp.readFile(f, "utf8")).trim(); } catch (e) {}
    if (!secret || secret.length < 32) { secret = crypto.randomBytes(32).toString("hex"); await writeAtomic(f, secret); }
  }
  // Parol o'zgarsa, eski tokenlar ham bekor bo'ladi
  return crypto.createHash("sha256").update(secret + "\n" + ADMIN_PASSWORD).digest();
}
const b64u = buf => buf.toString("base64").replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
async function makeToken() {
  const exp = String(Date.now() + TOKEN_TTL);
  return exp + "." + b64u(crypto.createHmac("sha256", await getKey()).update("admin." + exp).digest());
}
async function checkToken(req) {
  if (!ADMIN_PASSWORD) return false;
  const m = /^Bearer\s+(\d{10,16})\.([A-Za-z0-9_-]{20,})$/.exec(req.headers.authorization || "");
  if (!m || Number(m[1]) < Date.now()) return false;
  const want = Buffer.from(b64u(crypto.createHmac("sha256", await getKey()).update("admin." + m[1]).digest()));
  const got = Buffer.from(m[2]);
  return want.length === got.length && crypto.timingSafeEqual(want, got);
}
const sha = s => crypto.createHash("sha256").update(String(s)).digest();
const fails = new Map();   // ip -> { n, t }
function clientIp(req) {
  return String(req.headers["x-forwarded-for"] || "").split(",")[0].trim() || req.socket.remoteAddress || "?";
}

/* ---------- Javob yordamchilari ---------- */
function send(req, res, status, body, type, extra) {
  const headers = Object.assign({ "Content-Type": type, "X-Content-Type-Options": "nosniff", "Cache-Control": "no-cache" }, extra || {});
  let buf = Buffer.isBuffer(body) ? body : Buffer.from(body);
  if (buf.length > 1024 && /\bgzip\b/.test(req.headers["accept-encoding"] || "") && !/^image\//.test(type)) {
    buf = headers.__gz || zlib.gzipSync(buf);
    headers["Content-Encoding"] = "gzip";
    headers["Vary"] = "Accept-Encoding";
  }
  delete headers.__gz;
  headers["Content-Length"] = buf.length;
  res.writeHead(status, headers);
  res.end(req.method === "HEAD" ? undefined : buf);
}
const json = (req, res, status, obj) => send(req, res, status, JSON.stringify(obj), "application/json; charset=utf-8");
function readBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = []; let size = 0;
    req.on("data", c => {
      size += c.length;
      if (size > MAX_BODY) { reject(Object.assign(new Error("too big"), { status: 413 })); req.destroy(); return; }
      chunks.push(c);
    });
    req.on("end", () => {
      try { resolve(JSON.parse(Buffer.concat(chunks).toString("utf8") || "{}")); }
      catch (e) { reject(Object.assign(new Error("bad json"), { status: 400 })); }
    });
    req.on("error", reject);
  });
}

/* Menyu sahifasi: ma'lumot to'g'ridan-to'g'ri HTML ichiga qo'yiladi — sahifa bir zumda ochiladi */
function renderIndex() {
  if (pageCache && pageCache.version === menu.version) return pageCache;
  const data = JSON.stringify(menu).replace(/</g, "\\u003c").replace(/\u2028/g, "\\u2028").replace(/\u2029/g, "\\u2029");
  const html = indexTpl.replace('<script id="menu-data" type="application/json"></script>',
    () => '<script id="menu-data" type="application/json">' + data + "</script>");
  pageCache = { version: menu.version, html, gz: zlib.gzipSync(html) };
  return pageCache;
}

/* Hech bir taomga tegishli bo'lmagan eski rasmlarni tozalash */
async function cleanupUploads() {
  try {
    const used = JSON.stringify(menu);
    for (const f of await fsp.readdir(UPLOAD_DIR)) {
      if (used.includes("/uploads/" + f)) continue;
      const p = path.join(UPLOAD_DIR, f), st = await fsp.stat(p);
      if (Date.now() - st.mtimeMs > 24 * 3600 * 1000) await fsp.unlink(p);
    }
  } catch (e) { console.error("uploads tozalashda xato:", e.message); }
}

function imageType(buf) {
  if (buf.length > 3 && buf[0] === 0xFF && buf[1] === 0xD8 && buf[2] === 0xFF) return "jpg";
  if (buf.length > 8 && buf.slice(0, 8).equals(Buffer.from([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A]))) return "png";
  if (buf.length > 12 && buf.toString("ascii", 0, 4) === "RIFF" && buf.toString("ascii", 8, 12) === "WEBP") return "webp";
  return null;
}
const MIME = { jpg: "image/jpeg", png: "image/png", webp: "image/webp" };

/* ---------- Marshrutlar ---------- */
async function handle(req, res) {
  const url = new URL(req.url, "http://x");
  const p = url.pathname;
  const isGet = req.method === "GET" || req.method === "HEAD";

  // Ommaviy sahifalar
  if (isGet && (p === "/" || p === "/index.html")) {
    const pg = renderIndex();
    return send(req, res, 200, pg.html, "text/html; charset=utf-8", { __gz: pg.gz, "Referrer-Policy": "strict-origin-when-cross-origin" });
  }
  if (isGet && (p === "/admin" || p === "/admin/" || p === "/admin.html")) {
    return send(req, res, 200, adminHtml, "text/html; charset=utf-8", {
      "X-Frame-Options": "DENY", "Referrer-Policy": "no-referrer", "X-Robots-Tag": "noindex, nofollow" });
  }
  if (isGet && (p === "/api/menu" || p === "/menu.json")) return json(req, res, 200, menu);
  if (isGet && p.startsWith("/uploads/")) {
    const name = p.slice(9);
    if (!/^[a-f0-9]{16,40}\.(?:jpg|png|webp)$/.test(name)) return send(req, res, 404, "Topilmadi", "text/plain; charset=utf-8");
    try {
      const buf = await fsp.readFile(path.join(UPLOAD_DIR, name));
      return send(req, res, 200, buf, MIME[name.split(".").pop()], { "Cache-Control": "public, max-age=31536000, immutable" });
    } catch (e) { return send(req, res, 404, "Topilmadi", "text/plain; charset=utf-8"); }
  }
  if (isGet && p === "/robots.txt") return send(req, res, 200, "User-agent: *\nDisallow: /admin\n", "text/plain; charset=utf-8");

  // Admin API
  if (p === "/api/login" && req.method === "POST") {
    if (!ADMIN_PASSWORD) return json(req, res, 503, { error: "Serverda ADMIN_PASSWORD sozlanmagan" });
    const ip = clientIp(req), f = fails.get(ip);
    if (f && f.n >= 8 && Date.now() - f.t < 15 * 60 * 1000) return json(req, res, 429, { error: "Ko'p marta xato kiritildi. 15 daqiqadan keyin urinib ko'ring" });
    const body = await readBody(req);
    if (crypto.timingSafeEqual(sha(body.password || ""), sha(ADMIN_PASSWORD))) {
      fails.delete(ip);
      return json(req, res, 200, { token: await makeToken(), persistent: isPersistent() });
    }
    if (fails.size > 5000) fails.clear();
    fails.set(ip, { n: (f && Date.now() - f.t < 15 * 60 * 1000 ? f.n : 0) + 1, t: Date.now() });
    return json(req, res, 401, { error: "Parol noto'g'ri" });
  }
  if (p.startsWith("/api/")) {
    if (p === "/api/session" && isGet) {
      if (!ADMIN_PASSWORD) return json(req, res, 503, { error: "Serverda ADMIN_PASSWORD sozlanmagan" });
      return (await checkToken(req)) ? json(req, res, 200, { ok: true, persistent: isPersistent() }) : json(req, res, 401, { error: "Qaytadan kiring" });
    }
    if (!(await checkToken(req))) return json(req, res, 401, { error: "Qaytadan kiring" });

    if (p === "/api/menu" && req.method === "PUT") {
      const body = await readBody(req);
      if (body.version !== menu.version) return json(req, res, 409, { error: "Menyu boshqa joyda o'zgartirilgan", menu });
      let clean;
      try { clean = cleanMenu(body.menu); } catch (e) {
        if (e instanceof BadInput) return json(req, res, 400, { error: e.message });
        throw e;
      }
      menu = Object.assign({ version: menu.version + 1, updatedAt: new Date().toISOString() }, clean);
      await saveMenu();
      cleanupUploads();
      return json(req, res, 200, { ok: true, menu });
    }
    if (p === "/api/upload" && req.method === "POST") {
      const body = await readBody(req);
      const m = /^data:image\/[a-z+.-]+;base64,([A-Za-z0-9+/=\s]+)$/.exec(String(body.data || ""));
      if (!m) return json(req, res, 400, { error: "Rasm topilmadi" });
      const buf = Buffer.from(m[1], "base64");
      if (buf.length > MAX_IMAGE) return json(req, res, 413, { error: "Rasm juda katta" });
      const ext = imageType(buf);
      if (!ext) return json(req, res, 400, { error: "Faqat JPG, PNG yoki WEBP rasm" });
      const name = crypto.randomBytes(10).toString("hex") + "." + ext;
      await writeAtomic(path.join(UPLOAD_DIR, name), buf);
      return json(req, res, 200, { url: "/uploads/" + name });
    }
    return json(req, res, 404, { error: "Topilmadi" });
  }

  if (isGet && !path.extname(p)) {        // nginx'dagi kabi: noma'lum sahifa -> menyu
    const pg = renderIndex();
    return send(req, res, 200, pg.html, "text/html; charset=utf-8", { __gz: pg.gz });
  }
  return send(req, res, 404, "Topilmadi", "text/plain; charset=utf-8");
}

init().then(() => {
  const server = http.createServer((req, res) => {
    handle(req, res).catch(e => {
      if (!e.status) console.error(e);
      if (!res.headersSent) json(req, res, e.status || 500, { error: e.status === 413 ? "Fayl juda katta" : "Server xatosi" });
      else res.destroy();
    });
  });
  server.requestTimeout = 60000;
  server.listen(PORT, () => {
    console.log("Milliy Taomlar: http://localhost:" + PORT + "  (admin: /admin)");
    if (!ADMIN_PASSWORD) console.warn("DIQQAT: ADMIN_PASSWORD o'rnatilmagan — admin panel yopiq.");
    if (isPersistent() === false) console.warn("DIQQAT: " + DATA_DIR + " alohida volume emas — qayta deploy qilinganda admin o'zgarishlari yo'qoladi.");
  });
  const stop = () => { server.close(() => process.exit(0)); setTimeout(() => process.exit(0), 3000).unref(); };
  process.on("SIGTERM", stop);
  process.on("SIGINT", stop);
}).catch(e => { console.error("Ishga tushmadi:", e); process.exit(1); });
