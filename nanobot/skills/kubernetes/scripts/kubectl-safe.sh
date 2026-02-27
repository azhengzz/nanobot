#!/bin/bash

# ============================================
# Safe kubectl wrapper - blocks dangerous commands
# For Linux and macOS
# ============================================

# Configuration
DANGEROUS_COMMANDS=("delete" "apply" "create" "edit" "rollout" "patch" "replace" "scale" "label" "annotate" "taint" "cordon" "uncordon" "drain")
ALLOWED_COMMANDS=("get" "describe" "logs" "exec" "port-forward" "top" "api-resources" "api-versions" "cluster-info" "version" "explain" "options")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if any argument is a dangerous command
for dangerous_cmd in "${DANGEROUS_COMMANDS[@]}"; do
    if [[ "$*" == *"$dangerous_cmd"* ]] || [[ "$1" == "$dangerous_cmd" ]]; then
        echo -e "${RED}❌ ERROR: 'kubectl $dangerous_cmd' is PROHIBITED for security reasons.${NC}"
        echo -e "${YELLOW}This wrapper only allows read-only operations.${NC}"
        echo ""
        echo "Allowed commands:"
        printf "  ${GREEN}%s${NC}\n" "${ALLOWED_COMMANDS[@]}"
        echo ""
        echo "If you need to modify resources, please:"
        echo "  1. Run the command manually on your local machine"
        echo "  2. Or use: /usr/local/bin/kubectl-unsafe $@"
        exit 1
    fi
done

# Execute the command if it's safe
if command -v kubectl &> /dev/null; then
    KUBECTL_PATH=$(command -v kubectl)
else
    echo -e "${RED}❌ ERROR: kubectl not found in PATH${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Executing safe kubectl command...${NC}"
exec "$KUBECTL_PATH" "$@"