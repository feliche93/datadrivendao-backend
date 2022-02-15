# Deployment Guide Superset

1. Forked Repo from master to be able to fetch updates
2. Clone the fork
3. Created the `.env-non-dev` file in the docker folder of the repo
4. Added `docker-compose up` for `docker-compose-non-dev.yml` file
5. Added Caddyfile following tutorial https://caddyserver.com/docs/quick-starts/reverse-proxy
6. Addded A and AAAA records pointing to IPs

