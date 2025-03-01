# Basic configuration variables
variable "name_prefix" {
  description = "Prefix to be used for naming resources"
  type        = string
  default     = "justicebid"
}

variable "environment" {
  description = "Environment name (dev, staging, etc.)"
  type        = string
}

# Network configuration variables
variable "vpc_id" {
  description = "ID of the VPC where ECS resources will be deployed"
  type        = string
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs where ECS tasks will be deployed"
  type        = list(string)
}

variable "public_subnet_ids" {
  description = "List of public subnet IDs for load balancers"
  type        = list(string)
}

# Cluster configuration variables
variable "cluster_name" {
  description = "Name of the ECS cluster"
  type        = string
}

variable "capacity_providers" {
  description = "List of capacity providers to use for the cluster"
  type        = list(string)
  default     = ["FARGATE", "FARGATE_SPOT"]
}

variable "default_capacity_provider_strategy" {
  description = "Default capacity provider strategy for the cluster"
  type = list(object({
    capacity_provider = string
    weight            = number
    base              = number
  }))
  default = [
    {
      capacity_provider = "FARGATE"
      weight            = 1
      base              = 1
    },
    {
      capacity_provider = "FARGATE_SPOT"
      weight            = 4
      base              = 0
    }
  ]
}

variable "container_insights" {
  description = "Whether to enable CloudWatch Container Insights"
  type        = bool
  default     = true
}

# Service configuration variables
variable "services" {
  description = "Map of services to be deployed on the ECS cluster"
  type = map(object({
    name                 = string
    container_port       = number
    host_port            = number
    protocol             = string
    cpu                  = number
    memory               = number
    desired_count        = number
    min_capacity         = number
    max_capacity         = number
    container_definitions = string
    load_balancer = object({
      target_group_arn = string
      container_name   = string
      container_port   = number
    })
    health_check = object({
      path                = string
      interval            = number
      timeout             = number
      healthy_threshold   = number
      unhealthy_threshold = number
      matcher             = string
    })
    volume = list(object({
      name      = string
      host_path = string
      efs_volume_configuration = list(object({
        file_system_id          = string
        root_directory          = string
        transit_encryption      = string
        transit_encryption_port = number
        authorization_config = list(object({
          access_point_id = string
          iam             = string
        }))
      }))
    }))
  }))
  default = {}
}

# IAM role variables
variable "task_execution_role_arn" {
  description = "ARN of the IAM role for ECS task execution"
  type        = string
}

variable "task_role_arn" {
  description = "ARN of the IAM role for ECS tasks"
  type        = string
}

# Deployment configuration variables
variable "health_check_grace_period_seconds" {
  description = "Grace period for health checks on service startup"
  type        = number
  default     = 60
}

variable "deployment_maximum_percent" {
  description = "Maximum percentage of tasks that can be running during a deployment"
  type        = number
  default     = 200
}

variable "deployment_minimum_healthy_percent" {
  description = "Minimum percentage of tasks that must remain healthy during a deployment"
  type        = number
  default     = 100
}

# Autoscaling configuration variables
variable "enable_autoscaling" {
  description = "Whether to enable autoscaling for ECS services"
  type        = bool
  default     = true
}

variable "autoscaling_target_cpu_utilization" {
  description = "Target CPU utilization percentage for autoscaling"
  type        = number
  default     = 70
}

variable "autoscaling_target_memory_utilization" {
  description = "Target memory utilization percentage for autoscaling"
  type        = number
  default     = 70
}

variable "autoscaling_cooldown" {
  description = "Cooldown period in seconds after a scaling activity"
  type        = number
  default     = 300
}

# Load balancer configuration variables
variable "load_balancer_security_groups" {
  description = "List of security group IDs for the load balancer"
  type        = list(string)
}

variable "load_balancer_type" {
  description = "Type of load balancer to create (application, network, or gateway)"
  type        = string
  default     = "application"
}

# Tagging variables
variable "tags" {
  description = "Map of tags to apply to all resources"
  type        = map(string)
  default     = {}
}