provider "aws" {
  region = var.aws_region
}

# ECR Repository
resource "aws_ecr_repository" "ai_doc_parser" {
  force_delete = true
  name                 = "ai-doc-parser-ecr"
  image_tag_mutability = "MUTABLE"
}

# S3 Bucket
resource "aws_s3_bucket" "ai_doc_parser" {
  force_destroy = true
  bucket = "ai-doc-parser-s3"
}

resource "aws_s3_bucket_ownership_controls" "ai_doc_parser" {
  bucket = aws_s3_bucket.ai_doc_parser.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

# IAM Role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "ai-doc-parser-lambda-role"

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

# Lambda permissions: S3 access
resource "aws_iam_role_policy" "lambda_s3_policy" {
  name = "lambda-s3-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket",
          "s3:DeleteObject"
        ]
        Effect = "Allow"
        Resource = [
          aws_s3_bucket.ai_doc_parser.arn,
          "${aws_s3_bucket.ai_doc_parser.arn}/*"
        ]
      }
    ]
  })
}

# Lambda permissions: CloudWatch Logs
resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Lambda permissions: Self-invoke
resource "aws_iam_role_policy" "lambda_self_invoke" {
  name = "lambda-self-invoke-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action   = "lambda:InvokeFunction"
        Effect   = "Allow"
        Resource = aws_lambda_function.ai_doc_parser.arn
      }
    ]
  })
}

# Lambda Function
resource "aws_lambda_function" "ai_doc_parser" {
  function_name = "ai-doc-parser-lambda"
  role          = aws_iam_role.lambda_role.arn
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.ai_doc_parser.repository_url}:latest"
  
  memory_size = 4096
  timeout     = 90
  ephemeral_storage {
    size = 5120
  }

  environment {
    variables = {
      API_KEY         = var.api_key
      DB_HOST         = var.db_host
      DB_NAME         = var.db_name
      DB_PASSWORD     = var.db_password
      DB_PORT         = var.db_port
      DB_USER         = var.db_user
      OPENAI_API_KEY  = var.openai_api_key
      S3_BUCKET_NAME  = aws_s3_bucket.ai_doc_parser.bucket
    }
  }
}

# API Gateway
resource "aws_api_gateway_rest_api" "api" {
  name = "ai-doc-parser-api"
  binary_media_types = ["multipart/form-data", "*/*"]
}

# API Resources
resource "aws_api_gateway_resource" "api_resource" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "api"
}

resource "aws_api_gateway_resource" "process_document" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_resource.api_resource.id
  path_part   = "process-document"
}

resource "aws_api_gateway_resource" "process_pbm_document" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_resource.api_resource.id
  path_part   = "process-pbm-document"
}

resource "aws_api_gateway_resource" "task" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_resource.api_resource.id
  path_part   = "task"
}

resource "aws_api_gateway_resource" "task_id" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_resource.task.id
  path_part   = "{task_id}"
}

# POST /api/process-document
resource "aws_api_gateway_method" "process_document_post" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.process_document.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "process_document_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.process_document.id
  http_method             = aws_api_gateway_method.process_document_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.ai_doc_parser.invoke_arn
  timeout_milliseconds    = 29000
}

# POST /api/process-pbm-document
resource "aws_api_gateway_method" "process_pbm_document_post" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.process_pbm_document.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "process_pbm_document_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.process_pbm_document.id
  http_method             = aws_api_gateway_method.process_pbm_document_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.ai_doc_parser.invoke_arn
  timeout_milliseconds    = 29000
}

# GET /api/task/{task_id}
resource "aws_api_gateway_method" "task_id_get" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.task_id.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "task_id_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.task_id.id
  http_method             = aws_api_gateway_method.task_id_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.ai_doc_parser.invoke_arn
  timeout_milliseconds    = 29000
}

# Lambda permissions for API Gateway
resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ai_doc_parser.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.api.execution_arn}/*/*/*"
}

# API Deployment
resource "aws_api_gateway_deployment" "prod" {
  depends_on = [
    aws_api_gateway_integration.process_document_integration,
    aws_api_gateway_integration.process_pbm_document_integration,
    aws_api_gateway_integration.task_id_integration
  ]

  rest_api_id = aws_api_gateway_rest_api.api.id
  stage_name  = "prod"
}

# Output the API URL
output "api_url" {
  value = "${aws_api_gateway_deployment.prod.invoke_url}"
} 