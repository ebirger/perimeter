#!/usr/bin/python
import sys
import time
import json
import logging
import requests
from . import utils


log = logging.getLogger(sys.argv[0])


UNIFI_SITE_BASE = 'proxy/network/integrations/v1/sites'
UNIFI_CLIENTS_HISTORY = 'proxy/network/v2/api/site/default/clients/history'
PERIMETER_BASE = 'http://127.0.0.1:8001'
TIMEOUT = 30


def unifi_get(rel_path=None, params=None):
    headers = {'X-API-KEY': utils.ENV.UNIFI_TOKEN}
    url = f'{utils.ENV.UNIFI_BASE}/{rel_path}'
    resp = requests.get(url, headers=headers, timeout=TIMEOUT, params=params)
    resp.raise_for_status()
    ret = resp.json()
    log.debug(json.dumps(ret, indent=2))
    return ret


def get_unifi_site_id():
    try:
        resp = unifi_get(UNIFI_SITE_BASE)
        return resp['data'][0]['id']
    except:  # pylint: disable=bare-except
        log.exception('failed to get Unifi site ID')
        return None


def get_unifi_client_names(site_id):
    client_data = []
    while True:
        ret = unifi_get(f'{UNIFI_SITE_BASE}/{site_id}/clients',
                        params={'limit': 200, 'offset': len(client_data)})
        client_data += ret['data']
        total_count = ret['totalCount']
        n = len(client_data)
        if n >= total_count:
            break
        log.info('got %s/%s', n, total_count)

    return {mac: u['name'] for u in client_data if (mac := u.get('macAddress'))}


def get_unifi_historical_client_names():
    params = {
        'onlyNonBlocked': 'true',
        'includeUnifiDevices': 'true',
        'withinHours': '0',
    }
    ret = unifi_get(UNIFI_CLIENTS_HISTORY, params=params)
    return {mac: name for u in ret
            if ((mac := u.get('mac')) and (name := u.get('name')))}


def get_perimeter_clients():
    resp = requests.get(f'{PERIMETER_BASE}/api/devices/', timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()



def update_perimeter_client(c):
    requests.patch(f'{PERIMETER_BASE}/api/devices/{c["id"]}/',
                   json={'hostname': c['hostname']}, timeout=TIMEOUT)


def enrich_perimeter_clients(pcs, ucs):
    log.debug(json.dumps(ucs, indent=2))
    for c in pcs:
        if not (desired_name := ucs.get(c['mac_address'])):
            continue
        desired_name = desired_name.strip()
        if c['hostname'].strip() == desired_name:
            continue

        log.info('Updating device [%s,%s] name: "%s" -> "%s"', c['id'],
                 c['mac_address'], c['hostname'], desired_name)
        c['hostname'] = desired_name
        update_perimeter_client(c)


def main():
    utils.common_init(['UNIFI_TOKEN', 'UNIFI_BASE'])

    log.info('Starting unifi syncer')
    site_id = get_unifi_site_id()
    if not site_id:
        sys.exit(1)

    log.info('Unifi Site ID %s', site_id)

    while True:
        try:
            unifi_names = get_unifi_historical_client_names()
            unifi_names.update(get_unifi_client_names(site_id))
            enrich_perimeter_clients(get_perimeter_clients(), unifi_names)
        except:  # pylint: disable=bare-except
            log.exception('boom')

        time.sleep(60)


if __name__ == '__main__':
    main()
