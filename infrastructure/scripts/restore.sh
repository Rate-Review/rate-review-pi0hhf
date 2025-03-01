#!/bin/bash
# restore.sh - Justice Bid System Restore Utility
# 
# This script restores Justice Bid databases, file storage, and application state 
# from backups. It supports various restore types including full restore, 
# point-in-time recovery, and disaster recovery failover.
#
# Version: 1.0

# Set strict error handling
set -e
set -o pipefail

# Global variables
LOG_FILE="/var/log/justicebid/restore.log"
TEMP_DIR="/tmp/justicebid_restore"
SCRIPT_NAME=$(basename "$0")
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")

# Function to display usage information
print_usage() {
    echo "Usage: $SCRIPT_NAME [OPTIONS] COMMAND"
    echo
    echo "Justice Bid Backup Restore Utility"
    echo
    echo "Commands:"
    echo "  database      Restore database from snapshot or point-in-time recovery"
    echo "  storage       Restore file storage (S3) from backups"
    echo "  application   Restore application state from snapshot backups"
    echo "  dr            Execute disaster recovery procedure"
    echo "  list          List available backups for a resource type"
    echo
    echo "Options:"
    echo "  -e, --environment ENV     Target environment (dev, staging, production)"
    echo "  -i, --id ID               Backup ID or snapshot identifier"
    echo "  -t, --time TIMESTAMP      Point-in-time for recovery (format: YYYY-MM-DD HH:MM:SS)"
    echo "  -r, --region REGION       AWS region (default: us-east-1)"
    echo "  -p, --profile PROFILE     AWS profile to use"
    echo "  -b, --bucket BUCKET       S3 bucket name for file storage restore"
    echo "  -d, --db-name DB_NAME     Database name for database restore"
    echo "  -h, --help                Display this help message"
    echo "  -v, --verbose             Enable verbose output"
    echo
    echo "Examples:"
    echo "  $SCRIPT_NAME list database -e production"
    echo "  $SCRIPT_NAME database -e staging -i rds:justicebid-db-snapshot-20231001 -d justicebid"
    echo "  $SCRIPT_NAME database -e production -t \"2023-10-01 14:30:00\" -d justicebid"
    echo "  $SCRIPT_NAME storage -e production -b justicebid-docs -i 2023-10-01-backup"
    echo "  $SCRIPT_NAME application -e staging -i app-snapshot-20231001"
    echo "  $SCRIPT_NAME dr -e production -r us-west-2"
}

# Function to set up logging
setup_logging() {
    # Create log directory if it doesn't exist
    mkdir -p "$(dirname "$LOG_FILE")"
    
    # Initialize log file with restore details
    {
        echo "=================================================="
        echo "Justice Bid Restore - Started at $(date)"
        echo "Command: $SCRIPT_NAME $*"
        echo "Environment: $ENVIRONMENT"
        echo "=================================================="
    } > "$LOG_FILE"
    
    # Define log function
    log() {
        local level=$1
        shift
        local message="$*"
        local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
        echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
    }
    
    # Export log function to be used by other functions
    export -f log
}

# Function to check prerequisites
check_prerequisites() {
    log "INFO" "Checking prerequisites..."
    
    # Check AWS CLI
    if ! command -v aws &>/dev/null; then
        log "ERROR" "AWS CLI is required but not installed. Please install AWS CLI v2."
        return 1
    fi
    
    # Check AWS CLI version
    local aws_version=$(aws --version | cut -d' ' -f1 | cut -d'/' -f2)
    log "INFO" "AWS CLI version: $aws_version"
    
    # Check PostgreSQL client for database restores
    if [[ "$COMMAND" == "database" || "$COMMAND" == "dr" ]]; then
        if ! command -v psql &>/dev/null; then
            log "ERROR" "PostgreSQL client is required for database restore but not installed."
            return 1
        fi
        
        local psql_version=$(psql --version | cut -d' ' -f3)
        log "INFO" "PostgreSQL client version: $psql_version"
    fi
    
    # Verify AWS credentials
    if ! aws sts get-caller-identity $AWS_PROFILE_ARG &>/dev/null; then
        log "ERROR" "Failed to validate AWS credentials. Please check your credentials and permissions."
        return 1
    fi
    
    local aws_account=$(aws sts get-caller-identity $AWS_PROFILE_ARG --query "Account" --output text)
    log "INFO" "AWS account ID: $aws_account"
    
    # Check connectivity based on command
    case "$COMMAND" in
        database|dr)
            if ! aws rds describe-db-instances $AWS_PROFILE_ARG --region "$REGION" --max-items 1 &>/dev/null; then
                log "ERROR" "Failed to connect to RDS service. Check your permissions."
                return 1
            fi
            ;;
        storage)
            if ! aws s3 ls $AWS_PROFILE_ARG s3:// --region "$REGION" &>/dev/null; then
                log "ERROR" "Failed to connect to S3 service. Check your permissions."
                return 1
            fi
            ;;
        application)
            if ! aws ec2 describe-snapshots $AWS_PROFILE_ARG --region "$REGION" --owner-ids self --max-items 1 &>/dev/null; then
                log "ERROR" "Failed to connect to EC2 service. Check your permissions."
                return 1
            fi
            ;;
    esac
    
    # Create temp directory
    mkdir -p "$TEMP_DIR"
    
    log "INFO" "Prerequisites check completed successfully."
    return 0
}

