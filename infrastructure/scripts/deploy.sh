#!/bin/bash
# deploy.sh
# Deployment script for Justice Bid Rate Negotiation System
# Automates container image management, infrastructure provisioning, and application deployment

set -e

# Script constants and configuration
SCRIPT_DIR="$(dirname "${BASH_SOURCE[0]}")"
ECR_REGISTRY="${ECR_REGISTRY:-123456789012.dkr.ecr.us-east-1.amazonaws.com/justice-bid}"
AWS_REGION="${AWS_REGION:-us-east-1}"
ENVIRONMENTS=("dev" "staging" "production")
LOG_FILE="${SCRIPT_DIR}/deploy.log"

# Utility function for logging messages with timestamps
log() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $1"
    echo "[$timestamp] $1" >> "$LOG_FILE"
}

# Check if required tools and configurations are available
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check for required tools
    for tool in docker aws kubectl terraform jq; do
        if ! command -v $tool &> /dev/null; then
            log "ERROR: $tool is required but not installed. Please install $tool and try again."
            return 1
        fi
    done
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log "ERROR: AWS credentials not configured. Please configure AWS credentials and try again."
        return 1
    fi
    
    # Check for required environment variables
    if [[ -z $ECR_REGISTRY ]]; then
        log "ERROR: ECR_REGISTRY environment variable is not set."
        return 1
    fi
    
    log "All prerequisites met."
    return 0
}

# Validate that the specified environment is valid
validate_environment() {
    local env=$1
    
    for valid_env in "${ENVIRONMENTS[@]}"; do
        if [[ "$env" == "$valid_env" ]]; then
            log "Environment '$env' is valid."
            return 0
        fi
    done
    
    log "ERROR: Invalid environment '$env'. Valid environments are: ${ENVIRONMENTS[*]}"
    return 1
}

# Tag and push Docker images to ECR
tag_and_push() {
    local version=$1
    local environment=$2
    
    if [[ -z $version || -z $environment ]]; then
        log "ERROR: Version and environment are required for tag_and_push."
        return 1
    fi
    
    validate_environment "$environment" || return 1
    
    log "Tagging and pushing images for version $version to $environment environment..."
    
    # Check if Docker is running
    if ! docker info &> /dev/null; then
        log "ERROR: Docker is not running. Please start Docker and try again."
        return 1
    fi
    
    # Login to ECR
    log "Logging into ECR registry..."
    aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "$ECR_REGISTRY" || {
        log "ERROR: Failed to log in to ECR registry."
        return 1
    }
    
    # List of services to tag and push
    local services=("frontend" "api-gateway" "rate-service" "negotiation-service" "analytics-service" "integration-service" "ai-service" "document-service")
    
    for service in "${services[@]}"; do
        log "Tagging and pushing $service image..."
        
        # Tag local image with ECR repository URL
        docker tag "justice-bid/$service:latest" "$ECR_REGISTRY/$service:$version-$environment" || {
            log "ERROR: Failed to tag $service image."
            return 1
        }
        
        # Push image to ECR
        docker push "$ECR_REGISTRY/$service:$version-$environment" || {
            log "ERROR: Failed to push $service image to ECR."
            return 1
        }
        
        log "Successfully pushed $service image to ECR with tag $version-$environment."
    done
    
    log "All images tagged and pushed successfully."
    return 0
}

# Deploy or update infrastructure using Terraform
deploy_infrastructure() {
    local environment=$1
    local version=$2
    
    if [[ -z $environment || -z $version ]]; then
        log "ERROR: Environment and version are required for deploy_infrastructure."
        return 1
    fi
    
    validate_environment "$environment" || return 1
    
    local tf_dir="${SCRIPT_DIR}/../terraform/$environment"
    
    if [[ ! -d "$tf_dir" ]]; then
        log "ERROR: Terraform directory for $environment not found at $tf_dir."
        return 1
    fi
    
    log "Deploying infrastructure for $environment environment with version $version..."
    
    # Move to Terraform directory
    cd "$tf_dir" || {
        log "ERROR: Failed to change to Terraform directory $tf_dir."
        return 1
    }
    
    # Initialize Terraform
    log "Initializing Terraform..."
    terraform init || {
        log "ERROR: Failed to initialize Terraform."
        return 1
    }
    
    # Create a plan
    log "Creating Terraform plan..."
    terraform plan -var="app_version=$version" -out=tfplan || {
        log "ERROR: Failed to create Terraform plan."
        return 1
    }
    
    # Apply the plan
    log "Applying Terraform plan..."
    terraform apply -auto-approve tfplan || {
        log "ERROR: Failed to apply Terraform plan."
        return 1
    }
    
    log "Infrastructure deployment completed successfully."
    return 0
}

