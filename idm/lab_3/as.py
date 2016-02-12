import logging
from socketserver import ThreadingUDPServer, BaseRequestHandler
from time import time

import simplejson
from cryptography.fernet import Fernet

# input:
# {'username'}
# output:
# {'encrypted_as_session_key', 'encrypted_as_mandate'}

logging.basicConfig(level=logging.INFO)
DATABASE = {
    'user_1': b'2NZVT8vbYff8vuJcm1Q7mL1UJxbou2h90y8atnTNqmk=',
    'user_2': b'eBPeNlfHlHwPQR7-R__KCducAD3jUSAp0E3exFw3M0o='
}

PUBLIC_TEXT = 'public text'
TGS_KEY = b'AHorTta-0fQ1BpHpjY4IBILfRq8UjHweo2172i918-s='


class ASHandler(BaseRequestHandler):
    def handle(self):
        data, sock = self.request
        params = simplejson.loads(data)
        username = params['username']

        logging.info('[AS] Request from {username}'.format(username=username))

        if username in DATABASE:
            session_key = Fernet.generate_key()
            client_key = DATABASE[username]
            encrypted_session_key = Fernet(client_key).encrypt(session_key)
            client_ip, _ = self.client_address
            mandate = {'as_session_key': session_key,
                       'public_text': PUBLIC_TEXT,
                       'time': time(),
                       'client_ip': client_ip}
            encrypted_mandate = Fernet(TGS_KEY).encrypt(simplejson.dumps(mandate).encode('utf-8'))
            sock.sendto(simplejson.dumps({'encrypted_as_session_key': encrypted_session_key,
                                          'encrypted_as_mandate': encrypted_mandate}).encode('utf-8'),
                        self.client_address)
        else:
            sock.close()


if __name__ == '__main__':
    serv = ThreadingUDPServer(('', 20000), ASHandler)
    serv.serve_forever()
