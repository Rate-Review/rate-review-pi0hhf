# Import core configurations from parent modules
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.4.3"
    }
  }
  required_version = ">= 1.2.0"
  
  backend "s3" {
    bucket         = "justice-bid-terraform-state"
    key            = "production/terraform.tfstate"
    region         = "us-west-2"
    dynamodb_table = "justice-bid-terraform-locks"
    encrypt        = true
  }
}

provider "aws" {
  region = var.primary_region
  
  default_tags {
    tags = local.common_tags
  }
}

provider "aws" {
  alias  = "dr"
  region = var.dr_region
  
  default_tags {
    tags = local.common_tags
  }
}

locals {
  common_tags = {
    Project     = "JusticeBid"
    Environment = "production"
    ManagedBy   = "Terraform"
    CostCenter  = "JusticeBid-Prod"
  }
  
  name_prefix = "justice-bid-prod"
}

# Generate a random password for database
resource "random_password" "db_password" {
  length           = 24
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

# Secrets Management
resource "aws_secretsmanager_secret" "database_credentials" {
  name                    = "justice-bid-production/database-credentials"
  description             = "Database credentials for Justice Bid production environment"
  recovery_window_in_days = 7
  tags                    = local.common_tags
}

resource "aws_secretsmanager_secret_version" "database_credentials" {
  secret_id     = aws_secretsmanager_secret.database_credentials.id
  secret_string = "{\"username\":\"dbadmin\",\"password\":\"${random_password.db_password.result}\"}"
}

resource "aws_secretsmanager_secret" "api_keys" {
  name                    = "justice-bid-production/api-keys"
  description             = "API keys for external services in production environment"
  recovery_window_in_days = 7
  tags                    = local.common_tags
}

resource "aws_secretsmanager_secret_version" "api_keys" {
  secret_id     = aws_secretsmanager_secret.api_keys.id
  secret_string = "{\"openai\":\"${var.openai_api_key}\",\"unicourt\":\"${var.unicourt_api_key}\"}"
}

# VPC Module
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 3.19.0"
  
  name                 = "${local.name_prefix}-vpc"
  cidr                 = var.vpc_cidr
  azs                  = var.availability_zones
  private_subnets      = var.private_subnet_cidrs
  public_subnets       = var.public_subnet_cidrs
  database_subnets     = var.database_subnet_cidrs
  elasticache_subnets  = var.elasticache_subnet_cidrs
  
  enable_nat_gateway   = var.enable_nat_gateway
  single_nat_gateway   = var.single_nat_gateway
  enable_vpn_gateway   = false
  
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  create_database_subnet_group       = true
  create_elasticache_subnet_group    = true
  
  tags = local.common_tags
}

# EKS Module
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.0.0"
  
  cluster_name    = "${local.name_prefix}-eks"
  cluster_version = var.eks_cluster_version
  
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets
  
  instance_types = var.eks_node_instance_types
  min_size       = var.eks_min_size
  max_size       = var.eks_max_size
  desired_size   = var.eks_desired_capacity
  capacity_type  = "ON_DEMAND"
  
  cluster_endpoint_public_access       = true
  cluster_endpoint_private_access      = true
  cluster_endpoint_public_access_cidrs = ["0.0.0.0/0"]
  
  cluster_encryption_config = {
    resources = ["secrets"]
  }
  
  enable_irsa = true
  
  cluster_log_types = ["api", "audit", "authenticator", "controllerManager", "scheduler"]
  
  tags = local.common_tags
  
  depends_on = [module.vpc]
}

# RDS Module
module "rds" {
  source  = "terraform-aws-modules/rds/aws"
  version = "~> 5.0.0"
  
  environment        = "production"
  identifier         = "${local.name_prefix}-postgresql"
  engine             = "postgres"
  engine_version     = var.rds_engine_version
  instance_class     = var.rds_instance_class
  allocated_storage  = var.rds_allocated_storage
  max_allocated_storage = var.rds_max_allocated_storage
  
  db_name  = "justicebid"
  username = "dbadmin"
  password = random_password.db_password.result
  port     = 5432
  
  vpc_id              = module.vpc.vpc_id
  subnet_ids          = module.vpc.database_subnets
  
  multi_az             = var.rds_multi_az
  backup_retention_period = var.rds_backup_retention_period
  deletion_protection = var.rds_deletion_protection
  
  storage_encrypted   = true
  performance_insights_enabled = var.rds_enable_performance_insights
  monitoring_interval = 60
  create_monitoring_role = true
  
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
  
  replica_count = 1
  
  create_db_subnet_group = false
  db_subnet_group_name   = module.vpc.database_subnet_group_name
  
  family = "postgres15"
  
  tags = local.common_tags
  
  depends_on = [module.vpc]
}

# ElastiCache Module
module "elasticache" {
  source  = "terraform-aws-modules/elasticache/aws"
  version = "~> 4.0.0"
  
  environment        = "production"
  name               = "${local.name_prefix}-redis"
  engine             = "redis"
  engine_version     = var.elasticache_engine_version
  node_type          = var.elasticache_node_type
  
  cluster_mode_enabled = var.elasticache_cluster_mode_enabled
  num_node_groups      = var.elasticache_num_node_groups
  replicas_per_node_group = var.elasticache_replicas_per_node_group
  
  automatic_failover_enabled = true
  multi_az_enabled = true
  
  subnet_group_name  = module.vpc.elasticache_subnet_group_name
  security_group_ids = [aws_security_group.elasticache.id]
  
  tags = local.common_tags
  
  depends_on = [module.vpc]
}

