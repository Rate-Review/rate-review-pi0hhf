# Defines the outputs from the Terraform infrastructure for the Justice Bid Rate Negotiation System

# VPC Outputs
output "vpc_id" {
  description = "ID of the VPC created for the Justice Bid system"
  value       = module.vpc.vpc_id
}

output "public_subnet_ids" {
  description = "List of public subnet IDs in the VPC"
  value       = module.vpc.public_subnet_ids
}

output "private_subnet_ids" {
  description = "List of private subnet IDs in the VPC"
  value       = module.vpc.private_subnet_ids
}

# EKS Cluster Outputs
output "eks_cluster_name" {
  description = "Name of the EKS cluster"
  value       = module.eks.cluster_name
}

output "eks_cluster_endpoint" {
  description = "Endpoint URL for the Kubernetes API server"
  value       = module.eks.cluster_endpoint
}

output "eks_cluster_certificate_authority_data" {
  description = "Certificate authority data for the EKS cluster"
  value       = module.eks.cluster_certificate_authority_data
}

output "eks_node_group_role_arn" {
  description = "ARN of the IAM role used by EKS node groups"
  value       = module.eks.node_group_role_arn
}

output "eks_cluster_security_group_id" {
  description = "ID of the security group for the EKS cluster"
  value       = module.eks.cluster_security_group_id
}

output "kubeconfig" {
  description = "Generated kubeconfig for accessing the EKS cluster"
  value       = module.eks.kubeconfig
  sensitive   = true
}

# RDS Outputs
output "rds_endpoint" {
  description = "Connection endpoint for the PostgreSQL RDS instance"
  value       = module.rds.db_instance_endpoint
}

output "rds_instance_id" {
  description = "ID of the primary RDS instance"
  value       = module.rds.db_instance_id
}

output "rds_replica_endpoints" {
  description = "Connection endpoints for the RDS read replicas"
  value       = module.rds.db_replica_endpoints
}

# S3 Bucket Outputs
output "document_bucket_name" {
  description = "Name of S3 bucket for document storage"
  value       = module.s3.document_bucket
}

output "export_bucket_name" {
  description = "Name of S3 bucket for exports storage"
  value       = module.s3.export_bucket
}

output "upload_bucket_name" {
  description = "Name of S3 bucket for temporary uploads"
  value       = module.s3.upload_bucket
}

output "static_website_bucket_name" {
  description = "Name of S3 bucket for static website content"
  value       = module.s3.static_website_bucket
}

output "s3_bucket_arns" {
  description = "ARNs of all S3 buckets for permissions configuration"
  value       = module.s3.bucket_arns
}

# ElastiCache Outputs
output "elasticache_primary_endpoint" {
  description = "Primary endpoint address for the Redis cluster"
  value       = module.elasticache.aws_elasticache_replication_group.justice_bid_cache_replication_group.primary_endpoint_address
}

output "elasticache_reader_endpoint" {
  description = "Reader endpoint address for the Redis cluster"
  value       = module.elasticache.aws_elasticache_replication_group.justice_bid_cache_replication_group.reader_endpoint_address
}

# CloudFront Outputs
output "cloudfront_distribution_id" {
  description = "ID of the CloudFront distribution for static content"
  value       = module.cloudfront.distribution_id
}

# Secrets Manager Outputs
output "db_credentials_secret_arn" {
  description = "ARN of the secret containing database credentials"
  value       = module.secrets.db_credentials_secret_arn
}

# API Gateway Outputs
output "api_gateway_endpoint" {
  description = "Endpoint URL for the API Gateway"
  value       = module.api_gateway.api_endpoint
}

# Load Balancer Outputs
output "load_balancer_dns_name" {
  description = "DNS name of the application load balancer"
  value       = module.load_balancer.dns_name
}

# KMS Outputs
output "kms_key_arn" {
  description = "ARN of the KMS key used for encryption"
  value       = module.kms.key_arn
}

# Route53 Outputs
output "route53_zone_id" {
  description = "ID of the Route53 hosted zone"
  value       = module.route53.zone_id
}