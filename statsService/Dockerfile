FROM python:3.10

RUN pip install grpcio-tools

WORKDIR /app

COPY protocols/stats.proto ./stats.proto

RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. stats.proto

COPY ./statsService/* ./
RUN pip install --no-cache-dir -r requirements.txt
RUN chmod +x ./entry.sh

ENTRYPOINT ["./entry.sh"]