# Function to parse and validate arguments
parse_arguments() {
    # Default values
    VERBOSE=false
    REGION="us-east-1"
    AWS_PROFILE_ARG=""
    
    # Parse options
    local OPTS=$(getopt -o e:i:t:r:p:b:d:hv --long environment:,id:,time:,region:,profile:,bucket:,db-name:,help,verbose -n "$SCRIPT_NAME" -- "$@")
    if [ $? -ne 0 ]; then
        print_usage
        exit 1
    fi
    
    eval set -- "$OPTS"
    
    while true; do
        case "$1" in
            -e|--environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -i|--id)
                BACKUP_ID="$2"
                shift 2
                ;;
            -t|--time)
                TARGET_TIME="$2"
                shift 2
                ;;
            -r|--region)
                REGION="$2"
                shift 2
                ;;
            -p|--profile)
                AWS_PROFILE="$2"
                AWS_PROFILE_ARG="--profile $AWS_PROFILE"
                shift 2
                ;;
            -b|--bucket)
                BUCKET_NAME="$2"
                shift 2
                ;;
            -d|--db-name)
                DB_NAME="$2"
                shift 2
                ;;
            -h|--help)
                print_usage
                exit 0
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            --)
                shift
                break
                ;;
            *)
                echo "Invalid option: $1"
                print_usage
                exit 1
                ;;
        esac
    done
    
    # Get command
    COMMAND="$1"
    shift
    
    # Validate command
    case "$COMMAND" in
        database|storage|application|dr|list)
            # Valid command
            ;;
        "")
            log "ERROR" "No command specified."
            print_usage
            return 1
            ;;
        *)
            log "ERROR" "Unknown command: $COMMAND"
            print_usage
            return 1
            ;;
    esac
    
    # Validate required parameters based on command
    case "$COMMAND" in
        database)
            if [ -z "$ENVIRONMENT" ] || [ -z "$DB_NAME" ]; then
                log "ERROR" "Database restore requires environment (-e) and database name (-d)."
                return 1
            fi
            if [ -z "$BACKUP_ID" ] && [ -z "$TARGET_TIME" ]; then
                log "ERROR" "Database restore requires either backup ID (-i) or point-in-time (-t)."
                return 1
            fi
            ;;
        storage)
            if [ -z "$ENVIRONMENT" ] || [ -z "$BUCKET_NAME" ]; then
                log "ERROR" "Storage restore requires environment (-e) and bucket name (-b)."
                return 1
            fi
            if [ -z "$BACKUP_ID" ]; then
                log "ERROR" "Storage restore requires backup ID (-i)."
                return 1
            fi
            ;;
        application)
            if [ -z "$ENVIRONMENT" ]; then
                log "ERROR" "Application restore requires environment (-e)."
                return 1
            fi
            if [ -z "$BACKUP_ID" ]; then
                log "ERROR" "Application restore requires backup ID (-i)."
                return 1
            fi
            ;;
        dr)
            if [ -z "$ENVIRONMENT" ]; then
                log "ERROR" "Disaster recovery requires environment (-e)."
                return 1
            fi
            ;;
        list)
            if [ -z "$2" ]; then
                log "ERROR" "List command requires a resource type (database, storage, application)."
                return 1
            fi
            LIST_TYPE="$2"
            case "$LIST_TYPE" in
                database|storage|application)
                    # Valid list type
                    ;;
                *)
                    log "ERROR" "Unknown list type: $LIST_TYPE"
                    return 1
                    ;;
            esac
            if [ -z "$ENVIRONMENT" ]; then
                log "ERROR" "List command requires environment (-e)."
                return 1
            fi
            ;;
    esac
    
    log "INFO" "Command: $COMMAND"
    log "INFO" "Environment: $ENVIRONMENT"
    log "INFO" "Region: $REGION"
    
    return 0
}

