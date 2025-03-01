#!/usr/bin/env bash
#
# backup.sh - Comprehensive backup script for Justice Bid Rate Negotiation System
#
# This script performs comprehensive backups including database, storage,
# configuration, and application state according to the defined backup strategy.
# 
# Dependencies:
# - AWS CLI v2.x
# - PostgreSQL Client v14.x
# - jq v1.6+
#
# Usage:
#   ./backup.sh [options]
#
# Options:
#   --type=TYPE     Backup type (full, incremental, or all). Default: determined by schedule
#   --component=COMPONENT   Component to backup (database, storage, config, state, or all). Default: all
#   --config=FILE   Path to config file. Default: ../backup-config.json
#   --dry-run       Perform a dry run without making changes
#   --no-notify     Disable notifications
#   --help          Display this help message

set -e
set -o pipefail

# Global variables
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
CONFIG_FILE="${SCRIPT_DIR}/../backup-config.json"
LOG_DIR="${SCRIPT_DIR}/../logs"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_ROOT="/backup"
DRY_RUN=false
NOTIFY=true
BACKUP_TYPE=""
BACKUP_COMPONENT="all"
EXIT_CODE=0
START_TIME=$(date +%s)

# Color codes for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to log messages
log_message() {
    local level="$1"
    local message="$2"
    local log_file="${LOG_DIR}/backup_$(date +"%Y%m%d").log"
    local formatted_message="[$(date +"%Y-%m-%d %H:%M:%S")] [${level}] ${message}"
    
    # Create log directory if it doesn't exist
    mkdir -p "${LOG_DIR}"
    
    # Output to console with color
    case "${level}" in
        "INFO")
            echo -e "${BLUE}${formatted_message}${NC}"
            ;;
        "SUCCESS")
            echo -e "${GREEN}${formatted_message}${NC}"
            ;;
        "WARNING")
            echo -e "${YELLOW}${formatted_message}${NC}"
            ;;
        "ERROR")
            echo -e "${RED}${formatted_message}${NC}"
            ;;
        *)
            echo -e "${formatted_message}"
            ;;
    esac
    
    # Append to log file
    echo "${formatted_message}" >> "${log_file}"
}

# Function to load configuration
load_config() {
    if [[ ! -f "${CONFIG_FILE}" ]]; then
        log_message "ERROR" "Configuration file not found: ${CONFIG_FILE}"
        exit 1
    fi
    
    # Check if jq is installed
    if ! command -v jq &> /dev/null; then
        log_message "ERROR" "jq is required but not installed. Please install jq."
        exit 1
    fi
    
    # Parse and validate config file
    local config
    if ! config=$(jq '.' "${CONFIG_FILE}" 2>/dev/null); then
        log_message "ERROR" "Failed to parse configuration file: ${CONFIG_FILE}"
        exit 1
    fi
    
    # Validate required configuration parameters
    local required_params=("database" "s3_storage" "configurations" "application_state" "retention_policy" "notification")
    for param in "${required_params[@]}"; do
        if [[ $(jq -r "has(\"${param}\")" <<< "${config}") != "true" ]]; then
            log_message "ERROR" "Missing required configuration parameter: ${param}"
            exit 1
        fi
    done
    
    echo "${config}"
}

