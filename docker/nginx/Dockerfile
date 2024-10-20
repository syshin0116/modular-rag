# Nginx 이미지를 사용
FROM nginx:alpine

# Nginx 설정 파일을 복사
COPY nginx.conf /etc/nginx/nginx.conf

# 필요한 정적 파일이나 리소스를 복사할 수 있음
COPY /static /usr/share/nginx/html
