# ---------------------------------------------------------------------------------------------------------------------
# ECS MODULE for JUSTICE BID RATE NEGOTIATION SYSTEM
# Creates ECS cluster, services, task definitions, load balancers, and auto-scaling configuration
# ---------------------------------------------------------------------------------------------------------------------

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

# ---------------------------------------------------------------------------------------------------------------------
# ECS CLUSTER
# ---------------------------------------------------------------------------------------------------------------------

resource "aws_ecs_cluster" "justice_bid" {
  name = var.cluster_name

  setting {
    name  = "containerInsights"
    value = var.enable_container_insights ? "enabled" : "disabled"
  }

  tags = {
    Name        = var.cluster_name
    Environment = var.environment
    Project     = "JusticeBid"
    ManagedBy   = "Terraform"
  }
}

# ---------------------------------------------------------------------------------------------------------------------
# IAM ROLES
# ---------------------------------------------------------------------------------------------------------------------

# ECS Task Execution Role - Allows the ECS agent to perform actions on your behalf
resource "aws_iam_role" "ecs_task_execution_role" {
  name = var.task_execution_role_name

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    Name        = var.task_execution_role_name
    Environment = var.environment
    Project     = "JusticeBid"
    ManagedBy   = "Terraform"
  }
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# ECS Task Role - Permissions that containers in the task have
resource "aws_iam_role" "ecs_task_role" {
  name = var.task_role_name

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    Name        = var.task_role_name
    Environment = var.environment
    Project     = "JusticeBid"
    ManagedBy   = "Terraform"
  }
}

# Policy to allow additional permissions for the task role
resource "aws_iam_policy" "ecs_task_policy" {
  name = "${var.task_role_name}-policy"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_policy_attachment" {
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = aws_iam_policy.ecs_task_policy.arn
}

# ---------------------------------------------------------------------------------------------------------------------
# SECURITY GROUPS
# ---------------------------------------------------------------------------------------------------------------------

resource "aws_security_group" "ecs_tasks" {
  name        = var.security_group_name
  description = "Allow inbound traffic to ECS services"
  vpc_id      = var.vpc_id

  ingress {
    protocol        = "tcp"
    from_port       = 80
    to_port         = 80
    cidr_blocks     = ["0.0.0.0/0"]
    description     = "Allow HTTP inbound traffic"
  }

  ingress {
    protocol        = "tcp"
    from_port       = 443
    to_port         = 443
    cidr_blocks     = ["0.0.0.0/0"]
    description     = "Allow HTTPS inbound traffic"
  }

  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = {
    Name        = var.security_group_name
    Environment = var.environment
    Project     = "JusticeBid"
    ManagedBy   = "Terraform"
  }
}

# ---------------------------------------------------------------------------------------------------------------------
# LOAD BALANCER RESOURCES
# ---------------------------------------------------------------------------------------------------------------------

resource "aws_lb" "justice_bid" {
  name               = var.load_balancer_name
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.ecs_tasks.id]
  subnets            = var.public_subnet_ids

  enable_deletion_protection = var.environment == "production" ? true : false

  tags = {
    Name        = var.load_balancer_name
    Environment = var.environment
    Project     = "JusticeBid"
    ManagedBy   = "Terraform"
  }
}

# Target group for web service
resource "aws_lb_target_group" "web" {
  name        = var.web_target_group_name
  port        = 80
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  health_check {
    enabled             = true
    interval            = 30
    path                = "/"
    port                = "traffic-port"
    healthy_threshold   = 3
    unhealthy_threshold = 3
    timeout             = 5
    matcher             = "200-399"
  }

  tags = {
    Name        = var.web_target_group_name
    Environment = var.environment
    Project     = "JusticeBid"
    ManagedBy   = "Terraform"
  }
}

# Target group for API service
resource "aws_lb_target_group" "api" {
  name        = var.api_target_group_name
  port        = 80
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  health_check {
    enabled             = true
    interval            = 30
    path                = "/api/health"
    port                = "traffic-port"
    healthy_threshold   = 3
    unhealthy_threshold = 3
    timeout             = 5
    matcher             = "200-399"
  }

  tags = {
    Name        = var.api_target_group_name
    Environment = var.environment
    Project     = "JusticeBid"
    ManagedBy   = "Terraform"
  }
}

# HTTP listener
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.justice_bid.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.web.arn
  }
}

# HTTPS listener (for production environments)
resource "aws_lb_listener" "https" {
  count             = var.environment == "production" ? 1 : 0
  load_balancer_arn = aws_lb.justice_bid.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-2016-08"
  certificate_arn   = var.certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.web.arn
  }
}

# Listener rule for API traffic
resource "aws_lb_listener_rule" "api" {
  listener_arn = var.environment == "production" && var.certificate_arn != "" ? aws_lb_listener.https[0].arn : aws_lb_listener.http.arn
  priority     = 100

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.api.arn
  }

  condition {
    path_pattern {
      values = ["/api/*"]
    }
  }
}

# ---------------------------------------------------------------------------------------------------------------------
# CLOUDWATCH LOGS
# ---------------------------------------------------------------------------------------------------------------------

resource "aws_cloudwatch_log_group" "justice_bid" {
  name              = "/ecs/justice-bid-${var.environment}"
  retention_in_days = 30

  tags = {
    Name        = "/ecs/justice-bid-${var.environment}"
    Environment = var.environment
    Project     = "JusticeBid"
    ManagedBy   = "Terraform"
  }
}

# ---------------------------------------------------------------------------------------------------------------------
# WEB SERVICE RESOURCES
# ---------------------------------------------------------------------------------------------------------------------

