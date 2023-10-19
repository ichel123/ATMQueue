"""Programa que simula una cola de cajero de manera gráfica usando Pygame."""

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
    queue_elements_font = pygame.font.Font(None, 20)
    state = State.LAST_IN
    waiting = True
    client: view.Client = None
    time = 1
    current_id =  0
    restart_time = 0
    id_changed = False
    restart_time_used = False
    counter_sols = 0
    headers = ["Proceso","T.LLegada","Ráfaga","T.Comienzo","T.Final","T.Retorno","T.Espera"]

    # Declaración del evento para cambio de estado y si la ejecución es automática.
    AUTOMATIC_STATE_CHANGE = pygame.USEREVENT + 1
    pygame.time.set_timer(AUTOMATIC_STATE_CHANGE, params.STATE_CHANGE_TIME, -1)
    automatic = False

    # Declaración del evento para el cambio de estado manual
    MANUAL_STATE_CHANGE = pygame.USEREVENT + 2

    # Diagrama de Grant
    grant = view.Grant(600, 300, 350, 250, 'Comic Sans MS', 15)

    # Tabla
    table = view.Table(50, 300, 70, 20, 4, len(headers), 1)
    
    # Instanciación de la cola y respectivos representantes gráficos
    queue = logic.ATM_Queue(params.ATM_CAPACITY)
    atm = view.ATM(params.X_INIT_POS, params.Y_INIT_POS, queue_elements_font)
    clients_queue = []
    current_clients = []
    clients_done = []
    x_pos = atm.rect.right + params.PADDING
    
    for i in range(len(headers)):
        table.set_value(headers[i],0,i)
    
    for i in range(3):
        queue_client = logic.Queue_Client(i, random.randint(1,15))
        clients_queue.append(
            view.Client(
                x_pos,
                params.Y_INIT_POS,
                queue_client,
                queue_elements_font,
                0.9 * params.STATE_CHANGE_TIME
            )
        )
        
        table.set_value(queue_client.get_id(),i+1,0)
        table.set_value(time,i+1,1)
        table.set_value(queue_client.get_number_of_requests(),i+1,2)
        x_pos = clients_queue[-1].rect.right + params.PADDING
        queue.enqueue(queue_client)
        current_clients.append([queue_client.get_id(),queue_client.get_number_of_requests(), time])
        grant.add_tag(str(queue_client.get_id()))
    
    # Instanciación de etiquetas
    time_tag = view.Tag(750, 5, f'Tiempo: {time}', 'Comic Sans MS', 15, 'Black')
    tag_list = [
        view.Tag(750, 100, 'Id:', 'Comic Sans MS', 15, 'Black'),
        view.Tag(820, 100, 'Solicitudes:', 'Comic Sans MS', 15, 'Black'),
        time_tag
    ]

    # Instanciación de cajas de texto
    textbox_list = []

    id_textbox = view.Textbox(775, 100, 40, 30, 2, 'Comic Sans MS', 15)
    textbox_list.append(id_textbox)

    requests_textbox = view.Textbox(910, 100, 40, 30, 2, 'Comic Sans MS', 15)
    textbox_list.append(requests_textbox)

    # Instanciación de botones
    button_list = []

    automatic_button = view.Button(750, 30, 200, 30, 2, 'Encender Automático', 'Comic Sans MS', 15)
    automatic_button.box_color_idle = 'Red'
    button_list.append(automatic_button)

    nextstep_button = view.Button(750, 65, 200, 30, 2, 'Siguiente Paso', 'Comic Sans MS', 15)
    button_list.append(nextstep_button)

    addclient_button = view.Button(750, 140, 200, 30, 2, 'Añadir Cliente', 'Comic Sans MS', 15)
    button_list.append(addclient_button)

    # Acciones de los botones
    def automatic_button_action():
        """Activa o desactiva el modo automático."""

        global automatic
        if not automatic:
            automatic = True
            automatic_button.tag = 'Apagar Automático'
            automatic_button.box_color_idle = 'Green'
        else:
            automatic = False
            automatic_button.tag = 'Encender Automático'
            automatic_button.box_color_idle = 'Red'
    automatic_button.action = automatic_button_action

    def nextstep_button_action():
        """Envía el evento de cambio de estado manual."""

        pygame.event.post(pygame.event.Event(MANUAL_STATE_CHANGE)) 
    nextstep_button.action = nextstep_button_action

    def addclient_button_action():
        """Añade un nuevo cliente a la cola y sale del estado HALT."""

        global id_textbox, requests_textbox, state

        if id_textbox.text in [str(queue_client.get_id()) for queue_client in list(queue)[1:]]:
            id_textbox.text = '¡ERROR!'
            return

        try:
            requests = int(requests_textbox.text)
        except ValueError:
            requests_textbox.text = '¡ERROR!'
            return

        queue_client = logic.Queue_Client(id_textbox.text, requests)

        try:
            x_pos = clients_queue[-1].rect.right + params.PADDING
        except IndexError:
            x_pos = atm.rect.right + params.PADDING

        clients_queue.append(
            view.Client(
                x_pos,
                params.Y_INIT_POS,
                queue_client,
                queue_elements_font,
                0.9 * params.STATE_CHANGE_TIME
            )
        )
        queue.enqueue(queue_client)
        current_clients.append([queue_client.get_id(),queue_client.get_number_of_requests(), time])
        grant.add_tag(str(queue_client.get_id()))
        table.add_row(20)
        table.set_value(queue_client.get_id(),table.get_total_rows()-1,0)
        table.set_value(time,table.get_total_rows()-1,1)
        table.set_value(queue_client.get_number_of_requests(),table.get_total_rows()-1,2)
        id_textbox.text = ''
        requests_textbox.text = ''

        if state is State.HALT:
            state = State.LAST_IN
    
    addclient_button.action = addclient_button_action

    # Ejecución del programa
    while True:
        for event in pygame.event.get():
            # Oprimir el botón de cerrar ventana.
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Cambio de estado automático.
            if event.type == AUTOMATIC_STATE_CHANGE:
                if automatic and waiting:
                    waiting = False
                    if state != State.HALT:
                        state = State((state.value + 1) % (len(State) - 1))

            # Cambio de estado manual.
            if event.type == MANUAL_STATE_CHANGE:
                if waiting:
                    waiting = False
                    if state != State.HALT:
                        state = State((state.value + 1) % (len(State) - 1))

            # Hacer click en una caja de texto.
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    for textbox in textbox_list:
                        textbox.check_active()

            # Escribir en las cajas de texto.
            if event.type == pygame.KEYDOWN:
                for textbox in textbox_list:
                    textbox.add_text(event.unicode)
            
        screen.fill('White')

        # Máquina de estados.
        if not waiting:
            if state is State.RESPOND_QUEUE:
                # Los procesos de este estado sólo se realizan una vez.
                waiting = True 
                try:
                    # Cliente a la cabeza de la cola.
                    client = clients_queue[0]
                    id_aux = client.queue_client.get_id()
                    queue.dequeue()
                    if current_id == 0 and id_aux == 0 and not id_changed:
                        current_clients[current_id].append(1)
                        id_changed = True

                    if current_id != id_aux or queue._Queue__size <= 2:

                        if len(current_clients[current_id]) < 7:
                            current_clients[current_id].append(time)  #Se agrega t_final
                            current_clients[current_id].append(current_clients[current_id][4] - current_clients[current_id][2])
                            current_clients[current_id].append(current_clients[current_id][5] - (current_clients[current_id][4] - current_clients[current_id][3]))
                            table.set_value(str(current_clients[current_id][3]),current_id + 1,3)
                            table.set_value(str(current_clients[current_id][4]),current_id + 1,4)
                            table.set_value(str(current_clients[current_id][5]),current_id + 1,5)
                            table.set_value(str(current_clients[current_id][6]),current_id + 1,6)
                            
                            if len(current_clients) == current_id + 1:
                                restart_time = time
                            if len(current_clients) > current_id + 1: 
                                current_clients[current_id+1].append(time) #Se agrega t_inicial para el siguiente cliente
                            current_id = id_aux
                        else:
                            if queue._Queue__size <= 2:
                                requests_counter += 1
                            
                            is_less_equals_cero = True if current_clients[current_id][1] - params.ATM_CAPACITY <= 0 else False
                            if (queue._Queue__size <= 2 and not is_less_equals_cero and requests_counter == current_clients[current_id][1] - params.ATM_CAPACITY):
                                requests_counter = 0
                                current_id = id_aux

                                if not restart_time_used:
                                    current_clients[current_id][3] = restart_time
                                    restart_time_used = True
                                table.add_row(20)
                                current_clients[current_id][1] = current_clients[current_id][1] - params.ATM_CAPACITY
                                current_clients[current_id][4] = time
                                current_clients[current_id][5] = current_clients[current_id][4] - current_clients[current_id][2]
                                current_clients[current_id][6] = current_clients[current_id][5] - (current_clients[current_id][4] - current_clients[current_id][3])
                                
                                table.set_value(str(current_id),table.get_total_rows()-1,0)
                                table.set_value(str(current_clients[current_id][1]),table.get_total_rows()-1,2)
                                table.set_value(str(current_clients[current_id][2]),table.get_total_rows()-1,1)
                                table.set_value(str(current_clients[current_id][3]),table.get_total_rows()-1,3)
                                table.set_value(str(current_clients[current_id][4]),table.get_total_rows()-1,4)
                                table.set_value(str(current_clients[current_id][5]),table.get_total_rows()-1,5)
                                table.set_value(str(current_clients[current_id][6]),table.get_total_rows()-1,6)

                                if len(current_clients) > current_id + 1: 
                                    current_clients[current_id+1][3] = time #Se agrega t_inicial para el siguiente cliente    
                                
                            else:
                                if queue._Queue__size > 2: 
                                    if not restart_time_used:
                                        current_clients[current_id][3] = restart_time
                                        restart_time_used = True
                                    table.add_row(20)
                                    current_clients[current_id][1] = current_clients[current_id][1] - params.ATM_CAPACITY
                                    current_clients[current_id][4] = time
                                    current_clients[current_id][5] = current_clients[current_id][4] - current_clients[current_id][2]
                                    current_clients[current_id][6] = current_clients[current_id][5] - (current_clients[current_id][4] - current_clients[current_id][3])
                                    
                                    table.set_value(str(current_id),table.get_total_rows()-1,0)
                                    table.set_value(str(current_clients[current_id][1]),table.get_total_rows()-1,2)
                                    table.set_value(str(current_clients[current_id][2]),table.get_total_rows()-1,1)
                                    table.set_value(str(current_clients[current_id][3]),table.get_total_rows()-1,3)
                                    table.set_value(str(current_clients[current_id][4]),table.get_total_rows()-1,4)
                                    table.set_value(str(current_clients[current_id][5]),table.get_total_rows()-1,5)
                                    table.set_value(str(current_clients[current_id][6]),table.get_total_rows()-1,6)

                                    
                                    if len(current_clients) > current_id + 1: 
                                        current_clients[current_id+1][3] = time #Se agrega t_inicial para el siguiente cliente 
                                    if len(current_clients) == current_id + 1:
                                        restart_time = time
                                        restart_time_used = False
                                    current_id = id_aux 
                    
                    time += 1
                    grant.add_line(str(client.queue_client.get_id()))
                    
                    if (queue.get_current_service() > 0):
                        state = State.LAST_IN

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
                            params.SCREEN_WIDTH,
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
                        grant.remove_tag(str(client.queue_client.get_id()))

            elif state is State.LAST_IN:
                # Mover al cliente a su nuevo lugar en la cola de espera (gráfico).
                client.move(pygame.time.get_ticks())
                if client.move_done():
                    waiting = True
                    clients_done.clear()

            elif state is State.HALT:
                if automatic:
                    automatic_button.performAction()
                automatic_button.active = False
                waiting = True

        # Actualizar los botones.
        for button in button_list:
            button.update()

        if state is not state.HALT:
            automatic_button.active = True

        # El botón de añadir cliente no funciona el último cliente de la fila no esté en la última posición.
        if not waiting or state is State.FIRST_OUT:
            addclient_button.active = False
        else:
            addclient_button.active = True

        # El botón nextstep_button sólo debe estar disponible si se está en estado de espera no automático.
        if not waiting or automatic or state is State.HALT:
            nextstep_button.active = False
        else:
            nextstep_button.active = True

        # Actualizando el contador de tiempo.
        time_tag.tag = f'Tiempo: {time}'

        # Dibujar los elementos en pantalla.
        atm.draw(screen, queue)
        grant.draw(screen)
        table.draw(screen)
        for client_it in clients_queue + clients_done:
            client_it.draw(screen, queue)

        for tag in tag_list:
            tag.draw(screen)

        for textbox in textbox_list:
            textbox.draw(screen)

        for button in button_list:
            button.draw(screen)
        
        # Actualizar pantalla y esperar.
        pygame.display.update()
        clock.tick()
