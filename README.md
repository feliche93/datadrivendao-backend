# datadrivendao-backend

Backend for datadriven dao

## Airbyte Install

#### Install Docker

```bash
sudo apt-get update
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt-get install -y uidmap
dockerd-rootless-setuptool.sh install
```

#### Insstall Docker Compose

```bash
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker
-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### Install Airbyte

```bash
git clone https://github.com/airbytehq/airbyte.git
cd airbyte
docker-compose up
```

### Airbyte JSON Service Account

`datadrivendao-42c52b51132d.json`