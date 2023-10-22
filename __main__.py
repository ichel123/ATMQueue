"""Programa que simula una cola de cajero de manera gráfica usando Pygame."""

import sys, pygame, random, pandas
import logic, view, params

if __name__ == '__main__':
    pygame.init()

    # Declaración de variables de ejecución
    screen = pygame.display.set_mode((params.SCREEN_WIDTH, params.SCREEN_HEIGHT))
    pygame.display.set_caption('Proceso de colas')
    clock = pygame.time.Clock()
    time = 0

    # Declaración de los eventos para atención y si la ejecución es automática.
    MANUAL_RESPOND = pygame.USEREVENT + 1
    AUTOMATIC_RESPOND = pygame.USEREVENT + 2
    pygame.time.set_timer(AUTOMATIC_RESPOND, params.AUTOMATIC_RESPOND_TIME, -1)
    automatic = False

    # Instanciación de la tabla y su representación gráfica.
    table_data = pandas.DataFrame(columns=('Proceso', 'Estado', 'T. Llegada', 'Prioridad', 'Ráfaga', 'T. Comienzo', 'T. Final', 'T. Retorno', 'T. Espera'))
    table = view.Table(table_data, 10, 10, 100, 20, 1, 7, 2, 'Comic Sans MS', 15)

    # Instanciación del diagrama de Grant.
    grant = view.Grant(400, 250, 480, 280, 'Comic Sans MS', 15)

    # Instanciación de la cola.
    queue = logic.Priority_Server_Queue(params.DEFAULT_SERVER_CAPACITY)

    def create_new_client(id, n_requests, n_priority):
        """Crea un nuevo cliente para uso del programa."""

        queue_client = logic.Queue_Client(id,n_requests, time, n_priority)
        queue.enqueue(queue_client)
        grant.add_tag(str(queue_client.get_id()))

        # Nueva fila en la tabla.
        table_data.loc[len(table_data)] = (
            str(queue_client.get_id()),             # Id
            'Esperando',                            # Estado
            time + 1,                               # Tiempo de llegada
            queue_client.get_priority(),            # Prioridad
            queue_client.get_number_of_requests(),  # Número de solicitudes.
            None,
            None,
            None,
            None
        )

    # Clientes iniciales.
    for i in range(5):
        create_new_client(i+1,random.randint(1,15),random.randint(1,5))

    # Lista de clientes bloquados.
    blocked: list[logic.Queue_Client] = []

    # Instanciación de etiquetas
    time_tag = view.Tag(30, 250, f'Tiempo: {time}', 'Comic Sans MS', 15, 'Black')
    tag_list = [
        view.Tag(80, 330, 'Id:', 'Comic Sans MS', 15, 'Black'),
        view.Tag(20, 370, 'Solicitudes:', 'Comic Sans MS', 15, 'Black'),
        view.Tag(30, 410, 'Prioridad:', 'Comic Sans MS', 15, 'Black'),
        view.Tag(80, 450, 'Id:', 'Comic Sans MS', 15, 'Black'),
        time_tag
    ]

    # Instanciación de cajas de texto
    textbox_list = []

    id_textbox = view.Textbox(120, 330, 100, 30, 2, 'Comic Sans MS', 15)
    textbox_list.append(id_textbox)

    requests_textbox = view.Textbox(120, 370, 100, 30, 2, 'Comic Sans MS', 15)
    textbox_list.append(requests_textbox)
    
    priority_textbox = view.Textbox(120, 410, 100, 30, 2, 'Comic Sans MS', 15)
    textbox_list.append(priority_textbox)

    block_textbox = view.Textbox(120, 450, 100, 30, 2, 'Comic Sans MS', 15)
    textbox_list.append(block_textbox)

    # Instanciación de botones
    button_list = []

    automatic_button = view.Button(120, 250, 200, 30, 2, 'Encender Automático', 'Comic Sans MS', 15)
    automatic_button.box_color_idle = 'Red'
    button_list.append(automatic_button)

    manual_button = view.Button(120, 290, 200, 30, 2, 'Siguiente Paso', 'Comic Sans MS', 15)
    button_list.append(manual_button)

    addclient_button = view.Button(230, 330, 90, 110, 2, 'Añadir', 'Comic Sans MS', 15)
    button_list.append(addclient_button)

    block_button = view.Button(230, 450, 90, 30, 2, 'Blq/Dsblq', 'Comic Sans MS', 15)
    button_list.append(block_button)


    # Acciones de los botones
    def automatic_button_action() -> None:
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

    def manual_button_action() -> None:
        """Envía el evento de cambio de estado manual."""

        pygame.event.post(pygame.event.Event(MANUAL_RESPOND)) 

    manual_button.action = manual_button_action

    def addclient_button_action() -> None:
        """Añade un nuevo cliente a la cola y sale del estado HALT."""

        global id_textbox, requests_textbox

        if    id_textbox.text in [str(queue_client.get_id()) for queue_client in list(queue)[1:]]\
           or id_textbox.text in [str(queue_client.get_id()) for queue_client in blocked]\
           or id_textbox.text == '':
            id_textbox.text = '¡ERROR!'
            return

        try:
            requests = requests_textbox.text
            if requests == '':
                requests = random.randint(1, 15)
            else:
                requests = int(requests)
                if requests <= 0 or requests > 15:
                    requests_textbox.text = '¡ERROR!'
                    return
        except ValueError:
            requests_textbox.text = '¡ERROR!'
            return
        try:
            priority = priority_textbox.text
            if priority == '':
                priority = random.randint(1, 5)
            else:
                priority = int(priority)
                if priority <= 0 or priority > 5:
                    priority_textbox.text = '¡ERROR!'
                    return
        except ValueError:
            priority_textbox.text = '¡ERROR!'
            return

        create_new_client(id_textbox.text, int(requests), int(priority))

        id_textbox.text = ''
        requests_textbox.text = ''
        priority_textbox.text = ''

    addclient_button.action = addclient_button_action

    def block_button_action() -> None:
        """Bloquea o desbloquea un cliente dado."""

        searched_list = list(queue)[1:]
        other_list = blocked
        if block_textbox.text not in [str(queue_client.get_id()) for queue_client in list(queue)[1:]]:
            if block_textbox.text not in [str(queue_client.get_id()) for queue_client in blocked]:
                block_textbox.text = '¡ERROR!'
                return
            
            searched_list, other_list = other_list, searched_list
        
        queue_client = None
        for queue_client in searched_list:
            if str(queue_client.get_id()) == block_textbox.text:
                break

        client_row = table_data[table_data['Proceso'] == str(queue_client.get_id())].iloc[-1]

        if searched_list is not blocked:
            queue.remove(queue_client)
            blocked.append(queue_client)
            client_row['Estado'] = 'Bloqueado'

        else:
            blocked.remove(queue_client)
            queue.enqueue(queue_client)
            client_row['Estado'] = 'Esperando'

        table_data.loc[client_row.name] = client_row

    block_button.action = block_button_action

    # Ejecución del programa
    while True:
        for event in pygame.event.get():
            # Oprimir el botón de cerrar ventana.
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Atención a la cola.
            if event.type == MANUAL_RESPOND or event.type == AUTOMATIC_RESPOND and automatic:
                time += 1
                # Sólo si hay clientes en fila.
                if queue.get_size() >= 2:
                    queue_client = queue.get(1)
                    grant.add_line(str(queue_client.get_id()))

                    # Localizar el cliente en la tabla.
                    client_row = table_data[table_data['Proceso'] == str(queue_client.get_id())].iloc[-1]
                    client_row['Estado'] = 'En Ejecución'
                    if client_row['T. Comienzo'] is None:
                        client_row['T. Comienzo'] = time

                    queue.dequeue()
                    # Cuando se terminó de atender a un cliente.
                    if queue.get_current_service() == 0:
                        client_row['T. Final'] = time + 1
                        client_row['T. Retorno'] = client_row['T. Final'] - client_row['T. Llegada']
                        client_row['T. Espera'] = client_row['T. Retorno'] - client_row['Ráfaga']
                        client_row['Estado'] = 'Terminado'
                        grant.remove_tag(str(queue_client.get_id()))

                    # Actulizar la nueva fila en la tabla.
                    table_data.loc[client_row.name] = client_row

                # Cuando no hay clientes en fila.
                else:
                    grant.add_line()

            # Hacer click en una caja de texto.
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    for textbox in textbox_list:
                        textbox.check_active()

            # Escribir en las cajas de texto.
            if event.type == pygame.KEYDOWN:
                for textbox in textbox_list:
                    textbox.add_text(event.unicode)

        # Llenar la pantalla de blanco.
        screen.fill('White')

        # Actualizando elementos.
        if automatic:
            manual_button.active = False
        else:
            manual_button.active = True
            
        for button in button_list:
            button.update()

        time_tag.tag = f'Tiempo: {time}'

        # Dibujando elementos.
        for tag in tag_list:
            tag.draw(screen)

        for textbox in textbox_list:
            textbox.draw(screen)

        for button in button_list:
            button.draw(screen)

        table.draw(screen)
        grant.draw(screen)

        # Actualizar pantalla y esperar.
        pygame.display.update()
        clock.tick()
