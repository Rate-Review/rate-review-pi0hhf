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
    key            = "dev/terraform.tfstate"
    region         = "us-west-2"
    dynamodb_table = "justice-bid-terraform-locks"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = local.common_tags
  }
}

locals {
  common_tags = {
    Project     = "JusticeBid"
    Environment = "dev"
    ManagedBy   = "Terraform"
  }
  
  dev_config = {
    eks_min_size = 2
    eks_max_size = 4
    eks_desired_size = 2
    multi_az = false
    rds_instance_class = "db.t3.medium"
    rds_allocated_storage = 20
    elasticache_node_type = "cache.t3.small"
    cluster_mode = false
  }
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 3.19.0"

  name = "justice-bid-dev-vpc"
  cidr = var.vpc_cidr

  azs             = var.availability_zones
  private_subnets = var.private_subnet_cidrs
  public_subnets  = var.public_subnet_cidrs
  database_subnets = var.database_subnet_cidrs
  elasticache_subnets = ["10.0.31.0/24", "10.0.32.0/24"]

  enable_nat_gateway = true
  single_nat_gateway = true
  enable_vpn_gateway = false

  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = local.common_tags
}

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.0.0"

  cluster_name    = "justice-bid-dev-eks"
  cluster_version = "1.27"
  
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets
  
  eks_managed_node_groups = {
    default = {
      instance_types = ["t3.medium"]
      
      min_size     = local.dev_config.eks_min_size
      max_size     = local.dev_config.eks_max_size
      desired_size = local.dev_config.eks_desired_size
      
      # Use spot instances for cost savings in dev
      capacity_type = "SPOT"
    }
  }
  
  # Allow public access to the cluster API for easier development
  cluster_endpoint_public_access = true
  
  tags = local.common_tags
  
  depends_on = [module.vpc]
}

module "elasticache" {
  source  = "terraform-aws-modules/elasticache/aws"
  version = "~> 4.0.0"

  name = "justice-bid-dev-redis"
  
  engine          = "redis"
  engine_version  = "7.0"
  node_type       = local.dev_config.elasticache_node_type
  num_cache_nodes = var.redis_num_cache_nodes
  
  vpc_id         = module.vpc.vpc_id
  subnet_ids     = module.vpc.elasticache_subnets
  
  # Simplified HA for dev
  automatic_failover_enabled = false
  cluster_mode_enabled       = local.dev_config.cluster_mode
  
  tags = local.common_tags
  
  depends_on = [module.vpc]
}

module "s3" {
  source  = "terraform-aws-modules/s3-bucket/aws"
  version = "~> 3.0.0"

  bucket = "justice-bid-dev-data-${random_string.suffix.result}"
  acl    = "private"

  versioning = {
    enabled = true
  }

  server_side_encryption_configuration = {
    rule = {
      apply_server_side_encryption_by_default = {
        sse_algorithm = "AES256"
      }
    }
  }

  lifecycle_rule = [
    {
      id      = "dev-data"
      enabled = true
      
      transition = [
        {
          days          = 90
          storage_class = "STANDARD_IA"
        }
      ]
      
      expiration = {
        days = 365  # Shorter retention for dev environment
      }
    }
  ]

  tags = local.common_tags
}

resource "random_string" "suffix" {
  length  = 8
  special = false
  upper   = false
}

module "monitoring" {
  source = "../../modules/monitoring"
  count  = var.enable_monitoring ? 1 : 0
  
  environment              = "dev"
  eks_cluster_name         = module.eks.cluster_name
  elasticache_cluster_id   = module.elasticache.cluster_id
  alarm_email              = "dev-alerts@justicebid.com"
  enable_prometheus        = var.enable_monitoring
  prometheus_retention_days = 7
  
  depends_on = [module.eks, module.elasticache]
}

module "opensearch" {
  source = "../../modules/opensearch"
  count  = var.enable_opensearch ? 1 : 0
  
  domain_name         = "justice-bid-dev-search"
  environment         = "dev"
  vpc_id              = module.vpc.vpc_id
  private_subnet_ids  = module.vpc.private_subnets
  
  instance_type       = var.opensearch_instance_type
  instance_count      = 1
  zone_awareness_enabled = false
  ebs_volume_size     = 20
  
  depends_on = [module.vpc]
}

resource "random_password" "db_password" {
  length  = 16
  special = false
}

resource "aws_secretsmanager_secret" "database_credentials" {
  name                    = "justice-bid-dev/database-credentials"
  description             = "Database credentials for Justice Bid development environment"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "database_credentials" {
  secret_id     = aws_secretsmanager_secret.database_credentials.id
  secret_string = jsonencode({
    username = "dbadmin",
    password = random_password.db_password.result
  })
}

resource "aws_secretsmanager_secret" "api_keys" {
  name                    = "justice-bid-dev/api-keys"
  description             = "API keys for external services in development environment"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "api_keys" {
  secret_id     = aws_secretsmanager_secret.api_keys.id
  secret_string = jsonencode({
    openai    = var.openai_api_key,
    unicourt  = var.unicourt_api_key
  })
}

output "eks_cluster_endpoint" {
  description = "Endpoint for EKS control plane"
  value       = module.eks.cluster_endpoint
}

output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}