# Function to perform database backup
backup_database() {
    local config="$1"
    local success=true
    
    log_message "INFO" "Starting database backup..."
    
    # Extract database connection parameters
    local db_host=$(jq -r '.database.host' <<< "${config}")
    local db_port=$(jq -r '.database.port' <<< "${config}")
    local db_name=$(jq -r '.database.name' <<< "${config}")
    local db_user=$(jq -r '.database.user' <<< "${config}")
    local db_password_secret=$(jq -r '.database.password_secret' <<< "${config}")
    local s3_bucket=$(jq -r '.database.s3_bucket' <<< "${config}")
    local s3_prefix=$(jq -r '.database.s3_prefix' <<< "${config}")
    
    # Get DB password from AWS Secrets Manager
    local db_password
    if [[ -n "${db_password_secret}" ]]; then
        if ! db_password=$(aws secretsmanager get-secret-value --secret-id "${db_password_secret}" --query 'SecretString' --output text 2>/dev/null | jq -r '.password'); then
            log_message "ERROR" "Failed to retrieve database password from Secrets Manager"
            return 1
        fi
    else
        log_message "ERROR" "Database password secret not specified in config"
        return 1
    fi
    
    # Determine backup type (full or incremental) based on day of week and hour
    # if not explicitly specified
    local day_of_week=$(date +"%u") # 1-7, 1 is Monday
    local hour=$(date +"%H")
    
    if [[ -z "${BACKUP_TYPE}" ]]; then
        # Sunday full backup, or first hour of each day
        if [[ "${day_of_week}" -eq 7 ]] || [[ "${hour}" -eq 0 ]]; then
            BACKUP_TYPE="full"
        else
            BACKUP_TYPE="incremental"
        fi
    fi
    
    # Create backup directory
    local backup_dir="${BACKUP_ROOT}/database/${TIMESTAMP}"
    local backup_file="${backup_dir}/${db_name}_${BACKUP_TYPE}_${TIMESTAMP}.sql"
    local compressed_file="${backup_file}.gz"
    
    if [[ "${DRY_RUN}" = false ]]; then
        mkdir -p "${backup_dir}"
        
        # Set PGPASSWORD environment variable for authentication
        export PGPASSWORD="${db_password}"
        
        # Perform backup based on type
        if [[ "${BACKUP_TYPE}" = "full" ]]; then
            log_message "INFO" "Performing full database backup..."
            
            if ! pg_dump -h "${db_host}" -p "${db_port}" -U "${db_user}" -d "${db_name}" -f "${backup_file}" --verbose; then
                log_message "ERROR" "Full database backup failed"
                success=false
            else
                log_message "SUCCESS" "Full database backup completed successfully"
                
                # Compress the backup file
                if ! gzip -9 "${backup_file}"; then
                    log_message "ERROR" "Failed to compress database backup"
                    success=false
                else
                    log_message "INFO" "Database backup compressed successfully"
                fi
                
                # Upload to S3
                if ! aws s3 cp "${compressed_file}" "s3://${s3_bucket}/${s3_prefix}/full/${TIMESTAMP}/$(basename "${compressed_file}")"; then
                    log_message "ERROR" "Failed to upload database backup to S3"
                    success=false
                else
                    log_message "SUCCESS" "Database backup uploaded to S3 successfully"
                fi
            fi
        elif [[ "${BACKUP_TYPE}" = "incremental" ]]; then
            log_message "INFO" "Performing incremental database backup..."
            
            # For PostgreSQL, we can use WAL archiving
            # Here we'll simulate an incremental backup with a partial pg_dump
            # In a real scenario, you'd configure WAL archiving or use a tool like pgBackRest
            
            # Get the latest transaction ID for this incremental backup
            local last_xid
            if ! last_xid=$(psql -h "${db_host}" -p "${db_port}" -U "${db_user}" -d "${db_name}" -t -c "SELECT pg_current_xlog_location();" 2>/dev/null); then
                log_message "ERROR" "Failed to get current transaction ID"
                success=false
            else
                log_message "INFO" "Current transaction ID: ${last_xid}"
                
                # For this example, we'll just do a schema-only backup as a simplified "incremental"
                if ! pg_dump -h "${db_host}" -p "${db_port}" -U "${db_user}" -d "${db_name}" -f "${backup_file}" --verbose --schema-only; then
                    log_message "ERROR" "Incremental database backup failed"
                    success=false
                else
                    log_message "SUCCESS" "Incremental database backup completed successfully"
                    
                    # Add transaction ID to backup metadata
                    echo "LAST_XID=${last_xid}" > "${backup_dir}/backup_metadata.txt"
                    
                    # Compress the backup file
                    if ! gzip -9 "${backup_file}"; then
                        log_message "ERROR" "Failed to compress database backup"
                        success=false
                    else
                        log_message "INFO" "Database backup compressed successfully"
                    fi
                    
                    # Compress metadata
                    if ! gzip -9 "${backup_dir}/backup_metadata.txt"; then
                        log_message "WARNING" "Failed to compress backup metadata"
                    fi
                    
                    # Upload to S3
                    if ! aws s3 cp "${backup_dir}" "s3://${s3_bucket}/${s3_prefix}/incremental/${TIMESTAMP}/" --recursive; then
                        log_message "ERROR" "Failed to upload incremental database backup to S3"
                        success=false
                    else
                        log_message "SUCCESS" "Incremental database backup uploaded to S3 successfully"
                    fi
                fi
            fi
        else
            log_message "ERROR" "Unknown backup type: ${BACKUP_TYPE}"
            success=false
        fi
        
        # Clear PGPASSWORD
        unset PGPASSWORD
        
        # Apply retention policy
        apply_retention_policy "${config}" "database" "${BACKUP_ROOT}/database"
        
        # Generate checksum for backup integrity verification
        if [[ -f "${compressed_file}" ]]; then
            sha256sum "${compressed_file}" > "${compressed_file}.sha256"
            log_message "INFO" "Generated checksum for backup integrity verification"
        fi
    else
        log_message "INFO" "DRY RUN: Would perform ${BACKUP_TYPE} database backup to ${backup_dir}"
        log_message "INFO" "DRY RUN: Would upload to s3://${s3_bucket}/${s3_prefix}/${BACKUP_TYPE}/${TIMESTAMP}/"
    fi
    
    if [[ "${success}" = true ]]; then
        log_message "SUCCESS" "Database backup process completed successfully"
        return 0
    else
        log_message "ERROR" "Database backup process failed"
        return 1
    fi
}

# Function to backup S3 storage
backup_s3_storage() {
    local config="$1"
    local success=true
    
    log_message "INFO" "Starting S3 storage backup..."
    
    # Extract S3 backup configuration
    local buckets=($(jq -r '.s3_storage.buckets[]' <<< "${config}"))
    local backup_bucket=$(jq -r '.s3_storage.backup_bucket' <<< "${config}")
    
    if [[ "${DRY_RUN}" = false ]]; then
        for bucket in "${buckets[@]}"; do
            log_message "INFO" "Backing up S3 bucket: ${bucket}"
            
            # Create a prefix for this backup
            local prefix="${bucket}/${TIMESTAMP}"
            
            # Sync bucket to backup location
            if ! aws s3 sync "s3://${bucket}" "s3://${backup_bucket}/${prefix}" --only-show-errors; then
                log_message "ERROR" "Failed to backup S3 bucket: ${bucket}"
                success=false
            else
                log_message "SUCCESS" "S3 bucket backup completed successfully: ${bucket}"
                
                # Generate inventory report for the backup
                if ! aws s3 ls "s3://${backup_bucket}/${prefix}" --recursive | awk '{print $4}' > "/tmp/${bucket}_inventory_${TIMESTAMP}.txt"; then
                    log_message "WARNING" "Failed to generate inventory report for bucket: ${bucket}"
                else
                    # Upload inventory report
                    if ! aws s3 cp "/tmp/${bucket}_inventory_${TIMESTAMP}.txt" "s3://${backup_bucket}/${prefix}_inventory.txt"; then
                        log_message "WARNING" "Failed to upload inventory report for bucket: ${bucket}"
                    else
                        log_message "INFO" "Uploaded inventory report for bucket: ${bucket}"
                    fi
                    
                    # Clean up local inventory file
                    rm -f "/tmp/${bucket}_inventory_${TIMESTAMP}.txt"
                fi
            fi
        done
        
        # Apply retention policy for S3 backups
        apply_retention_policy "${config}" "s3_storage" "s3://${backup_bucket}"
    else
        log_message "INFO" "DRY RUN: Would backup S3 buckets: ${buckets[*]}"
        log_message "INFO" "DRY RUN: Would store backups in: s3://${backup_bucket}"
    fi
    
    if [[ "${success}" = true ]]; then
        log_message "SUCCESS" "S3 storage backup process completed successfully"
        return 0
    else
        log_message "ERROR" "S3 storage backup process failed"
        return 1
    fi
}

