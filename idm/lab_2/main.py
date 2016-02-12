import _md5


def send(message):
    hash_ = _md5.md5(message).digest()
    return message + hash_


def recieve(message):
    hash_ = message[-16:]
    if is_modified(message[:-16], hash_):
        raise Exception('The message was modified!')
    return message[:-16]


def is_modified(message, hash_):
    return _md5.md5(message).digest() != hash_


IN_FILE = 'in.txt'


def main():
    # read message
    message = open(IN_FILE, 'rb').read()
    # sign message with md5 hasg
    signed_message = send(message)
    # recieve message and check its consistent
    recieved_message = recieve(signed_message)
    print('All is OK, message:', recieved_message)
    # modify signed message and check recieve procedure
    signed_message = bytearray(signed_message)
    signed_message[0] = 0
    recieved_message = recieve(signed_message)


if __name__ == '__main__':
    main()
