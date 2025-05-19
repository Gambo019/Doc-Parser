#!/bin/bash
set -e

echo "Starting destruction process..."

# Step 1: Empty S3 bucket first
echo "Emptying S3 bucket..."
aws s3 rm s3://ai-doc-parser-s3 --recursive

# Step 2: Update Terraform resources to force delete
cd terraform

# Add force_delete for ECR repository
if ! grep -q "force_delete = true" main.tf; then
  sed -i '/resource "aws_ecr_repository" "ai_doc_parser" {/a \ \ force_delete = true' main.tf
fi

# Add force_destroy for S3 bucket
if ! grep -q "force_destroy = true" main.tf; then
  sed -i '/resource "aws_s3_bucket" "ai_doc_parser" {/a \ \ force_destroy = true' main.tf
fi

# Apply changes to update resources
terraform apply -auto-approve

# Destroy all resources
echo "Destroying all resources..."
terraform destroy -auto-approve

cd ..
echo "Destruction complete!"