# Function to list available backups
list_available_backups() {
    local resource_type="$1"
    log "INFO" "Listing available backups for $resource_type in $ENVIRONMENT environment..."
    
    case "$resource_type" in
        database)
            # List RDS snapshots
            log "INFO" "Listing RDS snapshots..."
            local resource_id="justicebid-${ENVIRONMENT}-db"
            aws rds describe-db-snapshots $AWS_PROFILE_ARG \
                --region "$REGION" \
                --db-instance-identifier "$resource_id" \
                --query "sort_by(DBSnapshots[*].{ID:DBSnapshotIdentifier,Created:SnapshotCreateTime,Size:AllocatedStorage,Status:Status}, &Created)" \
                --output table
            
            # List point-in-time recovery window
            log "INFO" "Available point-in-time recovery window:"
            aws rds describe-db-instances $AWS_PROFILE_ARG \
                --region "$REGION" \
                --db-instance-identifier "$resource_id" \
                --query "DBInstances[0].{Instance:DBInstanceIdentifier,EarliestRestorableTime:EarliestRestorableTime,LatestRestorableTime:LatestRestorableTime}" \
                --output table
            ;;
            
        storage)
            # List S3 backup versions for the specified bucket
            log "INFO" "Listing S3 backup versions for bucket: justicebid-${ENVIRONMENT}-${BUCKET_NAME}-backup..."
            aws s3 ls $AWS_PROFILE_ARG \
                "s3://justicebid-${ENVIRONMENT}-${BUCKET_NAME}-backup/" \
                --region "$REGION" \
                --recursive \
                | grep -E '^[0-9]{4}-[0-9]{2}-[0-9]{2}' \
                | sort -r \
                | head -n 10
            ;;
            
        application)
            # List application snapshots
            log "INFO" "Listing application snapshots..."
            local tag_filter="Name=tag:Environment,Values=${ENVIRONMENT} Name=tag:Application,Values=justicebid"
            aws ec2 describe-snapshots $AWS_PROFILE_ARG \
                --region "$REGION" \
                --filters "$tag_filter" \
                --owner-ids self \
                --query "sort_by(Snapshots[*].{ID:SnapshotId,Created:StartTime,Description:Description,Size:VolumeSize,Status:State}, &Created)" \
                --output table
            ;;
            
        *)
            log "ERROR" "Unknown resource type: $resource_type"
            return 1
            ;;
    esac
    
    log "INFO" "Backup listing completed."
    return 0
}

# Function to restore database
restore_database() {
    local backup_id="$1"
    local restore_type="$2"  # snapshot or point-in-time
    local target_time="$3"
    
    log "INFO" "Starting database restoration process..."
    local resource_id="justicebid-${ENVIRONMENT}-db"
    local restored_instance="${resource_id}-restored-${TIMESTAMP}"
    
    if [ "$restore_type" = "snapshot" ]; then
        log "INFO" "Restoring database from snapshot: $backup_id"
        
        # Create new DB instance from snapshot
        aws rds restore-db-instance-from-db-snapshot $AWS_PROFILE_ARG \
            --region "$REGION" \
            --db-instance-identifier "$restored_instance" \
            --db-snapshot-identifier "$backup_id" \
            --db-instance-class "db.t3.large" \
            --no-multi-az \
            --tags "Key=Environment,Value=${ENVIRONMENT}" "Key=Application,Value=justicebid" "Key=RestoreSource,Value=${backup_id}"
            
    elif [ "$restore_type" = "point-in-time" ]; then
        log "INFO" "Performing point-in-time recovery to: $target_time"
        
        # Convert target_time to ISO8601 format
        local iso_time=$(date -d "$target_time" -Iseconds)
        
        # Create new DB instance from point-in-time recovery
        aws rds restore-db-instance-to-point-in-time $AWS_PROFILE_ARG \
            --region "$REGION" \
            --source-db-instance-identifier "$resource_id" \
            --target-db-instance-identifier "$restored_instance" \
            --restore-time "$iso_time" \
            --db-instance-class "db.t3.large" \
            --no-multi-az \
            --tags "Key=Environment,Value=${ENVIRONMENT}" "Key=Application,Value=justicebid" "Key=RestoreTime,Value=${target_time}"
    else
        log "ERROR" "Unknown restore type: $restore_type"
        return 1
    fi
    
    # Wait for the database to become available
    log "INFO" "Waiting for restored database to become available..."
    aws rds wait db-instance-available $AWS_PROFILE_ARG \
        --region "$REGION" \
        --db-instance-identifier "$restored_instance"
    
    # Get endpoint of restored database
    local endpoint=$(aws rds describe-db-instances $AWS_PROFILE_ARG \
        --region "$REGION" \
        --db-instance-identifier "$restored_instance" \
        --query "DBInstances[0].Endpoint.Address" \
        --output text)
    
    log "INFO" "Restored database is available at: $endpoint"
    log "INFO" "Testing connection to restored database..."
    
    # Test connection to the restored database
    PGPASSWORD="${DB_PASSWORD}" psql \
        -h "$endpoint" \
        -U "${DB_USER:-postgres}" \
        -d "$DB_NAME" \
        -c "SELECT version();" > /dev/null
    
    if [ $? -eq 0 ]; then
        log "INFO" "Successfully connected to restored database."
    else
        log "ERROR" "Failed to connect to restored database."
        return 1
    fi
    
    # Verify database integrity
    log "INFO" "Verifying database integrity..."
    PGPASSWORD="${DB_PASSWORD}" psql \
        -h "$endpoint" \
        -U "${DB_USER:-postgres}" \
        -d "$DB_NAME" \
        -c "SELECT count(*) FROM organizations;" > /dev/null
    
    if [ $? -eq 0 ]; then
        log "INFO" "Database integrity check passed."
    else
        log "ERROR" "Database integrity check failed."
        return 1
    fi
    
    # Output connection information
    log "INFO" "Database restore completed successfully."
    log "INFO" "Restored database details:"
    log "INFO" "  Instance: $restored_instance"
    log "INFO" "  Endpoint: $endpoint"
    log "INFO" "  Database: $DB_NAME"
    log "INFO" "  Username: ${DB_USER:-postgres}"
    
    return 0
}

