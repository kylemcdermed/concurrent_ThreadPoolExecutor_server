import socket
import sys
from concurrent.futures import ThreadPoolExecutor
from enum import Enum


ProcessingState = Enum('ProcessingState', 'WAIT_FOR_MSG IN_MSG')


def serve_connection(sockobj, client_address):
    print(f'{client_address} connected')
    sockobj.sendall(b'*')
    state = ProcessingState.WAIT_FOR_MSG

    while True:
        try:
            buf = sockobj.recv(1024)
            if not buf:
                break
        except IOError:
            break

        for b in buf:
            if state == ProcessingState.WAIT_FOR_MSG:
                if b == ord(b'^'):
                    state = ProcessingState.IN_MSG
            elif state == ProcessingState.IN_MSG:
                if b == ord(b'$'):
                    state = ProcessingState.WAIT_FOR_MSG
                else:
                    sockobj.send(bytes([b + 1]))
            else:
                assert False

    print(f'{client_address} done')
    sys.stdout.flush()
    sockobj.close()


def main():
    HOST = 'localhost'
    PORT = 8080

    with ThreadPoolExecutor(max_workers=5) as pool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sockobj:
            sockobj.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sockobj.bind((HOST, PORT))
            sockobj.listen(15)
            print(f"Server listening on {HOST}:{PORT}")

            try:
                while True:
                    client_socket, client_address = sockobj.accept()
                    pool.submit(serve_connection, client_socket, client_address)
            except KeyboardInterrupt:
                print("Server shutting down")
                sockobj.close()


if __name__ == '__main__':
    main()
