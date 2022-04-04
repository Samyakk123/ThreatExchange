# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved

### Lambda for custodian ###

data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_lambda_function" "custodian" {
  function_name = "${var.prefix}_custodian"
  package_type  = "Image"
  role          = aws_iam_role.custodian.arn
  image_uri     = var.lambda_docker_info.uri
  image_config {
    command = ["hmalib.lambdas.custodian.lambda_handler"]
  }

  # Timeout is kept less than the fetch frequency. Right now, fetch frequency is
  # 15 minutes, so we timeout at 12. The more this value, the more time every
  # single fetch has to complete.
  # TODO: make this computed from var.fetch_frequency.
  timeout = 60 * 12

  memory_size = 128
}


resource "aws_cloudwatch_log_group" "custodian" {
  name = "/aws/lambda/${aws_lambda_function.custodian.function_name}"
  tags = merge(
    var.additional_tags,
    {
      Name = "FetcherLambdaLogGroup"
    }
  )
}

resource "aws_iam_role" "custodian" {
  name_prefix        = "${var.prefix}_custodian"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
  tags = merge(
    var.additional_tags,
    {
      Name = "CustodianLambdaRole"
    }
  )
}

data "aws_iam_policy_document" "custodian" {

  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "logs:DescribeLogStreams"
    ]
    resources = ["${aws_cloudwatch_log_group.custodian.arn}:*"]
  }

}

resource "aws_iam_policy" "custodian" {
  name_prefix = "${var.prefix}_custodian_role_policy"
  description = "Permissions for Fetcher Lambda"
  policy      = data.aws_iam_policy_document.custodian.json
}

resource "aws_iam_role_policy_attachment" "custodian" {
  role       = aws_iam_role.custodian.name
  policy_arn = aws_iam_policy.custodian.arn
}
