terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

locals {
  # Normalize bucket names with environment prefix
  documents_bucket_name = "${var.environment}-${var.bucket_prefix}-documents"
  exports_bucket_name   = "${var.environment}-${var.bucket_prefix}-exports"
  uploads_bucket_name   = "${var.environment}-${var.bucket_prefix}-uploads"
  dr_documents_bucket_name = var.create_replication ? "${var.environment}-${var.bucket_prefix}-dr-documents" : ""
  
  # Combine default tags with user-provided tags
  common_tags = merge(
    var.tags,
    {
      Environment = var.environment
      ManagedBy   = "terraform"
      Application = "JusticeBid"
    }
  )
  
  # Standard lifecycle rules
  standard_lifecycle_rules = var.lifecycle_rules_enabled ? [
    {
      id      = "transition-to-intelligent-tiering"
      status  = "Enabled"
      transition = [
        {
          days          = var.intelligent_tiering_days
          storage_class = "INTELLIGENT_TIERING"
        }
      ]
      noncurrent_version_transition = [
        {
          noncurrent_days = 30
          storage_class   = "STANDARD_IA"
        }
      ]
      noncurrent_version_expiration = {
        noncurrent_days = var.noncurrent_version_expiration_days
      }
    }
  ] : []
  
  # Export bucket lifecycle rules
  export_lifecycle_rules = var.lifecycle_rules_enabled ? [
    {
      id      = "transition-to-glacier"
      status  = "Enabled"
      transition = [
        {
          days          = var.glacier_transition_days
          storage_class = "GLACIER"
        }
      ]
      noncurrent_version_transition = [
        {
          noncurrent_days = 30
          storage_class   = "STANDARD_IA"
        }
      ]
      noncurrent_version_expiration = {
        noncurrent_days = var.noncurrent_version_expiration_days
      }
    }
  ] : []
  
  # Uploads bucket lifecycle rules
  uploads_lifecycle_rules = var.lifecycle_rules_enabled ? [
    {
      id      = "expire-temporary-uploads"
      status  = "Enabled"
      expiration = {
        days = var.uploads_expiration_days
      }
    }
  ] : []
}

# Create the documents bucket
resource "aws_s3_bucket" "documents" {
  bucket        = local.documents_bucket_name
  force_destroy = var.environment != "production"
  
  tags = merge(
    local.common_tags,
    {
      Name = "Justice Bid Documents"
    }
  )
}

# Create the exports bucket
resource "aws_s3_bucket" "exports" {
  bucket        = local.exports_bucket_name
  force_destroy = var.environment != "production"
  
  tags = merge(
    local.common_tags,
    {
      Name = "Justice Bid Exports"
    }
  )
}

# Create the uploads bucket
resource "aws_s3_bucket" "uploads" {
  bucket        = local.uploads_bucket_name
  force_destroy = true # Always allow force destroy for temporary uploads
  
  tags = merge(
    local.common_tags,
    {
      Name      = "Justice Bid Uploads"
      Temporary = "true"
    }
  )
}

# Enable versioning on documents bucket
resource "aws_s3_bucket_versioning" "documents" {
  bucket = aws_s3_bucket.documents.id
  
  versioning_configuration {
    status = var.versioning_enabled ? "Enabled" : "Suspended"
  }
}

# Enable versioning on exports bucket
resource "aws_s3_bucket_versioning" "exports" {
  bucket = aws_s3_bucket.exports.id
  
  versioning_configuration {
    status = var.versioning_enabled ? "Enabled" : "Suspended"
  }
}

