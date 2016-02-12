from socket import socket, AF_INET, SOCK_DGRAM
from cryptography.fernet import Fernet
import simplejson
from time import time

AS_ADDRESS = ('localhost', 20000)
TGS_ADDRESS = ('localhost', 20001)
TS_ADDRESS = ('localhost', 20002)
USERNAME = 'user_1'
CLIENT_KEY = b'2NZVT8vbYff8vuJcm1Q7mL1UJxbou2h90y8atnTNqmk='
PUBLIC_TEXT = 'public text'


def as_routine(as_address, username, client_key):
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.connect(as_address)

    params = {'username': username}
    data = simplejson.dumps(params).encode('utf-8')
    sock.send(data)

    as_response = simplejson.loads(sock.recv(8192))
    encrypted_as_session_key = as_response['encrypted_as_session_key'].encode('utf-8')
    as_session_key = Fernet(client_key).decrypt(encrypted_as_session_key)
    return as_session_key, as_response['encrypted_as_mandate']


def create_certificate(public_text):
    certificate = {'time': time(), 'public_text': public_text}
    return simplejson.dumps(certificate).encode('utf-8')


def tgs_routine(tgs_address, encrypted_as_mandate, as_session_key, public_text):
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.connect(tgs_address)

    certificate = create_certificate(public_text)
    encrypted_certificate = Fernet(as_session_key).encrypt(certificate)

    params = {'encrypted_certificate': encrypted_certificate,
              'encrypted_as_mandate': encrypted_as_mandate}
    data = simplejson.dumps(params).encode('utf-8')
    sock.send(data)

    tgs_response = simplejson.loads(sock.recv(8192))
    encrypted_tgs_session_key = tgs_response['encrypted_tgs_session_key']
    tgs_session_key = Fernet(as_session_key).decrypt(encrypted_tgs_session_key.encode('utf-8'))
    return tgs_session_key, tgs_response['encrypted_tgs_mandate']


def ts_gen_key_routine(ts_address, username, encrypted_tgs_mandate, tgs_session_key, public_text):
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.connect(ts_address)

    certificate = create_certificate(public_text)
    encrypted_certificate = Fernet(tgs_session_key).encrypt(certificate)

    params = {'request_type': 'gen_key',
              'username': username,
              'encrypted_certificate': encrypted_certificate,
              'encrypted_tgs_mandate': encrypted_tgs_mandate}
    data = simplejson.dumps(params).encode('utf-8')
    sock.send(data)

    ts_response = simplejson.loads(sock.recv(8192))
    encrypted_ts_session_key = ts_response['encrypted_ts_session_key'].encode('utf-8')
    ts_session_key = Fernet(tgs_session_key).decrypt(encrypted_ts_session_key)
    return ts_session_key


def ts_interaction_routine(ts_address, username, ts_session_key, data):
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.connect(ts_address)

    encrypted_data = Fernet(ts_session_key).encrypt(data)
    params = {'request_type': 'basic',
              'username': username,
              'encrypted_data': encrypted_data}
    data = simplejson.dumps(params).encode('utf-8')
    sock.send(data)

    ts_response = simplejson.loads(sock.recv(8192))
    result = ts_response['result']

    return result


def main():
    as_session_key, encrypted_as_mandate = as_routine(AS_ADDRESS, USERNAME, CLIENT_KEY)
    tgs_session_key, encrypted_tgs_mandate = tgs_routine(TGS_ADDRESS, encrypted_as_mandate,
                                                         as_session_key, PUBLIC_TEXT)
    ts_session_key = ts_gen_key_routine(TS_ADDRESS, USERNAME, encrypted_tgs_mandate,
                                        tgs_session_key, PUBLIC_TEXT)
    data = 'hello from user_1!!!'.encode('utf-8')
    print(ts_interaction_routine(TS_ADDRESS, USERNAME, ts_session_key, data))


if __name__ == '__main__':
    main()
