#!/bin/bash
# https://docs.konghq.com/gateway/3.8.x/install/docker/?install=oss#install-kong-gateway-in-db-less-mode

export current_dir=$(pwd)
export plugin_dir=/usr/local/share/lua/5.1/kong/plugins
export plugin_list="hcjwt,myheader,myauth,my-plugin"

docker rm kong-dbless -f

# 如果指定容器在一个network下via --network, 那么就会出现DNS name resolution failed的问题
docker run -d --name kong-dbless --network=kong-net \
-v "$current_dir/kong/plugins:/kong/plugins" \
-v "$current_dir/config:/kong/declarative" \
-v "$current_dir/config/kong.conf:/etc/kong/kong.conf" \
-e "KONG_LUA_PACKAGE_PATH=/kong/plugins/?.lua;/kong/plugins/?/init.lua;;" \
-e "KONG_PLUGINS=bundled,$plugin_list" \
-e "KONG_DATABASE=off" \
-e "KONG_DECLARATIVE_CONFIG=/kong/declarative/kong.yml" \
-e "KONG_PROXY_ACCESS_LOG=/dev/stdout" \
-e "KONG_ADMIN_ACCESS_LOG=/dev/stdout" \
-e "KONG_PROXY_ERROR_LOG=/dev/stderr" \
-e "KONG_ADMIN_ERROR_LOG=/dev/stderr" \
-e "KONG_LOG_LEVEL=debug" \
-e "KONG_ADMIN_LISTEN=0.0.0.0:8001, 0.0.0.0:8444 ssl" \
-p 8000:8000 \
-p 8443:8443 \
-p 8002:8002 \
-p 127.0.0.1:8001:8001 \
-p 127.0.0.1:8444:8444 \
kong-gateway_my-plugin:3.8-0.0.1
# hanaservice-dev.common.repositories.cloud.sap/com.sap.hana.cloud.cloudinfrastructure/hana-cloud-api-gateway:i321482-dev
# dockerio.int.repositories.cloud.sap/kong:3.8.0  kong:3.8.0
# 添加 "KONG_ADMIN_GUI_URL=http://0.0.0.0:8002" 会导致Kong一些信息访问失效