# Function to backup configurations
backup_configurations() {
    local config="$1"
    local success=true
    
    log_message "INFO" "Starting configuration backup..."
    
    # Extract configuration backup settings
    local terraform_state_path=$(jq -r '.configurations.terraform_state_path' <<< "${config}")
    local kubernetes_config_path=$(jq -r '.configurations.kubernetes_config_path' <<< "${config}")
    local config_files_path=$(jq -r '.configurations.config_files_path' <<< "${config}")
    local s3_bucket=$(jq -r '.configurations.s3_bucket' <<< "${config}")
    local s3_prefix=$(jq -r '.configurations.s3_prefix' <<< "${config}")
    
    # Create local backup directory
    local backup_dir="${BACKUP_ROOT}/configurations/${TIMESTAMP}"
    
    if [[ "${DRY_RUN}" = false ]]; then
        mkdir -p "${backup_dir}"
        
        # Backup Terraform state
        if [[ -d "${terraform_state_path}" ]]; then
            log_message "INFO" "Backing up Terraform state from: ${terraform_state_path}"
            
            local tf_backup_file="${backup_dir}/terraform_state_${TIMESTAMP}.tar.gz"
            if ! tar -czf "${tf_backup_file}" -C "$(dirname "${terraform_state_path}")" "$(basename "${terraform_state_path}")"; then
                log_message "ERROR" "Failed to backup Terraform state"
                success=false
            else
                log_message "SUCCESS" "Terraform state backup completed successfully"
            fi
        else
            log_message "WARNING" "Terraform state path not found: ${terraform_state_path}"
        fi
        
        # Backup Kubernetes configurations
        if [[ -d "${kubernetes_config_path}" ]]; then
            log_message "INFO" "Backing up Kubernetes configurations from: ${kubernetes_config_path}"
            
            local k8s_backup_file="${backup_dir}/kubernetes_config_${TIMESTAMP}.tar.gz"
            if ! tar -czf "${k8s_backup_file}" -C "$(dirname "${kubernetes_config_path}")" "$(basename "${kubernetes_config_path}")"; then
                log_message "ERROR" "Failed to backup Kubernetes configurations"
                success=false
            else
                log_message "SUCCESS" "Kubernetes configurations backup completed successfully"
            fi
            
            # Additionally export key Kubernetes resources
            if command -v kubectl &> /dev/null; then
                log_message "INFO" "Exporting Kubernetes resources..."
                
                mkdir -p "${backup_dir}/kubernetes_resources"
                
                # Export all namespaces
                if ! kubectl get namespaces -o yaml > "${backup_dir}/kubernetes_resources/namespaces.yaml"; then
                    log_message "WARNING" "Failed to export Kubernetes namespaces"
                fi
                
                # Export all deployments across all namespaces
                if ! kubectl get deployments --all-namespaces -o yaml > "${backup_dir}/kubernetes_resources/deployments.yaml"; then
                    log_message "WARNING" "Failed to export Kubernetes deployments"
                fi
                
                # Export all services across all namespaces
                if ! kubectl get services --all-namespaces -o yaml > "${backup_dir}/kubernetes_resources/services.yaml"; then
                    log_message "WARNING" "Failed to export Kubernetes services"
                fi
                
                # Export all configmaps across all namespaces
                if ! kubectl get configmaps --all-namespaces -o yaml > "${backup_dir}/kubernetes_resources/configmaps.yaml"; then
                    log_message "WARNING" "Failed to export Kubernetes configmaps"
                fi
                
                # Export all secrets across all namespaces (sensitive data)
                if ! kubectl get secrets --all-namespaces -o yaml > "${backup_dir}/kubernetes_resources/secrets.yaml"; then
                    log_message "WARNING" "Failed to export Kubernetes secrets"
                fi
                
                # Export Helm releases if Helm is installed
                if command -v helm &> /dev/null; then
                    log_message "INFO" "Exporting Helm releases..."
                    
                    mkdir -p "${backup_dir}/kubernetes_resources/helm"
                    
                    # List all Helm releases
                    local helm_releases
                    if ! helm_releases=$(helm list --all-namespaces -q); then
                        log_message "WARNING" "Failed to list Helm releases"
                    else
                        # Export each Helm release
                        for release in ${helm_releases}; do
                            local namespace
                            namespace=$(helm list --all-namespaces | grep "${release}" | awk '{print $2}')
                            
                            if ! helm get all "${release}" -n "${namespace}" > "${backup_dir}/kubernetes_resources/helm/${release}_${namespace}.yaml"; then
                                log_message "WARNING" "Failed to export Helm release: ${release} in namespace: ${namespace}"
                            fi
                        done
                    fi
                fi
                
                # Package Kubernetes resource exports
                local k8s_resources_file="${backup_dir}/kubernetes_resources_${TIMESTAMP}.tar.gz"
                if ! tar -czf "${k8s_resources_file}" -C "${backup_dir}" "kubernetes_resources"; then
                    log_message "WARNING" "Failed to package Kubernetes resource exports"
                else
                    # Remove unpackaged directory to save space
                    rm -rf "${backup_dir}/kubernetes_resources"
                fi
            else
                log_message "WARNING" "kubectl not found, skipping Kubernetes resource export"
            fi
        else
            log_message "WARNING" "Kubernetes config path not found: ${kubernetes_config_path}"
        fi
        
        # Backup configuration files
        if [[ -d "${config_files_path}" ]]; then
            log_message "INFO" "Backing up configuration files from: ${config_files_path}"
            
            local config_backup_file="${backup_dir}/config_files_${TIMESTAMP}.tar.gz"
            if ! tar -czf "${config_backup_file}" -C "$(dirname "${config_files_path}")" "$(basename "${config_files_path}")"; then
                log_message "ERROR" "Failed to backup configuration files"
                success=false
            else
                log_message "SUCCESS" "Configuration files backup completed successfully"
            fi
        else
            log_message "WARNING" "Configuration files path not found: ${config_files_path}"
        fi
        
        # Upload configuration backups to S3
        log_message "INFO" "Uploading configuration backups to S3..."
        
        if ! aws s3 cp "${backup_dir}" "s3://${s3_bucket}/${s3_prefix}/${TIMESTAMP}/" --recursive; then
            log_message "ERROR" "Failed to upload configuration backups to S3"
            success=false
        else
            log_message "SUCCESS" "Configuration backups uploaded to S3 successfully"
        fi
        
        # Apply retention policy
        apply_retention_policy "${config}" "configurations" "${BACKUP_ROOT}/configurations"
    else
        log_message "INFO" "DRY RUN: Would backup configurations from:"
        log_message "INFO" "DRY RUN:   - Terraform: ${terraform_state_path}"
        log_message "INFO" "DRY RUN:   - Kubernetes: ${kubernetes_config_path}"
        log_message "INFO" "DRY RUN:   - Config files: ${config_files_path}"
        log_message "INFO" "DRY RUN: Would upload to s3://${s3_bucket}/${s3_prefix}/${TIMESTAMP}/"
    fi
    
    if [[ "${success}" = true ]]; then
        log_message "SUCCESS" "Configuration backup process completed successfully"
        return 0
    else
        log_message "ERROR" "Configuration backup process failed"
        return 1
    fi
}

