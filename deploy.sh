#!/bin/bash
set -e

echo "Starting deployment process..."

AWS_REGION=${1:-${AWS_REGION:-"us-east-1"}}
ECR_REPO_NAME="ai-doc-parser-ecr"

# Step 1: Create only ECR repository first
echo "Creating ECR repository..."
cd terraform
terraform init
terraform apply -auto-approve -target=aws_ecr_repository.ai_doc_parser -target=aws_iam_role.lambda_role -target=aws_iam_role_policy.lambda_s3_policy -target=aws_iam_role_policy_attachment.lambda_logs
cd ..

# Step 2: Get AWS account ID and construct repository URI
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPO_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}"

# Step 3: Build and push Docker image
echo "Building and pushing Docker image to ECR..."
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REPO_URI}
docker build -t ${ECR_REPO_NAME}:latest .
docker tag ${ECR_REPO_NAME}:latest ${ECR_REPO_URI}:latest
docker push ${ECR_REPO_URI}:latest

# Step 4: Deploy the rest of the infrastructure
echo "Deploying remaining infrastructure..."
cd terraform
terraform apply -auto-approve
cd ..

echo "Deployment complete!"