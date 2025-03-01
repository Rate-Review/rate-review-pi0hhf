terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~> 3.0"
    }
  }
}

locals {
  cluster_name = var.cluster_name != "" ? var.cluster_name : "${var.project_name}-${var.environment}-eks"
  
  common_tags = merge(
    var.tags,
    {
      "Project"     = var.project_name
      "Environment" = var.environment
      "ManagedBy"   = "Terraform"
      "Component"   = "EKS"
    }
  )
}

# IAM role for the EKS cluster
resource "aws_iam_role" "cluster_role" {
  name = "${local.cluster_name}-cluster-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "eks.amazonaws.com"
        }
      }
    ]
  })
  
  tags = merge(
    local.common_tags,
    {
      "Name" = "${local.cluster_name}-cluster-role"
    }
  )
}

# Attach the required policies to the cluster role
resource "aws_iam_role_policy_attachment" "cluster_policies" {
  for_each = toset([
    "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy",
    "arn:aws:iam::aws:policy/AmazonEKSVPCResourceController"
  ])
  
  policy_arn = each.value
  role       = aws_iam_role.cluster_role.name
}

# IAM role for the EKS node groups
resource "aws_iam_role" "node_role" {
  name = "${local.cluster_name}-node-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
  
  tags = merge(
    local.common_tags,
    {
      "Name" = "${local.cluster_name}-node-role"
    }
  )
}