# Function to backup application state
backup_application_state() {
    local config="$1"
    local success=true
    
    log_message "INFO" "Starting application state backup..."
    
    # Extract application state backup settings
    local redis_enabled=$(jq -r '.application_state.redis.enabled' <<< "${config}")
    local redis_host=$(jq -r '.application_state.redis.host' <<< "${config}")
    local redis_port=$(jq -r '.application_state.redis.port' <<< "${config}")
    local redis_password_secret=$(jq -r '.application_state.redis.password_secret' <<< "${config}")
    local elasticache_enabled=$(jq -r '.application_state.elasticache.enabled' <<< "${config}")
    local elasticache_cluster_id=$(jq -r '.application_state.elasticache.cluster_id' <<< "${config}")
    local s3_bucket=$(jq -r '.application_state.s3_bucket' <<< "${config}")
    local s3_prefix=$(jq -r '.application_state.s3_prefix' <<< "${config}")
    
    # Create local backup directory
    local backup_dir="${BACKUP_ROOT}/application_state/${TIMESTAMP}"
    
    if [[ "${DRY_RUN}" = false ]]; then
        mkdir -p "${backup_dir}"
        
        # Backup Redis state if enabled
        if [[ "${redis_enabled}" = "true" ]]; then
            log_message "INFO" "Backing up Redis state from: ${redis_host}:${redis_port}"
            
            # Get Redis password from AWS Secrets Manager if specified
            local redis_password=""
            if [[ -n "${redis_password_secret}" ]]; then
                if ! redis_password=$(aws secretsmanager get-secret-value --secret-id "${redis_password_secret}" --query 'SecretString' --output text 2>/dev/null | jq -r '.password'); then
                    log_message "ERROR" "Failed to retrieve Redis password from Secrets Manager"
                    success=false
                fi
            fi
            
            # Trigger Redis SAVE command
            if command -v redis-cli &> /dev/null; then
                if [[ -n "${redis_password}" ]]; then
                    if ! redis-cli -h "${redis_host}" -p "${redis_port}" -a "${redis_password}" SAVE; then
                        log_message "ERROR" "Failed to trigger Redis SAVE command"
                        success=false
                    else
                        log_message "INFO" "Redis SAVE command executed successfully"
                    fi
                else
                    if ! redis-cli -h "${redis_host}" -p "${redis_port}" SAVE; then
                        log_message "ERROR" "Failed to trigger Redis SAVE command"
                        success=false
                    else
                        log_message "INFO" "Redis SAVE command executed successfully"
                    fi
                fi
                
                # Get Redis metadata
                log_message "INFO" "Getting Redis metadata..."
                
                local redis_info_file="${backup_dir}/redis_info_${TIMESTAMP}.txt"
                if [[ -n "${redis_password}" ]]; then
                    if ! redis-cli -h "${redis_host}" -p "${redis_port}" -a "${redis_password}" INFO > "${redis_info_file}"; then
                        log_message "WARNING" "Failed to get Redis INFO data"
                    else
                        log_message "INFO" "Redis INFO data saved successfully"
                    fi
                else
                    if ! redis-cli -h "${redis_host}" -p "${redis_port}" INFO > "${redis_info_file}"; then
                        log_message "WARNING" "Failed to get Redis INFO data"
                    else
                        log_message "INFO" "Redis INFO data saved successfully"
                    fi
                fi
                
                # In a real implementation, we would copy the actual dump.rdb file
                log_message "INFO" "Note: This is a simulated Redis backup. In production, implement direct RDB file copying."
            else
                log_message "ERROR" "redis-cli not found, cannot backup Redis state"
                success=false
            fi
        fi
        
        # Backup ElastiCache if enabled
        if [[ "${elasticache_enabled}" = "true" ]]; then
            log_message "INFO" "Creating ElastiCache snapshot for cluster: ${elasticache_cluster_id}"
            
            local snapshot_name="backup-${elasticache_cluster_id}-${TIMESTAMP}"
            
            # Check if it's a Redis or Memcached cluster
            local cache_engine
            if ! cache_engine=$(aws elasticache describe-cache-clusters --cache-cluster-id "${elasticache_cluster_id}" --query 'CacheClusters[0].Engine' --output text 2>/dev/null); then
                log_message "ERROR" "Failed to determine ElastiCache engine type"
                success=false
            else
                if [[ "${cache_engine}" = "redis" ]]; then
                    # Create Redis snapshot
                    if ! aws elasticache create-snapshot --cache-cluster-id "${elasticache_cluster_id}" --snapshot-name "${snapshot_name}" &> /dev/null; then
                        log_message "ERROR" "Failed to create ElastiCache Redis snapshot"
                        success=false
                    else
                        log_message "SUCCESS" "ElastiCache Redis snapshot created successfully: ${snapshot_name}"
                        
                        # Save snapshot metadata
                        echo "ELASTICACHE_SNAPSHOT=${snapshot_name}" > "${backup_dir}/elasticache_metadata.txt"
                    fi
                elif [[ "${cache_engine}" = "memcached" ]]; then
                    log_message "WARNING" "ElastiCache Memcached does not support snapshots. Data cannot be backed up."
                else
                    log_message "ERROR" "Unknown ElastiCache engine type: ${cache_engine}"
                    success=false
                fi
            fi
        fi
        
        # Upload application state backups to S3
        log_message "INFO" "Uploading application state backups to S3..."
        
        if [[ -d "${backup_dir}" ]] && [[ "$(ls -A "${backup_dir}" 2>/dev/null)" ]]; then
            if ! aws s3 cp "${backup_dir}" "s3://${s3_bucket}/${s3_prefix}/${TIMESTAMP}/" --recursive; then
                log_message "ERROR" "Failed to upload application state backups to S3"
                success=false
            else
                log_message "SUCCESS" "Application state backups uploaded to S3 successfully"
            fi
        else
            log_message "WARNING" "No application state backup files found to upload"
        fi
        
        # Apply retention policy
        apply_retention_policy "${config}" "application_state" "${BACKUP_ROOT}/application_state"
    else
        log_message "INFO" "DRY RUN: Would backup application state:"
        [[ "${redis_enabled}" = "true" ]] && log_message "INFO" "DRY RUN:   - Redis: ${redis_host}:${redis_port}"
        [[ "${elasticache_enabled}" = "true" ]] && log_message "INFO" "DRY RUN:   - ElastiCache: ${elasticache_cluster_id}"
        log_message "INFO" "DRY RUN: Would upload to s3://${s3_bucket}/${s3_prefix}/${TIMESTAMP}/"
    fi
    
    if [[ "${success}" = true ]]; then
        log_message "SUCCESS" "Application state backup process completed successfully"
        return 0
    else
        log_message "ERROR" "Application state backup process failed"
        return 1
    fi
}

