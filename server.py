import socket
import time


main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
main_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
main_socket.bind(("localhost", 22867))
main_socket.setblocking(False)
main_socket.listen(5)
print('сокет создан')

players = []
while True:
    try:
        client_socket, addr = main_socket.accept()
        print('подключился', addr)
        client_socket.setblocking(False)
        players.append(client_socket)
    except BlockingIOError:
        pass

    for sock in players:
        try:
            data = sock.recv(1024).decode()
            print('получено', data)
        except:
            pass

    time.sleep(1)