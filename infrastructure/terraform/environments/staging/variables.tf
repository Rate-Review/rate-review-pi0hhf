# AWS Region configuration
variable "aws_region" {
  description = "The AWS region to deploy resources into"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (staging)"
  type        = string
  default     = "staging"
}

# Network configuration
variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.1.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for the public subnets"
  type        = list(string)
  default     = ["10.1.0.0/24", "10.1.1.0/24", "10.1.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for the private subnets"
  type        = list(string)
  default     = ["10.1.10.0/24", "10.1.11.0/24", "10.1.12.0/24"]
}

variable "database_subnet_cidrs" {
  description = "CIDR blocks for the database subnets"
  type        = list(string)
  default     = ["10.1.20.0/24", "10.1.21.0/24", "10.1.22.0/24"]
}

# EKS configuration
variable "eks_cluster_name" {
  description = "Name of the EKS cluster"
  type        = string
  default     = "justicebid-staging"
}

variable "eks_node_instance_types" {
  description = "Instance types for the EKS worker nodes"
  type        = list(string)
  default     = ["t3.large"]
}

variable "eks_node_desired_capacity" {
  description = "Desired number of worker nodes"
  type        = number
  default     = 3
}

variable "eks_node_min_capacity" {
  description = "Minimum number of worker nodes"
  type        = number
  default     = 2
}

variable "eks_node_max_capacity" {
  description = "Maximum number of worker nodes"
  type        = number
  default     = 5
}

# Database configuration
variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.large"
}

variable "db_allocated_storage" {
  description = "Allocated storage for the RDS instance (GB)"
  type        = number
  default     = 100
}

variable "db_multi_az" {
  description = "Enable Multi-AZ deployment for RDS"
  type        = bool
  default     = true
}

# Redis configuration
variable "redis_node_type" {
  description = "ElastiCache Redis node type"
  type        = string
  default     = "cache.t3.medium"
}

variable "redis_num_cache_nodes" {
  description = "Number of Redis cache nodes"
  type        = number
  default     = 2
}

# S3 configuration
variable "s3_bucket_name" {
  description = "Name of the S3 bucket for file storage"
  type        = string
  default     = "justicebid-staging-storage"
}

# Disaster recovery configuration
variable "enable_cross_region_replication" {
  description = "Enable cross-region replication for disaster recovery"
  type        = bool
  default     = true
}

variable "dr_region" {
  description = "Secondary region for disaster recovery"
  type        = string
  default     = "us-west-2"
}

# Security configuration
variable "enable_waf" {
  description = "Enable AWS WAF for web application firewall protection"
  type        = bool
  default     = true
}

# Tagging configuration
variable "tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default = {
    Environment = "staging"
    Project     = "JusticeBid"
    ManagedBy   = "Terraform"
  }
}

# Monitoring configuration
variable "enable_datadog_monitoring" {
  description = "Enable Datadog monitoring integration"
  type        = bool
  default     = true
}

# API keys and secrets (stored in Parameter Store)
variable "datadog_api_key_parameter_name" {
  description = "SSM Parameter Store name for Datadog API key"
  type        = string
  default     = "/justicebid/staging/datadog/api_key"
}

variable "openai_api_key_parameter_name" {
  description = "SSM Parameter Store name for OpenAI API key"
  type        = string
  default     = "/justicebid/staging/openai/api_key"
}

variable "unicourt_api_key_parameter_name" {
  description = "SSM Parameter Store name for UniCourt API key"
  type        = string
  default     = "/justicebid/staging/unicourt/api_key"
}