# Function to apply retention policy
apply_retention_policy() {
    local config="$1"
    local backup_type="$2"
    local backup_path="$3"
    local success=true
    
    log_message "INFO" "Applying retention policy for ${backup_type} backups..."
    
    # Get retention period from config
    local retention_days
    case "${backup_type}" in
        "database")
            # Different retention for full vs incremental
            if [[ "${BACKUP_TYPE}" = "full" ]]; then
                retention_days=$(jq -r '.retention_policy.database.full_days // 30' <<< "${config}")
            else
                retention_days=$(jq -r '.retention_policy.database.incremental_days // 7' <<< "${config}")
            fi
            ;;
        "s3_storage")
            retention_days=$(jq -r '.retention_policy.s3_storage.days // 30' <<< "${config}")
            ;;
        "configurations")
            retention_days=$(jq -r '.retention_policy.configurations.days // 90' <<< "${config}")
            ;;
        "application_state")
            retention_days=$(jq -r '.retention_policy.application_state.days // 7' <<< "${config}")
            ;;
        *)
            log_message "ERROR" "Unknown backup type for retention policy: ${backup_type}"
            return 1
            ;;
    esac
    
    log_message "INFO" "Retention period for ${backup_type} backups: ${retention_days} days"
    
    if [[ "${DRY_RUN}" = false ]]; then
        # Calculate cutoff date
        local cutoff_date
        cutoff_date=$(date -d "${retention_days} days ago" +"%Y%m%d")
        
        # Check if backup_path is S3 or local
        if [[ "${backup_path}" == s3://* ]]; then
            # S3 path - use aws s3 ls and delete
            log_message "INFO" "Applying retention policy to S3 path: ${backup_path}"
            
            # List objects older than cutoff date
            local objects_to_delete
            if ! objects_to_delete=$(aws s3 ls "${backup_path}/" --recursive | grep -v "/${TIMESTAMP}/" | grep -v "_inventory" | awk '{print $4}' | grep -E "^[0-9]{8}_" | grep -E "^[0-9]{8}_[0-9]{6}" | grep -v "^${cutoff_date:0:8}" | sort); then
                log_message "WARNING" "No objects found or error listing objects in: ${backup_path}"
            else
                # Count objects to delete
                local count
                count=$(echo "${objects_to_delete}" | wc -l)
                
                if [[ ${count} -gt 0 ]]; then
                    log_message "INFO" "Found ${count} objects older than ${cutoff_date} to delete"
                    
                    # Delete objects
                    local delete_errors=0
                    while read -r object; do
                        if ! aws s3 rm "${backup_path}/${object}" --quiet; then
                            log_message "WARNING" "Failed to delete object: ${backup_path}/${object}"
                            ((delete_errors++))
                        fi
                    done <<< "${objects_to_delete}"
                    
                    if [[ ${delete_errors} -gt 0 ]]; then
                        log_message "WARNING" "Encountered ${delete_errors} errors while deleting old backups"
                        success=false
                    else
                        log_message "SUCCESS" "Successfully deleted ${count} old backup objects"
                    fi
                else
                    log_message "INFO" "No objects found older than ${cutoff_date} to delete"
                fi
            fi
        else
            # Local path - use find and delete
            log_message "INFO" "Applying retention policy to local path: ${backup_path}"
            
            # Ensure backup path exists
            if [[ -d "${backup_path}" ]]; then
                # Find directories older than retention_days
                local old_backups
                if ! old_backups=$(find "${backup_path}" -maxdepth 1 -type d -name "20*" -not -path "${backup_path}" -not -name "${TIMESTAMP}" | sort); then
                    log_message "WARNING" "Error finding old backups in: ${backup_path}"
                else
                    # Filter backups older than cutoff date
                    local dirs_to_delete=""
                    while read -r dir; do
                        local dir_date
                        dir_date=$(basename "${dir}" | cut -d'_' -f1)
                        if [[ "${dir_date}" < "${cutoff_date}" ]]; then
                            dirs_to_delete="${dirs_to_delete}${dir}\n"
                        fi
                    done <<< "${old_backups}"
                    
                    # Remove trailing newline
                    dirs_to_delete=$(echo -e "${dirs_to_delete}" | sed '/^$/d')
                    
                    # Count directories to delete
                    local count
                    count=$(echo -e "${dirs_to_delete}" | wc -l)
                    
                    if [[ ${count} -gt 0 ]]; then
                        log_message "INFO" "Found ${count} directories older than ${cutoff_date} to delete"
                        
                        # Delete directories
                        local delete_errors=0
                        while read -r dir; do
                            if ! rm -rf "${dir}"; then
                                log_message "WARNING" "Failed to delete directory: ${dir}"
                                ((delete_errors++))
                            fi
                        done <<< "${dirs_to_delete}"
                        
                        if [[ ${delete_errors} -gt 0 ]]; then
                            log_message "WARNING" "Encountered ${delete_errors} errors while deleting old backups"
                            success=false
                        else
                            log_message "SUCCESS" "Successfully deleted ${count} old backup directories"
                        fi
                    else
                        log_message "INFO" "No directories found older than ${cutoff_date} to delete"
                    fi
                fi
            else
                log_message "WARNING" "Backup path does not exist: ${backup_path}"
            fi
        fi
    else
        log_message "INFO" "DRY RUN: Would apply ${retention_days} day retention policy to ${backup_path}"
    fi
    
    if [[ "${success}" = true ]]; then
        log_message "SUCCESS" "Retention policy applied successfully for ${backup_type} backups"
        return 0
    else
        log_message "WARNING" "Issues encountered while applying retention policy for ${backup_type} backups"
        return 1
    fi
}

# Function to send notifications
notify_backup_status() {
    local config="$1"
    local success="$2"
    local message="$3"
    
    # Skip if notifications are disabled
    if [[ "${NOTIFY}" = false ]]; then
        log_message "INFO" "Notifications are disabled, skipping"
        return 0
    fi
    
    log_message "INFO" "Sending backup status notifications..."
    
    # Extract notification settings
    local email_enabled=$(jq -r '.notification.email.enabled' <<< "${config}")
    local email_sender=$(jq -r '.notification.email.sender' <<< "${config}")
    local email_recipients=$(jq -r '.notification.email.recipients[]' <<< "${config}")
    local slack_enabled=$(jq -r '.notification.slack.enabled' <<< "${config}")
    local slack_webhook=$(jq -r '.notification.slack.webhook_url' <<< "${config}")
    local monitoring_enabled=$(jq -r '.notification.monitoring.enabled' <<< "${config}")
    local monitoring_endpoint=$(jq -r '.notification.monitoring.endpoint' <<< "${config}")
    
    # Set status and subject based on success
    local status_text
    local subject
    if [[ "${success}" = true ]]; then
        status_text="SUCCESS"
        subject="Backup Successful: Justice Bid Rate Negotiation System (${TIMESTAMP})"
    else
        status_text="FAILURE"
        subject="Backup Failed: Justice Bid Rate Negotiation System (${TIMESTAMP})"
    fi
    
    # Prepare email body
    local email_body="
Backup Status: ${status_text}
Timestamp: ${TIMESTAMP}
Backup Type: ${BACKUP_TYPE}
Backup Component: ${BACKUP_COMPONENT}

${message}

For detailed logs, please check: ${LOG_DIR}/backup_$(date +"%Y%m%d").log
"
    
    # Prepare Slack message
    local slack_message="{
        \"text\": \"Backup ${status_text}: Justice Bid Rate Negotiation System\",
        \"attachments\": [
            {
                \"color\": \"$(if [[ "${success}" = true ]]; then echo "good"; else echo "danger"; fi)\",
                \"fields\": [
                    {
                        \"title\": \"Status\",
                        \"value\": \"${status_text}\",
                        \"short\": true
                    },
                    {
                        \"title\": \"Timestamp\",
                        \"value\": \"${TIMESTAMP}\",
                        \"short\": true
                    },
                    {
                        \"title\": \"Backup Type\",
                        \"value\": \"${BACKUP_TYPE}\",
                        \"short\": true
                    },
                    {
                        \"title\": \"Component\",
                        \"value\": \"${BACKUP_COMPONENT}\",
                        \"short\": true
                    },
                    {
                        \"title\": \"Details\",
                        \"value\": \"${message}\",
                        \"short\": false
                    }
                ]
            }
        ]
    }"
    
    # Prepare monitoring payload
    local monitoring_payload="{
        \"status\": \"${status_text}\",
        \"timestamp\": \"${TIMESTAMP}\",
        \"backup_type\": \"${BACKUP_TYPE}\",
        \"component\": \"${BACKUP_COMPONENT}\",
        \"message\": \"${message}\"
    }"
    
    if [[ "${DRY_RUN}" = false ]]; then
        # Send email notification if enabled
        if [[ "${email_enabled}" = "true" && -n "${email_sender}" && -n "${email_recipients}" ]]; then
            log_message "INFO" "Sending email notification..."
            
            # Check if AWS CLI is available
            if command -v aws &> /dev/null; then
                # Send email using AWS SES
                for recipient in ${email_recipients}; do
                    if ! aws ses send-email --from "${email_sender}" --destination "ToAddresses=${recipient}" --message "Subject={Data=${subject},Charset=UTF-8},Body={Text={Data=${email_body},Charset=UTF-8}}" &> /dev/null; then
                        log_message "WARNING" "Failed to send email notification to: ${recipient}"
                    else
                        log_message "INFO" "Email notification sent to: ${recipient}"
                    fi
                done
            else
                log_message "WARNING" "AWS CLI not found, cannot send email notification"
            fi
        fi
        
        # Send Slack notification if enabled
        if [[ "${slack_enabled}" = "true" && -n "${slack_webhook}" ]]; then
            log_message "INFO" "Sending Slack notification..."
            
            # Check if curl is available
            if command -v curl &> /dev/null; then
                # Send Slack notification
                if ! curl -s -X POST -H "Content-type: application/json" --data "${slack_message}" "${slack_webhook}" &> /dev/null; then
                    log_message "WARNING" "Failed to send Slack notification"
                else
                    log_message "INFO" "Slack notification sent successfully"
                fi
            else
                log_message "WARNING" "curl not found, cannot send Slack notification"
            fi
        fi
        
        # Send monitoring notification if enabled
        if [[ "${monitoring_enabled}" = "true" && -n "${monitoring_endpoint}" ]]; then
            log_message "INFO" "Sending monitoring notification..."
            
            # Check if curl is available
            if command -v curl &> /dev/null; then
                # Send monitoring notification
                if ! curl -s -X POST -H "Content-type: application/json" --data "${monitoring_payload}" "${monitoring_endpoint}" &> /dev/null; then
                    log_message "WARNING" "Failed to send monitoring notification"
                else
                    log_message "INFO" "Monitoring notification sent successfully"
                fi
            else
                log_message "WARNING" "curl not found, cannot send monitoring notification"
            fi
        fi
    else
        log_message "INFO" "DRY RUN: Would send notifications with status: ${status_text}"
        [[ "${email_enabled}" = "true" ]] && log_message "INFO" "DRY RUN:   - Email to: ${email_recipients}"
        [[ "${slack_enabled}" = "true" ]] && log_message "INFO" "DRY RUN:   - Slack webhook: ${slack_webhook}"
        [[ "${monitoring_enabled}" = "true" ]] && log_message "INFO" "DRY RUN:   - Monitoring endpoint: ${monitoring_endpoint}"
    fi
    
    log_message "INFO" "Notification process completed"
}

