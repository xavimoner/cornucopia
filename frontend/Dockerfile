
# frontend/Dockerfile
FROM nginx:alpine
# Copiar fitxers de frontend
COPY . /usr/share/nginx/html

# Substituïm configuració nginx per defecte amb la tunejada
COPY nginx.conf /etc/nginx/conf.d/default.conf