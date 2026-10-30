FROM node:20-alpine AS build
WORKDIR /app
COPY frontend/package.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
RUN printf 'server {\n listen 80;\n client_max_body_size 30m;\n location /api/ { proxy_pass http://backend:8000; proxy_read_timeout 300s; }\n location / { root /usr/share/nginx/html; try_files $uri /index.html; }\n}\n' > /etc/nginx/conf.d/default.conf
