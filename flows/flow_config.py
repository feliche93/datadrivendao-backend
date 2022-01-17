from prefect.run_configs import ECSRun
from prefect.storage import Docker

RUN_CONFIG = ECSRun(
    image="262367897508.dkr.ecr.eu-central-1.amazonaws.com/datadrivendao:latest",
    cpu="256",
    memory="512",
    labels=["prod"],
    task_role_arn="arn:aws:iam::262367897508:role/prefectTaskRole",
    execution_role_arn="arn:aws:iam::262367897508:role/prefectECSAgentTaskExecutionRole",
    run_task_kwargs=dict(
        cluster="prefectEcsCluster",
        launchType="FARGATE",
    ),
)

STORAGE = Docker(
    registry_url="262367897508.dkr.ecr.us-east-1.amazonaws.com",
    image_name="datadrivendao",
    dockerfile="Dockerfile",
)