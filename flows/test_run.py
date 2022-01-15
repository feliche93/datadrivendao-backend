"""Moduel to register new flows."""

from prefect.run_configs import ECSRun
from prefect.storage import Docker
from prefect import task, Flow
import prefect

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
    registry_url="262367897508.dkr.ecr.eu-central-1.amazonaws.com",
    image_name="datadrivendao",
    dockerfile="Dockerfile",
)

FLOW_NAME = "ecs_demo"


@task
def say_hi():
    logger = prefect.context.get("logger")
    logger.info("Hi from Prefect %s", prefect.__version__)


with Flow(
    FLOW_NAME,
    storage=STORAGE,
    run_config=RUN_CONFIG,
) as flow:
    say_hi()

if __name__ == "__main__":
    flow.register("datadrivendao")