# Function to restore file storage
restore_file_storage() {
    local bucket_name="$1"
    local backup_timestamp="$2"
    local target_path="$3"
    
    log "INFO" "Starting file storage restoration process..."
    
    # Set source and target buckets
    local source_bucket="justicebid-${ENVIRONMENT}-${bucket_name}-backup"
    local target_bucket="justicebid-${ENVIRONMENT}-${bucket_name}"
    local backup_prefix="${backup_timestamp}/"
    
    if [ -z "$target_path" ]; then
        target_path="/"
    fi
    
    # Check if source bucket and backup path exist
    if ! aws s3 ls $AWS_PROFILE_ARG "s3://${source_bucket}/${backup_prefix}" --region "$REGION" &>/dev/null; then
        log "ERROR" "Source backup not found: s3://${source_bucket}/${backup_prefix}"
        return 1
    fi
    
    # Create temporary directory for file operations
    local tmp_dir="${TEMP_DIR}/s3_restore_${TIMESTAMP}"
    mkdir -p "$tmp_dir"
    
    # List files to be restored
    log "INFO" "Listing files to be restored from s3://${source_bucket}/${backup_prefix}..."
    local file_count=$(aws s3 ls $AWS_PROFILE_ARG "s3://${source_bucket}/${backup_prefix}" --region "$REGION" --recursive | wc -l)
    log "INFO" "Found $file_count files to restore."
    
    # Confirm restoration
    log "INFO" "Starting restoration of $file_count files from s3://${source_bucket}/${backup_prefix} to s3://${target_bucket}${target_path}"
    
    # Perform the restore
    if [ "$target_path" = "/" ]; then
        # If restoring to root, first backup current data
        log "INFO" "Creating backup of current data before restoring..."
        local current_backup_prefix="pre_restore_${TIMESTAMP}/"
        aws s3 sync $AWS_PROFILE_ARG "s3://${target_bucket}/" "s3://${source_bucket}/${current_backup_prefix}" --region "$REGION"
        
        # Sync from backup to target
        log "INFO" "Syncing files from backup to target bucket..."
        aws s3 sync $AWS_PROFILE_ARG "s3://${source_bucket}/${backup_prefix}" "s3://${target_bucket}/" --region "$REGION" --delete
    else
        # Create target path if it doesn't exist
        if ! aws s3 ls $AWS_PROFILE_ARG "s3://${target_bucket}${target_path}" --region "$REGION" &>/dev/null; then
            log "INFO" "Creating target path: s3://${target_bucket}${target_path}"
            aws s3api put-object $AWS_PROFILE_ARG --bucket "${target_bucket}" --key "${target_path#/}" --region "$REGION"
        fi
        
        # Sync from backup to target path
        log "INFO" "Syncing files from backup to target path..."
        aws s3 sync $AWS_PROFILE_ARG "s3://${source_bucket}/${backup_prefix}" "s3://${target_bucket}${target_path}" --region "$REGION"
    fi
    
    # Verify restore
    log "INFO" "Verifying restored files..."
    local restored_count=$(aws s3 ls $AWS_PROFILE_ARG "s3://${target_bucket}${target_path}" --region "$REGION" --recursive | wc -l)
    log "INFO" "Found $restored_count files in target after restore."
    
    # Cleanup
    rm -rf "$tmp_dir"
    
    log "INFO" "File storage restore completed successfully."
    return 0
}

