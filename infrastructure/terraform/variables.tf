# AWS Provider Configuration
variable "aws_region" {
  description = "The AWS region to deploy the infrastructure"
  type        = string
  default     = "us-west-2"
}

variable "aws_profile" {
  description = "The AWS profile to use for authentication"
  type        = string
  default     = "default"
}

variable "environment" {
  description = "Deployment environment (dev, staging, production)"
  type        = string
  default     = "dev"
  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "Environment must be one of: dev, staging, production"
  }
}

# Project Information
variable "project_name" {
  description = "Project name used for resource naming and tagging"
  type        = string
  default     = "justice-bid"
}

variable "tags" {
  description = "Common resource tags for all created resources"
  type        = map(string)
  default     = {
    Project   = "JusticeBid"
    ManagedBy = "Terraform"
  }
}

# Networking Configuration
variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones to use for resources"
  type        = list(string)
  default     = ["us-west-2a", "us-west-2b", "us-west-2c"]
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.11.0/24", "10.0.12.0/24", "10.0.13.0/24"]
}

variable "database_subnet_cidrs" {
  description = "CIDR blocks for database subnets"
  type        = list(string)
  default     = ["10.0.21.0/24", "10.0.22.0/24", "10.0.23.0/24"]
}

variable "enable_nat_gateway" {
  description = "Enable NAT Gateways for private subnets outbound internet connectivity"
  type        = bool
  default     = true
}

variable "single_nat_gateway" {
  description = "Use a single NAT Gateway for all private subnets (cost savings for dev)"
  type        = bool
  default     = false
}

# Database Configuration
variable "rds_instance_class" {
  description = "RDS instance class for PostgreSQL database"
  type        = string
  default     = "db.t3.large"
}

variable "rds_allocated_storage" {
  description = "Allocated storage for RDS instances in GB"
  type        = number
  default     = 100
}

variable "rds_max_allocated_storage" {
  description = "Maximum allocated storage for RDS autoscaling in GB"
  type        = number
  default     = 500
}

variable "rds_engine_version" {
  description = "PostgreSQL engine version for RDS"
  type        = string
  default     = "15.3"
}

variable "rds_multi_az" {
  description = "Enable Multi-AZ deployment for RDS instances"
  type        = bool
  default     = true
}

variable "rds_backup_retention_period" {
  description = "Backup retention period in days for RDS"
  type        = number
  default     = 30
}

variable "rds_enable_performance_insights" {
  description = "Enable Performance Insights for RDS"
  type        = bool
  default     = true
}

variable "rds_deletion_protection" {
  description = "Enable deletion protection for RDS"
  type        = bool
  default     = true
}

# ElastiCache Configuration
variable "elasticache_node_type" {
  description = "ElastiCache node type for Redis"
  type        = string
  default     = "cache.t3.medium"
}

variable "elasticache_engine_version" {
  description = "Redis engine version for ElastiCache"
  type        = string
  default     = "7.0"
}

variable "elasticache_cluster_mode_enabled" {
  description = "Enable cluster mode for Redis ElastiCache"
  type        = bool
  default     = true
}

variable "elasticache_num_node_groups" {
  description = "Number of node groups for Redis cluster mode"
  type        = number
  default     = 2
}

variable "elasticache_replicas_per_node_group" {
  description = "Number of replicas per node group for Redis cluster"
  type        = number
  default     = 1
}

# EKS Configuration
variable "eks_cluster_version" {
  description = "Kubernetes version for EKS cluster"
  type        = string
  default     = "1.27"
}

variable "eks_node_instance_types" {
  description = "Instance types for EKS node groups"
  type        = list(string)
  default     = ["t3.xlarge"]
}

variable "eks_desired_capacity" {
  description = "Desired capacity for EKS node groups"
  type        = number
  default     = 3
}

variable "eks_min_size" {
  description = "Minimum size for EKS node groups"
  type        = number
  default     = 2
}

variable "eks_max_size" {
  description = "Maximum size for EKS node groups"
  type        = number
  default     = 10
}

# S3 Storage Configuration
variable "s3_bucket_names" {
  description = "Names for S3 buckets used by the application"
  type        = map(string)
  default     = {
    documents = "justice-bid-documents"
    exports   = "justice-bid-exports"
    backups   = "justice-bid-backups"
    logs      = "justice-bid-logs"
  }
}

variable "s3_versioning_enabled" {
  description = "Enable versioning for S3 buckets"
  type        = bool
  default     = true
}

variable "s3_encryption_enabled" {
  description = "Enable server-side encryption for S3 buckets"
  type        = bool
  default     = true
}

variable "s3_lifecycle_rules_enabled" {
  description = "Enable lifecycle rules for S3 buckets"
  type        = bool
  default     = true
}

# CDN and Security Configuration
variable "cloudfront_enabled" {
  description = "Enable CloudFront distribution for static assets"
  type        = bool
  default     = true
}

variable "waf_enabled" {
  description = "Enable WAF for API Gateway and CloudFront"
  type        = bool
  default     = true
}

variable "domain_name" {
  description = "Domain name for the application"
  type        = string
  default     = "justicebid.example.com"
}

variable "enable_ssl" {
  description = "Enable SSL/TLS for all endpoints"
  type        = bool
  default     = true
}

# Monitoring and Alerts
variable "alarm_email" {
  description = "Email address to receive CloudWatch alarm notifications"
  type        = string
  default     = "alerts@example.com"
}

variable "monitoring_enabled" {
  description = "Enable monitoring with CloudWatch and Prometheus"
  type        = bool
  default     = true
}

variable "prometheus_retention_in_days" {
  description = "Retention period in days for Prometheus metrics"
  type        = number
  default     = 30
}

# Disaster Recovery
variable "enable_disaster_recovery" {
  description = "Enable disaster recovery configuration with cross-region replication"
  type        = bool
  default     = true
}

variable "dr_region" {
  description = "Secondary region for disaster recovery"
  type        = string
  default     = "us-east-1"
}