# Makefile
.PHONY: init

ssh: 
	ssh -i ~/.ssh/datadrivendao-kp.pem ubuntu@44.200.153.172

rsync:
	rsync -avP -e "ssh -i~/.ssh/datadrivendao-kp.pem" . ubuntu@44.200.153.172:~/

compose-up:
	sudo docker-compose -f docker-compose.yml up