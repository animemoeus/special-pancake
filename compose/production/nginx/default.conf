# Upstream Django
upstream django {
    server django:5000;
}

# Django application
server {
    listen       80;
    server_name  special-pancake.animemoe.us, 178.128.114.236;

    client_max_body_size 50M;

    location / {
        resolver 127.0.0.11;
        proxy_pass http://django;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_redirect off;
    }
}
