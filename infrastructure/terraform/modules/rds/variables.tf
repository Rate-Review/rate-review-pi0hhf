# Basic Configuration Variables
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
  description = "The version of the database engine"
  type        = string
  default     = "15.4"
}

variable "instance_class" {
  description = "The instance type of the RDS instance"
  type        = string
  default     = "db.t3.large"
}

# Storage Configuration Variables
variable "allocated_storage" {
  description = "The allocated storage in gigabytes"
  type        = number
  default     = 100
}

variable "max_allocated_storage" {
  description = "The upper limit to which Amazon RDS can automatically scale the storage of the DB instance"
  type        = number
  default     = 1000
}

variable "storage_type" {
  description = "One of 'standard' (magnetic), 'gp2' (general purpose SSD), 'gp3' (general purpose SSD), or 'io1' (provisioned IOPS SSD)"
  type        = string
  default     = "gp3"
}

variable "storage_encrypted" {
  description = "Specifies whether the DB instance is encrypted"
  type        = bool
  default     = true
}

variable "kms_key_id" {
  description = "The ARN for the KMS encryption key. If creating an encrypted replica, set this to the destination KMS ARN"
  type        = string
  default     = null
}

# Network Configuration Variables
variable "subnet_ids" {
  description = "A list of VPC subnet IDs"
  type        = list(string)
}

variable "vpc_security_group_ids" {
  description = "List of VPC security groups to associate"
  type        = list(string)
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

# Database Configuration Variables
variable "db_name" {
  description = "The name of the database to create when the DB instance is created"
  type        = string
  default     = "justicebid"
}

variable "username" {
  description = "Username for the master DB user"
  type        = string
  default     = "postgres"
}

variable "password" {
  description = "Password for the master DB user"
  type        = string
  sensitive   = true
}

variable "parameter_group_family" {
  description = "The family of the DB parameter group"
  type        = string
  default     = "postgres15"
}

variable "parameter_group_parameters" {
  description = "A list of DB parameter maps to apply"
  type        = list(map(string))
  default     = [
    {
      name  = "max_connections"
      value = "500"
    },
    {
      name  = "shared_buffers"
      value = "4GB"
    },
    {
      name  = "work_mem"
      value = "64MB"
    },
    {
      name  = "maintenance_work_mem"
      value = "512MB"
    },
    {
      name  = "effective_cache_size"
      value = "12GB"
    },
    {
      name  = "log_min_duration_statement"
      value = "1000"
    }
  ]
}

# Backup and Maintenance Variables
variable "backup_retention_period" {
  description = "The days to retain backups for"
  type        = number
  default     = 35
}

variable "backup_window" {
  description = "The daily time range during which automated backups are created if automated backups are enabled"
  type        = string
  default     = "03:00-06:00"
}

variable "maintenance_window" {
  description = "The window to perform maintenance in. Syntax: 'ddd:hh24:mi-ddd:hh24:mi'"
  type        = string
  default     = "sun:00:00-sun:03:00"
}

variable "deletion_protection" {
  description = "If the DB instance should have deletion protection enabled"
  type        = bool
  default     = true
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

# Monitoring and Logging Variables
variable "monitoring_interval" {
  description = "The interval, in seconds, between points when Enhanced Monitoring metrics are collected for the DB instance"
  type        = number
  default     = 30
}

variable "monitoring_role_arn" {
  description = "The ARN for the IAM role that permits RDS to send enhanced monitoring metrics to CloudWatch Logs"
  type        = string
  default     = null
}

variable "create_monitoring_role" {
  description = "Create IAM role with a defined name that permits RDS to send enhanced monitoring metrics to CloudWatch Logs"
  type        = bool
  default     = true
}

variable "enable_performance_insights" {
  description = "Specifies whether Performance Insights are enabled"
  type        = bool
  default     = true
}

variable "performance_insights_retention_period" {
  description = "The amount of time in days to retain Performance Insights data"
  type        = number
  default     = 7
}

variable "enabled_cloudwatch_logs_exports" {
  description = "List of log types to enable for exporting to CloudWatch logs. Valid values (depending on engine): alert, audit, error, general, listener, slowquery, trace, postgresql, upgrade"
  type        = list(string)
  default     = ["postgresql", "upgrade"]
}

# Read Replica Variables
variable "replica_count" {
  description = "Number of read replicas to create"
  type        = number
  default     = 1
}

variable "replica_instance_class" {
  description = "Instance type to use for read replicas"
  type        = string
  default     = "db.t3.large"
}

# Tagging Variables
variable "tags" {
  description = "A mapping of tags to assign to all resources"
  type        = map(string)
  default     = {
    Environment = "production"
    Project     = "JusticeBid"
    Terraform   = "true"
  }
}