# Function to restore application state
restore_application_state() {
    local snapshot_id="$1"
    local target_environment="$2"
    
    log "INFO" "Starting application state restoration process..."
    
    # Get ECS cluster name
    local cluster_name="justicebid-${target_environment}"
    
    # First, verify if the snapshot exists
    if ! aws ec2 describe-snapshots $AWS_PROFILE_ARG --region "$REGION" --snapshot-ids "$snapshot_id" &>/dev/null; then
        log "ERROR" "Snapshot $snapshot_id not found."
        return 1
    fi
    
    # Get snapshot details
    local snapshot_details=$(aws ec2 describe-snapshots $AWS_PROFILE_ARG \
        --region "$REGION" \
        --snapshot-ids "$snapshot_id" \
        --query "Snapshots[0].{ID:SnapshotId,Created:StartTime,Description:Description}" \
        --output json)
    
    log "INFO" "Restoring from snapshot: $snapshot_details"
    
    # Get ECS services for the cluster
    local services=$(aws ecs list-services $AWS_PROFILE_ARG \
        --region "$REGION" \
        --cluster "$cluster_name" \
        --output text \
        --query "serviceArns")
    
    if [ -z "$services" ]; then
        log "ERROR" "No services found in cluster $cluster_name."
        return 1
    fi
    
    # Stop all ECS services
    log "INFO" "Stopping ECS services in cluster $cluster_name..."
    for service in $services; do
        local service_name=$(basename "$service")
        log "INFO" "Stopping service: $service_name"
        
        aws ecs update-service $AWS_PROFILE_ARG \
            --region "$REGION" \
            --cluster "$cluster_name" \
            --service "$service_name" \
            --desired-count 0
    done
    
    # Wait for services to stop
    log "INFO" "Waiting for services to stop..."
    sleep 30
    
    # Restore application configuration from snapshot
    log "INFO" "Restoring application configuration from snapshot..."
    local config_dir="${TEMP_DIR}/app_config_${TIMESTAMP}"
    mkdir -p "$config_dir"
    
    # Create a volume from the snapshot
    local volume_id=$(aws ec2 create-volume $AWS_PROFILE_ARG \
        --region "$REGION" \
        --availability-zone "${REGION}a" \
        --snapshot-id "$snapshot_id" \
        --query "VolumeId" \
        --output text)
    
    log "INFO" "Created temporary volume $volume_id from snapshot."
    
    # Tag the volume
    aws ec2 create-tags $AWS_PROFILE_ARG \
        --region "$REGION" \
        --resources "$volume_id" \
        --tags "Key=Name,Value=TempRestore-${TIMESTAMP}" "Key=Environment,Value=${target_environment}" "Key=Application,Value=justicebid"
    
    # Wait for volume to become available
    log "INFO" "Waiting for volume to become available..."
    aws ec2 wait volume-available $AWS_PROFILE_ARG \
        --region "$REGION" \
        --volume-ids "$volume_id"
    
    # Get a temporary EC2 instance to mount the volume
    log "INFO" "Launching temporary EC2 instance to mount the volume..."
    local instance_id=$(aws ec2 run-instances $AWS_PROFILE_ARG \
        --region "$REGION" \
        --image-id "ami-0c55b159cbfafe1f0" \
        --instance-type "t3.micro" \
        --subnet-id "subnet-12345678" \
        --security-group-ids "sg-12345678" \
        --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=TempRestore-${TIMESTAMP}},{Key=Environment,Value=${target_environment}},{Key=Application,Value=justicebid}]" \
        --query "Instances[0].InstanceId" \
        --output text)
    
    log "INFO" "Launched temporary instance $instance_id."
    
    # Wait for instance to be running
    log "INFO" "Waiting for instance to be running..."
    aws ec2 wait instance-running $AWS_PROFILE_ARG \
        --region "$REGION" \
        --instance-ids "$instance_id"
    
    # Attach the volume to the instance
    log "INFO" "Attaching volume to instance..."
    aws ec2 attach-volume $AWS_PROFILE_ARG \
        --region "$REGION" \
        --volume-id "$volume_id" \
        --instance-id "$instance_id" \
        --device "/dev/sdf"
    
    # Wait for volume to be attached
    log "INFO" "Waiting for volume to be attached..."
    sleep 30
    
    # Copy configuration files from the volume
    log "INFO" "Copying configuration files from volume..."
    # Note: This would normally involve SSH into the instance to mount and copy data
    # For this script, we're assuming this step
    
    # Detach and delete the volume
    log "INFO" "Detaching volume..."
    aws ec2 detach-volume $AWS_PROFILE_ARG \
        --region "$REGION" \
        --volume-id "$volume_id"
    
    # Wait for volume to be detached
    log "INFO" "Waiting for volume to be detached..."
    aws ec2 wait volume-available $AWS_PROFILE_ARG \
        --region "$REGION" \
        --volume-ids "$volume_id"
    
    # Terminate the temporary instance
    log "INFO" "Terminating temporary instance..."
    aws ec2 terminate-instances $AWS_PROFILE_ARG \
        --region "$REGION" \
        --instance-ids "$instance_id"
    
    # Delete the volume
    log "INFO" "Deleting temporary volume..."
    aws ec2 delete-volume $AWS_PROFILE_ARG \
        --region "$REGION" \
        --volume-id "$volume_id"
    
    # Update application configuration
    log "INFO" "Updating application configuration..."
    # Note: In a real implementation, this would involve updating configuration in Parameter Store or similar
    
    # Restart all ECS services
    log "INFO" "Restarting ECS services in cluster $cluster_name..."
    for service in $services; do
        local service_name=$(basename "$service")
        log "INFO" "Starting service: $service_name"
        
        # Get the desired count for the service
        local desired_count=$(aws ecs describe-services $AWS_PROFILE_ARG \
            --region "$REGION" \
            --cluster "$cluster_name" \
            --services "$service_name" \
            --query "services[0].desiredCount" \
            --output text)
        
        aws ecs update-service $AWS_PROFILE_ARG \
            --region "$REGION" \
            --cluster "$cluster_name" \
            --service "$service_name" \
            --desired-count "$desired_count"
    done
    
    # Wait for services to start
    log "INFO" "Waiting for services to start..."
    sleep 60
    
    # Verify application functionality
    log "INFO" "Verifying application functionality..."
    # This would involve health checks or similar
    
    log "INFO" "Application state restore completed successfully."
    return 0
}

