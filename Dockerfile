FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY index.html cv.html 404.html style.css cv.css fonts.css script.js robots.txt sitemap.xml llms.txt llms-full.txt /usr/share/nginx/html/
COPY fr /usr/share/nginx/html/fr
COPY assets /usr/share/nginx/html/assets

EXPOSE 80
