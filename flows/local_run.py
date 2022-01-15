"""Module for local Docker run."""

import os

from dotenv import load_dotenv
from prefect.run_configs import DockerRun

from flows.create_post import create_post_flow
from flows.get_notion_posts import get_notion_posts_flow

RUN_CONFIG = DockerRun(
    image="262367897508.dkr.ecr.eu-central-1.amazonaws.com/datadrivendao:latest",
)

load_dotenv()

get_notion_posts_flow.run_config = RUN_CONFIG
state = get_notion_posts_flow.run()
print(state.result)

# create_post_flow.run_config = RUN_CONFIG
# state = create_post_flow.run(
#     parameters={
#         "access_token": os.environ.get("LINKEDIN_ACCESS_TOKEN"),
#         "body": "Posting from ECS",
#         "description": "First Post from ECS",
#         "original_url": "https://docs.prefect.io/api/latest/run_configs.html#ecsrun",
#         "redirect_uri": "http://localhost:8080",
#         "title": "Post From ECS",
#         "visibility": "PUBLIC",
#     }
# )
