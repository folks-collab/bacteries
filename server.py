import socket
import time


main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
main_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
main_socket.bind(("localhost", 22867))
main_socket.setblocking(False)
main_socket.listen(5)
print('сокет создан')

