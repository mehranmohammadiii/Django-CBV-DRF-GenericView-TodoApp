FROM python:3.12.11-alpine3.22

ENV PATH="/opt/venv/bin:$PATH"
RUN apk update && apk add --no-cache postgresql-client libjpeg zlib curl && rm -rf /var/cache/apk/*

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

RUN mkdir -p /app/media /app/staticfiles

# RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["sh", "-c", "python manage.py runserver 0.0.0.0:8000"]