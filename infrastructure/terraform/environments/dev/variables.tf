# Environment settings
variable "environment" {
  description = "Environment name used for tagging and naming resources"
  default     = "dev"
  type        = string
}

# AWS settings
variable "aws_region" {
  description = "AWS region where resources will be deployed"
  default     = "us-east-1"
  type        = string
}

# Network settings
variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  default     = "10.0.0.0/16"
  type        = string
}

variable "availability_zones" {
  description = "Availability zones to use for the subnets in the VPC"
  default     = ["us-east-1a", "us-east-1b"]
  type        = list(string)
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for the public subnets"
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
  type        = list(string)
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for the private subnets"
  default     = ["10.0.3.0/24", "10.0.4.0/24"]
  type        = list(string)
}

variable "db_subnet_cidrs" {
  description = "CIDR blocks for the database subnets"
  default     = ["10.0.5.0/24", "10.0.6.0/24"]
  type        = list(string)
}

# Container orchestration settings
variable "container_orchestration" {
  description = "Container orchestration platform to use (ecs or eks)"
  default     = "ecs"  # Using ECS for dev as it's simpler to set up
  type        = string

  validation {
    condition     = contains(["ecs", "eks"], var.container_orchestration)
    error_message = "Valid values for container_orchestration are: ecs, eks."
  }
}

variable "frontend_container_name" {
  description = "Name for the frontend container"
  default     = "justicebid-frontend-dev"
  type        = string
}

variable "backend_container_name" {
  description = "Name for the backend container"
  default     = "justicebid-backend-dev"
  type        = string
}

# Database settings
variable "db_instance_class" {
  description = "RDS instance type for the development environment"
  default     = "db.t3.medium"  # Smaller instance for dev
  type        = string
}

variable "db_allocated_storage" {
  description = "Allocated storage for the RDS instance in GB"
  default     = 20  # Smaller storage for dev
  type        = number
}

variable "db_multi_az" {
  description = "Whether to enable multi-AZ for the RDS instance"
  default     = false  # Single AZ for dev to reduce costs
  type        = bool
}

# ElastiCache settings
variable "redis_node_type" {
  description = "ElastiCache Redis node type"
  default     = "cache.t3.small"  # Smaller instance for dev
  type        = string
}

variable "redis_num_cache_nodes" {
  description = "Number of ElastiCache Redis nodes"
  default     = 1  # Single node for dev
  type        = number
}

# S3 bucket settings
variable "s3_frontend_bucket_name" {
  description = "Name of the S3 bucket for frontend assets"
  default     = "justicebid-frontend-dev"
  type        = string
}

variable "s3_documents_bucket_name" {
  description = "Name of the S3 bucket for document storage"
  default     = "justicebid-documents-dev"
  type        = string
}

# CloudFront settings
variable "cloudfront_enabled" {
  description = "Whether to enable CloudFront for frontend assets"
  default     = true
  type        = bool
}

# OpenSearch settings
variable "enable_opensearch" {
  description = "Whether to enable OpenSearch for full-text search"
  default     = true
  type        = bool
}

variable "opensearch_instance_type" {
  description = "OpenSearch instance type"
  default     = "t3.small.search"  # Smaller instance for dev
  type        = string
}

# Monitoring settings
variable "enable_monitoring" {
  description = "Whether to enable monitoring with CloudWatch and Datadog"
  default     = true
  type        = bool
}

# Backup settings
variable "backup_retention_days" {
  description = "Number of days to retain database backups"
  default     = 7  # Shorter retention for dev
  type        = number
}

# Instance and scaling settings
variable "instance_type_frontend" {
  description = "Instance type for frontend containers"
  default     = "t3.small"  # Smaller instance for dev
  type        = string
}

variable "instance_type_backend" {
  description = "Instance type for backend containers"
  default     = "t3.medium"  # Smaller instance for dev
  type        = string
}

variable "autoscaling_min_capacity_frontend" {
  description = "Minimum number of frontend container instances"
  default     = 1  # Fewer instances for dev
  type        = number
}

variable "autoscaling_max_capacity_frontend" {
  description = "Maximum number of frontend container instances"
  default     = 3  # Fewer max instances for dev
  type        = number
}

# AI services settings
variable "enable_ai_services" {
  description = "Whether to enable AWS AI services integration"
  default     = true
  type        = bool
}

variable "openai_api_key" {
  description = "API key for OpenAI (will be retrieved from AWS Secrets Manager if null)"
  default     = null
  type        = string
  sensitive   = true
}

variable "unicourt_api_key" {
  description = "API key for UniCourt (will be retrieved from AWS Secrets Manager if null)"
  default     = null
  type        = string
  sensitive   = true
}

# Tagging
variable "tags" {
  description = "Tags to apply to all resources"
  default = {
    Environment = "dev"
    Project     = "JusticeBid"
    ManagedBy   = "Terraform"
  }
  type = map(string)
}