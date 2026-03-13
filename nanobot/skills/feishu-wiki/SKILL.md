---
name: feishu-wiki
description: Navigate Feishu knowledge bases via CLI. Commands include spaces, nodes, get, create. Use when the user mentions Wiki, knowledge base, or /wiki/ links.
---

# Feishu Wiki Skill

Navigate Feishu knowledge bases.

## Usage

```bash
python scripts/feishu_wiki.py --app-id <ID> --app-secret <SECRET> <COMMAND> [options]
```

## Commands

| Command | Options | Description |
|---------|---------|-------------|
| `spaces` | - | List all wiki spaces |
| `nodes` | `--space-id` (required), `--parent-node-token` | List nodes in a space |
| `get` | `--token` or `--url` | Get node details by token or URL |
| `create` | `--space-id`, `--title`, `--obj-type`, `--node-type`, `--parent-node-token`, `--origin-node-token` | Create a new wiki node |

## Options

### Global Options (required for all commands)
- `--app-id`: Feishu app ID (can use env var `FEISHU_APP_ID`)
- `--app-secret`: Feishu app secret (can use env var `FEISHU_APP_SECRET`)

### Command-Specific Options

#### `spaces` command
| Option | Required | Description |
|--------|----------|-------------|
| - | - | No additional options |

#### `nodes` command
| Option | Required | Description |
|--------|----------|-------------|
| `--space-id` | Yes | Wiki space ID |
| `--parent-node-token` | No | Parent node token for listing children (default: empty for top-level) |

#### `get` command
| Option | Required | Description |
|--------|----------|-------------|
| `--token` | No* | Node token |
| `--url` | No* | Wiki page URL to extract token from |

*Either `--token` or `--url` must be provided.

#### `create` command
| Option | Required | Description |
|--------|----------|-------------|
| `--space-id` | Yes | Wiki space ID |
| `--title` | Yes | Node title |
| `--obj-type` | Yes | Object type: `docx`, `sheet`, `mindnote`, `bitable`, `file`, `slides` (default: `docx`) |
| `--node-type` | Yes | Node type: `origin`, `shortcut` (default: `origin`) |
| `--parent-node-token` | No | Parent node token (empty for top-level) |
| `--origin-node-token` | No | The corresponding entity node_token for the shortcut. When the node is a shortcut, this value is not empty |

## Examples

```bash
# List all wiki spaces
python scripts/feishu_wiki.py --app-id $APP_ID --app-secret $APP_SECRET spaces

# List top-level nodes in a space
python scripts/feishu_wiki.py --app-id $APP_ID --app-secret $APP_SECRET nodes --space-id 123

# List child nodes under a parent node
python scripts/feishu_wiki.py --app-id $APP_ID --app-secret $APP_SECRET nodes --space-id 123 --parent-node-token abc123

# Get node details by token
python scripts/feishu_wiki.py --app-id $APP_ID --app-secret $APP_SECRET get --token abc123

# Get node details by URL
python scripts/feishu_wiki.py --app-id $APP_ID --app-secret $APP_SECRET get --url "https://example.feishu.cn/wiki/abc123"

# Create a docx page at root level
python scripts/feishu_wiki.py --app-id $APP_ID --app-secret $APP_SECRET create --space-id 123 --title "My Page"

# Create a sheet
python scripts/feishu_wiki.py --app-id $APP_ID --app-secret $APP_SECRET create --space-id 123 --obj-type sheet --title "My Sheet"

# Create a node under a parent node
python scripts/feishu_wiki.py --app-id $APP_ID --app-secret $APP_SECRET create --space-id 123 --parent-node-token abc123 --title "Child Node"

# Create a shortcut to an existing node
python scripts/feishu_wiki.py --app-id $APP_ID --app-secret $APP_SECRET create --space-id 123 --node-type shortcut --origin-node-token xyz789 --title "Shortcut to Node"
```

## Output

All commands output the complete lark-oapi SDK response as JSON to stdout, including all fields (code, msg, data, etc.).

Example successful response:
```json
{
    "code": 0,
    "msg": "success",
    "data": {...}
}
```

Error response (from exception):
```json
{
    "error": "error message"
}
```