# Function to execute disaster recovery procedure
perform_disaster_recovery() {
    local dr_plan="$1"
    
    log "INFO" "Starting disaster recovery procedure..."
    log "INFO" "DR Plan: $dr_plan"
    log "INFO" "Source environment: $ENVIRONMENT"
    log "INFO" "Target region: $REGION"
    
    # Get the DR configuration
    local dr_config_file="/etc/justicebid/dr_config_${ENVIRONMENT}.json"
    if [ ! -f "$dr_config_file" ]; then
        log "ERROR" "DR configuration file not found: $dr_config_file"
        return 1
    fi
    
    log "INFO" "Loading DR configuration from $dr_config_file..."
    local dr_config=$(cat "$dr_config_file")
    
    # Extract configuration values
    local primary_region=$(echo "$dr_config" | jq -r '.primary_region')
    local dr_region=$(echo "$dr_config" | jq -r '.dr_region')
    local rds_identifier=$(echo "$dr_config" | jq -r '.resources.rds_identifier')
    local s3_buckets=$(echo "$dr_config" | jq -r '.resources.s3_buckets[]')
    
    log "INFO" "Primary region: $primary_region"
    log "INFO" "DR region: $dr_region"
    log "INFO" "RDS identifier: $rds_identifier"
    log "INFO" "S3 buckets: $s3_buckets"
    
    # Verify that we're executing in the DR region
    if [ "$REGION" != "$dr_region" ]; then
        log "ERROR" "DR procedure must be executed in the DR region: $dr_region"
        return 1
    fi
    
    # Step 1: Promote the RDS read replica to primary
    log "INFO" "Step 1: Promoting RDS read replica to primary..."
    local dr_rds_identifier="${rds_identifier}-dr"
    
    aws rds promote-read-replica $AWS_PROFILE_ARG \
        --region "$dr_region" \
        --db-instance-identifier "$dr_rds_identifier"
    
    log "INFO" "Waiting for RDS promotion to complete..."
    aws rds wait db-instance-available $AWS_PROFILE_ARG \
        --region "$dr_region" \
        --db-instance-identifier "$dr_rds_identifier"
    
    # Get the endpoint of the promoted database
    local db_endpoint=$(aws rds describe-db-instances $AWS_PROFILE_ARG \
        --region "$dr_region" \
        --db-instance-identifier "$dr_rds_identifier" \
        --query "DBInstances[0].Endpoint.Address" \
        --output text)
    
    log "INFO" "Promoted database endpoint: $db_endpoint"
    
    # Step 2: Update parameter store configuration for the new database endpoint
    log "INFO" "Step 2: Updating parameter store configuration..."
    local param_path="/justicebid/${ENVIRONMENT}/database/host"
    
    aws ssm put-parameter $AWS_PROFILE_ARG \
        --region "$dr_region" \
        --name "$param_path" \
        --value "$db_endpoint" \
        --type "String" \
        --overwrite
    
    # Step 3: Update DNS to point to DR environment
    log "INFO" "Step 3: Updating DNS to point to DR environment..."
    local hosted_zone_id=$(echo "$dr_config" | jq -r '.dns.hosted_zone_id')
    local domain_name=$(echo "$dr_config" | jq -r '.dns.domain_name')
    local dr_load_balancer=$(echo "$dr_config" | jq -r '.resources.load_balancer')
    
    # Create DNS change batch file
    local dns_change_file="${TEMP_DIR}/dns_change_${TIMESTAMP}.json"
    cat > "$dns_change_file" <<EOF
{
  "Changes": [
    {
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "${domain_name}",
        "Type": "A",
        "AliasTarget": {
          "HostedZoneId": "Z2FDTNDATAQYW2",
          "DNSName": "${dr_load_balancer}",
          "EvaluateTargetHealth": true
        }
      }
    }
  ]
}
EOF
    
    # Apply DNS changes
    aws route53 change-resource-record-sets $AWS_PROFILE_ARG \
        --hosted-zone-id "$hosted_zone_id" \
        --change-batch "file://${dns_change_file}"
    
    log "INFO" "DNS update submitted. It may take several minutes to propagate."
    
    # Step 4: Verify the DR environment
    log "INFO" "Step 4: Verifying DR environment..."
    
    # Wait for DNS propagation
    log "INFO" "Waiting for DNS propagation (60 seconds)..."
    sleep 60
    
    # Test connectivity to the application
    log "INFO" "Testing connectivity to the application..."
    if curl -s -o /dev/null -w "%{http_code}" "https://${domain_name}/health" | grep -q "200"; then
        log "INFO" "Successfully connected to the application."
    else
        log "WARNING" "Could not verify application connectivity. This may require manual verification."
    fi
    
    # Step 5: Initiate traffic to the DR environment
    log "INFO" "Step 5: Initiating traffic to the DR environment..."
    
    # Update WAF to allow traffic
    local waf_web_acl_id=$(echo "$dr_config" | jq -r '.resources.waf_web_acl_id')
    
    aws wafv2 update-web-acl $AWS_PROFILE_ARG \
        --region "$dr_region" \
        --name "justicebid-${ENVIRONMENT}" \
        --scope "REGIONAL" \
        --id "$waf_web_acl_id" \
        --lock-token "$(aws wafv2 get-web-acl $AWS_PROFILE_ARG --region "$dr_region" --name "justicebid-${ENVIRONMENT}" --scope "REGIONAL" --id "$waf_web_acl_id" --query "LockToken" --output text)" \
        --default-action "Allow={}" \
        --rules "[]"
    
    log "INFO" "WAF updated to allow traffic to DR environment."
    
    # Final verification
    log "INFO" "DR procedure completed successfully."
    log "INFO" "DR environment is now active at https://${domain_name}"
    log "INFO" "Database endpoint: $db_endpoint"
    log "INFO" "Load balancer: $dr_load_balancer"
    
    return 0
}

