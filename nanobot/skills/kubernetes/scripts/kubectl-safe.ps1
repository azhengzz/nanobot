# ============================================
# Safe kubectl wrapper - blocks dangerous commands
# For Windows PowerShell
# ============================================

# Set UTF-8 encoding for proper character display
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# Get all arguments
$Arguments = $args

# Handle null/empty arguments
if ($null -eq $Arguments) {
    $Arguments = @()
}

# Configuration
$DANGEROUS_COMMANDS = @("delete", "apply", "create", "edit", "rollout", "patch", "replace", "scale", "label", "annotate", "taint", "cordon", "uncordon", "drain")
$ALLOWED_COMMANDS = @("get", "describe", "logs", "exec", "port-forward", "top", "api-resources", "api-versions", "cluster-info", "version", "explain", "options")

# Colors
$RED = "Red"
$GREEN = "Green"
$YELLOW = "Yellow"

# Check if any argument is a dangerous command
$commandString = $Arguments -join " "
foreach ($dangerousCmd in $DANGEROUS_COMMANDS) {
    if ($commandString -match $dangerousCmd -or ($Arguments.Count -gt 0 -and $Arguments[0] -eq $dangerousCmd)) {
        Write-Host "[ERROR] 'kubectl $dangerousCmd' is PROHIBITED for security reasons." -ForegroundColor $RED
        Write-Host "This wrapper only allows read-only operations." -ForegroundColor $YELLOW
        Write-Host ""
        Write-Host "Allowed commands:" -ForegroundColor $YELLOW
        $ALLOWED_COMMANDS | ForEach-Object { Write-Host "  $_" -ForegroundColor $GREEN }
        Write-Host ""
        Write-Host "If you need to modify resources, please:"
        Write-Host "  1. Run the command manually on your local machine"
        Write-Host "  2. Or use: kubectl-unsafe $commandString"
        exit 1
    }
}

# Find kubectl
$kubectlPath = Get-Command kubectl -ErrorAction SilentlyContinue
if (-not $kubectlPath) {
    Write-Host "[ERROR] kubectl not found in PATH" -ForegroundColor $RED
    exit 1
}

Write-Host "[OK] Executing safe kubectl command..." -ForegroundColor $GREEN
& $kubectlPath.Source @Arguments
