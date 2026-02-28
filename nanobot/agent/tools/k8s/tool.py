# coding=utf-8


import json

from nanobot.agent.tools.base import Tool


class GetK8sKubeConfigFilePath(Tool):
    """Get all available Kubernetes kubeconfig file paths with aliases."""

    name = "get_k8s_kube_config_file_path"
    description = (
        "Get all available Kubernetes kubeconfig file paths with their aliases. "
        "Returns a list of entries, each containing 'absolute_path' and 'alias' fields. "
        "Use this to discover available K8s environments before calling other K8s tools."
    )
    parameters = {
        "type": "object",
        "properties": {},
        "required": []
    }

    def __init__(self):
        pass

    async def execute(self, **kwargs) -> str:
        """Execute the tool to return all kubeconfig paths with aliases."""
        from nanobot.agent.tools.k8s.env import KubeConfigPath

        return json.dumps(KubeConfigPath, ensure_ascii=False, indent=2)
        

