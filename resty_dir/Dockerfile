FROM openresty/openresty:1.21.4.1-0-jammy

RUN apt-get update && \
    apt-get install -y luarocks build-essential && \
    rm -rf /var/lib/apt/lists/*

RUN luarocks install lua-resty-openssl

WORKDIR /usr/local/openresty/nginx/html

EXPOSE 8080

CMD ["/usr/local/openresty/bin/openresty", "-g", "daemon off;"]
