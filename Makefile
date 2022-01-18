# Makefile
.PHONY: init

help:
	@echo "init - set up the application"

setup:
	(\
		pyenv virtualenv datadrivendao; \
		. ~/.pyenv/versions/datadrivendao/bin/activate ; \
		python3 -m pip install -U pip; \
		python -m pip install pip-tools; \
		python -m pip install --upgrade pip; \
		pip-compile requirements.in; \
		pip-compile requirements-dev.in; \
		pre-commit install; \
		pip3 install -r requirements-dev.txt -r requirements.txt; \
	)

install-package:
	pip install -e .

format:
	pre-commit run --all-files

ssh:
	ssh -i ~/.ssh/datadrivendao.pem ubuntu@18.195.95.95

rsync:
	rsync -avP -e "ssh -i ~/.ssh/datadrivendao.pem" . ubuntu@18.195.95.95:~/social_notion

build-image:
	docker build . -t datadrivendao:latest

delete-image:
	docker rmi datadrivendao:latest

rebuild-image: delete-image build-image

login-ecr:
	aws ecr get-login-password | docker login --username AWS --password-stdin $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com

create-ecr-repo:
	aws ecr describe-repositories --repository-names datadrivendao || aws ecr create-repository --repository-name datadrivendao

push-ecr:
	docker tag "datadrivendao:latest" "$(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/datadrivendao:latest"
	aws ecr get-login-password | docker login --username AWS --password-stdin $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com
	docker push "$(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/datadrivendao:latest"

# prefect ECS Setup
# https://towardsdatascience.com/how-to-cut-your-aws-ecs-costs-with-fargate-spot-and-prefect-1a1ba5d2e2df#2587

connect-airbyte:
	ssh -i ~/.ssh/datadrivendao-kp.pem -L 8000:localhost:8000 -N -f ubuntu@34.206.52.76