# Deploy application to Kubernetes cluster
deploy_application() {
    local environment=$1
    local version=$2
    
    if [[ -z $environment || -z $version ]]; then
        log "ERROR: Environment and version are required for deploy_application."
        return 1
    fi
    
    validate_environment "$environment" || return 1
    
    log "Deploying application to $environment environment with version $version..."
    
    # Get EKS cluster name based on environment
    local cluster_name="justice-bid-$environment"
    
    # Update kubeconfig for the target cluster
    log "Updating kubeconfig for cluster $cluster_name..."
    aws eks update-kubeconfig --name "$cluster_name" --region "$AWS_REGION" || {
        log "ERROR: Failed to update kubeconfig for cluster $cluster_name."
        return 1
    }
    
    # Path to Kustomize directory for the environment
    local kustomize_dir="${SCRIPT_DIR}/../k8s/$environment"
    
    if [[ ! -d "$kustomize_dir" ]]; then
        log "ERROR: Kustomize directory for $environment not found at $kustomize_dir."
        return 1
    }
    
    # Update image tags in kustomization.yaml
    log "Updating image tags in Kustomize configuration..."
    
    local services=("frontend" "api-gateway" "rate-service" "negotiation-service" "analytics-service" "integration-service" "ai-service" "document-service")
    
    for service in "${services[@]}"; do
        # Use sed to update image versions in kustomization.yaml
        sed -i.bak "s|$ECR_REGISTRY/$service:.*|$ECR_REGISTRY/$service:$version-$environment|g" "$kustomize_dir/kustomization.yaml" || {
            log "ERROR: Failed to update image tag for $service in Kustomize configuration."
            return 1
        }
    done
    
    # Apply the Kubernetes manifests using Kustomize
    log "Applying Kubernetes manifests with Kustomize..."
    kubectl apply -k "$kustomize_dir" || {
        log "ERROR: Failed to apply Kubernetes manifests."
        return 1
    }
    
    # Implement deployment strategy based on service
    # For frontend and api-gateway, use blue-green deployment
    if [[ "$environment" == "production" ]]; then
        log "Implementing blue-green deployment for frontend and api-gateway..."
        
        # Frontend blue-green deployment
        kubectl apply -f "${SCRIPT_DIR}/../k8s/production/blue-green/frontend-green.yaml" || {
            log "ERROR: Failed to deploy green version of frontend."
            return 1
        }
        
        # Wait for green deployment to be ready
        kubectl rollout status deployment/frontend-green -n justice-bid --timeout=300s || {
            log "ERROR: Green deployment of frontend not ready after timeout."
            return 1
        }
        
        # Switch traffic to green deployment
        kubectl apply -f "${SCRIPT_DIR}/../k8s/production/blue-green/frontend-service-green.yaml" || {
            log "ERROR: Failed to switch traffic to green deployment of frontend."
            return 1
        }
        
        # Similar process for api-gateway
        kubectl apply -f "${SCRIPT_DIR}/../k8s/production/blue-green/api-gateway-green.yaml" || {
            log "ERROR: Failed to deploy green version of api-gateway."
            return 1
        }
        
        kubectl rollout status deployment/api-gateway-green -n justice-bid --timeout=300s || {
            log "ERROR: Green deployment of api-gateway not ready after timeout."
            return 1
        }
        
        kubectl apply -f "${SCRIPT_DIR}/../k8s/production/blue-green/api-gateway-service-green.yaml" || {
            log "ERROR: Failed to switch traffic to green deployment of api-gateway."
            return 1
        }
    else
        # For other environments and services, use rolling updates
        log "Waiting for all deployments to complete rollout..."
        
        # Wait for all deployments to complete their rollouts with timeout
        for service in "${services[@]}"; do
            kubectl rollout status deployment/"$service" -n justice-bid --timeout=300s || {
                log "ERROR: Deployment of $service not ready after timeout."
                return 1
            }
        done
    fi
    
    # Verify deployment health
    log "Verifying deployment health..."
    
    # Check that all pods are running
    local pods_not_running=$(kubectl get pods -n justice-bid -o json | jq -r '.items[] | select(.status.phase != "Running" and .status.phase != "Succeeded") | .metadata.name')
    
    if [[ -n "$pods_not_running" ]]; then
        log "ERROR: Some pods are not running: $pods_not_running"
        return 1
    fi
    
    log "Application deployment completed successfully."
    return 0
}

