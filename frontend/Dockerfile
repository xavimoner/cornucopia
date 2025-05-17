
# frontend/Dockerfile
FROM nginx:alpine
# Copiar fitxers de frontend
COPY . /usr/share/nginx/html

# Substituir configuració nginx per defecte amb la nostra
COPY nginx.conf /etc/nginx/conf.d/default.conf