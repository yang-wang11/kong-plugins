# Install Kong Gateway

## With a database

Reference guide https://docs.konghq.com/gateway/latest/install/docker/

### Create a Docker network

```
docker network create kong-net
```


### Start and prepare Postgres DB

```
docker run -d --name kong-database \
 --network=kong-net \
 -p 5432:5432 \
 -e "POSTGRES_USER=kong" \
 -e "POSTGRES_DB=kong" \
 -e "POSTGRES_PASSWORD=kongpass" \
 postgres:13

-- kong初始化数据库
docker run --rm --network=kong-net \
-e "KONG_DATABASE=postgres" \
-e "KONG_PG_HOST=kong-database" \
-e "KONG_PG_PASSWORD=kongpass" \
-e "KONG_PASSWORD=kong" \
kong/kong:3.8.0 kong migrations bootstrap
```

### Start kong proxy

```
docker run -d --name kong --network=kong-net \
    -e "KONG_DATABASE=postgres" \
    -e "KONG_PG_HOST=kong-database" \
    -e "KONG_PG_USER=kong" \
    -e "KONG_PG_PASSWORD=kongpass" \
    -e "KONG_PROXY_ACCESS_LOG=/dev/stdout" \
    -e "KONG_ADMIN_ACCESS_LOG=/dev/stdout" \
    -e "KONG_PROXY_ERROR_LOG=/dev/stderr" \
    -e "KONG_ADMIN_ERROR_LOG=/dev/stderr" \
    -e "KONG_ADMIN_LISTEN=0.0.0.0:8001, 0.0.0.0:8444 ssl" \
    -e "KONG_ADMIN_GUI_URL=http://localhost:8002" \
    -p 8000:8000 \
    -p 8443:8443 \
    -p 8001:8001 \
    -p 8444:8444 \
    -p 8002:8002 \
    -p 8445:8445 \
    -p 8003:8003 \
    -p 8004:8004 \
    kong/kong:3.8.0
```

### Functionality validation

- **No Upstreams，only validate the route**

Create service：

```
curl -i -X POST http://localhost:8001/services/ --data "name=example-service" --data "url=https://www.baidu.com" 
```

Create route：

```
curl -i -X POST http://localhost:8001/services/example-service/routes --data "hosts[]=baidu.com"
```

测试向本地的 `localhost` 发起请求，但模拟了请求是发往 **`baidu.com`**。很多反向代理和 API 网关（如 Kong）会根据 `Host` 头来选择不同的服务。即使目标 URL 是 `localhost`，由于 `Host` 头是 `baidu.com`，服务器可能会根据这个头将请求转发到一个处理 `baidu.com` 流量的后端服务。

```
curl -i --url http://localhost --header 'Host: baidu.com'
```

* **Upstreams**

Create Upstream：

```
curl -i -X POST http://localhost:8001/upstreams --data "name=my_upstream"
```

Map the Target to its Upstream：

```
curl -i -X POST http://localhost:8001/upstreams/my_upstream/targets --data "target=192.168.1.100:8080" --data "weight=100"
```

Create service：

```
curl -i -X POST http://localhost:8001/services --data "name=my_service" --data "host=my_upstream" --data "port=80" --data "protocol=http"
```

Create route：

```
curl -i -X POST http://localhost:8001/routes --data "paths[]=/my-service" --data "service.name=my_service"
```

validation：

```
http://localhost:8000/my-service
```

###  Install konga

https://hub.docker.com/r/pantsel/konga/#installation

```
docker pull pantsel/konga

// DB_HOST: the name or ID of your Kong Postgres container
// 暂时不支持   --platform linux/arm64 \
// 使用临时方案 https://github.com/gorositopablo/konga/blob/master/Dockerfile
docker run --name konga -p 1337:1337 --network=kong-net \
     -e "TOKEN_SECRET=abc123" \
     -e "DB_ADAPTER=postgres" \
     -e "DB_HOST=kong-database" \
     -e "DB_USER=kong" \
     -e "DB_PASSWORD=kongpass" \
     -e "DB_DATABASE=konga" \
     -e "NODE_ENV=development" \
     -e "DB_PORT=5432" \
     gorositopablo/konga
```

### Cleanup 

```
docker container rm kong -f
docker container rm konga -f
docker container rm kong-database -f
docker network rm kong-net
```


## DB-less mode

### Prepare your configuration file

```yaml
 _format_version: "3.0"
 _transform: true

 services:
 ...
```

Named the above file as `kong.yml`.

```
docker run -d --name kong-dbless --network=kong-net \
-v "/Users/elan/Desktop/kong/conf:/kong/declarative/" \
-e "KONG_DATABASE=off" \
-e "KONG_DECLARATIVE_CONFIG=/kong/declarative/kong.yml" \
-e "KONG_PROXY_ACCESS_LOG=/dev/stdout" \
-e "KONG_ADMIN_ACCESS_LOG=/dev/stdout" \
-e "KONG_PROXY_ERROR_LOG=/dev/stderr" \
-e "KONG_ADMIN_ERROR_LOG=/dev/stderr" \
-e "KONG_ADMIN_LISTEN=0.0.0.0:8001, 0.0.0.0:8444 ssl" \
-e "KONG_ADMIN_GUI_URL=http://localhost:8002" \
-p 8000:8000 \
-p 8443:8443 \
-p 8001:8001 \
-p 8444:8444 \
-p 8002:8002 \
-p 8445:8445 \
-p 8003:8003 \
-p 8004:8004 \
kong/kong:3.8.0
```

###  Install konga

https://hub.docker.com/r/pantsel/konga/#installation

```
docker pull pantsel/konga
docker run -d --name konga --network kong-net -p 1337:1337 \
           -e "NODE_ENV=development" \
           -e "TOKEN_SECRET=abc123" \
           pantsel/konga
```

### Cleanup 

```
docker container rm kong-dbless -f
docker container rm konga -f
docker network rm kong-net
```

## Note

The root directory of kong is /usr/local/kong，and its config file located in file /etc/kong

```
curl http://localhost:8001/routes | jq
access the kong admin ui via the link http://localhost:8002
```

**端口说明:**

**8000**：监听来自客户端的 HTTP 请求流量，并将其路由转发给上游服务器。

**8443**：监听来自客户端的 HTTPS 请求流量，并将其路由转发给上游服务器。

**8001**：监听来自 Kong Admin API 的 HTTP 请求流量。

**8444**：监听来自 Kong Admin API 的 HTTPS 请求流量。