# Generate backup report
generate_backup_report() {
    local success="$1"
    local report_file="${BACKUP_ROOT}/reports/backup_report_${TIMESTAMP}.json"
    
    # Create reports directory if it doesn't exist
    mkdir -p "${BACKUP_ROOT}/reports"
    
    # Prepare report data
    local status
    [[ "${success}" = true ]] && status="SUCCESS" || status="FAILURE"
    
    local report="{
        \"timestamp\": \"${TIMESTAMP}\",
        \"status\": \"${status}\",
        \"backup_type\": \"${BACKUP_TYPE}\",
        \"component\": \"${BACKUP_COMPONENT}\",
        \"duration_seconds\": $(($(date +%s) - ${START_TIME})),
        \"dry_run\": ${DRY_RUN},
        \"log_file\": \"${LOG_DIR}/backup_$(date +"%Y%m%d").log\"
    }"
    
    # Write report to file
    if [[ "${DRY_RUN}" = false ]]; then
        echo "${report}" > "${report_file}"
        log_message "INFO" "Backup report generated: ${report_file}"
        
        # Copy report to S3 if possible
        if command -v aws &> /dev/null; then
            local config
            config=$(load_config 2>/dev/null || echo '{}')
            
            if [[ -n "${config}" ]]; then
                local s3_bucket=$(jq -r '.configurations.s3_bucket' <<< "${config}")
                
                if [[ -n "${s3_bucket}" && "${s3_bucket}" != "null" ]]; then
                    if ! aws s3 cp "${report_file}" "s3://${s3_bucket}/reports/backup_report_${TIMESTAMP}.json" &> /dev/null; then
                        log_message "WARNING" "Failed to upload backup report to S3"
                    else
                        log_message "INFO" "Backup report uploaded to S3 successfully"
                    fi
                fi
            fi
        fi
    else
        log_message "INFO" "DRY RUN: Would generate backup report: ${report_file}"
    fi
}

