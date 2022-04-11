# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved

locals {
  common_tags = {
    "HMAPrefix" = var.prefix
  }
}

resource "aws_cloudwatch_log_group" "streamLCCWriter" {
  name              = "/aws/lambda/${aws_lambda_function.streamLCCWriter.function_name}"
  retention_in_days = var.log_retention_in_days
  tags = merge(
    var.additional_tags,
    {
      Name = "StreamLCCWriterLambdaLogGroup"
    }
  )
}

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

resource "aws_iam_role" "ddb_streamLCCWriter_lambda_role" {
  name_prefix        = "${var.prefix}_ddb_streamLCCWriter"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
  tags = merge(
    var.additional_tags,
    {
      Name = "StreamCounterLambdaRole"
    }
  )
}

resource "aws_lambda_function" "streamLCCWriter" {
  function_name = "${var.prefix}_ddb_streamLCCWriter_${var.source_table_type}"
  package_type  = "Image"
  role          = aws_iam_role.ddb_streamLCCWriter_lambda_role.arn
  image_uri     = var.lambda_docker_info.uri
  image_config {
    command = [var.lambda_docker_info.commands.streamLCCWriter]
  }
  timeout     = 300
  memory_size = 128
  environment {
    variables = {
      SOURCE_TABLE_TYPE   = var.source_table_type
      MEASURE_PERFORMANCE = var.measure_performance ? "True" : "False"
      COUNTS_TABLE_NAME   = var.counts_datastore.name
    }
  }
  tags = merge(
    var.additional_tags,
    {
      Name = "DDBStreamCounter"
    }
  )
}

data "aws_iam_policy_document" "streamLCCWriter_iam_policy_document" {
  statement {
    effect    = "Allow"
    actions   = ["dynamodb:GetRecords", "dynamodb:GetShardIterator", "dynamodb:DescribeStream", "dynamodb:ListShards", "dynamodb:ListStreams"]
    resources = [var.source_stream_arn]
  }

  statement {
    effect    = "Allow"
    actions   = ["dynamodb:GetItem", "dynamodb:Query", "dynamodb:Scan", "dynamodb:PutItem", "dynamodb:UpdateItem"]
    resources = [var.counts_datastore.arn]
  }

  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "logs:DescribeLogStreams"
    ]

    resources = ["${aws_cloudwatch_log_group.streamLCCWriter.arn}:*"]
  }
}

resource "aws_iam_policy" "streamLCCWriter_iam_policy" {
  name_prefix = "${var.prefix}_match_counter_iam_policy"
  description = "Permissions for Stream Counter Lambda"
  policy      = data.aws_iam_policy_document.streamLCCWriter_iam_policy_document.json
}

resource "aws_iam_role_policy_attachment" "streamLCCWriter" {
  role       = aws_iam_role.ddb_streamLCCWriter_lambda_role.name
  policy_arn = aws_iam_policy.streamLCCWriter_iam_policy.arn
}

resource "aws_lambda_event_source_mapping" "ddb_stream_mappings" {
  event_source_arn  = var.source_stream_arn
  starting_position = "LATEST"

  function_name                      = aws_lambda_function.streamLCCWriter.arn
  batch_size                         = 200
  maximum_batching_window_in_seconds = 30
  maximum_retry_attempts             = 5
}
