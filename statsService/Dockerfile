FROM python:3.10

WORKDIR /app

COPY ./statsService/* ./
RUN pip install --no-cache-dir -r requirements.txt
RUN chmod +x ./entry.sh

ENTRYPOINT ["./entry.sh"]