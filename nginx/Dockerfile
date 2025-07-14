FROM nginx:1.25

RUN apt-get update && apt-get install -y netcat-openbsd

COPY nginx.conf /etc/nginx/nginx.conf
COPY wait-for-backend.sh /wait-for-backend.sh

RUN chmod +x /wait-for-backend.sh

CMD ["/wait-for-backend.sh", "backend", "8000", "nginx", "-g", "daemon off;"]
