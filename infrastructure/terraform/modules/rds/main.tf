# Terraform module for RDS PostgreSQL instances
# Supports multi-AZ, read replicas, encryption, and enhanced monitoring

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

# Local variables for internal calculations
locals {
  is_postgres = var.engine == "postgres"
  final_snapshot_id = var.final_snapshot_identifier == null ? "${var.identifier}-final-snapshot-${formatdate("YYYYMMDDhhmmss", timestamp())}" : var.final_snapshot_identifier
}

# Create DB Parameter Group
resource "aws_db_parameter_group" "this" {
  name        = "${var.identifier}-pg"
  family      = var.parameter_group_family
  description = "Parameter group for ${var.identifier} RDS instance"

  dynamic "parameter" {
    for_each = var.parameter_group_parameters
    content {
      name         = parameter.value.name
      value        = parameter.value.value
      apply_method = lookup(parameter.value, "apply_method", "immediate")
    }
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.identifier}-parameter-group"
    }
  )
}

# Create DB Subnet Group
resource "aws_db_subnet_group" "this" {
  count       = var.create_subnet_group ? 1 : 0
  name        = "${var.identifier}-subnet-group"
  subnet_ids  = var.subnet_ids
  description = "Subnet group for ${var.identifier} RDS instance"

  tags = merge(
    var.tags,
    {
      Name = "${var.identifier}-subnet-group"
    }
  )
}

# Create Primary RDS Instance
resource "aws_db_instance" "this" {
  identifier                  = var.identifier
  engine                      = var.engine
  engine_version              = var.engine_version
  instance_class              = var.instance_class
  allocated_storage           = var.allocated_storage
  max_allocated_storage       = var.max_allocated_storage
  storage_type                = var.storage_type
  storage_encrypted           = var.storage_encrypted
  kms_key_id                  = var.kms_key_id
  db_name                     = var.db_name
  username                    = var.username
  password                    = var.password
  port                        = var.port
  multi_az                    = var.multi_az
  maintenance_window          = var.maintenance_window
  backup_window               = var.backup_window
  backup_retention_period     = var.backup_retention_period
  deletion_protection         = var.deletion_protection
  skip_final_snapshot         = var.skip_final_snapshot
  final_snapshot_identifier   = local.final_snapshot_id
  vpc_security_group_ids      = var.vpc_security_group_ids
  db_subnet_group_name        = var.create_subnet_group ? aws_db_subnet_group.this[0].name : var.db_subnet_group_name
  parameter_group_name        = aws_db_parameter_group.this.name
  option_group_name           = var.option_group_name
  apply_immediately           = var.apply_immediately
  copy_tags_to_snapshot       = var.copy_tags_to_snapshot
  auto_minor_version_upgrade  = var.auto_minor_version_upgrade
  allow_major_version_upgrade = var.allow_major_version_upgrade
  performance_insights_enabled = var.performance_insights_enabled
  performance_insights_retention_period = var.performance_insights_enabled ? var.performance_insights_retention_period : null
  performance_insights_kms_key_id       = var.performance_insights_enabled ? var.performance_insights_kms_key_id : null
  monitoring_interval                   = var.monitoring_interval
  monitoring_role_arn                   = var.monitoring_interval > 0 ? var.monitoring_role_arn : null
  enabled_cloudwatch_logs_exports       = var.enabled_cloudwatch_logs_exports
  
  lifecycle {
    ignore_changes = [
      password
    ]
  }

  tags = merge(
    var.tags,
    {
      Name = var.identifier
    }
  )
}

# Create Read Replicas
resource "aws_db_instance" "replica" {
  count                   = var.replica_count
  identifier              = "${var.identifier}-replica-${count.index + 1}"
  replicate_source_db     = aws_db_instance.this.id
  instance_class          = var.replica_instance_class != null ? var.replica_instance_class : var.instance_class
  vpc_security_group_ids  = var.vpc_security_group_ids
  parameter_group_name    = aws_db_parameter_group.this.name
  maintenance_window      = var.maintenance_window
  backup_retention_period = 0  # Automated backups are disabled for read replicas
  skip_final_snapshot     = true
  apply_immediately       = var.apply_immediately
  auto_minor_version_upgrade  = var.auto_minor_version_upgrade
  performance_insights_enabled = var.performance_insights_enabled
  performance_insights_retention_period = var.performance_insights_enabled ? var.performance_insights_retention_period : null
  performance_insights_kms_key_id       = var.performance_insights_enabled ? var.performance_insights_kms_key_id : null
  monitoring_interval                   = var.monitoring_interval
  monitoring_role_arn                   = var.monitoring_interval > 0 ? var.monitoring_role_arn : null
  
  tags = merge(
    var.tags,
    {
      Name = "${var.identifier}-replica-${count.index + 1}"
    }
  )
}

# Output values
output "db_instance_endpoint" {
  description = "The connection endpoint for the primary RDS instance"
  value       = aws_db_instance.this.endpoint
}

output "db_instance_id" {
  description = "The ID of the primary RDS instance"
  value       = aws_db_instance.this.id
}

output "db_instance_arn" {
  description = "The ARN of the primary RDS instance"
  value       = aws_db_instance.this.arn
}

output "db_instance_status" {
  description = "The current status of the primary RDS instance"
  value       = aws_db_instance.this.status
}

