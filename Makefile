# Makefile
.PHONY: init

help:
	@echo "init - set up the application"

setup:
	(\
		pyenv virtualenv social-notion; \
		. ~/.pyenv/versions/social-notion/bin/activate ; \
		python3 -m pip install -U pip; \
		python -m pip install pip-tools; \
		python -m pip install --upgrade pip; \
		pip-compile requirements.in; \
		pip-compile requirements-dev.in; \
		pip-compile requirements-dev.in; \
		pre-commit install; \
		pip3 install -r requirements-dev.txt -r requirements.txt; \
	)

install-package:
	pip install -e .

format:
	pre-commit run --all-files

ssh:
	ssh -i ~/.ssh/social-notion.pem ubuntu@18.195.95.95

rsync:
	rsync -avP -e "ssh -i ~/.ssh/social-notion.pem" . ubuntu@18.195.95.95:~/social_notion

build-image:
	docker build . -t social-notion:latest

delete-image:
	docker rmi social-notion:latest

rebuild-image: delete-image build-image

login-ecr:
	aws ecr get-login-password | docker login --username AWS --password-stdin $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com

push-ecr:
	aws ecr describe-repositories --repository-names social-notion || aws ecr create-repository --repository-name social-notion
	docker tag "social-notion:latest" "$(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/social-notion:latest"
	aws ecr get-login-password | docker login --username AWS --password-stdin $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com
	docker push "$(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/social-notion:latest"

# prefect ECS Setup
# https://towardsdatascience.com/how-to-cut-your-aws-ecs-costs-with-fargate-spot-and-prefect-1a1ba5d2e2df#2587

store-secrets:
	aws ssm put-parameter --type SecureString --name PREFECT__CLOUD__API_KEY --value $(PREFECT_API_KEY) --region $(AWS_REGION) --overwrite

ecs-cluster:
	aws ecs create-cluster --cluster-name $(ECS_CLUSTER_NAME) \
	--capacity-providers FARGATE_SPOT FARGATE \
	--default-capacity-provider-strategy \
	capacityProvider=FARGATE_SPOT,weight=3 \
	capacityProvider=FARGATE,base=1,weight=2 \
	--region $(AWS_REGION)

create-execution-role:
	aws iam create-role --role-name prefectECSAgentTaskExecutionRole \
	--assume-role-policy-document file://ecs_tasks_trust_policy.json --region $(AWS_REGION)

create-task-role-s3:
	aws iam put-role-policy --role-name prefectTaskRole --policy-name prefectTaskRoleS3Policy --policy-document file://ecs_task_role_s3.json

attach-general-service-role:
	aws iam attach-role-policy --role-name prefectECSAgentTaskExecutionRole \
	--policy-arn "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"

attach-custom-role-policy:
	aws iam put-role-policy --role-name prefectECSAgentTaskExecutionRole \
	--policy-name prefectECSAgentTaskExecutionRolePolicy \
	--policy-document file://ecs_tasks_execution_role.json

create-task-role:
	sh create_ecs_tasks_trust_policy.sh
	sh create_ecs_task_role.sh
	aws iam create-role --role-name prefectTaskRole --assume-role-policy-document file://ecs_tasks_trust_policy.json --region $(AWS_REGION)
	aws iam put-role-policy --role-name prefectTaskRole --policy-name prefectTaskRolePolicy --policy-document file://ecs_task_role.json

create-cloud-watch-log-group:
	aws logs create-log-group --log-group-name $(ECS_LOG_GROUP_NAME) --region $(AWS_REGION)

register-task-definition:
	sh create_task_definition.sh
	aws ecs register-task-definition --cli-input-json file://ecs_prefect_agent_task_definition.json --region $(AWS_REGION)

vpc-export:
	export VPC=$(aws ec2 describe-vpcs --filters Name=is-default,Values=true)
	export VPC_ID=$(echo $VPC | jq -r '.Vpcs | .[0].VpcId')
	SUBNETS=$(aws ec2 describe-subnets --filters Name=vpc-id,Values=$VPC_ID --region $AWS_REGION)
	export SUBNET1=$(echo $SUBNETS | jq -r '.Subnets | .[0].SubnetId')
	export SUBNET2=$(echo $SUBNETS | jq -r '.Subnets | .[1].SubnetId')
	export SUBNET3=$(echo $SUBNETS | jq -r '.Subnets | .[2].SubnetId')

create-ecs-service:
	aws ecs create-service \
		--service-name $(ECS_SERVICE_NAME)\
		--task-definition $(ECS_SERVICE_NAME):6 \
		--desired-count 1 \
		--launch-type FARGATE \
		--platform-version LATEST \
		--cluster $(ECS_CLUSTER_NAME) \
		--network-configuration awsvpcConfiguration="{subnets=[$(SUBNET1), $(SUBNET2), $(SUBNET3)],assignPublicIp=ENABLED}" --region $(AWS_REGION)
