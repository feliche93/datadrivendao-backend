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

# RESULT = PrefectResult()

# create_post_flow.result = RESULT

create_post_flow.run_config = RUN_CONFIG
create_post_flow.storage = STORAGE
create_post_flow.register(project_name="datadrivendao")

get_notion_posts_flow.run_config = RUN_CONFIG
get_notion_posts_flow.storage = STORAGE
get_notion_posts_flow.register(project_name="datadrivendao")

schedule_posts_flow.run_config = RUN_CONFIG
schedule_posts_flow.storage = STORAGE
schedule_posts_flow.register(project_name="datadrivendao")
