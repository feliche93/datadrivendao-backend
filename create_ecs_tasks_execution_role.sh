cat <<EOF >ecs_tasks_execution_role.json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ssm:GetParameters"
      ],
      "Resource": "arn:aws:ssm:$AWS_REGION:$AWS_ACCOUNT_ID:parameter/PREFECT__CLOUD__API_KEY"
    }
  ]
}
EOF
