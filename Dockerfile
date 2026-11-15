# Dokploy uchun: Node.js server — menyu sayti + admin panel (/admin)
# Muhit o'zgaruvchisi: ADMIN_PASSWORD (admin panel paroli)
# Doimiy saqlash uchun /app/data papkasiga volume ulang (README'ga qarang)
FROM node:22-alpine
WORKDIR /app
ENV NODE_ENV=production PORT=80 DATA_DIR=/app/data
COPY server.js index.html admin.html menu.json ./
# Eslatma: VOLUME bu yerda e'lon qilinmagan — Dokploy'da nomli volume ulanadi
RUN mkdir -p /app/data/uploads
EXPOSE 80
CMD ["node", "server.js"]
