# search-replace the $AWS_ACCOUNT_ID below with your AWS account ID. Also, replace or add ECS Agent labels
cat <<EOF >ecs_prefect_agent_task_definition.json
{
    "family": "$ECS_SERVICE_NAME",
    "requiresCompatibilities": [
        "FARGATE"
    ],
    "networkMode": "awsvpc",
    "cpu": "256",
    "memory": "512",
    "taskRoleArn": "arn:aws:iam::$AWS_ACCOUNT_ID:role/prefectTaskRole",
    "executionRoleArn": "arn:aws:iam::$AWS_ACCOUNT_ID:role/prefectECSAgentTaskExecutionRole",
    "containerDefinitions": [
        {
            "name": "$ECS_SERVICE_NAME",
            "image": "prefecthq/prefect:latest-python3.9",
            "essential": true,
            "command": [
                "prefect",
                "agent",
                "ecs",
                "start"
            ],
            "environment": [
                {
                    "name": "PREFECT__CLOUD__AGENT__LABELS",
                    "value": "['prod']"
                },
                {
                    "name": "PREFECT__CLOUD__AGENT__LEVEL",
                    "value": "INFO"
                },
                {
                    "name": "PREFECT__CLOUD__API",
                    "value": "https://api.prefect.io"
                }
            ],
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": "$ECS_LOG_GROUP_NAME",
                    "awslogs-region": "$AWS_REGION",
                    "awslogs-stream-prefix": "ecs",
                    "awslogs-create-group": "true"
                }
            },
            "secrets": [
                {
                    "name": "PREFECT__CLOUD__API_KEY",
                    "valueFrom": "arn:aws:ssm:$AWS_REGION:$AWS_ACCOUNT_ID:parameter/PREFECT__CLOUD__API_KEY"
                }
            ]
        }
    ]
}
EOF
