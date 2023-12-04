# 綁定要監聽的 ip 跟 port，這個主要是要讓 nginx container 反向代理到特定的 port 路徑
bind = "0.0.0.0:10000"
# 執行的進程數
workers = 4
# 工作模式：預設為 sync，也可以使用異步的 gevent，這邊使用 uvicorn 提供的 worker
worker_class = "uvicorn.workers.UvicornWorker"
# 反向代理需要拿到 client 端的 IP
forwarded_allow_ips = "*"
# access log 檔案位置
accesslog = "/var/log/gunicorn/access/access.log"
# error log 檔案位置
errorlog = "/var/log/gunicorn/error/error.log"
