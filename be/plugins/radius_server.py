#!/usr/bin/python
import sys
import logging
import enum
from dataclasses import dataclass
import requests
from pyrad import dictionary, packet, server
from . import utils


DEVICES_URL = 'http://127.0.0.1:8001/api/devices/'
SETTINGS_URL = 'http://127.0.0.1:8001/api/global_settings/1/'
TIMEOUT = 30
DEFAULT_SETTINGS = {
    'enforcement_mode': 'TRUST_AND_VERIFY'
}


log = logging.getLogger(sys.argv[0])


class ClientState(enum.Enum):
    CLIENT_UNKNOWN = 'unknown'
    CLIENT_PENDING = 'pending'
    CLIENT_BLOCKED = 'blocked'
    CLIENT_ALLOWED = 'allowed'


def get_settings():
    try:
        resp = requests.get(SETTINGS_URL, timeout=TIMEOUT)
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            log.debug('Settings not found. using defaults')
            return DEFAULT_SETTINGS
        raise

    return resp.json()


@dataclass
class Client:
    name: str
    mac_address: str
    ip_addr: str
    state: ClientState
    hostname: str | None = None
    obj_id: int | None = None

    @classmethod
    def from_pkt(cls, pkt):
        ipaddr = pkt.get('Framed-IP-Address', [''])[0]
        staid = pkt.get('Calling-Station-Id', [''])[0]
        name = pkt.get('User-Name', [''])[0]
        mac = staid.replace('-', ':').lower()
        log.debug('%s: MAC %s ip %s', name, mac, ipaddr)
        return cls(name=name, mac_address=mac, ip_addr=ipaddr,
                   state=ClientState.CLIENT_PENDING)

    def post(self):
        if not self.mac_address:
            return
        j = {'mac_address': self.mac_address,
             'status': 'pending'}
        if self.name:
            j['hostname'] = self.name
        if self.ip_addr:
            j['ip_address'] = self.ip_addr
        resp = requests.post(DEVICES_URL, json=j, timeout=TIMEOUT)
        resp.raise_for_status()
        log.debug(resp.json())

    def fetch(self):
        self.state = ClientState.CLIENT_UNKNOWN
        if not self.mac_address:
            return
        resp = requests.get(DEVICES_URL,
                            params={'mac_address': self.mac_address},
                            timeout=TIMEOUT)
        resp.raise_for_status()
        if not (j := resp.json()):
            # pylint: disable=broad-exception-raised
            raise Exception('Not found')
        j = j[0]
        self.obj_id = j['id']
        self.hostname = j['hostname']
        match j['status']:
            case 'blocked':
                self.state = ClientState.CLIENT_BLOCKED
            case 'allowed':
                self.state = ClientState.CLIENT_ALLOWED
            case 'pending':
                self.state = ClientState.CLIENT_PENDING

    def update(self):
        if self.obj_id is None:
            return
        resp = requests.patch(f'{DEVICES_URL}{self.obj_id}/',
                              json={'ip_address': self.ip_addr},
                              timeout=TIMEOUT)
        log.debug(resp.json())

    def get_create(self):
        try:
            self.fetch()
        except BaseException:  # pylint: disable=broad-exception-caught
            self.post()
            self.fetch()


class RadServer(server.Server):
    def HandleAuthPacket(self, pkt):
        log.debug('Received an authentication request')
        log.debug('Attributes:')
        for k, v in pkt.items():
            log.debug('%s: %s', k, v)

        reply = self.CreateReplyPacket(pkt)

        settings = get_settings()
        log.debug('enforcement_mode: %s', settings['enforcement_mode'])

        c = Client.from_pkt(pkt)
        c.get_create()
        state = c.state
        log.debug('MAC %s state is %s', c.mac_address, state)

        match state:
            case ClientState.CLIENT_UNKNOWN | ClientState.CLIENT_PENDING:
                if settings["enforcement_mode"] == 'LOCK':
                    reply.code = packet.AccessReject
                else:
                    reply.code = packet.AccessAccept
            case ClientState.CLIENT_BLOCKED:
                reply.code = packet.AccessReject
            case ClientState.CLIENT_ALLOWED:
                reply.code = packet.AccessAccept

        if reply.code == packet.AccessReject:
            log.info('Blocked %s [%s]', c.hostname, c.mac_address)

        self.SendReplyPacket(pkt.fd, reply)

    def HandleAcctPacket(self, pkt):
        log.debug('Received an accounting request')
        log.debug('Attributes:')
        for k, v in pkt.items():
            log.debug('%s: %s', k, v)

        reply = self.CreateReplyPacket(pkt)
        self.SendReplyPacket(pkt.fd, reply)

        c = Client.from_pkt(pkt)
        c.get_create()
        c.update()


if __name__ == '__main__':
    utils.common_init(['RADIUS_PASSWORD',
                       ('RADIUS_AUTH_PORT', '1812'),
                       ('RADIUS_ACCT_PORT', '1813')])

    auth_port = int(utils.ENV.RADIUS_AUTH_PORT)
    acct_port = int(utils.ENV.RADIUS_ACCT_PORT)

    log.info('Creating RADIUS Server. auth %s, acct %s', auth_port, acct_port)

    srv = RadServer(authport=auth_port, acctport=acct_port,
                    dict=dictionary.Dictionary('plugins/dictionary'))

    # add clients (address, secret, name)
    passwd = utils.ENV.RADIUS_PASSWORD.encode('utf-8')
    srv.hosts['0.0.0.0'] = server.RemoteHost('0.0.0.0', passwd, 'any')
    srv.BindToAddress('0.0.0.0')

    srv.Run()
