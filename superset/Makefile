ssh:
	ssh -i ~/.ssh/datadrivendao-kp.pem ubuntu@54.167.159.220

rsync:
	rsync -avP -e "ssh -i~/.ssh/datadrivendao-kp.pem" . ubuntu@54.167.159.220:~/superset

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

sync-backup:
	rsync -avP -e "ssh -i~/.ssh/datadrivendao-kp.pem" ubuntu@54.167.159.220:~/superset/dump_17-02-2022_09_39_11.sql .

back-up:
	sudo docker exec -t superset_db pg_dumpall -c -U superset > dump_`date +%d-%m-%Y"_"%H_%M_%S`.sql
