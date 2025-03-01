# Terraform configuration for the Justice Bid Rate Negotiation System's staging environment
# This file defines all the infrastructure resources required for the staging environment

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
  
  backend "s3" {
    bucket         = "justice-bid-terraform-state"
    key            = "staging/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "justice-bid-terraform-locks"
  }
  
  required_version = "~> 1.0"
}

provider "aws" {
  region  = "us-east-1"
  profile = "justice-bid-staging"
  
  default_tags {
    tags = {
      Environment = "staging"
      Project     = "justice-bid"
      ManagedBy   = "terraform"
    }
  }
}

# Variables for configuration
variable "ssl_certificate_arn" {
  description = "ARN of the SSL certificate for HTTPS"
  type        = string
}

variable "hosted_zone_id" {
  description = "Route53 hosted zone ID for DNS records"
  type        = string
}

variable "alert_email" {
  description = "Email address for monitoring alerts"
  type        = string
}

# Local variables for environment-specific configuration
locals {
  environment     = "staging"
  vpc_cidr        = "10.1.0.0/16"
  azs             = ["us-east-1a", "us-east-1b", "us-east-1c"]
  resource_prefix = "jb-${local.environment}"
}

# VPC and Networking
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "3.14.0"

  name = "justice-bid-staging-vpc"
  cidr = "10.1.0.0/16"
  
  azs              = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnets  = ["10.1.1.0/24", "10.1.2.0/24", "10.1.3.0/24"]
  public_subnets   = ["10.1.101.0/24", "10.1.102.0/24", "10.1.103.0/24"]
  database_subnets = ["10.1.21.0/24", "10.1.22.0/24", "10.1.23.0/24"]
  elasticache_subnets = ["10.1.31.0/24", "10.1.32.0/24", "10.1.33.0/24"]
  
  enable_nat_gateway   = true
  single_nat_gateway   = true
  enable_dns_hostnames = true
}

# ECS Cluster for Container Orchestration
module "ecs" {
  source = "../../../modules/ecs"

  name            = "jb-staging-cluster"
  vpc_id          = module.vpc.vpc_id
  subnet_ids      = module.vpc.private_subnets
  environment     = "staging"
  instance_type   = "t3.large"
  min_size        = 2
  max_size        = 4
  desired_capacity = 2
}

# PostgreSQL Database
module "rds" {
  source = "../../../modules/rds"

  identifier       = "jb-staging-postgres"
  engine           = "postgres"
  engine_version   = "13.7"
  instance_class   = "db.t3.large"
  allocated_storage = 50
  vpc_id           = module.vpc.vpc_id
  subnet_ids       = module.vpc.database_subnets
  environment      = "staging"
  multi_az         = true
  backup_retention_period = 7
}

# Redis Cache
module "elasticache" {
  source = "../../../modules/elasticache"

  cluster_id      = "jb-staging-redis"
  node_type       = "cache.t3.medium"
  vpc_id          = module.vpc.vpc_id
  subnet_ids      = module.vpc.elasticache_subnets
  environment     = "staging"
  num_cache_nodes = 2
  engine_version  = "6.x"
  automatic_failover_enabled = true
}

# S3 Buckets for Storage
module "s3" {
  source = "../../../modules/s3"

  bucket_prefix        = "jb-staging"
  environment          = "staging"
  versioning_enabled   = true
  lifecycle_rules_enabled = true
}

# Application Load Balancer
module "load_balancer" {
  source  = "terraform-aws-modules/alb/aws"
  version = "6.0.0"

  name                      = "jb-staging-alb"
  vpc_id                    = module.vpc.vpc_id
  subnets                   = module.vpc.public_subnets
  internal                  = false
  enable_deletion_protection = true
  
  http_tcp_listeners = [
    {
      port        = 80
      protocol    = "HTTP"
      action_type = "redirect"
    }
  ]
  
  https_listeners = [
    {
      port            = 443
      protocol        = "HTTPS"
      certificate_arn = var.ssl_certificate_arn
    }
  ]
}

# CloudWatch Monitoring
module "monitoring" {
  source = "../../../modules/monitoring"

  environment            = "staging"
  ecs_cluster_name       = module.ecs.cluster_name
  rds_identifier         = module.rds.identifier
  elasticache_cluster_id = module.elasticache.cluster_id
  alb_arn_suffix         = module.load_balancer.lb_arn_suffix
  notification_email     = var.alert_email
}

# WAF for API Protection
module "waf" {
  source  = "terraform-aws-modules/waf/aws"
  version = "1.1.1"

  name         = "jb-staging-waf"
  scope        = "REGIONAL"
  resource_arn = module.load_balancer.lb_arn
  
  rules = [
    {
      name     = "AWSManagedRulesCommonRuleSet",
      priority = 10
    },
    {
      name     = "RateLimitRule",
      priority = 20,
      limit    = 3000
    }
  ]
}

# Add DNS record for the staging environment
resource "aws_route53_record" "justicebid_staging" {
  zone_id = var.hosted_zone_id
  name    = "staging.justicebid.com"
  type    = "A"
  
  alias {
    name                   = module.load_balancer.lb_dns_name
    zone_id                = module.load_balancer.lb_zone_id
    evaluate_target_health = true
  }
}