# Function to check dependencies
check_dependencies() {
    local missing_deps=()
    
    # Check for AWS CLI
    if ! command -v aws &> /dev/null; then
        missing_deps+=("aws-cli")
    else
        log_message "INFO" "Found AWS CLI: $(aws --version | head -n1)"
    fi
    
    # Check for PostgreSQL client
    if ! command -v pg_dump &> /dev/null; then
        missing_deps+=("postgresql-client")
    else
        log_message "INFO" "Found PostgreSQL client: $(pg_dump --version | head -n1)"
    fi
    
    # Check for jq
    if ! command -v jq &> /dev/null; then
        missing_deps+=("jq")
    else
        log_message "INFO" "Found jq: $(jq --version)"
    fi
    
    # Check for tar
    if ! command -v tar &> /dev/null; then
        missing_deps+=("tar")
    fi
    
    # Check for gzip
    if ! command -v gzip &> /dev/null; then
        missing_deps+=("gzip")
    fi
    
    # Report missing dependencies
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        log_message "ERROR" "Missing required dependencies: ${missing_deps[*]}"
        log_message "ERROR" "Please install the missing dependencies and try again."
        return 1
    fi
    
    return 0
}

# Function to parse command line arguments
parse_arguments() {
    for arg in "$@"; do
        case "${arg}" in
            --type=*)
                BACKUP_TYPE="${arg#*=}"
                if [[ "${BACKUP_TYPE}" != "full" && "${BACKUP_TYPE}" != "incremental" && "${BACKUP_TYPE}" != "all" ]]; then
                    log_message "ERROR" "Invalid backup type: ${BACKUP_TYPE}. Must be 'full', 'incremental', or 'all'."
                    exit 1
                fi
                ;;
            --component=*)
                BACKUP_COMPONENT="${arg#*=}"
                if [[ "${BACKUP_COMPONENT}" != "database" && "${BACKUP_COMPONENT}" != "storage" && "${BACKUP_COMPONENT}" != "config" && "${BACKUP_COMPONENT}" != "state" && "${BACKUP_COMPONENT}" != "all" ]]; then
                    log_message "ERROR" "Invalid backup component: ${BACKUP_COMPONENT}. Must be 'database', 'storage', 'config', 'state', or 'all'."
                    exit 1
                fi
                ;;
            --config=*)
                CONFIG_FILE="${arg#*=}"
                ;;
            --dry-run)
                DRY_RUN=true
                ;;
            --no-notify)
                NOTIFY=false
                ;;
            --help)
                echo "Usage: $0 [options]"
                echo ""
                echo "Options:"
                echo "  --type=TYPE     Backup type (full, incremental, or all). Default: determined by schedule"
                echo "  --component=COMPONENT   Component to backup (database, storage, config, state, or all). Default: all"
                echo "  --config=FILE   Path to config file. Default: ../backup-config.json"
                echo "  --dry-run       Perform a dry run without making changes"
                echo "  --no-notify     Disable notifications"
                echo "  --help          Display this help message"
                exit 0
                ;;
            *)
                log_message "ERROR" "Unknown argument: ${arg}"
                exit 1
                ;;
        esac
    done
}

