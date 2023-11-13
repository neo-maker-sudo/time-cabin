#!/bin/bash

reload_nginx() {  
    docker exec chinchin_proxy /usr/sbin/nginx -s reload
}

service_name=app

# 取得舊容器 id
old_container_id=$(docker ps -f name=$service_name -q | tail -n1)

# -d, --detach  背景執行容器
# --no-deps     不去建立關聯的 container
# --scale       擴展服務到幾個容器，如果在 compose 檔案有寫 scale 覆寫掉 scale 設定
# --build       在開始執行容器前建立 image
# --no-recreate 如果容器已經存在，不會再重複建立
docker compose up -d --no-deps --scale $service_name=2 --build --no-recreate $service_name

# 取得新容器 id
new_container_id=$(docker ps -f name=$service_name -q | head -n1)

# 重新配置 nginx
reload_nginx

# 關掉舊容器
docker stop $old_container_id
# 刪除舊容器
docker rm $old_container_id

docker compose up -d --no-deps --scale $service_name=1 --no-recreate $service_name