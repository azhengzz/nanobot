---
name: feishu-doc
description: Operate Feishu DocX documents via CLI. Commands include read, list_blocks, get_block, create. Use when the user mentions DocX, documents, or /docx/ links.
---

# Feishu Doc Skill

Operate Feishu DocX documents.

## Usage

```bash
python scripts/feishu_doc.py --app-id <ID> --app-secret <SECRET> <COMMAND> [options]
```

## Commands

| Command | Options | Description |
|---------|---------|-------------|
| `read` | `--document-id` or `--url` | Read document content |
| `list-blocks` | `--document-id` or `--url`, `--page-size` | List all blocks in document |
| `get-block` | `--document-id` or `--url`, `--block-id` (required) | Get specific block details |
| `create` | `--title` (required), `--content`, `--folder-token` | Create new document |

## Options

### Global Options (required for all commands)
- `--app-id`: Feishu app ID (can use env var `FEISHU_APP_ID`)
- `--app-secret`: Feishu app secret (can use env var `FEISHU_APP_SECRET`)

### Command-Specific Options
- `--document-id`: Document ID
- `--url`: DocX URL to extract token from
- `--title`: Document title (required for `create`)
- `--content`: Initial content (for `create`)
- `--folder-token`: Folder token to create document in (for `create`)
- `--block-id`: Block ID (required for `get_block`)
- `--page-size`: Number of results per page for `list_blocks` (default: 200)

## Examples

```bash
# Read document by ID
python scripts/feishu_doc.py --app-id $APP_ID --app-secret $APP_SECRET read --document-id "doxxx"

# Read document from URL
python scripts/feishu_doc.py --app-id $APP_ID --app-secret $APP_SECRET read --url "https://xxx.feishu.cn/docx/xxx"

# List blocks
python scripts/feishu_doc.py --app-id $APP_ID --app-secret $APP_SECRET list_blocks --document-id "doxxx"

# Get specific block
python scripts/feishu_doc.py --app-id $APP_ID --app-secret $APP_SECRET get_block --document-id "doxxx" --block-id "xxx"

# Create new document
python scripts/feishu_doc.py --app-id $APP_ID --app-secret $APP_SECRET create --title "My Document"

# Create document in folder
python scripts/feishu_doc.py --app-id $APP_ID --app-secret $APP_SECRET create --title "My Document" --folder-token "folder123"
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