output "db_parameter_group_id" {
  description = "The ID of the database parameter group"
  value       = aws_db_parameter_group.this.id
}

output "db_replica_endpoints" {
  description = "The connection endpoints for the read replicas"
  value       = aws_db_instance.replica[*].endpoint
}

# Variables
variable "identifier" {
  description = "The identifier for the RDS instance"
  type        = string
}

variable "engine" {
  description = "The database engine to use"
  type        = string
  default     = "postgres"
}

variable "engine_version" {
  description = "The version of the database engine to use"
  type        = string
}

variable "instance_class" {
  description = "The instance class to use for the RDS instance"
  type        = string
}

variable "allocated_storage" {
  description = "The amount of allocated storage in GiB"
  type        = number
}

variable "max_allocated_storage" {
  description = "The upper limit to which Amazon RDS can automatically scale the storage of the DB instance"
  type        = number
  default     = 0
}

variable "storage_type" {
  description = "The type of storage to use (io1, gp2, standard)"
  type        = string
  default     = "gp2"
}

variable "storage_encrypted" {
  description = "Specifies whether the DB instance is encrypted"
  type        = bool
  default     = true
}

variable "kms_key_id" {
  description = "The ARN for the KMS encryption key"
  type        = string
  default     = null
}

variable "db_name" {
  description = "The name of the database to create when the DB instance is created"
  type        = string
  default     = null
}

variable "username" {
  description = "Username for the master DB user"
  type        = string
}

variable "password" {
  description = "Password for the master DB user"
  type        = string
  sensitive   = true
}

variable "port" {
  description = "The port on which the DB accepts connections"
  type        = number
  default     = 5432
}

variable "multi_az" {
  description = "Specifies if the RDS instance is multi-AZ"
  type        = bool
  default     = true
}

variable "deletion_protection" {
  description = "If the DB instance should have deletion protection enabled"
  type        = bool
  default     = true
}

variable "backup_retention_period" {
  description = "The backup retention period in days"
  type        = number
  default     = 30
}

variable "backup_window" {
  description = "The daily time range during which automated backups are created"
  type        = string
  default     = "03:00-06:00"  # UTC
}

variable "maintenance_window" {
  description = "The window to perform maintenance in"
  type        = string
  default     = "Sun:00:00-Sun:03:00"  # UTC
}

variable "skip_final_snapshot" {
  description = "Determines whether a final DB snapshot is created before the DB instance is deleted"
  type        = bool
  default     = false
}

variable "final_snapshot_identifier" {
  description = "The name of your final DB snapshot when this DB instance is deleted"
  type        = string
  default     = null
}

variable "copy_tags_to_snapshot" {
  description = "Copy all tags from DB instance to snapshots"
  type        = bool
  default     = true
}

variable "vpc_security_group_ids" {
  description = "List of VPC security groups to associate"
  type        = list(string)
}

variable "create_subnet_group" {
  description = "Whether to create a subnet group for the RDS instance"
  type        = bool
  default     = true
}

variable "subnet_ids" {
  description = "A list of VPC subnet IDs to use in the subnet group"
  type        = list(string)
  default     = []
}

variable "db_subnet_group_name" {
  description = "Name of DB subnet group to use if not creating one"
  type        = string
  default     = null
}

variable "parameter_group_family" {
  description = "The family of the DB parameter group"
  type        = string
}

variable "parameter_group_parameters" {
  description = "A list of DB parameters to apply"
  type        = list(map(string))
  default     = []
}

variable "option_group_name" {
  description = "Name of the DB option group to associate"
  type        = string
  default     = null
}

variable "performance_insights_enabled" {
  description = "Specifies whether Performance Insights are enabled"
  type        = bool
  default     = true
}

variable "performance_insights_retention_period" {
  description = "The amount of time in days to retain Performance Insights data"
  type        = number
  default     = 7
}

variable "performance_insights_kms_key_id" {
  description = "The ARN for the KMS key to encrypt Performance Insights data"
  type        = string
  default     = null
}

variable "monitoring_interval" {
  description = "The interval, in seconds, between points when Enhanced Monitoring metrics are collected"
  type        = number
  default     = 60
}

variable "monitoring_role_arn" {
  description = "The ARN for the IAM role that permits RDS to send enhanced monitoring metrics to CloudWatch"
  type        = string
  default     = null
}

variable "enabled_cloudwatch_logs_exports" {
  description = "List of log types to enable for exporting to CloudWatch logs"
  type        = list(string)
  default     = ["postgresql", "upgrade"]
}

variable "apply_immediately" {
  description = "Specifies whether any modifications are applied immediately, or during maintenance window"
  type        = bool
  default     = false
}

variable "auto_minor_version_upgrade" {
  description = "Indicates that minor engine upgrades will be applied automatically during maintenance window"
  type        = bool
  default     = true
}

variable "allow_major_version_upgrade" {
  description = "Indicates that major version upgrades are allowed"
  type        = bool
  default     = false
}

variable "replica_count" {
  description = "Number of read replicas to create"
  type        = number
  default     = 0
}

variable "replica_instance_class" {
  description = "The instance type of the read replica (defaults to same as primary if not specified)"
  type        = string
  default     = null
}

variable "tags" {
  description = "A mapping of tags to assign to the resource"
  type        = map(string)
  default     = {}
}