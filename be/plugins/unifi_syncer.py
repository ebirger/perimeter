#!/usr/bin/python
import sys
import os
import time
import logging
import requests
from . import utils


log = logging.getLogger(sys.argv[0])


UNIFI_BASE = 'https://unifi.birger.me'
CLIENTS_PATH = '/proxy/network/v2/api/site/default/clients/active'
PERIMETER_BASE = 'http://127.0.0.1:8001'
TIMEOUT = 30


def get_unifi_clients():
    headers = {'X-API-KEY': os.environ.get('UNIFI_TOKEN')}
    resp = requests.get(f'{UNIFI_BASE}/{CLIENTS_PATH}', headers=headers,
                        timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def get_perimeter_clients():
    resp = requests.get(f'{PERIMETER_BASE}/api/devices/', timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def update_perimeter_client(c):
    resp = requests.patch(f'{PERIMETER_BASE}/api/devices/{c["id"]}/',
                          json={'hostname': c['hostname']}, timeout=TIMEOUT)
    resp.raise_for_status()


def enrich_perimeter_clients(pcs, ucs):
    ucs = {mac: u for u in ucs if (mac := u.get('mac'))}
    for c in pcs:
        if not (u := ucs.get(c['mac_address'])):
            continue
        if not (desired_name := u.get('name')):
            continue
        if c['hostname'] == desired_name:
            continue

        c['hostname'] = u['name']
        update_perimeter_client(c)


if __name__ == '__main__':
    utils.log_setup()

    log.info('Starting unifi syncer')

    while True:
        try:
            enrich_perimeter_clients(get_perimeter_clients(),
                                     get_unifi_clients())
        except:  # pylint: disable=bare-except
            pass

        time.sleep(60)
