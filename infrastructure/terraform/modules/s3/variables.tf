variable "bucket_name_prefix" {
  description = "Prefix for the S3 bucket names to ensure uniqueness"
  type        = string
  default     = "justicebid"
}

variable "environment" {
  description = "Deployment environment (dev, staging, production)"
  type        = string
  default     = "dev"
}

variable "bucket_purposes" {
  description = "List of bucket purposes to create (documents, assets, backups, exports)"
  type        = list(string)
  default     = ["documents", "assets", "backups", "exports"]
}

variable "versioning_enabled" {
  description = "Whether to enable versioning for S3 buckets"
  type        = bool
  default     = true
}

variable "encryption_enabled" {
  description = "Whether to enable server-side encryption for S3 buckets"
  type        = bool
  default     = true
}

variable "encryption_kms_key_arn" {
  description = "ARN of the KMS key to use for encryption (if not provided, AWS managed keys will be used)"
  type        = string
  default     = null
}

variable "replication_enabled" {
  description = "Whether to enable cross-region replication for S3 buckets"
  type        = bool
  default     = false
}

variable "replication_region" {
  description = "AWS region for cross-region replication destination"
  type        = string
  default     = "us-west-2"
}

variable "lifecycle_rules" {
  description = "S3 lifecycle rules for automatic transitions and expirations"
  type = list(object({
    id                          = string
    enabled                     = bool
    prefix                      = string
    expiration_days             = optional(number)
    noncurrent_version_expiration_days = optional(number)
    transitions = optional(list(object({
      days          = number
      storage_class = string
    })))
    noncurrent_version_transitions = optional(list(object({
      days          = number
      storage_class = string
    })))
  }))
  default = []
}

variable "static_website_enabled" {
  description = "Whether to enable static website hosting for asset buckets"
  type        = bool
  default     = false
}

variable "static_website_index_document" {
  description = "Index document for static website hosting"
  type        = string
  default     = "index.html"
}

variable "static_website_error_document" {
  description = "Error document for static website hosting"
  type        = string
  default     = "error.html"
}

variable "cors_enabled" {
  description = "Whether to enable CORS for S3 buckets"
  type        = bool
  default     = false
}

variable "cors_rules" {
  description = "CORS rules for S3 buckets"
  type = list(object({
    allowed_headers = list(string)
    allowed_methods = list(string)
    allowed_origins = list(string)
    expose_headers  = optional(list(string))
    max_age_seconds = optional(number)
  }))
  default = []
}

variable "bucket_acl" {
  description = "ACL for S3 buckets (private, public-read, etc.)"
  type        = string
  default     = "private"
}

variable "logging_enabled" {
  description = "Whether to enable access logging for S3 buckets"
  type        = bool
  default     = true
}

variable "logging_target_bucket" {
  description = "Target bucket for access logs"
  type        = string
  default     = null
}

variable "logging_target_prefix" {
  description = "Prefix for access logs"
  type        = string
  default     = "logs/"
}

variable "access_logs_retention_days" {
  description = "Number of days to retain access logs"
  type        = number
  default     = 90
}

variable "block_public_access" {
  description = "Whether to enable S3 Block Public Access"
  type        = bool
  default     = true
}

variable "force_destroy" {
  description = "Whether to force destroy buckets even if they contain objects"
  type        = bool
  default     = false
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default     = {}
}