# Main function
main() {
    # Parse command line arguments
    parse_arguments "$@"
    
    # Display script info
    log_message "INFO" "Justice Bid Rate Negotiation System Backup Script"
    log_message "INFO" "Timestamp: ${TIMESTAMP}"
    [[ "${DRY_RUN}" = true ]] && log_message "INFO" "Running in DRY RUN mode - no changes will be made"
    
    # Load configuration
    log_message "INFO" "Loading configuration from: ${CONFIG_FILE}"
    local config
    if ! config=$(load_config); then
        log_message "ERROR" "Failed to load configuration"
        exit 1
    fi
    
    # Check dependencies
    log_message "INFO" "Checking dependencies..."
    if ! check_dependencies; then
        log_message "ERROR" "Missing required dependencies"
        exit 1
    fi
    
    # Create backup root directory if it doesn't exist and we're not in dry run mode
    if [[ "${DRY_RUN}" = false ]]; then
        mkdir -p "${BACKUP_ROOT}"
        log_message "INFO" "Created backup root directory: ${BACKUP_ROOT}"
    fi
    
    # Track successful components
    local database_success=true
    local storage_success=true
    local config_success=true
    local state_success=true
    
    # Perform backups based on component selection
    if [[ "${BACKUP_COMPONENT}" = "all" || "${BACKUP_COMPONENT}" = "database" ]]; then
        if ! backup_database "${config}"; then
            database_success=false
            EXIT_CODE=1
        fi
    fi
    
    if [[ "${BACKUP_COMPONENT}" = "all" || "${BACKUP_COMPONENT}" = "storage" ]]; then
        if ! backup_s3_storage "${config}"; then
            storage_success=false
            EXIT_CODE=1
        fi
    fi
    
    if [[ "${BACKUP_COMPONENT}" = "all" || "${BACKUP_COMPONENT}" = "config" ]]; then
        if ! backup_configurations "${config}"; then
            config_success=false
            EXIT_CODE=1
        fi
    fi
    
    if [[ "${BACKUP_COMPONENT}" = "all" || "${BACKUP_COMPONENT}" = "state" ]]; then
        if ! backup_application_state "${config}"; then
            state_success=false
            EXIT_CODE=1
        fi
    fi
    
    # Determine overall success
    local overall_success=true
    if [[ "${database_success}" = false || "${storage_success}" = false || "${config_success}" = false || "${state_success}" = false ]]; then
        overall_success=false
    fi
    
    # Generate summary
    local summary=""
    summary+="Database: $(if [[ "${database_success}" = true ]]; then echo "SUCCESS"; else echo "FAILURE"; fi)\n"
    summary+="Storage: $(if [[ "${storage_success}" = true ]]; then echo "SUCCESS"; else echo "FAILURE"; fi)\n"
    summary+="Configuration: $(if [[ "${config_success}" = true ]]; then echo "SUCCESS"; else echo "FAILURE"; fi)\n"
    summary+="Application State: $(if [[ "${state_success}" = true ]]; then echo "SUCCESS"; else echo "FAILURE"; fi)\n"
    summary+="Duration: $(($(date +%s) - ${START_TIME})) seconds"
    
    # Log summary
    log_message "INFO" "Backup Summary:"
    echo -e "${summary}" | while read -r line; do
        log_message "INFO" "${line}"
    done
    
    # Generate backup report
    generate_backup_report "${overall_success}"
    
    # Send notifications
    notify_backup_status "${config}" "${overall_success}" "${summary}"
    
    # Log completion
    if [[ "${overall_success}" = true ]]; then
        log_message "SUCCESS" "Backup completed successfully"
    else
        log_message "ERROR" "Backup completed with errors"
    fi
    
    return ${EXIT_CODE}
}

# Run main function
main "$@"
exit ${EXIT_CODE}