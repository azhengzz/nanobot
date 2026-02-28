#!/bin/bash
# install-kubectl-safe.sh
# Simple and reliable wrapper installer for Linux/macOS

set -e

echo -e "\033[36mInstalling kubectl-safe wrapper...\033[0m"

# Get user's home directory
HOME_DIR="${HOME:-$(cd ~ && pwd)}"
BIN_DIR="$HOME_DIR/bin"

# Create bin directory
if [ ! -d "$BIN_DIR" ]; then
    mkdir -p "$BIN_DIR"
    echo -e "\033[32mCreated directory: $BIN_DIR\033[0m"
fi

# Path to the actual script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_PATH="$SCRIPT_DIR/kubectl-safe.sh"

# Create kubectl-safe wrapper script
WRAPPER_PATH="$BIN_DIR/kubectl-safe"
cat > "$WRAPPER_PATH" << EOF
#!/bin/bash
# kubectl-safe wrapper script
# This script wraps the actual kubectl-safe.sh implementation

# Direct absolute path to the actual script
ACTUAL_SCRIPT="$SCRIPT_PATH/kubectl-safe.sh"

if [ -f "$ACTUAL_SCRIPT" ]; then
    exec bash "$ACTUAL_SCRIPT" "$@"
else
    echo "Error: Cannot find kubectl-safe.sh at \$ACTUAL_SCRIPT" >&2
    exit 1
fi
EOF

chmod +x "$WRAPPER_PATH"
echo -e "\033[32mCreated: $WRAPPER_PATH\033[0m"

# Detect shell and add to PATH
add_to_path() {
    local config_file="$1"
    local bin_dir="$2"

    if [ -f "$config_file" ] && ! grep -q "$bin_dir" "$config_file" 2>/dev/null; then
        echo "" >> "$config_file"
        echo "# Added by kubectl-safe installer" >> "$config_file"
        echo "export PATH=\"$bin_dir:\$PATH\"" >> "$config_file"
        return 0
    fi
    return 1
}

PATH_UPDATED=false

# Check if bin directory is already in PATH
if echo "$PATH" | grep -q "$BIN_DIR"; then
    echo -e "\033[33mDirectory already in PATH.\033[0m"
else
    # Try to add to shell config files
    case "$SHELL" in
        */zsh)
            if [ -f "$HOME_DIR/.zshrc" ]; then
                if add_to_path "$HOME_DIR/.zshrc" "$BIN_DIR"; then
                    echo -e "\033[32mAdded to PATH in ~/.zshrc\033[0m"
                    PATH_UPDATED=true
                fi
            fi
            ;;
        */bash)
            if [ -f "$HOME_DIR/.bashrc" ]; then
                if add_to_path "$HOME_DIR/.bashrc" "$BIN_DIR"; then
                    echo -e "\033[32mAdded to PATH in ~/.bashrc\033[0m"
                    PATH_UPDATED=true
                fi
            fi
            ;;
        *)
            # Try common config files
            for config in ".bashrc" ".zshrc" ".profile" ".bash_profile"; do
                if [ -f "$HOME_DIR/$config" ]; then
                    if add_to_path "$HOME_DIR/$config" "$BIN_DIR"; then
                        echo -e "\033[32mAdded to PATH in ~/$config\033[0m"
                        PATH_UPDATED=true
                        break
                    fi
                fi
            done
            ;;
    esac

    if [ "$PATH_UPDATED" = false ]; then
        echo -e "\033[33mPlease add '$BIN_DIR' to your PATH manually.\033[0m"
    fi
fi

echo ""
echo -e "\033[32m[OK] Installation completed!\033[0m"
echo ""
echo -e "\033[37mNext steps:\033[0m"
if [ "$PATH_UPDATED" = true ]; then
    echo -e "\033[33m1. Close and reopen your terminal (or run: source ~/.bashrc or source ~/.zshrc)\033[0m"
else
    echo -e "\033[33m1. Start a new shell session\033[0m"
fi
echo -e "\033[33m2. Test the command: kubectl-safe get pods\033[0m"
echo ""
echo -e "\033[90mNote: Dangerous commands like 'kubectl-safe delete' will be automatically blocked\033[0m"
