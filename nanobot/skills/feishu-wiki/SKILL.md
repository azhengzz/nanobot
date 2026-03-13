---
name: feishu-wiki
description: Navigate Feishu knowledge bases via CLI. Commands include spaces, nodes, get. Use when the user mentions Wiki, knowledge base, or /wiki/ links.
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

## Options

### Global Options (required for all commands)
- `--app-id`: Feishu app ID (can use env var `FEISHU_APP_ID`)
- `--app-secret`: Feishu app secret (can use env var `FEISHU_APP_SECRET`)

### Command-Specific Options
- `--space-id`: Wiki space ID (required for `nodes`)
- `--parent-node-token`: Parent node token for listing children (default: empty for top-level)
- `--token`: Node token (for `get`)
- `--url`: Wiki page URL to extract token from (for `get`)

## Examples

```bash
# List all wiki spaces
python scripts/feishu_wiki.py --app-id $APP_ID --app-secret $APP_SECRET spaces

# List nodes in a space
python scripts/feishu_wiki.py --app-id $APP_ID --app-secret $APP_SECRET nodes --space-id 123

# Get node details by token
python scripts/feishu_wiki.py --app-id $APP_ID --app-secret $APP_SECRET get --token abc123

# Get node details by URL
python scripts/feishu_wiki.py --app-id $APP_ID --app-secret $APP_SECRET get --url "https://example.feishu.cn/wiki/abc123"
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