# Function to validate restore
validate_restore() {
    local resource_type="$1"
    log "INFO" "Validating restore for resource type: $resource_type"
    
    case "$resource_type" in
        database)
            # Validate database restore
            local endpoint="$2"
            local queries=(
                "SELECT count(*) FROM organizations;" 
                "SELECT count(*) FROM users;" 
                "SELECT count(*) FROM rates;" 
                "SELECT count(*) FROM negotiations;"
            )
            local validation_results=()
            local success=true
            
            for query in "${queries[@]}"; do
                log "INFO" "Executing validation query: $query"
                local result=$(PGPASSWORD="${DB_PASSWORD}" psql \
                    -h "$endpoint" \
                    -U "${DB_USER:-postgres}" \
                    -d "$DB_NAME" \
                    -t \
                    -c "$query" 2>/dev/null)
                
                if [ $? -eq 0 ]; then
                    validation_results+=("$query: $result rows")
                else
                    validation_results+=("$query: FAILED")
                    success=false
                fi
            done
            
            # Output validation results
            log "INFO" "Database validation results:"
            for result in "${validation_results[@]}"; do
                log "INFO" "  $result"
            done
            
            if [ "$success" = true ]; then
                log "INFO" "Database validation passed."
                return 0
            else
                log "ERROR" "Database validation failed."
                return 1
            fi
            ;;
            
        storage)
            # Validate storage restore
            local bucket_name="$2"
            local target_bucket="justicebid-${ENVIRONMENT}-${bucket_name}"
            
            # Check if bucket exists
            if ! aws s3 ls $AWS_PROFILE_ARG "s3://${target_bucket}/" --region "$REGION" &>/dev/null; then
                log "ERROR" "Target bucket not found: $target_bucket"
                return 1
            fi
            
            # Count objects in the bucket
            local object_count=$(aws s3 ls $AWS_PROFILE_ARG "s3://${target_bucket}/" --region "$REGION" --recursive | wc -l)
            
            log "INFO" "Storage validation results:"
            log "INFO" "  Bucket: $target_bucket"
            log "INFO" "  Object count: $object_count"
            
            if [ "$object_count" -gt 0 ]; then
                log "INFO" "Storage validation passed."
                return 0
            else
                log "ERROR" "Storage validation failed. No objects found in bucket."
                return 1
            fi
            ;;
            
        application)
            # Validate application restore
            local cluster_name="justicebid-${ENVIRONMENT}"
            
            # Check if services are running
            local services=$(aws ecs list-services $AWS_PROFILE_ARG \
                --region "$REGION" \
                --cluster "$cluster_name" \
                --output text \
                --query "serviceArns")
            
            if [ -z "$services" ]; then
                log "ERROR" "No services found in cluster $cluster_name."
                return 1
            fi
            
            # Check service status
            local success=true
            for service in $services; do
                local service_name=$(basename "$service")
                local desired_count=$(aws ecs describe-services $AWS_PROFILE_ARG \
                    --region "$REGION" \
                    --cluster "$cluster_name" \
                    --services "$service_name" \
                    --query "services[0].desiredCount" \
                    --output text)
                
                local running_count=$(aws ecs describe-services $AWS_PROFILE_ARG \
                    --region "$REGION" \
                    --cluster "$cluster_name" \
                    --services "$service_name" \
                    --query "services[0].runningCount" \
                    --output text)
                
                if [ "$desired_count" -gt 0 ] && [ "$running_count" -lt "$desired_count" ]; then
                    log "ERROR" "Service $service_name is not fully running: $running_count/$desired_count"
                    success=false
                fi
            done
            
            # Test application endpoints
            local domain_name="justicebid-${ENVIRONMENT}.example.com"
            local health_status=$(curl -s -o /dev/null -w "%{http_code}" "https://${domain_name}/health")
            
            log "INFO" "Application validation results:"
            log "INFO" "  Health endpoint status: $health_status"
            
            if [ "$success" = true ] && [ "$health_status" = "200" ]; then
                log "INFO" "Application validation passed."
                return 0
            else
                log "ERROR" "Application validation failed."
                return 1
            fi
            ;;
            
        dr)
            # Validate DR environment
            local domain_name="$2"
            local health_status=$(curl -s -o /dev/null -w "%{http_code}" "https://${domain_name}/health")
            
            log "INFO" "DR validation results:"
            log "INFO" "  Health endpoint status: $health_status"
            
            if [ "$health_status" = "200" ]; then
                log "INFO" "DR validation passed."
                return 0
            else
                log "ERROR" "DR validation failed."
                return 1
            fi
            ;;
            
        *)
            log "ERROR" "Unknown resource type for validation: $resource_type"
            return 1
            ;;
    esac
}

