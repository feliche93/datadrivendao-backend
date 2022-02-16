ssh:
	ssh -i ~/.ssh/datadrivendao-kp.pem ubuntu@35.175.109.76

rsync:
	rsync -avP -e "ssh -i~/.ssh/datadrivendao-kp.pem" . ubuntu@35.175.109.76:~/superset

compose-up:
	sudo docker-compose -f docker-compose-non-dev.yml up

compose-down:
	sudo docker-compose -f docker-compose-non-dev.yml down