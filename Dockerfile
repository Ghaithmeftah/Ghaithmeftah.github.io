FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY index.html style.css script.js /usr/share/nginx/html/
COPY assets /usr/share/nginx/html/assets

EXPOSE 80
