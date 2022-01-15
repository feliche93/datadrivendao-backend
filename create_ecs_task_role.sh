cat <<EOF >ecs_task_role.json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:AuthorizeSecurityGroupIngress",
                "ec2:CreateSecurityGroup",
                "ec2:CreateTags",
                "ec2:DescribeNetworkInterfaces",
                "ec2:DescribeSecurityGroups",
                "ec2:DescribeSubnets",
                "ec2:DescribeVpcs",
                "ec2:DeleteSecurityGroup",
                "ecs:CreateCluster",
                "ecs:DeleteCluster",
                "ecs:DeregisterTaskDefinition",
                "ecs:DescribeClusters",
                "ecs:DescribeTaskDefinition",
                "ecs:DescribeTasks",
                "ecs:ListAccountSettings",
                "ecs:ListClusters",
                "ecs:ListTaskDefinitions",
                "ecs:RegisterTaskDefinition",
                "ecs:RunTask",
                "ecs:StopTask",
                "iam:PassRole",
                "logs:CreateLogStream",
                "logs:PutLogEvents",
                "logs:DescribeLogGroups",
                "logs:GetLogEvents"
            ],
            "Resource": "*"
        }
    ]
}
EOF