resource "aws_ecs_task_definition" "web" {
  family                   = var.web_task_family
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.web_task_cpu
  memory                   = var.web_task_memory
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([{
    name      = "web"
    image     = var.web_image
    essential = true
    portMappings = [{
      containerPort = 80
      hostPort      = 80
      protocol      = "tcp"
    }]
    environment = [
      {
        name  = "NODE_ENV"
        value = var.environment
      },
      {
        name  = "API_URL"
        value = "http://${aws_lb.justice_bid.dns_name}/api"
      }
    ]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.justice_bid.name
        "awslogs-region"        = var.region
        "awslogs-stream-prefix" = "web"
      }
    }
  }])

  tags = {
    Name        = var.web_task_family
    Environment = var.environment
    Project     = "JusticeBid"
    ManagedBy   = "Terraform"
  }
}

resource "aws_ecs_service" "web" {
  name            = var.web_service_name
  cluster         = aws_ecs_cluster.justice_bid.id
  task_definition = aws_ecs_task_definition.web.arn
  desired_count   = var.web_service_desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.web.arn
    container_name   = "web"
    container_port   = 80
  }

  health_check_grace_period_seconds = 120

  depends_on = [
    aws_lb_listener.http,
    aws_iam_role_policy_attachment.ecs_task_execution_policy
  ]

  tags = {
    Name        = var.web_service_name
    Environment = var.environment
    Project     = "JusticeBid"
    ManagedBy   = "Terraform"
  }

  lifecycle {
    ignore_changes = [desired_count]
  }
}

# ---------------------------------------------------------------------------------------------------------------------
# API SERVICE RESOURCES
# ---------------------------------------------------------------------------------------------------------------------

resource "aws_ecs_task_definition" "api" {
  family                   = var.api_task_family
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.api_task_cpu
  memory                   = var.api_task_memory
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([{
    name      = "api"
    image     = var.api_image
    essential = true
    portMappings = [{
      containerPort = 80
      hostPort      = 80
      protocol      = "tcp"
    }]
    environment = [
      {
        name  = "FLASK_ENV"
        value = var.environment
      },
      {
        name  = "DATABASE_URL"
        value = var.database_url
      }
    ]
    secrets = [
      {
        name      = "SECRET_KEY"
        valueFrom = var.secret_key_arn
      }
    ]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.justice_bid.name
        "awslogs-region"        = var.region
        "awslogs-stream-prefix" = "api"
      }
    }
  }])

  tags = {
    Name        = var.api_task_family
    Environment = var.environment
    Project     = "JusticeBid"
    ManagedBy   = "Terraform"
  }
}

resource "aws_ecs_service" "api" {
  name            = var.api_service_name
  cluster         = aws_ecs_cluster.justice_bid.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = var.api_service_desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.api.arn
    container_name   = "api"
    container_port   = 80
  }

  health_check_grace_period_seconds = 120

  depends_on = [
    aws_lb_listener_rule.api,
    aws_iam_role_policy_attachment.ecs_task_execution_policy
  ]

  tags = {
    Name        = var.api_service_name
    Environment = var.environment
    Project     = "JusticeBid"
    ManagedBy   = "Terraform"
  }

  lifecycle {
    ignore_changes = [desired_count]
  }
}

# ---------------------------------------------------------------------------------------------------------------------
# AUTO SCALING RESOURCES
# ---------------------------------------------------------------------------------------------------------------------

resource "aws_appautoscaling_target" "web" {
  max_capacity       = var.web_service_max_count
  min_capacity       = var.web_service_min_count
  resource_id        = "service/${aws_ecs_cluster.justice_bid.name}/${aws_ecs_service.web.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "web_cpu" {
  name               = "${var.web_service_name}-cpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.web.resource_id
  scalable_dimension = aws_appautoscaling_target.web.scalable_dimension
  service_namespace  = aws_appautoscaling_target.web.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value       = 70.0
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}

resource "aws_appautoscaling_policy" "web_memory" {
  name               = "${var.web_service_name}-memory-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.web.resource_id
  scalable_dimension = aws_appautoscaling_target.web.scalable_dimension
  service_namespace  = aws_appautoscaling_target.web.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageMemoryUtilization"
    }
    target_value       = 70.0
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}

resource "aws_appautoscaling_target" "api" {
  max_capacity       = var.api_service_max_count
  min_capacity       = var.api_service_min_count
  resource_id        = "service/${aws_ecs_cluster.justice_bid.name}/${aws_ecs_service.api.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "api_cpu" {
  name               = "${var.api_service_name}-cpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.api.resource_id
  scalable_dimension = aws_appautoscaling_target.api.scalable_dimension
  service_namespace  = aws_appautoscaling_target.api.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value       = 70.0
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}

resource "aws_appautoscaling_policy" "api_memory" {
  name               = "${var.api_service_name}-memory-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.api.resource_id
  scalable_dimension = aws_appautoscaling_target.api.scalable_dimension
  service_namespace  = aws_appautoscaling_target.api.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageMemoryUtilization"
    }
    target_value       = 70.0
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}

resource "aws_appautoscaling_policy" "api_requests" {
  name               = "${var.api_service_name}-request-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.api.resource_id
  scalable_dimension = aws_appautoscaling_target.api.scalable_dimension
  service_namespace  = aws_appautoscaling_target.api.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ALBRequestCountPerTarget"
      resource_label         = "${aws_lb.justice_bid.arn_suffix}/${aws_lb_target_group.api.arn_suffix}"
    }
    target_value       = 1000
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}