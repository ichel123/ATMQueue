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
    grant = view.Grant(400, 370, 480, 270, 'Comic Sans MS', 15)

    # Instanciación de la cola.
    if params.ENABLE_PRIORITY:
        queue = logic.Priority_Server_Queue(params.SERVER_CAPACITY)
    else:
        queue = logic.SRTF_Server_Queue(params.SERVER_CAPACITY)

    def create_new_client(id: str, n_requests: int, n_priority: int) -> None:
        """Crea un nuevo cliente para uso del programa."""

        if not params.ENABLE_PRIORITY:
            n_priority = None

        queue_client = logic.Queue_Client(id,n_requests, time, n_priority)
        queue.enqueue(queue_client)
        grant.add_tag(str(queue_client.get_id()))
        new_table_line(queue_client)

    def new_table_line(queue_client: logic.Queue_Client, arrival_time: int = None) -> None:
        """Crea una nueva línea en la tabla con la información del cliente y el tiempo de llegada indicado."""
        table_data.loc[len(table_data)] = (
            str(queue_client.get_id()),                         # Id
            'Esperando',                                        # Estado
            time + 1 if arrival_time is None else arrival_time, # Tiempo de llegada
            queue_client.get_priority(),                        # Prioridad
            queue_client.get_number_of_requests(),              # Número de solicitudes.
            None,
            None,
            None,
            None
        )

    def expel_table_line(queue_client: logic.Queue_Client) -> pandas.Series:
        """Devuelve una fila con la infomarción calculada tras la expulsión de un proceso."""

        # Obtener todas las filas del proceso.
        client_rows = table_data[table_data['Proceso'] == queue_client.get_id()].iloc

        # Agregar el tiempo final en la última.
        client_rows[-1, table_data.columns.get_loc('T. Final')] = time + 1

        # Agregar el tiempo de retorno en la última.
        client_rows[-1, table_data.columns.get_loc('T. Retorno')] =\
            client_rows[-1]['T. Final'] - client_rows[-1]['T. Llegada']

        # Para calcular el tiempo de espera se inicia con el tiempo de retorno actual.
        client_rows[-1, table_data.columns.get_loc('T. Espera')] = client_rows[-1]['T. Retorno']
        # Se le resta la ráfaga ejecutada de cada fila del proceso.
        for client_row in client_rows:
            # Sólo se restan los que tienen el mismo tiempo de llegada.
            if client_row['T. Llegada'] != client_rows[-1]['T. Llegada']:
                continue
            
            client_rows[-1, table_data.columns.get_loc('T. Espera')] -=\
                client_row['T. Final'] - client_row['T. Comienzo']

        # Cambiar estado a expulsado.
        client_rows[-1, table_data.columns.get_loc('Estado')] = 'Expulsado'

        return client_rows[-1]

    # Clientes iniciales.
    for i in range(5):
        id = chr(ord('A') + i)
        create_new_client(id,random.randint(1,15),random.randint(1,5))

    # Cliente bloqueado actualmente.
    blocked_client: logic.Queue_Client = None

    # Instanciación de etiquetas
    time_tag = view.Tag(20, 370, f'Tiempo: {time + 1}', 'Comic Sans MS', 15, 'Black')
    critical_section_tag = view.Tag(20, 610, f'En sección crítica: -', 'Comic Sans MS', 15, 'Black')
    waiting_tag = view.Tag(200, 610, f'Procesos en espera: {queue.get_size() - 1}', 'Comic Sans MS', 15, 'Black')
    tag_list = [
        view.Tag(80, 450, 'Id:', 'Comic Sans MS', 15, 'Black'),
        view.Tag(20, 490, 'Solicitudes:', 'Comic Sans MS', 15, 'Black'),
        time_tag,
        critical_section_tag,
        waiting_tag
    ]

    if params.ENABLE_PRIORITY:
        tag_list.append(view.Tag(30, 530, 'Prioridad:', 'Comic Sans MS', 15, 'Black'))

    # Instanciación de cajas de texto
    textbox_list = []

    id_textbox = view.Textbox(120, 450, 100, 30, 2, 'Comic Sans MS', 15)
    textbox_list.append(id_textbox)

    requests_textbox = view.Textbox(120, 490, 100, 30, 2, 'Comic Sans MS', 15)
    textbox_list.append(requests_textbox)
    
    priority_textbox = view.Textbox(120, 530, 100, 30, 2, 'Comic Sans MS', 15)
    if params.ENABLE_PRIORITY:
        textbox_list.append(priority_textbox)

    # Instanciación de botones
    button_list = []

    automatic_button = view.Button(120, 370, 200, 30, 2, 'Encender Automático', 'Comic Sans MS', 15)
    automatic_button.box_color_idle = 'Red'
    button_list.append(automatic_button)

    manual_button = view.Button(120, 410, 200, 30, 2, 'Siguiente Paso', 'Comic Sans MS', 15)
    button_list.append(manual_button)

    addclient_button = view.Button(230, 450, 90, 110, 2, 'Añadir', 'Comic Sans MS', 15)
    button_list.append(addclient_button)

    block_button = view.Button(120, 570, 200, 30, 2, 'Bloquear Primero', 'Comic Sans MS', 15)
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
           or (blocked_client and id_textbox.text == blocked_client.get_id())\
           or id_textbox.text == '':
            id_textbox.text = '¡ERROR!'
            return

        try:
            requests = requests_textbox.text
            if requests == '':
                requests = random.randint(1, 15)
            else:
                requests = int(requests)
                if requests <= 0:
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

        past_service = queue.get_current_service()
        try: front_client = queue.get(1)
        except IndexError: front_client = None
        create_new_client(id_textbox.text, int(requests), int(priority))
        if queue.get_current_service() != past_service and front_client is not None:
            client_row = expel_table_line(front_client)
            table_data.loc[client_row.name] = client_row
            new_table_line(queue_client, client_row['T. Llegada'])
            table_data.iloc[-1, table_data.columns.get_loc('Estado')] = 'Esperando'

        id_textbox.text = ''
        requests_textbox.text = ''
        priority_textbox.text = ''

    addclient_button.action = addclient_button_action

    def block_button_action() -> None:
        """Bloquea o desbloquea un cliente dado."""
        
        global blocked_client
        if blocked_client:
            new_state = 'Esperando'
            block_button.tag = 'Bloquear Primero'
            queue_client = blocked_client
            blocked_client = None
            index = table_data[table_data['Proceso'] == queue_client.get_id()].iloc[-1].name
            queue.enqueue(queue_client)

        else:
            new_state = 'Bloqueado'
            block_button.tag = 'Desbloquear Bloqueado'
            queue_client = queue.get(1)
            blocked_client = queue_client
            index = table_data[table_data['Proceso'] == queue_client.get_id()].iloc[-1].name
            if queue.get_current_service() > 0:
                client_row = expel_table_line(queue_client)
                table_data.loc[client_row.name] = client_row
                new_table_line(queue_client, client_row['T. Llegada'])
                index = table_data.iloc[-1].name

            queue.remove(queue_client)

        table_data.loc[index, 'Estado'] = new_state

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
                if queue.get_size() > 1:
                    queue_client = queue.get(1)
                    grant.add_line(
                        current_tag=str(queue_client.get_id()),
                        blocked_tag=str(blocked_client.get_id()) if blocked_client else None
                    )
                    queue.dequeue()

                    # Dando tiempo de llegada a proceso actual.
                    client_row = table_data[table_data['Proceso'] == str(queue_client.get_id())].iloc[-1]
                    client_row['Estado'] = 'En Ejecución'
                    if client_row['T. Comienzo'] is None:
                        client_row['T. Comienzo'] = time

                    # Actulizar la nueva fila en la tabla.
                    table_data.loc[client_row.name] = client_row

                    # Cuando se terminó de atender a un cliente.
                    if queue.get_current_service() == 0 and queue.get_size() == 1 or queue.get(1) is not queue_client:
                        client_row = expel_table_line(queue_client)
                        if queue_client.is_done():
                            grant.remove_tag(str(queue_client.get_id()))
                            client_row['Estado'] = 'Terminado'
                        else:
                            new_table_line(queue_client, client_row['T. Llegada'])
                                    
                        # Actulizar la nueva fila en la tabla.
                        table_data.loc[client_row.name] = client_row

                # Cuando no hay clientes en fila.
                else:
                    grant.add_line(
                        blocked_tag=str(blocked_client.get_id()) if blocked_client else None
                    )

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

        if blocked_client or queue.get_size() > 1:
            block_button.active = True
        else:
            block_button.active = False
            
        for button in button_list:
            button.update()

        # Simulación Semáforo
        time_tag.tag = f'Tiempo: {time}'
        if queue.get_current_service() > 0 and queue.get_size() > 1:
            queue_client = queue.get(1)
            critical_section_tag.tag = f'En sección crítica: {queue_client.get_id()}'
            waiting_tag.tag = f'Procesos en espera: {queue.get_size() - 2}'

        else:
            critical_section_tag.tag = f'En seccion crítica: -'
            waiting_tag.tag = f'Procesos en espera: {queue.get_size() - 1}'

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