# Configure encryption for documents bucket
resource "aws_s3_bucket_server_side_encryption_configuration" "documents" {
  count  = var.encryption_enabled ? 1 : 0
  bucket = aws_s3_bucket.documents.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Configure encryption for exports bucket
resource "aws_s3_bucket_server_side_encryption_configuration" "exports" {
  count  = var.encryption_enabled ? 1 : 0
  bucket = aws_s3_bucket.exports.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Configure lifecycle rules for documents bucket
resource "aws_s3_bucket_lifecycle_configuration" "documents" {
  count  = var.lifecycle_rules_enabled ? 1 : 0
  bucket = aws_s3_bucket.documents.id
  
  dynamic "rule" {
    for_each = local.standard_lifecycle_rules
    content {
      id     = rule.value.id
      status = rule.value.status
      
      dynamic "transition" {
        for_each = rule.value.transition
        content {
          days          = transition.value.days
          storage_class = transition.value.storage_class
        }
      }
      
      dynamic "noncurrent_version_transition" {
        for_each = rule.value.noncurrent_version_transition
        content {
          noncurrent_days = noncurrent_version_transition.value.noncurrent_days
          storage_class   = noncurrent_version_transition.value.storage_class
        }
      }
      
      noncurrent_version_expiration {
        noncurrent_days = rule.value.noncurrent_version_expiration.noncurrent_days
      }
    }
  }
  
  depends_on = [aws_s3_bucket_versioning.documents]
}

# Configure lifecycle rules for exports bucket
resource "aws_s3_bucket_lifecycle_configuration" "exports" {
  count  = var.lifecycle_rules_enabled ? 1 : 0
  bucket = aws_s3_bucket.exports.id
  
  dynamic "rule" {
    for_each = local.export_lifecycle_rules
    content {
      id     = rule.value.id
      status = rule.value.status
      
      dynamic "transition" {
        for_each = rule.value.transition
        content {
          days          = transition.value.days
          storage_class = transition.value.storage_class
        }
      }
      
      dynamic "noncurrent_version_transition" {
        for_each = rule.value.noncurrent_version_transition
        content {
          noncurrent_days = noncurrent_version_transition.value.noncurrent_days
          storage_class   = noncurrent_version_transition.value.storage_class
        }
      }
      
      noncurrent_version_expiration {
        noncurrent_days = rule.value.noncurrent_version_expiration.noncurrent_days
      }
    }
  }
  
  depends_on = [aws_s3_bucket_versioning.exports]
}

# Configure lifecycle rules for uploads bucket
resource "aws_s3_bucket_lifecycle_configuration" "uploads" {
  count  = var.lifecycle_rules_enabled ? 1 : 0
  bucket = aws_s3_bucket.uploads.id
  
  dynamic "rule" {
    for_each = local.uploads_lifecycle_rules
    content {
      id     = rule.value.id
      status = rule.value.status
      
      expiration {
        days = rule.value.expiration.days
      }
    }
  }
}

# Block public access for documents bucket
resource "aws_s3_bucket_public_access_block" "documents" {
  bucket = aws_s3_bucket.documents.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Block public access for exports bucket
resource "aws_s3_bucket_public_access_block" "exports" {
  bucket = aws_s3_bucket.exports.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Block public access for uploads bucket
resource "aws_s3_bucket_public_access_block" "uploads" {
  bucket = aws_s3_bucket.uploads.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Create IAM role for replication
resource "aws_iam_role" "replication" {
  count = var.create_replication ? 1 : 0
  
  name = "${var.environment}-s3-replication-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "s3.amazonaws.com"
        }
      }
    ]
  })
  
  tags = local.common_tags
}

# Create IAM policy for replication
resource "aws_iam_policy" "replication" {
  count = var.create_replication ? 1 : 0
  
  name = "${var.environment}-s3-replication-policy"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:GetReplicationConfiguration",
          "s3:ListBucket"
        ]
        Effect = "Allow"
        Resource = [
          aws_s3_bucket.documents.arn
        ]
      },
      {
        Action = [
          "s3:GetObjectVersionForReplication",
          "s3:GetObjectVersionAcl",
          "s3:GetObjectVersionTagging"
        ]
        Effect = "Allow"
        Resource = [
          "${aws_s3_bucket.documents.arn}/*"
        ]
      },
      {
        Action = [
          "s3:ReplicateObject",
          "s3:ReplicateDelete",
          "s3:ReplicateTags"
        ]
        Effect = "Allow"
        Resource = var.create_replication ? "${aws_s3_bucket.dr_documents[0].arn}/*" : null
      }
    ]
  })
}

# Attach replication policy to role
resource "aws_iam_role_policy_attachment" "replication" {
  count = var.create_replication ? 1 : 0
  
  role       = aws_iam_role.replication[0].name
  policy_arn = aws_iam_policy.replication[0].arn
}

# Create DR bucket in secondary region
resource "aws_s3_bucket" "dr_documents" {
  count = var.create_replication ? 1 : 0
  
  provider = aws.dr
  bucket   = local.dr_documents_bucket_name
  
  tags = merge(
    local.common_tags,
    {
      Name = "Justice Bid Documents DR"
    }
  )
}

# Enable versioning on DR bucket
resource "aws_s3_bucket_versioning" "dr_documents" {
  count = var.create_replication ? 1 : 0
  
  provider = aws.dr
  bucket   = aws_s3_bucket.dr_documents[0].id
  
  versioning_configuration {
    status = "Enabled"
  }
}

# Configure encryption for DR bucket
resource "aws_s3_bucket_server_side_encryption_configuration" "dr_documents" {
  count = var.create_replication && var.encryption_enabled ? 1 : 0
  
  provider = aws.dr
  bucket   = aws_s3_bucket.dr_documents[0].id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Configure replication from documents to DR bucket
resource "aws_s3_bucket_replication_configuration" "documents" {
  count = var.create_replication ? 1 : 0
  
  role   = aws_iam_role.replication[0].arn
  bucket = aws_s3_bucket.documents.id
  
  rule {
    id     = "replicate-all"
    status = "Enabled"
    
    destination {
      bucket        = aws_s3_bucket.dr_documents[0].arn
      storage_class = "STANDARD"
    }
  }
  
  depends_on = [aws_s3_bucket_versioning.documents]
}