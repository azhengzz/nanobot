# coding=utf-8

from pathlib import Path

KUBE_CONFIG_DIR = Path(__file__).parent / "kube_config"

KubeConfigPath = [
    {
        'absolute_path': f'{KUBE_CONFIG_DIR / '192.168.81.7'}',
        'alias': ['192.168.81.7', 'Code&One压测环境']
    },
    {
        'absolute_path': f'{KUBE_CONFIG_DIR / '192.168.90.17'}',
        'alias': ['192.168.90.17', 'Repo&Wiki压测环境']
    },

]
