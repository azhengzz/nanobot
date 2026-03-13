#!/usr/bin/env python3
"""Feishu DocX operations - CLI skill"""
import json
import re
import sys
from typing import Optional
from urllib.parse import urlparse
import click

try:
    import lark_oapi as lark
    import lark_oapi.api.docx.v1 as lark_docx
    FEISHU_SDK_AVAILABLE = True
except ImportError:
    FEISHU_SDK_AVAILABLE = False


def create_client(app_id: str, app_secret: str) -> lark.Client:
    """Create a Feishu client with the given credentials."""
    return lark.Client.builder().app_id(app_id).app_secret(app_secret).log_level(lark.LogLevel.INFO).build()


def output_result(result: dict) -> None:
    """Output result as JSON."""
    click.echo(json.dumps(result, ensure_ascii=False, indent=2))


def output_response(response) -> dict:
    """Convert lark-oapi response to dict, including all raw data."""
    if not response.success():
        return output_result({
                "code": response.code,
                "msg": response.msg,
                "success": response.success(),
            })
    return click.echo(lark.JSON.marshal(response, indent=4))


def resolve_document_id_from_url(url: str) -> tuple[str, bool]:
    """Resolve document_id from DocX URL and return (token, is_wiki)."""
    parsed = urlparse(url)
    path = parsed.path
    is_wiki = "/wiki/" in path

    patterns = [
        r'/docx/([a-zA-Z0-9]+)',
        r'/wiki/([a-zA-Z0-9]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, path)
        if match:
            return match.group(1), is_wiki
    return "", is_wiki


# Click CLI group
@click.group(help='Feishu DocX operations - Read, create, and manipulate documents')
@click.option('--app-id', required=True, envvar='FEISHU_APP_ID', help='Feishu app ID')
@click.option('--app-secret', required=True, envvar='FEISHU_APP_SECRET', help='Feishu app secret')
@click.pass_context
def cli(ctx: click.Context, app_id: str, app_secret: str):
    """Feishu DocX CLI tool."""
    if not FEISHU_SDK_AVAILABLE:
        output_result({"error": "lark-oapi not installed"})
        ctx.exit(1)

    # Store client in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj['client'] = create_client(app_id, app_secret)


@cli.command(help='Read document raw content')
@click.option('--document-id', type=str, help='Document Id')
@click.option('--url', type=str, help='DocX URL (extracts token from URL)')
@click.pass_context
def read(ctx: click.Context, document_id: Optional[str], url: Optional[str]):
    """Read document Raw Content by Document Id or URL."""
    client = ctx.obj['client']

    if not document_id and url:
        document_id, _ = resolve_document_id_from_url(url)

    if not document_id:
        output_result({"error": "Requires --doc-id or --url"})
        return

    request: lark_docx.RawContentDocumentRequest = lark_docx.RawContentDocumentRequest.builder() \
        .document_id(document_id) \
        .lang(0) \
        .build()
    try:
        response: lark_docx.RawContentDocumentResponse = client.docx.v1.document.raw_content(request)
    except Exception as e:
        output_result({"error": f"{e}"})
        return
    output_response(response)


@cli.command(help='List document blocks')
@click.option('--document-id', type=str, help='Document ID')
@click.option('--url', type=str, help='DocX URL (extracts token from URL)')
@click.option('--page-size', type=int, default=200, help='Number of results per page (default: 200)')
@click.pass_context
def list_blocks(ctx: click.Context, document_id: Optional[str], url: Optional[str], page_size: int):
    """List all blocks in a document."""
    client = ctx.obj['client']

    if not document_id and url:
        document_id, _ = resolve_document_id_from_url(url)

    if not document_id:
        output_result({"error": "Requires --document-id or --url"})
        return

    request = lark_docx.ListDocumentBlockRequest.builder() \
        .document_id(document_id) \
        .page_size(page_size) \
        .build()
    try:
        response = client.docx.v1.document_block.list(request)
    except Exception as e:
        output_result({"error": f"{e}"})
        return
    output_response(response)


@cli.command(help='Get specific block details')
@click.option('--document-id', type=str, help='Document ID')
@click.option('--url', type=str, help='DocX URL (extracts token from URL)')
@click.option('--block-id', required=True, type=str, help='Block ID to retrieve')
@click.pass_context
def get_block(ctx: click.Context, document_id: Optional[str], url: Optional[str], block_id: str):
    """Get a specific block in a document."""
    client = ctx.obj['client']

    if not document_id and url:
        document_id, _ = resolve_document_id_from_url(url)

    if not document_id:
        output_result({"error": "Requires --document-id or --url"})
        return

    request = lark_docx.GetDocumentBlockRequest.builder() \
        .document_id(document_id) \
        .block_id(block_id) \
        .build()
    try:
        response = client.docx.v1.document_block.get(request)
    except Exception as e:
        output_result({"error": f"{e}"})
        return
    output_response(response)


@cli.command(help='Create new document')
@click.option('--title', required=True, type=str, help='Document title')
@click.option('--content', type=str, default='', help='Initial content')
@click.option('--folder-token', type=str, default='', help='Folder token to create document in')
@click.pass_context
def create(ctx: click.Context, title: str, content: str, folder_token: str):
    """Create a new DocX document."""
    client = ctx.obj['client']

    request = lark_docx.CreateDocumentRequest.builder() \
        .request_body(lark_docx.CreateDocumentRequestBody.builder()
            .title(title)
            .folder_token(folder_token)
            .build()) \
        .build()
    try:
        response = client.docx.v1.document.create(request)
    except Exception as e:
        output_result({"error": f"{e}"})
        return
    output_response(response)


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
