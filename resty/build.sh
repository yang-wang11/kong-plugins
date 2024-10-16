docker rm resty -f;
docker rmi local_resty;
docker build -t local_resty .