# Security group for ElastiCache
resource "aws_security_group" "elasticache" {
  name        = "${local.name_prefix}-elasticache-sg"
  description = "Security group for ElastiCache Redis cluster"
  vpc_id      = module.vpc.vpc_id
  
  ingress {
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = var.private_subnet_cidrs
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = merge(local.common_tags, { Name = "${local.name_prefix}-elasticache-sg" })
}

# S3 Storage Module
module "s3" {
  source = "../../modules/s3"
  
  environment = "production"
  bucket_prefix = var.s3_bucket_prefix
  versioning_enabled = var.s3_versioning_enabled
  encryption_enabled = var.s3_encryption_enabled
  create_replication = var.s3_create_replication
  dr_region = var.dr_region
  
  tags = local.common_tags
}

# CloudFront Distribution
resource "aws_cloudfront_distribution" "frontend" {
  enabled             = var.cloudfront_enabled
  price_class         = "PriceClass_100"
  aliases             = [var.domain_name, "www.${var.domain_name}"]
  
  origin {
    domain_name = "${module.s3.static_website_bucket}.s3-website-${var.primary_region}.amazonaws.com"
    origin_id   = "S3-${module.s3.static_website_bucket}"
    
    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "http-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }
  
  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-${module.s3.static_website_bucket}"
    
    viewer_protocol_policy = "redirect-to-https"
    compress               = true
    min_ttl                = 0
    default_ttl            = 86400
    max_ttl                = 31536000
    
    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
  }
  
  custom_error_response {
    error_code         = 404
    response_code      = 200
    response_page_path = "/index.html"
  }
  
  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
  
  viewer_certificate {
    acm_certificate_arn      = var.certificate_arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }
  
  tags = local.common_tags
}

# Route53 Records
resource "aws_route53_record" "domain" {
  zone_id = var.zone_id
  name    = var.domain_name
  type    = "A"
  
  alias {
    name                   = aws_cloudfront_distribution.frontend.domain_name
    zone_id                = aws_cloudfront_distribution.frontend.hosted_zone_id
    evaluate_target_health = false
  }
}

resource "aws_route53_record" "www" {
  zone_id = var.zone_id
  name    = "www.${var.domain_name}"
  type    = "A"
  
  alias {
    name                   = aws_cloudfront_distribution.frontend.domain_name
    zone_id                = aws_cloudfront_distribution.frontend.hosted_zone_id
    evaluate_target_health = false
  }
}

# WAF Module
module "waf" {
  source = "../../modules/waf"
  
  enabled                    = var.waf_enabled
  name                       = "${local.name_prefix}-waf"
  rate_limit                 = var.waf_rate_limit
  cloudfront_distribution_id = aws_cloudfront_distribution.frontend.id
  
  tags = local.common_tags
  
  count = var.waf_enabled ? 1 : 0
}

# OpenSearch Module
module "opensearch" {
  source = "../../modules/opensearch"
  
  environment        = "production"
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnets
  domain_name        = "${local.name_prefix}-search"
  instance_type      = var.opensearch_instance_type
  instance_count     = var.opensearch_instance_count
  zone_awareness_enabled = var.opensearch_zone_awareness_enabled
  ebs_volume_size    = var.opensearch_ebs_volume_size
  encrypt_at_rest    = true
  node_to_node_encryption = true
  
  tags = local.common_tags
  
  depends_on = [module.vpc]
  
  count = var.opensearch_enabled ? 1 : 0
}

# Monitoring Module
module "monitoring" {
  source = "../../modules/monitoring"
  
  environment         = "production"
  eks_cluster_name    = module.eks.cluster_name
  rds_instance_id     = module.rds.db_instance_id
  elasticache_cluster_id = module.elasticache.cluster_id
  alarm_email         = var.alarm_email
  enable_prometheus   = var.monitoring_enabled
  prometheus_retention_days = var.prometheus_retention_days
  
  tags = local.common_tags
  
  depends_on = [module.eks, module.rds, module.elasticache]
  
  count = var.monitoring_enabled ? 1 : 0
}

# SNS Topic for Alerts
resource "aws_sns_topic" "alerts" {
  name = "${local.name_prefix}-alerts"
  tags = local.common_tags
}

resource "aws_sns_topic_subscription" "email" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alarm_email
}

# CloudWatch Alarms
resource "aws_cloudwatch_metric_alarm" "rds_cpu" {
  alarm_name          = "${local.name_prefix}-rds-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "Alert when RDS CPU exceeds 80% for 15 minutes"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  ok_actions          = [aws_sns_topic.alerts.arn]
  
  dimensions = {
    DBInstanceIdentifier = module.rds.db_instance_id
  }
  
  tags = local.common_tags
}

resource "aws_cloudwatch_metric_alarm" "elasticache_cpu" {
  alarm_name          = "${local.name_prefix}-elasticache-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ElastiCache"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "Alert when ElastiCache CPU exceeds 80% for 15 minutes"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  ok_actions          = [aws_sns_topic.alerts.arn]
  
  dimensions = {
    CacheClusterId = module.elasticache.cluster_id
  }
  
  tags = local.common_tags
}

# Outputs
output "vpc_id" {
  description = "The ID of the VPC"
  value       = module.vpc.vpc_id
}

output "eks_cluster_endpoint" {
  description = "The endpoint for the EKS Kubernetes API"
  value       = module.eks.cluster_endpoint
}

output "database_endpoint" {
  description = "The connection endpoint for the RDS database"
  value       = module.rds.db_instance_endpoint
}

output "elasticache_endpoint" {
  description = "The connection endpoint for ElastiCache"
  value       = module.elasticache.cluster_endpoint
}

output "s3_bucket_names" {
  description = "The names of the S3 buckets created"
  value       = module.s3.bucket_names
}

output "cloudfront_distribution_id" {
  description = "The ID of the CloudFront distribution"
  value       = aws_cloudfront_distribution.frontend.id
}