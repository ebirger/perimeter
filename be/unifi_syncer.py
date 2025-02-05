#!/usr/bin/python
import os
import time
import json
import requests


UNIFI_BASE = 'https://unifi.birger.me'
CLIENTS_PATH = '/proxy/network/v2/api/site/default/clients/active'
PERIMETER_BASE = 'http://127.0.0.1:8001'


def get_unifi_clients():
    headers = {'X-API-KEY': os.environ.get('UNIFI_TOKEN')}
    resp = requests.get(f'{UNIFI_BASE}/{CLIENTS_PATH}', headers=headers)
    resp.raise_for_status()
    return resp.json()


def get_perimeter_clients():
    resp = requests.get(f'{PERIMETER_BASE}/api/devices/')
    resp.raise_for_status()
    return resp.json()


def update_perimeter_client(c):
    resp = requests.patch(f'{PERIMETER_BASE}/api/devices/{c["id"]}/',
                          json={'hostname': c['hostname']})
    resp.raise_for_status()


def enrich_perimeter_clients(pcs, ucs):
    ucs = {u['mac']: u for u in ucs}
    for c in pcs:
        if not (u := ucs.get(c['mac_address'])):
            continue
        
        desired_name = u['name']
        if c['hostname'] == desired_name:
            continue

        c['hostname'] = u['name']
        update_perimeter_client(c)

 
while True:    
    pcs = get_perimeter_clients()
    ucs = get_unifi_clients()
    enrich_perimeter_clients(pcs, ucs)
    time.sleep(60)
