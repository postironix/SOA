FROM python:3.10

RUN pip install grpcio-tools

WORKDIR /app


COPY protocols/tasks.proto ./tasks.proto

RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. tasks.proto

COPY ./taskService/* ./

RUN pip install --no-cache-dir -r requirements.txt
RUN chmod +x ./entry.sh

ENTRYPOINT ["./entry.sh"]