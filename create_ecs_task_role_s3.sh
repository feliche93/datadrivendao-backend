# adjust it to include permissions needed by your flows
cat <<EOF >ecs_task_role_s3.json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:*"
      ],
      "Resource": "arn:aws:s3:::*prefect*"
    }
  ]
}
EOF
