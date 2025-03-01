# main.tf - Main Terraform configuration for Justice Bid Rate Negotiation System
# This file defines the infrastructure resources required for the application,
# including VPC, compute, database, caching, and storage resources.

terraform {
  required_version = ">= 1.0.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
    local = {
      source  = "hashicorp/local"
      version = "~> 2.0"
    }
  }
  
  backend "s3" {
    bucket         = "justicebid-terraform-state"
    key            = "infrastructure/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "justicebid-terraform-locks"
  }
}

provider "aws" {
  region  = var.primary_region
  profile = var.aws_profile
  
  default_tags {
    tags = {
      Project     = "JusticeBid"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# Configure a secondary region for disaster recovery
provider "aws" {
  alias   = "dr"
  region  = var.dr_region
  profile = var.aws_profile
  
  default_tags {
    tags = {
      Project     = "JusticeBid"
      Environment = var.environment
      ManagedBy   = "Terraform"
      Role        = "DR"
    }
  }
}

locals {
  name_prefix = "${var.project_name}-${var.environment}"
  
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
    Owner       = "DevOps"
  }
  
  # VPC CIDR blocks for primary and DR regions
  primary_vpc_cidr     = "10.0.0.0/16"
  dr_vpc_cidr          = "10.1.0.0/16"
  
  # Availability zones
  primary_azs = slice(data.aws_availability_zones.available.names, 0, 3)
  
  # Subnet CIDR blocks
  primary_public_subnets  = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  primary_private_subnets = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
  primary_database_subnets = ["10.0.201.0/24", "10.0.202.0/24", "10.0.203.0/24"]
  
  dr_public_subnets  = ["10.1.1.0/24", "10.1.2.0/24", "10.1.3.0/24"]
  dr_private_subnets = ["10.1.101.0/24", "10.1.102.0/24", "10.1.103.0/24"]
  dr_database_subnets = ["10.1.201.0/24", "10.1.202.0/24", "10.1.203.0/24"]
}

# Get available AZs in the region
data "aws_availability_zones" "available" {}

# Generate a random string for resource naming
resource "random_string" "suffix" {
  length  = 8
  special = false
  upper   = false
}

# VPC Module for Primary Region
module "vpc" {
  source = "./modules/vpc"
  
  name                 = "${local.name_prefix}-vpc"
  cidr                 = local.primary_vpc_cidr
  azs                  = local.primary_azs
  public_subnets       = local.primary_public_subnets
  private_subnets      = local.primary_private_subnets
  database_subnets     = local.primary_database_subnets
  
  enable_nat_gateway   = true
  single_nat_gateway   = var.environment != "production"
  enable_vpn_gateway   = false
  
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  # Database subnet configuration
  create_database_subnet_group       = true
  create_database_subnet_route_table = true
  
  tags = local.common_tags
}

# VPC Module for DR Region
module "vpc_dr" {
  source = "./modules/vpc"
  providers = {
    aws = aws.dr
  }
  
  name                 = "${local.name_prefix}-vpc-dr"
  cidr                 = local.dr_vpc_cidr
  azs                  = slice(data.aws_availability_zones.available_dr.names, 0, 3)
  public_subnets       = local.dr_public_subnets
  private_subnets      = local.dr_private_subnets
  database_subnets     = local.dr_database_subnets
  
  enable_nat_gateway   = true
  single_nat_gateway   = var.environment != "production"
  enable_vpn_gateway   = false
  
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  # Database subnet configuration
  create_database_subnet_group       = true
  create_database_subnet_route_table = true
  
  tags = merge(local.common_tags, {
    Role = "DR"
  })
}

# Get available AZs in the DR region
data "aws_availability_zones" "available_dr" {
  provider = aws.dr
}

# KMS Module for encryption
module "kms" {
  source = "./modules/kms"
  
  name                    = "${local.name_prefix}-key"
  description             = "KMS key for Justice Bid application encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true
  
  tags = local.common_tags
}

# KMS Module for DR region
module "kms_dr" {
  source = "./modules/kms"
  providers = {
    aws = aws.dr
  }
  
  name                    = "${local.name_prefix}-key-dr"
  description             = "KMS key for Justice Bid DR encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true
  
  tags = merge(local.common_tags, {
    Role = "DR"
  })
}

# EKS Module
module "eks" {
  source = "./modules/eks"
  
  cluster_name    = "${local.name_prefix}-cluster"
  cluster_version = var.kubernetes_version
  
  vpc_id          = module.vpc.vpc_id
  subnet_ids      = module.vpc.private_subnets
  
  # Node groups
  node_groups = {
    application = {
      desired_capacity = var.app_node_desired_capacity
      max_capacity     = var.app_node_max_capacity
      min_capacity     = var.app_node_min_capacity
      instance_types   = var.app_node_instance_types
      disk_size        = 50
    },
    analytics = {
      desired_capacity = var.analytics_node_desired_capacity
      max_capacity     = var.analytics_node_max_capacity
      min_capacity     = var.analytics_node_min_capacity
      instance_types   = var.analytics_node_instance_types
      disk_size        = 100
    }
  }
  
  # IAM roles for service accounts
  enable_irsa = true
  
  # Cluster encryption
  cluster_encryption_config = [
    {
      provider_key_arn = module.kms.key_arn
      resources        = ["secrets"]
    }
  ]
  
  tags = local.common_tags
}

# RDS Module
module "rds" {
  source = "./modules/rds"
  
  identifier           = "${local.name_prefix}-postgres"
  engine               = "postgres"
  engine_version       = "15.3"
  instance_class       = var.db_instance_class
  allocated_storage    = var.db_allocated_storage
  max_allocated_storage = var.db_max_allocated_storage
  
  db_name              = "justicebid"
  username             = "dbadmin"
  port                 = 5432
  
  vpc_security_group_ids = [module.security_groups.database_sg_id]
  subnet_ids             = module.vpc.database_subnets
  
  multi_az               = var.environment == "production"
  backup_retention_period = var.environment == "production" ? 30 : 7
  deletion_protection    = var.environment == "production"
  
  storage_encrypted      = true
  kms_key_id             = module.kms.key_arn
  
  # Enhanced monitoring
  monitoring_interval    = 60
  monitoring_role_name   = "${local.name_prefix}-rds-monitoring-role"
  create_monitoring_role = true
  
  # Automated backups to S3
  backup_window          = "03:00-06:00"
  maintenance_window     = "Mon:00:00-Mon:03:00"
  
  # Parameter group
  family                 = "postgres15"
  parameters = [
    {
      name  = "shared_buffers"
      value = "{DBInstanceClassMemory/4}"
    },
    {
      name  = "max_connections"
      value = "500"
    },
    {
      name  = "log_statement"
      value = "ddl"
    }
  ]
  
  tags = local.common_tags
}

# Read replica in DR region
module "rds_replica" {
  source = "./modules/rds"
  providers = {
    aws = aws.dr
  }
  
  identifier           = "${local.name_prefix}-postgres-replica"
  replicate_source_db  = module.rds.db_instance_arn
  
  vpc_security_group_ids = [module.security_groups_dr.database_sg_id]
  subnet_ids             = module.vpc_dr.database_subnets
  
  backup_retention_period = 7
  deletion_protection     = var.environment == "production"
  
  storage_encrypted       = true
  kms_key_id              = module.kms_dr.key_arn
  
  # Enhanced monitoring
  monitoring_interval     = 60
  monitoring_role_name    = "${local.name_prefix}-rds-replica-monitoring-role"
  create_monitoring_role  = true
  
  tags = merge(local.common_tags, {
    Role = "DR"
  })
}

# ElastiCache Module
module "elasticache" {
  source = "./modules/elasticache"
  
  name                = "${local.name_prefix}-redis"
  engine              = "redis"
  engine_version      = "6.x"
  node_type           = var.cache_node_type
  num_cache_nodes     = var.environment == "production" ? 3 : 1
  
  vpc_id              = module.vpc.vpc_id
  subnet_ids          = module.vpc.private_subnets
  security_group_ids  = [module.security_groups.cache_sg_id]
  
  automatic_failover_enabled = var.environment == "production"
  multi_az_enabled           = var.environment == "production"
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  
  tags = local.common_tags
}

# S3 Module for file storage
module "s3" {
  source = "./modules/s3"
  
  bucket_name         = "${local.name_prefix}-files-${random_string.suffix.result}"
  versioning_enabled  = true
  
  # Lifecycle rules
  lifecycle_rules = [
    {
      id      = "archive-old-files"
      enabled = true
      
      transition = [
        {
          days          = 90
          storage_class = "STANDARD_IA"
        },
        {
          days          = 365
          storage_class = "GLACIER"
        }
      ]
      
      expiration = {
        days = 2555  # 7 years
      }
    }
  ]
  
  # Server-side encryption
  server_side_encryption_configuration = {
    rule = {
      apply_server_side_encryption_by_default = {
        kms_master_key_id = module.kms.key_arn
        sse_algorithm     = "aws:kms"
      }
    }
  }
  
  # CORS configuration
  cors_rule = {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "PUT", "POST", "DELETE", "HEAD"]
    allowed_origins = var.environment == "production" ? ["https://*.justicebid.com"] : ["*"]
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
  
  # Replication to DR region
  replication_configuration = {
    role = module.iam.replication_role_arn
    rules = [
      {
        id       = "EntireBucket"
        status   = "Enabled"
        priority = 10
        
        destination = {
          bucket        = module.s3_dr.bucket_arn
          storage_class = "STANDARD"
        }
      }
    ]
  }
  
  tags = local.common_tags
}

# S3 Module for DR region
module "s3_dr" {
  source = "./modules/s3"
  providers = {
    aws = aws.dr
  }
  
  bucket_name         = "${local.name_prefix}-files-dr-${random_string.suffix.result}"
  versioning_enabled  = true
  
  # Server-side encryption
  server_side_encryption_configuration = {
    rule = {
      apply_server_side_encryption_by_default = {
        kms_master_key_id = module.kms_dr.key_arn
        sse_algorithm     = "aws:kms"
      }
    }
  }
  
  tags = merge(local.common_tags, {
    Role = "DR"
  })
}

# CloudFront Module
module "cloudfront" {
  source = "./modules/cloudfront"
  
  name                = "${local.name_prefix}-cdn"
  s3_bucket_domain    = module.s3.bucket_regional_domain_name
  
  # Origin access identity
  create_origin_access_identity = true
  origin_access_identity_comment = "CloudFront access to ${local.name_prefix} S3 bucket"
  
  # Cache behavior
  default_cache_behavior = {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = module.s3.bucket_regional_domain_name
    
    forwarded_values = {
      query_string = true
      cookies = {
        forward = "none"
      }
    }
    
    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
  }
  
  # Custom error responses
  custom_error_response = [
    {
      error_code            = 404
      response_code         = 200
      response_page_path    = "/index.html"
      error_caching_min_ttl = 10
    }
  ]
  
  # WAF integration
  web_acl_id = module.waf.web_acl_arn
  
  tags = local.common_tags
}

# WAF Module
module "waf" {
  source = "./modules/waf"
  
  name        = "${local.name_prefix}-waf"
  description = "WAF for Justice Bid application"
  
  # IP rate limiting
  ip_rate_limit = 2000
  
  # Rule sets
  rule_groups = [
    "AWSManagedRulesCommonRuleSet",
    "AWSManagedRulesAmazonIpReputationList",
    "AWSManagedRulesSQLiRuleSet"
  ]
  
  tags = local.common_tags
}

# IAM Module
module "iam" {
  source = "./modules/iam"
  
  name_prefix = local.name_prefix
  
  # Create roles for various services
  eks_role_name              = "${local.name_prefix}-eks-role"
  eks_node_role_name         = "${local.name_prefix}-eks-node-role"
  s3_replication_role_name   = "${local.name_prefix}-s3-replication-role"
  
  # S3 replication configuration
  s3_source_bucket      = module.s3.bucket_arn
  s3_destination_bucket = module.s3_dr.bucket_arn
  
  tags = local.common_tags
}

# Security Groups Module
module "security_groups" {
  source = "./modules/security_groups"
  
  vpc_id      = module.vpc.vpc_id
  name_prefix = local.name_prefix
  
  # CIDR blocks for security group rules
  private_subnets_cidr = module.vpc.private_subnets_cidr_blocks
  
  tags = local.common_tags
}

# Security Groups Module for DR region
module "security_groups_dr" {
  source = "./modules/security_groups"
  providers = {
    aws = aws.dr
  }
  
  vpc_id      = module.vpc_dr.vpc_id
  name_prefix = "${local.name_prefix}-dr"
  
  # CIDR blocks for security group rules
  private_subnets_cidr = module.vpc_dr.private_subnets_cidr_blocks
  
  tags = merge(local.common_tags, {
    Role = "DR"
  })
}

# Route53 Module
module "route53" {
  source = "./modules/route53"
  
  domain_name     = var.domain_name
  
  # A records
  a_records = {
    "" = {
      name    = ""
      type    = "A"
      alias = {
        name                   = module.cloudfront.distribution_domain_name
        zone_id                = module.cloudfront.distribution_hosted_zone_id
        evaluate_target_health = false
      }
    }
  }
  
  # CNAME records
  cname_records = {
    "api" = {
      name  = "api"
      type  = "CNAME"
      ttl   = 300
      records = [module.alb.dns_name]
    }
  }
  
  tags = local.common_tags
}

# Application Load Balancer Module
module "alb" {
  source = "./modules/alb"
  
  name               = "${local.name_prefix}-alb"
  internal           = false
  load_balancer_type = "application"
  
  vpc_id          = module.vpc.vpc_id
  subnets         = module.vpc.public_subnets
  security_groups = [module.security_groups.alb_sg_id]
  
  # Target groups
  target_groups = {
    api = {
      name        = "${local.name_prefix}-api"
      port        = 80
      protocol    = "HTTP"
      target_type = "ip"
      health_check = {
        path                = "/health"
        interval            = 30
        timeout             = 5
        healthy_threshold   = 2
        unhealthy_threshold = 3
        matcher             = "200"
      }
    }
  }
  
  # HTTPS Listener
  https_listeners = [
    {
      port               = 443
      protocol           = "HTTPS"
      certificate_arn    = module.acm.certificate_arn
      target_group_index = 0
      
      actions = [{
        type               = "forward"
        target_group_index = 0
      }]
    }
  ]
  
  # HTTP to HTTPS redirect
  http_tcp_listeners = [
    {
      port               = 80
      protocol           = "HTTP"
      action_type        = "redirect"
      redirect = {
        port        = "443"
        protocol    = "HTTPS"
        status_code = "HTTP_301"
      }
    }
  ]
  
  # WAF integration
  web_acl_id = module.waf.web_acl_arn
  
  tags = local.common_tags
}

# ACM Module
module "acm" {
  source = "./modules/acm"
  
  domain_name         = var.domain_name
  validation_method   = "DNS"
  zone_id             = module.route53.zone_id
  
  subject_alternative_names = [
    "*.${var.domain_name}"
  ]
  
  # Validation record creation
  create_route53_validation_record = true
  
  tags = local.common_tags
}

# CloudWatch Module for monitoring
module "cloudwatch" {
  source = "./modules/cloudwatch"
  
  name_prefix = local.name_prefix
  
  # Dashboard configuration
  create_dashboard = true
  dashboard_name   = "${local.name_prefix}-dashboard"
  
  # Alarms
  alarms = {
    high_cpu = {
      alarm_name          = "${local.name_prefix}-high-cpu"
      comparison_operator = "GreaterThanThreshold"
      evaluation_periods  = 2
      metric_name         = "CPUUtilization"
      namespace           = "AWS/EC2"
      period              = 300
      statistic           = "Average"
      threshold           = 80
      alarm_description   = "This metric monitors ec2 cpu utilization"
    },
    db_connections = {
      alarm_name          = "${local.name_prefix}-db-connections"
      comparison_operator = "GreaterThanThreshold"
      evaluation_periods  = 2
      metric_name         = "DatabaseConnections"
      namespace           = "AWS/RDS"
      period              = 300
      statistic           = "Average"
      threshold           = 450  # 90% of max 500
      alarm_description   = "This metric monitors database connections"
    }
  }
  
  tags = local.common_tags
}

# Outputs
output "vpc_id" {
  description = "The ID of the VPC"
  value       = module.vpc.vpc_id
}

output "public_subnet_ids" {
  description = "List of IDs of public subnets"
  value       = module.vpc.public_subnets
}

output "private_subnet_ids" {
  description = "List of IDs of private subnets"
  value       = module.vpc.private_subnets
}

output "database_subnet_ids" {
  description = "List of IDs of database subnets"
  value       = module.vpc.database_subnets
}

output "eks_cluster_endpoint" {
  description = "Endpoint for EKS control plane"
  value       = module.eks.cluster_endpoint
}

output "eks_cluster_certificate_authority_data" {
  description = "Base64 encoded certificate data required to communicate with the cluster"
  value       = module.eks.cluster_certificate_authority_data
  sensitive   = true
}

output "rds_endpoint" {
  description = "The connection endpoint for the RDS instance"
  value       = module.rds.db_instance_endpoint
}

output "rds_replica_endpoint" {
  description = "The connection endpoint for the RDS replica"
  value       = module.rds_replica.db_instance_endpoint
}

output "elasticache_endpoint" {
  description = "The DNS name of the ElastiCache cluster"
  value       = module.elasticache.cluster_endpoint
}

output "s3_bucket_name" {
  description = "The name of the S3 bucket"
  value       = module.s3.bucket_name
}

output "cloudfront_distribution_id" {
  description = "The ID of the CloudFront distribution"
  value       = module.cloudfront.distribution_id
}

output "cloudfront_domain_name" {
  description = "The domain name of the CloudFront distribution"
  value       = module.cloudfront.distribution_domain_name
}

output "alb_dns_name" {
  description = "The DNS name of the load balancer"
  value       = module.alb.dns_name
}