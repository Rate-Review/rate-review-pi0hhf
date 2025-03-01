# Amazon ElastiCache (Redis) module for Justice Bid Rate Negotiation System
# This module provisions a highly available Redis cluster for the application's caching needs

# Create subnet group for ElastiCache
resource "aws_elasticache_subnet_group" "justice_bid_cache_subnet_group" {
  name        = "${var.name_prefix}-cache-subnet-group"
  description = "Subnet group for Justice Bid Redis cache"
  subnet_ids  = var.subnet_ids

  tags = merge(
    var.tags,
    {
      Name = "${var.name_prefix}-cache-subnet-group"
    }
  )
}

# Create parameter group for Redis configuration
resource "aws_elasticache_parameter_group" "justice_bid_cache_parameter_group" {
  name        = "${var.name_prefix}-cache-params"
  family      = "redis6.x"
  description = "Parameter group for Justice Bid Redis cache"

  # Configure volatile-lru to evict only keys with TTL when memory is full
  parameter {
    name  = "maxmemory-policy"
    value = "volatile-lru"
  }

  # Enable keyspace notifications for cache invalidation support
  parameter {
    name  = "notify-keyspace-events"
    value = "Ex"
  }

  # Enable active defragmentation to optimize memory usage
  parameter {
    name  = "activedefrag"
    value = "yes"
  }

  # Set client output buffer limits for pubsub channels
  parameter {
    name  = "client-output-buffer-limit-pubsub-hard-limit"
    value = "64mb"
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.name_prefix}-cache-params"
    }
  )
}

# Create security group for Redis access
resource "aws_security_group" "justice_bid_cache_security_group" {
  name        = "${var.name_prefix}-cache-sg"
  description = "Security group for Justice Bid Redis cache"
  vpc_id      = var.vpc_id

  # Allow Redis traffic from application security groups
  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = var.app_security_group_ids
    description     = "Allow Redis traffic from application tier"
  }

  # Allow all outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.name_prefix}-cache-sg"
    }
  )
}

# Create Redis replication group (cluster)
resource "aws_elasticache_replication_group" "justice_bid_cache_replication_group" {
  replication_group_id       = "${var.name_prefix}-redis-cluster"
  description                = "Redis cluster for Justice Bid caching"
  
  # Redis engine configuration
  engine                     = "redis"
  engine_version             = var.redis_version
  port                       = 6379
  node_type                  = var.cache_node_type
  parameter_group_name       = aws_elasticache_parameter_group.justice_bid_cache_parameter_group.name
  
  # Network configuration
  subnet_group_name          = aws_elasticache_subnet_group.justice_bid_cache_subnet_group.name
  security_group_ids         = [aws_security_group.justice_bid_cache_security_group.id]
  
  # High availability configuration
  automatic_failover_enabled = true
  multi_az_enabled           = var.environment == "production" ? true : false
  num_cache_clusters         = var.environment == "production" ? 3 : 2
  
  # Security configuration
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  kms_key_id                 = var.kms_key_id
  
  # Backup configuration
  snapshot_retention_limit   = var.environment == "production" ? 7 : 1
  snapshot_window            = "03:00-05:00"
  
  # Maintenance configuration
  maintenance_window         = "sat:05:00-sat:09:00"
  
  # For high throughput requirements in production
  dynamic "log_delivery_configuration" {
    for_each = var.environment == "production" ? [1] : []
    content {
      destination      = var.cloudwatch_log_group_name
      destination_type = "cloudwatch-logs"
      log_format       = "text"
      log_type         = "slow-log"
    }
  }
  
  # Apply auto minor version upgrades for security patches
  auto_minor_version_upgrade = true
  
  tags = merge(
    var.tags,
    {
      Name        = "${var.name_prefix}-redis-cluster"
      Environment = var.environment
    }
  )

  # Prevent replacement when changing certain parameters
  lifecycle {
    ignore_changes = [
      engine_version
    ]
  }
}