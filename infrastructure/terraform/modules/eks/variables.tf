variable "cluster_name" {
  type        = string
  description = "Name of the EKS cluster for the Justice Bid system"
}

variable "cluster_version" {
  type        = string
  default     = "1.24"
  description = "Kubernetes version to use for the EKS cluster"
}

variable "environment" {
  type        = string
  description = "Environment name (e.g., production, staging, development)"
}

variable "region" {
  type        = string
  description = "AWS region to deploy the EKS cluster"
}

variable "vpc_id" {
  type        = string
  description = "ID of the VPC where the EKS cluster will be deployed"
}

variable "subnet_ids" {
  type        = list(string)
  description = "List of subnet IDs where the EKS nodes will be deployed"
}

variable "create_eks" {
  type        = bool
  default     = true
  description = "Controls if EKS resources should be created"
}

variable "cluster_endpoint_private_access" {
  type        = bool
  default     = true
  description = "Indicates whether or not the EKS private API server endpoint is enabled"
}

variable "cluster_endpoint_public_access" {
  type        = bool
  default     = true
  description = "Indicates whether or not the EKS public API server endpoint is enabled"
}

variable "cluster_endpoint_public_access_cidrs" {
  type        = list(string)
  default     = ["0.0.0.0/0"]
  description = "List of CIDR blocks which can access the Amazon EKS public API server endpoint"
}

variable "cluster_log_types" {
  type        = list(string)
  default     = ["api", "audit", "authenticator", "controllerManager", "scheduler"]
  description = "List of the desired control plane logging to enable"
}

variable "cluster_log_retention_in_days" {
  type        = number
  default     = 90
  description = "Number of days to retain cluster logs"
}

variable "cluster_security_group_id" {
  type        = string
  default     = ""
  description = "Security group ID attached to the EKS cluster"
}

variable "worker_security_group_id" {
  type        = string
  default     = ""
  description = "Security group ID attached to the EKS workers"
}

variable "cluster_create_timeout" {
  type        = string
  default     = "30m"
  description = "Timeout value when creating the EKS cluster"
}

variable "cluster_delete_timeout" {
  type        = string
  default     = "15m"
  description = "Timeout value when deleting the EKS cluster"
}

variable "node_groups" {
  type = map(any)
  default = {
    default = {
      desired_capacity = 2
      max_capacity     = 10
      min_capacity     = 2
      instance_types   = ["m5.large"]
    }
  }
  description = "Map of EKS node group configurations for the Justice Bid services"
}

variable "node_groups_defaults" {
  type = map(any)
  default = {
    ami_type  = "AL2_x86_64"
    disk_size = 50
  }
  description = "Default configurations for all node groups"
}

variable "map_roles" {
  type = list(object({
    rolearn  = string
    username = string
    groups   = list(string)
  }))
  default     = []
  description = "Additional IAM roles to add to the aws-auth configmap"
}

variable "map_users" {
  type = list(object({
    userarn  = string
    username = string
    groups   = list(string)
  }))
  default     = []
  description = "Additional IAM users to add to the aws-auth configmap"
}

variable "workers_additional_policies" {
  type        = list(string)
  default     = []
  description = "Additional IAM policy ARNs to attach to the worker nodes"
}

variable "enable_irsa" {
  type        = bool
  default     = true
  description = "Enable IAM Roles for Service Accounts for the EKS cluster"
}

variable "fargate_profiles" {
  type        = any
  default     = {}
  description = "Fargate profiles to create for the EKS cluster"
}

variable "enable_monitoring" {
  type        = bool
  default     = true
  description = "Enable detailed monitoring for worker nodes"
}

variable "cloudwatch_log_group_retention_in_days" {
  type        = number
  default     = 90
  description = "Number of days to retain CloudWatch logs"
}

variable "create_cloudwatch_log_group" {
  type        = bool
  default     = true
  description = "Determines whether a CloudWatch log group is created for each enabled log type"
}

variable "cluster_encryption_config" {
  type = list(object({
    provider_key_arn = string
    resources        = list(string)
  }))
  default     = []
  description = "Configuration for cluster encryption"
}

variable "frontend_node_group" {
  type = map(any)
  default = {
    desired_capacity = 2
    max_capacity     = 6
    min_capacity     = 2
    instance_types   = ["m5.large"]
  }
  description = "Node group configuration for frontend services"
}

variable "backend_node_group" {
  type = map(any)
  default = {
    desired_capacity = 2
    max_capacity     = 8
    min_capacity     = 2
    instance_types   = ["m5.xlarge"]
  }
  description = "Node group configuration for backend services"
}

variable "analytics_node_group" {
  type = map(any)
  default = {
    desired_capacity = 2
    max_capacity     = 6
    min_capacity     = 2
    instance_types   = ["m5.2xlarge"]
  }
  description = "Node group configuration for analytics services which require more CPU and memory"
}

variable "ai_node_group" {
  type = map(any)
  default = {
    desired_capacity = 2
    max_capacity     = 4
    min_capacity     = 2
    instance_types   = ["g4dn.xlarge"]
  }
  description = "Node group configuration for AI services which may require GPU support"
}

variable "kubernetes_labels" {
  type        = map(string)
  default     = {}
  description = "Additional Kubernetes labels to apply to the EKS cluster resources"
}

variable "auto_scaling_group_tags" {
  type        = map(string)
  default     = {}
  description = "Additional tags for the auto scaling groups"
}

variable "tags" {
  type        = map(string)
  default     = {}
  description = "A map of tags to add to all resources"
}