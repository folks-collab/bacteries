import socket
import pygame
import time

main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
main_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
main_socket.connect(("localhost", 22867))
pygame.init()

HEIGHT = 600
WEIGHT = 800
old = (0,0)
radius = 50
fps = 100
ck = pygame.time.Clock()

screen = pygame.display.set_mode((WEIGHT, HEIGHT))
pygame.display.set_caption('бактерии')
run = True

while run:
    events = pygame.event.get()
    

    for event in events:
        if pygame.mouse.get_focused():
            pos = pygame.mouse.get_pos()
            CC = (WEIGHT//2, HEIGHT//2)
            vector = (pos[0]-CC[0], pos[1]-CC[1])

            if vector != old:
                main_socket.send(f"<{vector[0]},{vector[1]}>".encode())
                time.sleep(0.1)
                old = vector

        if event.type == pygame.QUIT:
            run = False
    screen.fill('#cccccc')
    pygame.draw.circle(screen, '#ff0000', (WEIGHT//2, HEIGHT//2), radius)
    
pygame.quit()
