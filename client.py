import socket


main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
main_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
main_socket.connect(("localhost", 22867))

while True:
    main_socket.send("привет".encode())

