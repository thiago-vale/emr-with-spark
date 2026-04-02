data "aws_caller_identity" "current" {}

resource "aws_iam_role" "lambda" {
  name = "thiago-lambda-role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": "AssumeRole"
    }
  ]
}
EOF

  tags = {
    IES   = "IGTI",
    CURSO = "EDC"
  }

}



resource "aws_iam_policy" "lambda" {
  name        = "thiago-lambda-policy"
  path        = "/"
  description = "Provides restrictive permissions to CloudWatch Logs, S3 buckets and EMR"

  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "CloudWatchLogsForLambda",
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/${var.lambda_function_name}:*"
        },
        {
            "Sid": "S3DataLakeAccess",
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:PutObjectAcl",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::datalake-test-thiago",
                "arn:aws:s3:::datalake-test-thiago/*"
            ]
        },
        {
            "Sid": "S3TerraformStateReadOnly",
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket"
            ],
            "Resource": "arn:aws:s3:::00-terraform-state"
        },
        {
            "Sid": "EMRClusterManagement",
            "Effect": "Allow",
            "Action": [
                "elasticmapreduce:RunJobFlow",
                "elasticmapreduce:DescribeCluster",
                "elasticmapreduce:DescribeStep",
                "elasticmapreduce:ListClusters",
                "elasticmapreduce:ListSteps",
                "elasticmapreduce:AddJobFlowSteps",
                "elasticmapreduce:TerminateJobFlows"
            ],
            "Resource": "*"
        },
        {
            "Sid": "IAMPassRole",
            "Effect": "Allow",
            "Action": "iam:PassRole",
            "Resource": [
                "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/EMR_DefaultRole",
                "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/EMR_EC2_DefaultRole"
            ]
        }
    ]
}
EOF
}


resource "aws_iam_role_policy_attachment" "lambda_attach" {
  role       = aws_iam_role.lambda.name
  policy_arn = aws_iam_policy.lambda.arn
}
