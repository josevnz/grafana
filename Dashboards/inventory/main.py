"""
Simple Webservice that provides required REST API for Grafana to use an Ansible inventory file to populate host and group
values
Author: Jose Vicente Nunez (kodegeek.com@protonmail.com)
"""
import os
from typing import Dict, Any
from pathlib import Path
import yaml
from fastapi import FastAPI

app = FastAPI()
inventory_data: Dict[str, Any] = {}
inventory_file = os.getenv('DASHBOARD_INVENTORY_FILE', Path.cwd().joinpath('hosts.yaml'))
PROMETHEUS_PORT = 9100


@app.on_event("startup")
async def startup_event():
    print(f"Loading host inventory file from '{inventory_file}'")
    with open(inventory_file, 'r') as yaml_data:
        inventory_data.update(yaml.safe_load(yaml_data))


@app.get("/")
async def root():
    return {"details": f"Ansible inventory API, relevant keys={len(inventory_data['all']['children'].keys())}"}


@app.get("/search")
async def search():
    groups = []
    for group in inventory_data['all']['children'].keys():
        groups.append(group)
    groups.sort(reverse=True)
    return groups


@app.get("/query")
async def default_query(enrich: bool = True):
    """
    This default endpoint is here to make it easier to test with Grafana if a group is not provided
    :param enrich:
    :return:
    """
    hosts = []
    for group in inventory_data['all']['children']:
        for host_data in inventory_data['all']['children'][group]['hosts']:
            if enrich:
                hosts.append(f"{host_data}:{PROMETHEUS_PORT}")
            else:
                hosts.append(host_data)
    hosts.sort(reverse=True)
    return hosts


@app.get("/query/{group}")
async def query(group: str, enrich: bool = True):
    hosts = []
    if group in inventory_data['all']['children']:
        for host_data in inventory_data['all']['children'][group]['hosts']:
            if enrich:
                hosts.append(f"{host_data}:{PROMETHEUS_PORT}")
            else:
                hosts.append(host_data)
        hosts.sort(reverse=True)
    return hosts
