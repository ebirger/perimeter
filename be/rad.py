#!/usr/bin/python
import sys
import requests
import enum
from dataclasses import dataclass
from pyrad import dictionary, packet, server


DEVICES_URL = 'http://127.0.0.1:8001/api/devices/'


class ClientState(enum.Enum):
    CLIENT_UNKNOWN = 'unknown'
    CLIENT_PENDING = 'pending'
    CLIENT_BLOCKED = 'blocked'
    CLIENT_ALLOWED = 'allowed'


@dataclass
class Client:
    name: str
    mac_address: str
    ip_addr: str
    state: ClientState
    obj_id: int | None = None

    @classmethod
    def from_pkt(cls, pkt):
        ipaddr = pkt.get('Framed-IP-Address', [''])[0]
        staid = pkt.get('Calling-Station-Id', [''])[0]
        name = pkt.get('User-Name', [''])[0]
        mac = staid.replace('-', ':').lower()
        print(f'{name}: MAC {mac} ip {ipaddr}')
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
        resp = requests.post(DEVICES_URL, json=j)
        resp.raise_for_status()
        print(resp.json())

    def fetch(self):
        self.state = ClientState.CLIENT_UNKNOWN
        if not self.mac_address:
            return
        resp = requests.get(DEVICES_URL,
                            params={'mac_address': self.mac_address})
        resp.raise_for_status()
        if not (j := resp.json()):
            raise Exception('Not found')
        j = j[0]
        self.obj_id = j['id']
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
                              json={'ip_address': self.ip_addr})
        print(resp.json())

    def get_create(self):
        try:
            self.fetch()
        except Exception as ex:
            self.post()
            self.fetch()


class RadServer(server.Server):
    def HandleAuthPacket(self, pkt):
        print('Received an authentication request')
        print('Attributes:')
        for attr in pkt.keys():
            print(f'{attr}: {pkt[attr]}')
        sys.stdout.flush()

        reply = self.CreateReplyPacket(pkt)

        c = Client.from_pkt(pkt)
        c.get_create()
        state = c.state
        print(f'MAC {c.mac_address} state is {state}')
        sys.stdout.flush()

        match state:
            case ClientState.CLIENT_UNKNOWN:
                c.post()
                # reply.code = packet.AccessReject
                reply.code = packet.AccessAccept
            case ClientState.CLIENT_BLOCKED:
                reply.code = packet.AccessReject
            case ClientState.CLIENT_ALLOWED:
                reply.code = packet.AccessAccept

        self.SendReplyPacket(pkt.fd, reply)

    def HandleAcctPacket(self, pkt):
        print('Received an accounting request')
        print('Attributes:')
        for attr in pkt.keys():
            print(f'{attr}: {pkt[attr]}')
        sys.stdout.flush()

        reply = self.CreateReplyPacket(pkt)
        self.SendReplyPacket(pkt.fd, reply)
        
        c = Client.from_pkt(pkt)
        c.get_create()
        c.update()


if __name__ == '__main__':
    AUTH_PORT = 1911
    ACCT_PORT = 1912
    
    print(f'Creating RADIUS Server. auth {AUTH_PORT}, acct {ACCT_PORT}')
    sys.stdout.flush()
    srv = RadServer(authport=AUTH_PORT, acctport=ACCT_PORT,
                     dict=dictionary.Dictionary('dictionary'))

    # add clients (address, secret, name)
    srv.hosts['0.0.0.0'] = server.RemoteHost('0.0.0.0', b'fufu', 'any')
    srv.BindToAddress('0.0.0.0')

    srv.Run()
