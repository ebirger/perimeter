FROM node:23 AS frontend

WORKDIR /fe
COPY fe/package.json ./
RUN npm install
COPY fe .
RUN npm run build

FROM python:3.13 AS backend

WORKDIR /app

RUN apt-get update && apt-get install -y supervisor
RUN mkdir -p /var/log/supervisor

COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY docker/entrypoint.sh .

COPY be/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY be/ .
COPY --from=frontend /fe/dist /app/staticfiles/dist/

CMD ["/app/entrypoint.sh"]
