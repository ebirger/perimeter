#!/usr/bin/python
import sys
import os
import time
import json
import logging
import requests
import utils


log = logging.getLogger(sys.argv[0])


UNIFI_BASE = 'https://unifi.birger.me'
UNIFI_SITE_BASE = 'proxy/network/integrations/v1/sites'
PERIMETER_BASE = 'http://127.0.0.1:8001'
TIMEOUT = 30


def unifi_get(rel_path=None, params=None):
    headers = {'X-API-KEY': os.environ.get('UNIFI_TOKEN')}
    url = f'{UNIFI_BASE}/{UNIFI_SITE_BASE}'
    if rel_path:
        url = '/'.join([url, rel_path])
    resp = requests.get(url, headers=headers, timeout=TIMEOUT, params=params)
    resp.raise_for_status()
    return resp.json()


def get_unifi_site_id():
    try:
        resp = unifi_get()
        return resp['data'][0]['id']
    except:
        log.exception('failed to get Unifi site ID')
        return None


def get_unifi_clients(site_id):
    ret = unifi_get(f'{site_id}/clients', params={'limit': 200})
    return ret['data']


def get_perimeter_clients():
    resp = requests.get(f'{PERIMETER_BASE}/api/devices/', timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def update_perimeter_client(c):
    log.info('Updating device %s, mac %s, to name %s', c['id'],
             c['mac_address'], c['hostname'])
    resp = requests.patch(f'{PERIMETER_BASE}/api/devices/{c["id"]}/',
                          json={'hostname': c['hostname']}, timeout=TIMEOUT)


def enrich_perimeter_clients(pcs, ucs):
    ucs = {mac: u for u in ucs if (mac := u.get('macAddress'))}
    log.debug(json.dumps(ucs, indent=2))
    for c in pcs:
        if not (u := ucs.get(c['mac_address'])):
            continue
        if not (desired_name := u.get('name')):
            continue
        desired_name = desired_name.strip()
        if c['hostname'].strip() == desired_name:
            continue

        log.info('Updating device [%s,%s] name: "%s" -> "%s"', c['id'],
                 c['mac_address'], c['hostname'], desired_name)
        c['hostname'] = desired_name
        update_perimeter_client(c)


if __name__ == '__main__':
    utils.log_setup()

    log.info('Starting unifi syncer')
    site_id = get_unifi_site_id()
    if not site_id:
        sys.exit(1)

    log.info('Unifi Site ID %s', site_id)

    while True:
        try:
            enrich_perimeter_clients(get_perimeter_clients(),
                                     get_unifi_clients(site_id))
        except:  # pylint: disable=bare-except
            log.exception('boom')

        time.sleep(60)
