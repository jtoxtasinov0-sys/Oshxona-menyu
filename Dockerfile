# Dokploy uchun: oddiy nginx server, faqat index.html ni tarqatadi
FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY index.html /usr/share/nginx/html/index.html
EXPOSE 80
