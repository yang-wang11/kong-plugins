docker rm resty -f;

docker run -d \
  -p 8888:8080 \
  -v $(pwd)/nginx.conf:/usr/local/openresty/nginx/conf/nginx.conf \
  -v $(pwd)/lua:/usr/local/openresty/lua \
  --name resty local_resty;