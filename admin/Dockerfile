FROM node:22-alpine AS build

WORKDIR /app

ARG VITE_API_BASE_URL=http://localhost:8000/api/v1
ARG VITE_APP_ENV=local
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL \
    VITE_APP_ENV=$VITE_APP_ENV

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginxinc/nginx-unprivileged:1.29-alpine AS runtime

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 8080

HEALTHCHECK --interval=10s --timeout=3s --retries=5 \
  CMD wget -q -O /dev/null http://127.0.0.1:8080/ || exit 1
