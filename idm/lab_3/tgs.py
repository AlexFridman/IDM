import logging
from socketserver import ThreadingUDPServer, BaseRequestHandler
from time import time

import simplejson
from cryptography.fernet import Fernet

# input:
# {'encrypted_certificate', 'encrypted_as_mandate'}
# output:
# {'encrypted_tgs_session_key', 'encrypted_tgs_mandate'}

logging.basicConfig(level=logging.INFO)
PUBLIC_TEXT = 'public text'
TGS_KEY = b'AHorTta-0fQ1BpHpjY4IBILfRq8UjHweo2172i918-s='


class TGSHandler(BaseRequestHandler):
    def validate_mandate(self, mandate):
        client_ip, _ = self.client_address
        return client_ip == mandate['client_ip'] and \
               PUBLIC_TEXT == mandate['public_text'] and \
               time() - mandate['time'] < 86400

    def handle(self):
        data, sock = self.request
        params = simplejson.loads(data)

        ip, _ = self.client_address
        logging.info('[TGS] Request from {ip}'.format(ip=ip))

        encrypted_as_mandate = params['encrypted_as_mandate'].encode('utf-8')
        as_mandate = simplejson.loads(Fernet(TGS_KEY).decrypt(encrypted_as_mandate))
        as_session_key = as_mandate['as_session_key']

        if self.validate_mandate(as_mandate):
            session_key = Fernet.generate_key()
            encrypted_session_key = Fernet(as_session_key).encrypt(session_key)
            client_ip, _ = self.client_address
            mandate = {'tgs_session_key': session_key,
                       'public_text': PUBLIC_TEXT,
                       'time': time(),
                       'client_ip': client_ip}
            encrypted_mandate = Fernet(TGS_KEY).encrypt(simplejson.dumps(mandate).encode('utf-8'))
            sock.sendto(simplejson.dumps({'encrypted_tgs_session_key': encrypted_session_key,
                                          'encrypted_tgs_mandate': encrypted_mandate}).encode('utf-8'),
                        self.client_address)
        else:
            sock.close()


if __name__ == '__main__':
    serv = ThreadingUDPServer(('', 20001), TGSHandler)
    serv.serve_forever()
