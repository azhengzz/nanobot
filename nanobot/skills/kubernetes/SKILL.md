---
name: kubernetes
description: "Kubernetes cluster access via kubectl-safe wrapper. When users mention kubectl, k8s, or Kubernetes, I MUST use this skill's safe wrapper; direct kubectl usage is prohibited. keywords: kubernetes, k8s, deployment, pod, service, helm, kubectl, cluster, ingress."
metadata: {"nanobot":{"emoji":"☸️","requires":{"bins":["kubectl-safe"]},"os":["linux","darwin","win32"]}}
---

Use the safe wrapper `kubectl-safe` CLI to interact with Kubernetes clusters securely.

## Prerequisites

## Best Practices

1. Use the `get_k8s_kube_config_file_path` tool to obtain the kubeconfig file path
2. **ALWAYS use the safe wrapper** instead of direct kubectl:
   ```bash
   # ✅ CORRECT - Use safe wrapper
   kubectl-safe --kubeconfig <path> get pods
   
   # ❌ WRONG - Never use direct kubectl
   # kubectl --kubeconfig <path> get pods
   ```

## Important Notes

1. **⚠️ Strict Read-Only Policy**: `kubectl` commands are ABSOLUTELY restricted to query operations only.  
    ❌ **NEVER execute these commands** (the safe wrapper will block them):
    ```bash
    kubectl-safe delete
    kubectl-safe apply
    kubectl-safe create
    kubectl-safe edit
    kubectl-safe rollout
    kubectl-safe patch
    kubectl-safe replace
    kubectl-safe scale
    ```
2. **Safety Check**: Before any kubectl command, ALWAYS verify it starts with:
    ```bash
    kubectl-safe --kubeconfig <path> get
    kubectl-safe --kubeconfig <path> describe
    kubectl-safe --kubeconfig <path> logs
    kubectl-safe --kubeconfig <path> top
    ```
3. **If you need to modify resources**
    - Do NOT attempt to run modification commands directly
    - Instead, print the exact command for the user to run manually
    - Example: "Please run this command manually if needed: kubectl delete pod xxx"
4. **Self-Check**: Before executing any command, ask yourself:
    - "Does this command modify anything?"
    - "Would I be comfortable running this in production?"
    - If answer is NO to either, DO NOT execute it.
