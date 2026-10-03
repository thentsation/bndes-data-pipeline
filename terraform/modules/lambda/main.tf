resource "aws_sqs_queue" "dlq" {
  name                      = "${var.project_name}-dlq"
  message_retention_seconds = 1209600
  visibility_timeout_seconds = 900

  tags = {
    Name        = "${var.project_name}-dlq"
    Project     = var.project_name
    ManagedBy   = "Terraform"
    Environment = "Production"
  }
}

resource "aws_iam_role" "lambda_role" {
  name = "${var.project_name}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "lambda_s3_policy" {
  name = "${var.project_name}-s3-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          var.s3_bucket_arn,
          "${var.s3_bucket_arn}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy" "lambda_kms_policy" {
  count = var.s3_kms_key_arn != "" ? 1 : 0
  name  = "${var.project_name}-kms-policy"
  role  = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:GenerateDataKey"
        ]
        Resource = [var.s3_kms_key_arn]
      }
    ]
  })
}

# AM policy for SQS DLQ access
resource "aws_iam_role_policy" "lambda_dlq_policy" {
  name = "${var.project_name}-dlq-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sqs:SendMessage",
          "sqs:GetQueueUrl"
        ]
        Resource = aws_sqs_queue.dlq.arn
      }
    ]
  })
}

resource "null_resource" "build_and_push_image" {
  triggers = {
    dockerfile_hash = filesha1("${path.module}/../../../docker/Dockerfile")
    app_hash        = filesha1("${path.module}/../../../src/app.py")
  }

  provisioner "local-exec" {
    working_dir = "${path.module}/../.."
    command = <<EOT
      set -e
      AWS_REGION=${var.aws_region}
      ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
      REPO_URL=${var.ecr_repository_url}

      aws ecr describe-repositories --repository-names ${var.ecr_repository_name} >/dev/null 2>&1 || \
        aws ecr create-repository --repository-name ${var.ecr_repository_name} >/dev/null

      aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

      docker build --target runtime -f docker/Dockerfile -t ${var.project_name}-lambda .
      docker tag ${var.project_name}-lambda $REPO_URL:latest

      docker push $REPO_URL:latest
    EOT
    interpreter = ["/bin/bash", "-c"]
  }
}

resource "aws_lambda_function" "bndes_lambda" {
  function_name = "${var.project_name}-fn"
  role          = aws_iam_role.lambda_role.arn
  package_type  = "Image"

  image_uri = "${var.ecr_repository_url}:latest"

  timeout       = var.lambda_timeout
  memory_size   = var.lambda_memory_size
  architectures = ["x86_64"]

  environment {
    variables = {
      S3_BUCKET_NAME = var.s3_bucket_name
    }
  }

  dead_letter_config {
    target_arn = aws_sqs_queue.dlq.arn
  }

  depends_on = [null_resource.build_and_push_image]
}