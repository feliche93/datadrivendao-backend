ssh:
	ssh -i ~/.ssh/datadrivendao-kp.pem ubuntu@3.208.129.88

rsync:
	rsync -avP -e "ssh -i~/.ssh/datadrivendao-kp.pem" . ubuntu@3.208.129.88:~/superset

compose-up:
	sudo docker-compose -f docker-compose-non-dev.yml up

compose-down:
	sudo docker-compose -f docker-compose-non-dev.yml down

compose-stop:
	sudo docker-compose -f docker-compose-non-dev.yml stop

compose-start:
	sudo docker-compose -f docker-compose-non-dev.yml start

check-a-record:
	curl "https://cloudflare-dns.com/dns-query?name=superset.datadrivendao.xyz&type=A" -H "accept: application/dns-json"

check-aaaa-record:
	curl "https://cloudflare-dns.com/dns-query?name=superset.datadrivendao.xyz&type=AAAA" -H "accept: application/dns-json"