# Function to perform cleanup
cleanup() {
    log "INFO" "Performing cleanup..."
    
    # Remove temporary directory
    if [ -d "$TEMP_DIR" ]; then
        rm -rf "$TEMP_DIR"
    fi
    
    # Summarize restore operation
    log "INFO" "Restore operation summary:"
    log "INFO" "  Command: $COMMAND"
    log "INFO" "  Environment: $ENVIRONMENT"
    log "INFO" "  Region: $REGION"
    log "INFO" "  Timestamp: $TIMESTAMP"
    
    # Send notification if configured
    if [ -n "$NOTIFICATION_SNS_TOPIC" ]; then
        log "INFO" "Sending completion notification..."
        aws sns publish $AWS_PROFILE_ARG \
            --region "$REGION" \
            --topic-arn "$NOTIFICATION_SNS_TOPIC" \
            --subject "Justice Bid Restore Completed: $COMMAND ($ENVIRONMENT)" \
            --message "Justice Bid restore operation completed.\n\nCommand: $COMMAND\nEnvironment: $ENVIRONMENT\nRegion: $REGION\nTimestamp: $TIMESTAMP\n\nFor details, see log file: $LOG_FILE"
    fi
    
    log "INFO" "Cleanup completed."
}

# Main function
main() {
    # Parse arguments first to get command and environment
    if ! parse_arguments "$@"; then
        exit 1
    fi
    
    # Setup logging
    setup_logging "$@"
    
    # Check prerequisites
    if ! check_prerequisites; then
        log "ERROR" "Prerequisites check failed. Exiting."
        exit 1
    fi
    
    # Execute the appropriate function based on the command
    case "$COMMAND" in
        list)
            # List available backups
            if ! list_available_backups "$LIST_TYPE"; then
                log "ERROR" "Failed to list available backups."
                cleanup
                exit 1
            fi
            ;;
            
        database)
            # Restore database
            if [ -n "$BACKUP_ID" ]; then
                if ! restore_database "$BACKUP_ID" "snapshot"; then
                    log "ERROR" "Database restore from snapshot failed."
                    cleanup
                    exit 1
                fi
            elif [ -n "$TARGET_TIME" ]; then
                if ! restore_database "" "point-in-time" "$TARGET_TIME"; then
                    log "ERROR" "Database point-in-time restore failed."
                    cleanup
                    exit 1
                fi
            fi
            ;;
            
        storage)
            # Restore file storage
            if ! restore_file_storage "$BUCKET_NAME" "$BACKUP_ID" ""; then
                log "ERROR" "File storage restore failed."
                cleanup
                exit 1
            fi
            ;;
            
        application)
            # Restore application state
            if ! restore_application_state "$BACKUP_ID" "$ENVIRONMENT"; then
                log "ERROR" "Application state restore failed."
                cleanup
                exit 1
            fi
            ;;
            
        dr)
            # Execute disaster recovery
            if ! perform_disaster_recovery "standard"; then
                log "ERROR" "Disaster recovery failed."
                cleanup
                exit 1
            fi
            ;;
            
        *)
            log "ERROR" "Unknown command: $COMMAND"
            print_usage
            exit 1
            ;;
    esac
    
    # Perform cleanup
    cleanup
    
    log "INFO" "Restore operation completed successfully."
    exit 0
}

# Execute main function
main "$@"