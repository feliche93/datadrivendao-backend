ssh:
	ssh -i ~/.ssh/datadrivendao-kp.pem ubuntu@3.222.205.54

rsync:
	rsync -avP -e "ssh -i~/.ssh/datadrivendao-kp.pem" . ubuntu@3.222.205.54:~/superset

compose-up:
	sudo docker-compose -f docker-compose-non-dev.yml up

compose-down:
	sudo docker-compose -f docker-compose-non-dev.yml down