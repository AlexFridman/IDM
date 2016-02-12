from pyDes import des, PAD_PKCS5
import argparse


# usage
# python3 des.py -M encrypt -K 12345678 -I in.txt -O encrypted.txt
# python3 des.py -M decrypt -K 12345678 -I encrypted.txt -O decrypted.txt

def main():
    parser = argparse.ArgumentParser(description='DES algorith demo.')
    parser.add_argument('--mode', '-M', type=str,
                        help='Mode of work (encrypt, decrypt)')
    parser.add_argument('--key', '-K', type=str,
                        help='Private key')
    parser.add_argument('--in_file', '-I', type=str,
                        help='Input file')
    parser.add_argument('--out_file', '-O', type=str,
                        help='Output file')

    args = parser.parse_args()

    with open(args.in_file, 'rb') as in_f, \
            open(args.out_file, 'wb+') as out_f:
        if args.mode == 'encrypt':
            out_f.write(des(args.key, padmode=PAD_PKCS5).encrypt(in_f.read()))
        else:
            out_f.write(des(args.key, padmode=PAD_PKCS5).decrypt(in_f.read()))


if __name__ == '__main__':
    main()
