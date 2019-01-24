FROM ubuntu:18.04
RUN mkdir /app 
ADD . /app/
WORKDIR /app
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends python3 python3-pip && \
    pip3 install -r requirements.txt && \
    rm -rf /var/lib/apt/lists/*

CMD ["./runme.py"]