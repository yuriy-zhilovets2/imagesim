FROM python:3.11
WORKDIR /var/www
COPY ext.py server.py .
RUN pip install --no-cache-dir --upgrade flask gunicorn weaviate-client imagededup
CMD ["gunicorn", "--bind=0.0.0.0:80", "--workers=5", "server:app"]
