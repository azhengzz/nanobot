#!/usr/bin/env python3
"""Feishu Wiki operations - CLI skill"""
import json
import re
import sys
from typing import Optional
from urllib.parse import urlparse
import click


try:
    import lark_oapi as lark
    import lark_oapi.api.wiki.v2 as lark_wiki_v2
    from lark_oapi.api.wiki.v2.model import Node
    # from lark_oapi.api.wiki.v1 import SearchNodeRequest, SearchNodeResponse, SearchNodeRequestBody
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
    return click.echo(lark.JSON.marshal(response, indent=4))  # ensure_ascii=False

# Click CLI group
@click.group(help='Feishu Wiki operations - Manage wiki spaces, nodes, and search')
@click.option('--app-id', required=True, envvar='FEISHU_APP_ID', help='Feishu app ID')
@click.option('--app-secret', required=True, envvar='FEISHU_APP_SECRET', help='Feishu app secret')
@click.pass_context
def cli(ctx: click.Context, app_id: str, app_secret: str):
    """Feishu Wiki CLI tool."""
    if not FEISHU_SDK_AVAILABLE:
        output_result({"error": "lark-oapi not installed"})
        ctx.exit(1)

    # Store client in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj['client'] = create_client(app_id, app_secret)


@cli.command(help='List all wiki spaces')
@click.pass_context
def spaces(ctx: click.Context):
    """List all wiki spaces accessible to the app."""
    # 获取知识空间列表 https://open.feishu.cn/api-explorer/cli_a9c750e92b385bdd?apiName=list&from=op_doc_tab&project=wiki&resource=space&version=v2
    client = ctx.obj['client']
    request = lark_wiki_v2.ListSpaceRequest.builder().build()
    try:
        response = client.wiki.v2.space.list(request)
    except Exception as e:
        output_result({"error": f"{e}"})
        return
    output_response(response)


@cli.command(help='List wiki nodes in a space')
@click.option('--space-id', required=True, help='Wiki space ID')
@click.option('--parent-node-token', default='', help='Parent node token (empty for top-level)')
@click.pass_context
def nodes(ctx: click.Context, space_id: str, parent_node_token: str):
    """List wiki nodes in a space."""
    # 获取知识空间子节点列表 https://open.feishu.cn/api-explorer/cli_a9c750e92b385bdd?apiName=list&from=op_doc_tab&project=wiki&resource=space.node&version=v2
    client = ctx.obj['client']
    request = lark_wiki_v2.ListSpaceNodeRequest.builder() \
        .space_id(space_id) \
        .parent_node_token(parent_node_token) \
        .build()
    try:
        response = client.wiki.v2.space_node.list(request)
    except Exception as e:
        output_result({"error": f"{e}"})
        return
    output_response(response)


@cli.command(help='Get wiki node details')
@click.option('--token', type=str, help='Node token')
@click.option('--url', type=str, help='Wiki page URL (extracts token from URL)')
@click.pass_context
def get(ctx: click.Context, token: Optional[str], url: Optional[str]):
    """Get wiki node details by token or URL."""
    # 获取知识空间节点信息 https://open.feishu.cn/api-explorer/cli_a9c750e92b385bdd?apiName=get_node&from=op_doc_tab&project=wiki&resource=space&version=v2
    client = ctx.obj['client']
    node_token = token
    if not node_token and url:
        parsed = urlparse(url)
        match = re.search(r'/wiki/([a-zA-Z0-9]+)', parsed.path)
        if match:
            node_token = match.group(1)
    if not node_token:
        output_result({"error": "Requires --token or --url"})
        return

    request: lark_wiki_v2.GetNodeSpaceRequest = lark_wiki_v2.GetNodeSpaceRequest.builder().token(node_token).build()
    try:
        response = client.wiki.v2.space.get_node(request)
    except Exception as e:
        output_result({"error": f"{e}"})
        return
    output_response(response)



@cli.command(help='Create a new wiki node')
@click.option('--space-id', required=True, help='Wiki space ID')
@click.option('--obj-type', required=True, type=click.Choice(['docx', 'sheet', 'mindnote', 'bitable', 'file', 'slides']),
              default='docx', help='Document type, for shortcuts, this field represents the obj_type of the corresponding entity. (default: docx)')
@click.option('--node-type', required=True, type=click.Choice(['origin', 'shortcut']),
              default='origin', help='Node type (default: origin)')
@click.option('--title', required=True, help='Node title')
@click.option('--parent-node-token', default='', help='Parent node token (empty for top-level)')
@click.option('--origin-node-token', type=str, help='The corresponding entity node_token for the shortcut. When the node is a shortcut, this value is not empty')
@click.pass_context
def create(ctx: click.Context, space_id: str, obj_type: str, node_type: str, title: str,
           parent_node_token: str, origin_node_token: Optional[str]):
    """Create a new wiki node."""
    # 创建知识空间节点 https://open.feishu.cn/api-explorer/cli_a9c750e92b385bdd?apiName=create&from=op_doc_tab&project=wiki&resource=space.node&version=v2
    client = ctx.obj['client']

    # Build the request body with Node object
    node_builder = Node.builder() \
        .obj_type(obj_type) \
        .node_type(node_type) \
        .title(title)

    # Add optional parameters
    if parent_node_token:
        node_builder.parent_node_token(parent_node_token)
    if origin_node_token:
        node_builder.origin_node_token(origin_node_token)

    request: lark_wiki_v2.CreateSpaceNodeRequest = lark_wiki_v2.CreateSpaceNodeRequest.builder() \
        .space_id(space_id) \
        .request_body(node_builder.build()) \
        .build()

    try:
        response: lark_wiki_v2.CreateSpaceNodeResponse = client.wiki.v2.space_node.create(request)
    except Exception as e:
        output_result({"error": f"{e}"})
        return

    output_response(response)


# @cli.command(help='Search wiki nodes')
# @click.option('--query', required=True, help='Search query keyword')
# @click.option('--space-id', type=str, help='Limit search to this space ID')
# @click.option('--node-id', type=str, help='Limit search to this node ID')
# @click.option('--page-token', default='', help='Page token for pagination')
# @click.option('--page-size', type=int, default=20, help='Number of results per page (default: 10)')
# @click.pass_context
# def search(ctx: click.Context, query: str, space_id: Optional[str], node_id: Optional[str],
#            page_token: str, page_size: int):
#     """Search wiki nodes by keyword."""
#     client = ctx.obj['client']
#     request: SearchNodeRequest = SearchNodeRequest.builder() \
#         .page_token(page_token) \
#         .page_size(page_size) \
#         .request_body(SearchNodeRequestBody.builder()
#             .query(query)
#             .build()) \
#         .build()
#     # 发起请求
#     option = lark.RequestOption.builder() \
#         .user_access_token("u-f8c2l0zwx0YGFxgYXomJ0950mqih1hMjo2GaFww027sZ") \
#         .build()
#     response: SearchNodeResponse = client.wiki.v1.node.search(request, option)


#     if not response.success():
#         output_result({
#             "error": response.msg,
#             "code": response.code,
#         })
#         return

#     output_result({
#         "nodes": [{
#             "title": node.title,
#             "obj_token": node.obj_token,
#             "node_id": node.node_id,
#             "space_id": node.space_id,
#             "obj_type": node.obj_type,
#         } for node in response.data.items],
#         "page_token": response.data.page_token,
#         "has_more": response.data.has_more
#     })


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
