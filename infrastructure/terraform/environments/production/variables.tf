# ---------------------------------------------------------------------------
# Production Environment Variables
# ---------------------------------------------------------------------------
# This file defines variables for the production environment of the
# Justice Bid Rate Negotiation System with configurations emphasizing
# high availability, security, performance, and disaster recovery.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Region Configuration
# ---------------------------------------------------------------------------

variable "primary_region" {
  description = "The primary AWS region for production deployment"
  type        = string
  default     = "us-west-2"
}

variable "dr_region" {
  description = "The disaster recovery AWS region for cross-region replication"
  type        = string
  default     = "us-east-1"
}

# ---------------------------------------------------------------------------
# Network Configuration
# ---------------------------------------------------------------------------

variable "vpc_cidr" {
  description = "CIDR block for the production VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones to use for production resources"
  type        = list(string)
  default     = ["us-west-2a", "us-west-2b", "us-west-2c"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for production private subnets"
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.11.0/24", "10.0.12.0/24"]
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for production public subnets"
  type        = list(string)
  default     = ["10.0.0.0/24", "10.0.1.0/24", "10.0.2.0/24"]
}

variable "database_subnet_cidrs" {
  description = "CIDR blocks for production database subnets"
  type        = list(string)
  default     = ["10.0.20.0/24", "10.0.21.0/24", "10.0.22.0/24"]
}

variable "elasticache_subnet_cidrs" {
  description = "CIDR blocks for production ElastiCache subnets"
  type        = list(string)
  default     = ["10.0.30.0/24", "10.0.31.0/24", "10.0.32.0/24"]
}

variable "enable_nat_gateway" {
  description = "Enable NAT Gateways for private subnets outbound connectivity"
  type        = bool
  default     = true
}

variable "single_nat_gateway" {
  description = "Use a single NAT Gateway for all private subnets (production uses multiple NAT gateways)"
  type        = bool
  default     = false
}

# ---------------------------------------------------------------------------
# EKS Cluster Configuration
# ---------------------------------------------------------------------------

variable "eks_cluster_version" {
  description = "Kubernetes version for production EKS cluster"
  type        = string
  default     = "1.27"
}

variable "eks_node_instance_types" {
  description = "Instance types for production EKS node groups"
  type        = list(string)
  default     = ["m5.2xlarge"]
}

variable "eks_min_size" {
  description = "Minimum size for production EKS node groups"
  type        = number
  default     = 3
}

variable "eks_max_size" {
  description = "Maximum size for production EKS node groups"
  type        = number
  default     = 15
}

variable "eks_desired_capacity" {
  description = "Desired capacity for production EKS node groups"
  type        = number
  default     = 5
}

# ---------------------------------------------------------------------------
# RDS Database Configuration
# ---------------------------------------------------------------------------

variable "rds_instance_class" {
  description = "RDS instance class for production PostgreSQL database"
  type        = string
  default     = "db.r6g.large"
}

variable "rds_allocated_storage" {
  description = "Allocated storage for production RDS instances in GB"
  type        = number
  default     = 200
}

variable "rds_max_allocated_storage" {
  description = "Maximum allocated storage for production RDS autoscaling in GB"
  type        = number
  default     = 1000
}

variable "rds_engine_version" {
  description = "PostgreSQL engine version for production RDS"
  type        = string
  default     = "15.3"
}

variable "rds_multi_az" {
  description = "Enable Multi-AZ deployment for production RDS instances"
  type        = bool
  default     = true
}

variable "rds_backup_retention_period" {
  description = "Backup retention period in days for production RDS"
  type        = number
  default     = 35
}

variable "rds_deletion_protection" {
  description = "Enable deletion protection for production RDS"
  type        = bool
  default     = true
}

variable "rds_enable_performance_insights" {
  description = "Enable Performance Insights for production RDS"
  type        = bool
  default     = true
}

# ---------------------------------------------------------------------------
# ElastiCache Configuration
# ---------------------------------------------------------------------------

variable "elasticache_node_type" {
  description = "ElastiCache node type for production Redis cluster"
  type        = string
  default     = "cache.r6g.large"
}

variable "elasticache_engine_version" {
  description = "Redis engine version for production ElastiCache"
  type        = string
  default     = "7.0"
}

variable "elasticache_cluster_mode_enabled" {
  description = "Enable cluster mode for production Redis ElastiCache"
  type        = bool
  default     = true
}

variable "elasticache_num_node_groups" {
  description = "Number of node groups for production Redis cluster mode"
  type        = number
  default     = 3
}

variable "elasticache_replicas_per_node_group" {
  description = "Number of replicas per node group for production Redis cluster"
  type        = number
  default     = 2
}

# ---------------------------------------------------------------------------
# S3 Storage Configuration
# ---------------------------------------------------------------------------

variable "s3_bucket_prefix" {
  description = "Prefix for S3 bucket names in production environment"
  type        = string
  default     = "justice-bid-prod"
}

variable "s3_versioning_enabled" {
  description = "Enable versioning for production S3 buckets"
  type        = bool
  default     = true
}

variable "s3_encryption_enabled" {
  description = "Enable server-side encryption for production S3 buckets"
  type        = bool
  default     = true
}

variable "s3_create_replication" {
  description = "Create cross-region replication for production S3 buckets"
  type        = bool
  default     = true
}

# ---------------------------------------------------------------------------
# CDN and Security Configuration
# ---------------------------------------------------------------------------

variable "cloudfront_enabled" {
  description = "Enable CloudFront distribution for production static assets"
  type        = bool
  default     = true
}

variable "waf_enabled" {
  description = "Enable WAF for production API Gateway and CloudFront"
  type        = bool
  default     = true
}

variable "waf_rate_limit" {
  description = "Request rate limit for WAF in production environment"
  type        = number
  default     = 1000
}

# ---------------------------------------------------------------------------
# Monitoring and Logging Configuration
# ---------------------------------------------------------------------------

variable "alarm_email" {
  description = "Email address to receive production CloudWatch alarm notifications"
  type        = string
  default     = "ops-alerts@justicebid.com"
}

variable "monitoring_enabled" {
  description = "Enable comprehensive monitoring for production environment"
  type        = bool
  default     = true
}

variable "prometheus_retention_days" {
  description = "Retention period in days for production Prometheus metrics"
  type        = number
  default     = 90
}

# ---------------------------------------------------------------------------
# OpenSearch Configuration
# ---------------------------------------------------------------------------

variable "opensearch_enabled" {
  description = "Enable OpenSearch for full-text search in production"
  type        = bool
  default     = true
}

variable "opensearch_instance_type" {
  description = "Instance type for production OpenSearch cluster"
  type        = string
  default     = "r6g.large.search"
}

variable "opensearch_instance_count" {
  description = "Number of instances in production OpenSearch cluster"
  type        = number
  default     = 3
}

variable "opensearch_ebs_volume_size" {
  description = "EBS volume size for production OpenSearch instances in GB"
  type        = number
  default     = 100
}

variable "opensearch_zone_awareness_enabled" {
  description = "Enable zone awareness for production OpenSearch cluster"
  type        = bool
  default     = true
}

# ---------------------------------------------------------------------------
# Domain and SSL Configuration
# ---------------------------------------------------------------------------

variable "domain_name" {
  description = "Production domain name for the application"
  type        = string
  default     = "app.justicebid.com"
}

variable "zone_id" {
  description = "Route 53 hosted zone ID for the production domain"
  type        = string
}

variable "certificate_arn" {
  description = "ARN of the SSL certificate for production CloudFront distribution"
  type        = string
}

# ---------------------------------------------------------------------------
# API Keys and Secrets
# ---------------------------------------------------------------------------

variable "openai_api_key" {
  description = "API key for OpenAI in production (will be stored in AWS Secrets Manager)"
  type        = string
  sensitive   = true
  default     = ""
}

variable "unicourt_api_key" {
  description = "API key for UniCourt in production (will be stored in AWS Secrets Manager)"
  type        = string
  sensitive   = true
  default     = ""
}