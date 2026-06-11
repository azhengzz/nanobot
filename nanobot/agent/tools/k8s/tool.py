# coding=utf-8

import json

from nanobot.agent.tools.base import Tool, tool_parameters
from nanobot.agent.tools.schema import tool_parameters_schema


@tool_parameters(
    tool_parameters_schema(
        required=[],
    )
)
class GetK8sKubeConfigFilePath(Tool):
    """Get all available Kubernetes kubeconfig file paths with aliases."""
    _scopes = {"core"}

    @property
    def name(self) -> str:
        return "get_k8s_kube_config_file_path"

    @property
    def description(self) -> str:
        return (
            "Get all available Kubernetes kubeconfig file paths with their aliases. "
            "Returns a list of entries, each containing 'absolute_path' and 'alias' fields. "
            "Use this to discover available K8s environments before calling other K8s tools."
        )

    async def execute(self, **_kwargs) -> str:
        from nanobot.agent.tools.k8s.env import KubeConfigPath

        return json.dumps(KubeConfigPath, ensure_ascii=False, indent=2)