# Run database migrations after deployment
run_migrations() {
    local environment=$1
    
    if [[ -z $environment ]]; then
        log "ERROR: Environment is required for run_migrations."
        return 1
    fi
    
    validate_environment "$environment" || return 1
    
    log "Running database migrations for $environment environment..."
    
    # Get EKS cluster name based on environment
    local cluster_name="justice-bid-$environment"
    
    # Update kubeconfig for the target cluster if not already done
    if ! kubectl config current-context | grep -q "$cluster_name"; then
        log "Updating kubeconfig for cluster $cluster_name..."
        aws eks update-kubeconfig --name "$cluster_name" --region "$AWS_REGION" || {
            log "ERROR: Failed to update kubeconfig for cluster $cluster_name."
            return 1
        }
    fi
    
    # Create a migration job
    cat <<EOF > /tmp/migration-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: database-migration-$(date +%s)
  namespace: justice-bid
spec:
  ttlSecondsAfterFinished: 3600
  template:
    spec:
      containers:
      - name: migration
        image: $ECR_REGISTRY/database-migration:latest
        command: ["alembic", "upgrade", "head"]
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: database-credentials
              key: url
      restartPolicy: Never
  backoffLimit: 3
EOF

    # Apply the migration job
    kubectl apply -f /tmp/migration-job.yaml || {
        log "ERROR: Failed to apply migration job."
        rm /tmp/migration-job.yaml
        return 1
    }
    
    # Clean up the job file
    rm /tmp/migration-job.yaml
    
    # Get the job name
    local job_name=$(kubectl get jobs -n justice-bid -o json | jq -r '.items[] | select(.metadata.name | startswith("database-migration-")) | .metadata.name' | sort | tail -n 1)
    
    # Wait for the migration job to complete
    log "Waiting for migration job $job_name to complete..."
    kubectl wait --for=condition=complete --timeout=300s job/"$job_name" -n justice-bid || {
        # Check if the job failed
        if kubectl get job "$job_name" -n justice-bid -o json | jq -e '.status.failed > 0' > /dev/null; then
            log "ERROR: Migration job failed. Check pod logs for details."
            # Get the pod name for the job
            local pod_name=$(kubectl get pods -n justice-bid -o json | jq -r '.items[] | select(.metadata.name | startswith("'"$job_name"'")) | .metadata.name')
            if [[ -n "$pod_name" ]]; then
                log "Migration job pod logs:"
                kubectl logs "$pod_name" -n justice-bid
            fi
            return 1
        else
            log "ERROR: Timed out waiting for migration job to complete."
            return 1
        fi
    }
    
    log "Database migrations completed successfully."
    return 0
}

# Create a git tag for the deployment
create_deployment_tag() {
    local environment=$1
    local version=$2
    
    if [[ -z $environment || -z $version ]]; then
        log "ERROR: Environment and version are required for create_deployment_tag."
        return 1
    fi
    
    validate_environment "$environment" || return 1
    
    log "Creating deployment tag for $environment environment with version $version..."
    
    local tag_name="deployment-$environment-$version"
    local tag_message="Deployment to $environment environment with version $version on $(date '+%Y-%m-%d %H:%M:%S')"
    
    # Create the tag
    git tag -a "$tag_name" -m "$tag_message" || {
        log "ERROR: Failed to create git tag $tag_name."
        return 1
    }
    
    # Push the tag to the remote repository
    git push origin "$tag_name" || {
        log "ERROR: Failed to push git tag $tag_name to remote repository."
        return 1
    }
    
    log "Deployment tag $tag_name created and pushed successfully."
    return 0
}

