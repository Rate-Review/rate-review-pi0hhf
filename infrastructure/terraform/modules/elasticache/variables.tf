variable "cluster_id" {
  description = "The identifier for the ElastiCache cluster. Must be unique within the AWS account."
  type        = string
}

variable "node_type" {
  description = "The compute and memory capacity of the nodes. See https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/CacheNodes.SupportedTypes.html"
  type        = string
  default     = "cache.t3.medium"
}

variable "engine" {
  description = "The name of the cache engine to be used for the cluster. Currently only 'redis' is supported for Justice Bid."
  type        = string
  default     = "redis"
  validation {
    condition     = contains(["redis", "memcached"], var.engine)
    error_message = "The engine value must be either 'redis' or 'memcached'."
  }
}

variable "engine_version" {
  description = "The version number of the cache engine to be used for the cluster."
  type        = string
  default     = "7.0"
}

variable "vpc_id" {
  description = "The ID of the VPC where the ElastiCache cluster will be deployed."
  type        = string
}

variable "subnet_ids" {
  description = "A list of VPC subnet IDs for the ElastiCache subnet group."
  type        = list(string)
}

variable "num_node_groups" {
  description = "The number of node groups (shards) for this Redis replication group. Changing this number will trigger a recreation of the resource."
  type        = number
  default     = 1
  validation {
    condition     = var.num_node_groups > 0
    error_message = "The number of node groups must be greater than 0."
  }
}

variable "replicas_per_node_group" {
  description = "The number of replica nodes in each node group. Valid values are 0 to 5."
  type        = number
  default     = 1
  validation {
    condition     = var.replicas_per_node_group >= 0 && var.replicas_per_node_group <= 5
    error_message = "The number of replicas per node group must be between 0 and 5."
  }
}

variable "multi_az_enabled" {
  description = "Specifies whether Multi-AZ is enabled. When Multi-AZ is enabled, a read-only replica is created in a different AZ."
  type        = bool
  default     = true
}

variable "automatic_failover_enabled" {
  description = "Specifies whether a read-only replica will be automatically promoted to read/write primary if the existing primary fails."
  type        = bool
  default     = true
}

variable "at_rest_encryption_enabled" {
  description = "Whether to enable encryption at rest. Required for Justice Bid's security compliance."
  type        = bool
  default     = true
}

variable "transit_encryption_enabled" {
  description = "Whether to enable encryption in transit. Required for Justice Bid's security compliance."
  type        = bool
  default     = true
}

variable "auth_token" {
  description = "The password used to access a password protected server. Can be specified only if transit_encryption_enabled is true."
  type        = string
  default     = null
  sensitive   = true
}

variable "default_ttl" {
  description = "The default TTL (Time To Live) for cache keys in seconds. Default is 10 minutes."
  type        = number
  default     = 600
}

variable "maxmemory_policy" {
  description = "The eviction policy when maxmemory is reached. Available policies: volatile-lru, allkeys-lru, volatile-random, allkeys-random, volatile-ttl, noeviction."
  type        = string
  default     = "volatile-lru"
  validation {
    condition     = contains(["volatile-lru", "allkeys-lru", "volatile-random", "allkeys-random", "volatile-ttl", "noeviction"], var.maxmemory_policy)
    error_message = "The maxmemory policy must be one of: volatile-lru, allkeys-lru, volatile-random, allkeys-random, volatile-ttl, noeviction."
  }
}

variable "create_cloudwatch_alarms" {
  description = "Whether to create CloudWatch alarms for the ElastiCache cluster."
  type        = bool
  default     = true
}

variable "cpu_threshold_alarm" {
  description = "The CPU utilization threshold percentage for triggering CloudWatch alarms."
  type        = number
  default     = 75
  validation {
    condition     = var.cpu_threshold_alarm > 0 && var.cpu_threshold_alarm <= 100
    error_message = "The CPU threshold must be between 1 and 100 percent."
  }
}

variable "memory_threshold_alarm" {
  description = "The memory utilization threshold percentage for triggering CloudWatch alarms."
  type        = number
  default     = 75
  validation {
    condition     = var.memory_threshold_alarm > 0 && var.memory_threshold_alarm <= 100
    error_message = "The memory threshold must be between 1 and 100 percent."
  }
}

variable "snapshot_retention_limit" {
  description = "The number of days for which ElastiCache will retain automatic snapshots before deleting them."
  type        = number
  default     = 7
  validation {
    condition     = var.snapshot_retention_limit >= 0 && var.snapshot_retention_limit <= 35
    error_message = "The snapshot retention limit must be between 0 and 35 days."
  }
}

variable "maintenance_window" {
  description = "The weekly time range during which system maintenance can occur. Format: ddd:hh24:mi-ddd:hh24:mi (24H Clock UTC)."
  type        = string
  default     = "sun:05:00-sun:07:00"
}

variable "parameter_group_name" {
  description = "The name of the parameter group to associate with this cluster. If not provided, a default parameter group will be used."
  type        = string
  default     = null
}

variable "security_group_ids" {
  description = "One or more VPC security groups to associate with the cluster."
  type        = list(string)
  default     = []
}

variable "tags" {
  description = "A map of tags to assign to the ElastiCache resources."
  type        = map(string)
  default     = {}
}