# Attach the required policies to the node role
resource "aws_iam_role_policy_attachment" "node_policies" {
  for_each = toset([
    "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy",
    "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy",
    "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  ])
  
  policy_arn = each.value
  role       = aws_iam_role.node_role.name
}

# Security group for the EKS cluster
resource "aws_security_group" "cluster_sg" {
  name        = "${local.cluster_name}-cluster-sg"
  description = "Security group for ${local.cluster_name} EKS cluster"
  vpc_id      = var.vpc_id
  
  tags = merge(
    local.common_tags,
    {
      "Name" = "${local.cluster_name}-cluster-sg"
    }
  )
}

# Security group rules for the EKS cluster
resource "aws_security_group_rule" "cluster_rules" {
  for_each = {
    # API server ingress rule
    api_ingress = {
      type        = "ingress"
      from_port   = 443
      to_port     = 443
      protocol    = "tcp"
      cidr_blocks = [var.vpc_cidr]
      description = "Allow HTTPS access to the Kubernetes API server"
    },
    # Egress rule for all traffic
    all_egress = {
      type        = "egress"
      from_port   = 0
      to_port     = 0
      protocol    = "-1"
      cidr_blocks = ["0.0.0.0/0"]
      description = "Allow all outbound traffic"
    }
  }
  
  security_group_id = aws_security_group.cluster_sg.id
  type              = each.value.type
  from_port         = each.value.from_port
  to_port           = each.value.to_port
  protocol          = each.value.protocol
  cidr_blocks       = each.value.cidr_blocks
  description       = each.value.description
}

# EKS Cluster
resource "aws_eks_cluster" "this" {
  name     = local.cluster_name
  role_arn = aws_iam_role.cluster_role.arn
  version  = var.kubernetes_version
  
  vpc_config {
    subnet_ids              = var.subnet_ids
    security_group_ids      = [aws_security_group.cluster_sg.id]
    endpoint_private_access = var.endpoint_private_access
    endpoint_public_access  = var.endpoint_public_access
  }
  
  enabled_cluster_log_types = [
    "api",
    "audit",
    "authenticator",
    "controllerManager",
    "scheduler"
  ]
  
  tags = merge(
    local.common_tags,
    {
      "Name" = local.cluster_name
    }
  )
  
  depends_on = [
    aws_iam_role_policy_attachment.cluster_policies
  ]
}

# EKS Node Groups
resource "aws_eks_node_group" "this" {
  for_each = var.node_groups

  cluster_name    = aws_eks_cluster.this.name
  node_group_name = each.key
  node_role_arn   = aws_iam_role.node_role.arn
  subnet_ids      = var.subnet_ids
  
  scaling_config {
    desired_size = each.value.desired_size
    min_size     = each.value.min_size
    max_size     = each.value.max_size
  }
  
  instance_types = each.value.instance_types
  capacity_type  = each.value.capacity_type
  disk_size      = each.value.disk_size
  
  labels = each.value.labels
  
  tags = merge(
    local.common_tags,
    {
      "Name" = "${local.cluster_name}-${each.key}"
    },
    each.value.tags
  )
  
  depends_on = [
    aws_iam_role_policy_attachment.node_policies
  ]
}

# Generate kubeconfig for the cluster
locals {
  kubeconfig = <<-EOT
    apiVersion: v1
    kind: Config
    current-context: ${aws_eks_cluster.this.name}
    clusters:
    - name: ${aws_eks_cluster.this.name}
      cluster:
        certificate-authority-data: ${aws_eks_cluster.this.certificate_authority[0].data}
        server: ${aws_eks_cluster.this.endpoint}
    contexts:
    - name: ${aws_eks_cluster.this.name}
      context:
        cluster: ${aws_eks_cluster.this.name}
        user: ${aws_eks_cluster.this.name}
    users:
    - name: ${aws_eks_cluster.this.name}
      user:
        exec:
          apiVersion: client.authentication.k8s.io/v1alpha1
          command: aws
          args:
            - "eks"
            - "get-token"
            - "--cluster-name"
            - "${aws_eks_cluster.this.name}"
  EOT
}

# Variables
variable "project_name" {
  description = "The name of the project"
  type        = string
}

variable "environment" {
  description = "The environment (dev, test, prod, etc.)"
  type        = string
}

variable "cluster_name" {
  description = "Name of the EKS cluster"
  type        = string
  default     = ""
}

variable "kubernetes_version" {
  description = "Kubernetes version to use for the EKS cluster"
  type        = string
  default     = "1.25"
}

variable "vpc_id" {
  description = "ID of the VPC where the EKS cluster will be created"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block of the VPC"
  type        = string
}

variable "subnet_ids" {
  description = "A list of subnet IDs where the EKS cluster (ENIs) will be provisioned along with the nodes/node groups"
  type        = list(string)
}

variable "endpoint_public_access" {
  description = "Indicates whether or not the Amazon EKS public API server endpoint is enabled"
  type        = bool
  default     = true
}

variable "endpoint_private_access" {
  description = "Indicates whether or not the Amazon EKS private API server endpoint is enabled"
  type        = bool
  default     = true
}

variable "node_groups" {
  description = "Map of EKS node group definitions to create"
  type = map(object({
    desired_size   = number
    min_size       = number
    max_size       = number
    instance_types = list(string)
    capacity_type  = string
    disk_size      = number
    labels         = map(string)
    tags           = map(string)
  }))
  default = {}
}

variable "tags" {
  description = "A map of tags to add to all resources"
  type        = map(string)
  default     = {}
}

# Outputs
output "cluster_id" {
  description = "ID of the provisioned EKS cluster"
  value       = aws_eks_cluster.this.id
}

output "cluster_name" {
  description = "Name of the provisioned EKS cluster"
  value       = aws_eks_cluster.this.name
}

output "cluster_endpoint" {
  description = "Endpoint URL for the Kubernetes API server"
  value       = aws_eks_cluster.this.endpoint
}

output "cluster_certificate_authority_data" {
  description = "Certificate authority data for the cluster"
  value       = aws_eks_cluster.this.certificate_authority[0].data
}

output "node_group_role_arn" {
  description = "ARN of the IAM role used by node groups"
  value       = aws_iam_role.node_role.arn
}

output "cluster_security_group_id" {
  description = "ID of the security group for the EKS cluster"
  value       = aws_security_group.cluster_sg.id
}

output "kubeconfig" {
  description = "Generated kubeconfig for accessing the cluster"
  value       = local.kubeconfig
  sensitive   = true
}