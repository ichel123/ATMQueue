"""Programa que simula una cola de cajero de manera gráfica usando Pygame."""

import sys
sys.path.append('RUTA_COMPLETA_A_PYTHON_3.11/lib')

import sys, pygame, random, enum
import logic, view, params

class State(enum.Enum):
    """Representa los estados por los que pasa el programa."""

    RESPOND_QUEUE = 0
    FIRST_OUT = 1
    MOVING = 2
    LAST_IN = 3
    HALT = 4

if __name__ == '__main__':
    pygame.init()

    # Declaración de variables de ejecución
    screen = pygame.display.set_mode((params.SCREEN_WIDTH, params.SCREEN_HEIGHT))
    pygame.display.set_caption('Proceso de colas')
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 20)
    state = State.LAST_IN
    waiting = True
    client: view.Client = None

    button = view.Button(20, 500, 200, 100, 2, 'Botón', 'Fira Code', 10, lambda: print('Oprimido'))
    textbox = view.Textbox(20, 400, 200, 30, 2, 'Arial', 15)
    table = view.Table(300, 400, 100, 20, 4, 6)
    table.set_value('perrito', 1, 1)

    # Declaración del evento para cambio de estado y su respectivo temporizador.
    STATE_CHANGE = pygame.USEREVENT + 1
    pygame.time.set_timer(STATE_CHANGE, params.STATE_CHANGE_TIME, -1)

    # Instanciación de la cola y respectivos representantes gráficos
    queue = logic.ATM_Queue()
    atm = view.ATM(params.X_INIT_POS, params.Y_INIT_POS, font)
    clients_queue = []
    clients_done = []
    x_pos = atm.rect.right + params.PADDING
    for i in range(5):
        queue_client = logic.Queue_Client(i, random.randint(1,15))
        clients_queue.append(
            view.Client(
                x_pos,
                params.Y_INIT_POS,
                queue_client,
                font,
                0.9 * params.STATE_CHANGE_TIME
            )
        )
        x_pos = clients_queue[-1].rect.right + params.PADDING
        queue.enqueue(queue_client)

    # Ejecución del programa
    while True:
        for evento in pygame.event.get():
            # Oprimir el botón de cerrar ventana.
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Cambio de estado
            if evento.type == STATE_CHANGE:
                waiting = False
                if state != State.HALT:
                    state = State((state.value + 1) % (len(State) - 1))

            if evento.type == pygame.MOUSEBUTTONDOWN:
                textbox.check_active()

            if evento.type == pygame.KEYDOWN:
                textbox.add_text(evento.unicode)

        screen.fill('White')
        # Máquina de estados
        if not waiting:
            if state is State.RESPOND_QUEUE:
                # Los procesos de este estado sólo se realizan una vez.
                waiting = True 
                try:
                    # Cliente a la cabeza de la cola.
                    client = clients_queue[0]
                    queue.dequeue()

                    # Si el cliente finaliza, sale de la lista de clientes en espera (estructura).
                    if client.queue_client.is_done():
                        clients_queue.remove(client)
                        clients_done.append(client)
                    
                    # Mover el cliente fuera de la cola de espera (gráfico).
                    client.set_destination_point(
                        client.rect.x,
                        client.rect.bottom + params.PADDING
                    )

                # Cuando se han terminado los clientes en la cola de espera.
                except IndexError:
                    state = State.HALT

            elif state is State.FIRST_OUT:
                # El cliente se mueve a la nueva posición.
                client.move(pygame.time.get_ticks())

                # Al llegar a la posición, se ejecutan estos procesos una sola vez.
                if client.move_done():
                    waiting = True

                    # Mover el segundo cliente a la cabeza (gráfico).
                    if clients_queue and clients_queue[0] is not client:
                        clients_queue[0].set_destination_point(
                            client.rect.x,
                            clients_queue[0].rect.y
                        )
                    # Mover a todos los demás clientes a su nueva posición (gráfico).
                    for i, client_it in enumerate(clients_queue[1:]):
                        client_it.set_destination_point(
                            clients_queue[i].rect.x,
                            client_it.rect.y
                        )

                    # Mover al cliente al final de la cola (gráfico).
                    if clients_queue and clients_queue[0] is client:
                        client.set_destination_point(
                            clients_queue[-1].rect.left,
                            client.rect.y
                        )
                    else: # O a la cola de terminados, si corresonde (gráfico).
                        client.set_destination_point(
                            params.SCREEN_WIDTH
                                - (client.rect.width + params.PADDING) * len(clients_done),
                            client.rect.y
                        )

                    # Si corresponde, mover el primer cliente al final de la cola (estructura).
                    if clients_queue and clients_queue[0] is client:
                        clients_queue.append(clients_queue.pop(0))

            elif state is State.MOVING:
                # Todos los clientes se mueven a su nueva posición.
                for client_it in clients_queue:
                    client_it.move(pygame.time.get_ticks())
                client.move(pygame.time.get_ticks())

                # Al llegar a la posición, se ejecutan estos procesos una sola vez.
                if client.move_done():
                    waiting = True
                    # Volver a meter al cliente a la cola (gráfico).
                    if not client.queue_client.is_done():
                        client.set_destination_point(
                            client.rect.x,
                            params.Y_INIT_POS
                        )
                    else: # O, si ya terminó, saltarse el estado de volver a entrar.
                        state = State.LAST_IN

            elif state is State.LAST_IN:
                # Mover al cliente a su nuevo lugar en la cola de espera (gráfico).
                client.move(pygame.time.get_ticks())

        # Revisar si se oprime el botón
        button.update()

        # Dibujar los elementos en pantalla.
        atm.draw(screen, queue)
        for client_it in clients_queue + clients_done:
            client_it.draw(screen, queue)
        
        button.draw(screen)
        textbox.draw(screen)
        table.draw(screen)

        # Actualizar pantalla y esperar.
        pygame.display.update()
        clock.tick()
