我们将按照以下步骤进行：

1. **在Docker中运行Kong(DBless模式)**
2. **配置Kong的服务(Service)和路由(Route)**
3. **配置消费者(Consumer)以及插件(Plugin)启用**
4. **测试**



### **部署一个简单的Web服务容器**

为了简单起见，我们使用一个简单的Nginx容器。

**运行Nginx容器：**

```
docker run -d --network=kong-net --name my-web-service -p 8080:80 nginx
```

这将在本地主机的8080端口运行一个Nginx服务器。

**验证Nginx服务是否正常运行：**

在浏览器中访问 http://localhost:8080
应该看到Nginx的默认欢迎页面。

------



### **在Docker中运行Kong(DBless模式)**

**创建Kong的配置文件**

由于我们使用DBless模式，需要使用YAML文件来配置Kong。

创建名为 kong.yml 的文件，初始内容如下：

```
_format_version: "3.0"
_transform: true

services: []
```



**运行Kong容器**

创建一个自定义网络，后续所有的docker conatiners需要在一个network下。

```
docker network create kong-net
```

假设您已经在主机上开发了插件，并在/kong/plugins 目录下。

运行Kong容器，并挂载插件和配置文件：

```
docker run -d --name kong-dbless \
--network=kong-net \
-v "$current_dir/config:/kong/declarative" \
-v "$current_dir/plugins:/kong/plugins" \
-e "KONG_LUA_PACKAGE_PATH=/kong/plugins/?.lua;/kong/plugins/?/init.lua;;" \
-e "KONG_PLUGINS=bundled,$plugin_list" \
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
-p 127.0.0.1:8001:8001 \
-p 127.0.0.1:8444:8444 \
kong:3.8.0
```

------



### **配置Kong的服务(Service)和路由(Route)**

**运行Nginx容器时指定网络**

为了简单起见，我们使用一个简单的Nginx容器进行测试。在浏览器中访问 http://localhost:8080，可以验证Nginx是否正常工作。

```
docker run -d --name my-web-service --network=kong-net -p 8080:80 nginx
```

**更新kong.yml中的服务URL**

注意: 将服务的url更新为容器名称

```
_format_version: "3.0"
_transform: true

services:
- name: my-service
  url: http://my-web-service:80

routes:
- name: my-route
  service: my-service
  paths:
  - /my-service
```

------



### **配置消费者(Consumer)以及插件(Plugin)启用**

在 kong.yml 中，添加消费者信息：

```
consumers:
- username: testuser
  custom_id: testuserid
  tags: [test, local]
```

**更新插件配置**

如果您的插件需要与消费者关联，可以更新插件配置：

```
plugins:
- name: myauth
  service: my-service
  consumer: test-user  -- 特定给某个consumer，其他user没有这个限制
  config:
    username: admin
    password: secret
```



------



### **测试**

**发送请求**

使用正确的用户名和密码，发送请求到Kong：

```
curl -i -X GET http://localhost:8000/my-service \
  -H "username: admin" \
  -H "password: secret"
  
  
curl -i -X GET http://localhost:8000/my-service \
   -H 'Authorization: Basic dGVzdHVzZXI6dGVzdA=='
```

**预期结果**

- 如果认证成功，Kong会将请求转发到Nginx服务，您将收到Nginx的默认响应。
- 如果认证失败，Kong会返回401未授权的错误。



**测试认证失败的情况**

使用错误的用户名和密码：

```
curl -i -X GET http://localhost:8000/my-service \
  -H "username: test-user" \
  -H "password: wrong"
```

**预期结果**

- Kong返回401未授权的错误。