# Rollback to a previous version if deployment fails
rollback() {
    local environment=$1
    local previous_version=$2
    
    if [[ -z $environment ]]; then
        log "ERROR: Environment is required for rollback."
        return 1
    fi
    
    validate_environment "$environment" || return 1
    
    # If previous version wasn't provided, try to determine it from the most recent successful deployment
    if [[ -z $previous_version ]]; then
        log "Previous version not specified, attempting to determine from git tags..."
        
        previous_version=$(git tag -l "deployment-$environment-*" | sort -V | tail -n 1 | sed "s/deployment-$environment-//")
        
        if [[ -z $previous_version ]]; then
            log "ERROR: Unable to determine previous version from git tags."
            return 1
        fi
        
        log "Determined previous version: $previous_version"
    fi
    
    log "Rolling back $environment environment to version $previous_version..."
    
    # Get EKS cluster name based on environment
    local cluster_name="justice-bid-$environment"
    
    # Update kubeconfig for the target cluster
    log "Updating kubeconfig for cluster $cluster_name..."
    aws eks update-kubeconfig --name "$cluster_name" --region "$AWS_REGION" || {
        log "ERROR: Failed to update kubeconfig for cluster $cluster_name."
        return 1
    }
    
    if [[ "$environment" == "production" ]]; then
        # For blue-green deployments, switch back to the blue version
        log "Switching back to blue deployment for frontend and api-gateway..."
        
        kubectl apply -f "${SCRIPT_DIR}/../k8s/production/blue-green/frontend-service-blue.yaml" || {
            log "ERROR: Failed to switch traffic back to blue deployment of frontend."
            return 1
        }
        
        kubectl apply -f "${SCRIPT_DIR}/../k8s/production/blue-green/api-gateway-service-blue.yaml" || {
            log "ERROR: Failed to switch traffic back to blue deployment of api-gateway."
            return 1
        }
    else
        # For rolling updates, use rollout undo
        log "Performing rollout undo for all services..."
        
        local services=("frontend" "api-gateway" "rate-service" "negotiation-service" "analytics-service" "integration-service" "ai-service" "document-service")
        
        for service in "${services[@]}"; do
            kubectl rollout undo deployment/"$service" -n justice-bid || {
                log "ERROR: Failed to rollback deployment of $service."
                return 1
            }
            
            kubectl rollout status deployment/"$service" -n justice-bid --timeout=300s || {
                log "WARNING: Rollback of $service not completed after timeout."
            }
        done
    fi
    
    # Update the Kustomize files to point back to the previous version
    local kustomize_dir="${SCRIPT_DIR}/../k8s/$environment"
    
    if [[ -d "$kustomize_dir" ]]; then
        log "Updating Kustomize configuration to use previous version $previous_version..."
        
        local services=("frontend" "api-gateway" "rate-service" "negotiation-service" "analytics-service" "integration-service" "ai-service" "document-service")
        
        for service in "${services[@]}"; do
            sed -i.bak "s|$ECR_REGISTRY/$service:.*|$ECR_REGISTRY/$service:$previous_version-$environment|g" "$kustomize_dir/kustomization.yaml" || {
                log "ERROR: Failed to update image tag for $service in Kustomize configuration."
                return 1
            }
        done
        
        # Apply the updated configuration
        kubectl apply -k "$kustomize_dir" || {
            log "ERROR: Failed to apply Kubernetes manifests with previous version."
            return 1
        }
    fi
    
    log "Rollback to version $previous_version completed successfully."
    return 0
}

# Full deployment process that combines all steps
full_deploy() {
    local environment=$1
    local version=$2
    
    if [[ -z $environment || -z $version ]]; then
        log "ERROR: Environment and version are required for full_deploy."
        return 1
    fi
    
    validate_environment "$environment" || return 1
    
    log "Starting full deployment process for $environment environment with version $version..."
    
    # Check prerequisites
    check_prerequisites || {
        log "ERROR: Failed to meet prerequisites. Deployment aborted."
        return 1
    }
    
    # Tag and push images
    tag_and_push "$version" "$environment" || {
        log "ERROR: Failed to tag and push images. Deployment aborted."
        return 1
    }
    
    # Deploy infrastructure
    deploy_infrastructure "$environment" "$version" || {
        log "ERROR: Failed to deploy infrastructure. Deployment aborted."
        return 1
    }
    
    # Deploy application
    deploy_application "$environment" "$version" || {
        log "ERROR: Failed to deploy application. Rolling back..."
        rollback "$environment"
        return 1
    }
    
    # Run migrations
    run_migrations "$environment" || {
        log "ERROR: Failed to run migrations. Rolling back..."
        rollback "$environment"
        return 1
    }
    
    # Create deployment tag
    create_deployment_tag "$environment" "$version" || {
        log "WARNING: Failed to create deployment tag, but deployment was successful."
    }
    
    log "Full deployment process completed successfully."
    return 0
}

# Main function to handle command-line arguments
main() {
    local command=$1
    shift
    
    case "$command" in
        check_prerequisites)
            check_prerequisites
            return $?
            ;;
        tag_and_push)
            tag_and_push "$1" "$2"
            return $?
            ;;
        deploy_infrastructure)
            deploy_infrastructure "$1" "$2"
            return $?
            ;;
        deploy_application)
            deploy_application "$1" "$2"
            return $?
            ;;
        run_migrations)
            run_migrations "$1"
            return $?
            ;;
        create_deployment_tag)
            create_deployment_tag "$1" "$2"
            return $?
            ;;
        rollback)
            rollback "$1" "$2"
            return $?
            ;;
        full_deploy)
            full_deploy "$1" "$2"
            return $?
            ;;
        *)
            log "ERROR: Unknown command '$command'."
            log "Usage:"
            log "  $0 check_prerequisites"
            log "  $0 tag_and_push <version> <environment>"
            log "  $0 deploy_infrastructure <environment> <version>"
            log "  $0 deploy_application <environment> <version>"
            log "  $0 run_migrations <environment>"
            log "  $0 create_deployment_tag <environment> <version>"
            log "  $0 rollback <environment> [previous_version]"
            log "  $0 full_deploy <environment> <version>"
            return 1
            ;;
    esac
}

# Execute main function with command-line arguments
main "$@"
exit $?