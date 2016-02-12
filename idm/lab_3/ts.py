import logging
from socketserver import ThreadingUDPServer, BaseRequestHandler
from time import time

import simplejson
from cryptography.fernet import Fernet

# input:
# {'request_type=gen_key', 'username', 'encrypted_certificate', 'encrypted_as_mandate'}
# {'request_type=basic', 'username', 'data'}
# output:
# {'encrypted_key'}
# {'encrypted_data'}

logging.basicConfig(level=logging.INFO)
PUBLIC_TEXT = 'public text'
TGS_KEY = b'AHorTta-0fQ1BpHpjY4IBILfRq8UjHweo2172i918-s='
DATABASE = {}


class TSHandler(BaseRequestHandler):
    def validate_mandate(self, mandate):
        client_ip, _ = self.client_address
        return client_ip == mandate['client_ip'] and \
               PUBLIC_TEXT == mandate['public_text'] and \
               time() - mandate['time'] < 86400

    def handle(self):
        raw_data, sock = self.request
        params = simplejson.loads(raw_data)

        request_type = params.get('request_type', None)
        username = params['username']

        logging.info('[TS] Request from {username}'.format(username=username))

        if request_type == 'gen_key':
            encrypted_tgs_mandate = params['encrypted_tgs_mandate']
            tgs_mandate = simplejson.loads(Fernet(TGS_KEY).decrypt(encrypted_tgs_mandate.encode('utf-8')))
            tgs_session_key = tgs_mandate['tgs_session_key']
            if self.validate_mandate(tgs_mandate):
                session_key = Fernet.generate_key()
                DATABASE[username] = (session_key, time())
                encrypted_session_key = Fernet(tgs_session_key).encrypt(session_key)
                sock.sendto(simplejson.dumps({'encrypted_ts_session_key': encrypted_session_key}).encode('utf-8'),
                            self.client_address)
            else:
                sock.close()
        elif request_type == 'basic':
            key, key_creation_time = DATABASE[username]
            if time() - key_creation_time < 86400:
                encrypted_data = params['encrypted_data'].encode('utf-8')
                data = Fernet(key).decrypt(encrypted_data)

                user_ip, _ = self.client_address
                print('Request from {ip}: {data}'.format(ip=user_ip, data=data))
                sock.sendto(simplejson.dumps({'result': 'data is recieved'}).encode('utf-8'),
                            self.client_address)
            else:
                sock.close()


if __name__ == '__main__':
    serv = ThreadingUDPServer(('', 20002), TSHandler)
    serv.serve_forever()
