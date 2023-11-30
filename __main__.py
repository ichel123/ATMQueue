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
    grant = view.Grant(450, 370, 480, 270, 'Comic Sans MS', 15)

    # Instanciación de la cola.
    multi_queue = logic.Multi_Queue_Server_Queue(
        logic.FIFO_Server_Queue(params.SERVER_CAPACITY),
        logic.FIFO_Server_Queue(),
        logic.Priority_Server_Queue(),
        max_priority=params.MAX_PRIORITY
    )

    queue_tables = []
    queue_table_names = []

    def create_new_client(id: str, n_requests: int, n_priority: int) -> None:
        """Crea un nuevo cliente para uso del programa."""

        queue_client = logic.Queue_Client(id,n_requests, time, n_priority)
        multi_queue.enqueue(queue_client)
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

    def new_queue_table(arrival_time: int = None):
        """Trae la información de los clientes de cada cola y las dibuja."""
        names = ['Round Robin', 'FCFS', 'Prioridad']
        y_position = 300
        for i in range(len(multi_queue.queues)):
            # Crear un título para la tabla
            title_tag = view.Tag(10, y_position - 20, 'Tabla: ' + names[i], 'Comic Sans MS', 15, 'Black')
            
            view.Tag(950, 170, 'Prioridad:', 'Comic Sans MS', 15, 'Black'),
            queue_data = {'Proceso': [], 'T. Llegada': [], 'Ráfaga': []}
            clients_in_queue = multi_queue.get_clients_in_queue(i)

            for client in clients_in_queue:
                queue_data['Proceso'].append(str(client['id']))
                queue_data['T. Llegada'].append(time + 1 if arrival_time is None else arrival_time)
                queue_data['Ráfaga'].append(client['requests'])
            queue_table = view.Table(pandas.DataFrame(queue_data), 10, y_position, 100, 20, 1, 5, 2, 'Comic Sans MS', 15)
            queue_tables.append(queue_table)
            
            # Dibujar el título antes de la tabla
            queue_table_names.append(title_tag)
            queue_table.draw(screen)
            
            y_position += 130
            print(f"queue_data {i}: {queue_data}")
        
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

    # print(multi_queue.elementos())
    new_queue_table(1)
    # Cliente bloqueado actualmente.
    blocked_client: logic.Queue_Client = None

    # Instanciación de etiquetas
    time_tag = view.Tag(950, 10, f'Tiempo: {time + 1}', 'Comic Sans MS', 15, 'Black')
    critical_section_tag = view.Tag(500, 300, f'En sección crítica: -', 'Comic Sans MS', 15, 'Black')
    waiting_tag = view.Tag(680, 300, f'Procesos en espera: {multi_queue.get_size()}', 'Comic Sans MS', 15, 'Black')
    tag_list = [
        view.Tag(950, 90, 'Id:', 'Comic Sans MS', 15, 'Black'),
        view.Tag(950, 130, 'Solicitudes:', 'Comic Sans MS', 15, 'Black'),
        view.Tag(950, 170, 'Prioridad:', 'Comic Sans MS', 15, 'Black'),
        time_tag,
        critical_section_tag,
        waiting_tag
    ]

    # Instanciación de cajas de texto
    textbox_list = []

    id_textbox = view.Textbox(1050, 90, 100, 30, 2, 'Comic Sans MS', 15)
    textbox_list.append(id_textbox)

    requests_textbox = view.Textbox(1050, 130, 100, 30, 2, 'Comic Sans MS', 15)
    textbox_list.append(requests_textbox)
    
    priority_textbox = view.Textbox(1050, 170, 100, 30, 2, 'Comic Sans MS', 15)
    textbox_list.append(priority_textbox)

    # Instanciación de botones
    button_list = []

    automatic_button = view.Button(1050, 10, 200, 30, 2, 'Encender Automático', 'Comic Sans MS', 15)
    automatic_button.box_color_idle = 'Red'
    button_list.append(automatic_button)

    manual_button = view.Button(1050, 50, 200, 30, 2, 'Siguiente Paso', 'Comic Sans MS', 15)
    button_list.append(manual_button)

    addclient_button = view.Button(1160, 90, 90, 110, 2, 'Añadir', 'Comic Sans MS', 15)
    button_list.append(addclient_button)

    block_button = view.Button(1050, 210, 200, 30, 2, 'Bloquear', 'Comic Sans MS', 15)
    button_list.append(block_button)

    # multi_queue.__iter__()
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

        if    id_textbox.text in [str(queue_client.get_id()) for queue_client in list(multi_queue)]\
           or (blocked_client and id_textbox.text == blocked_client.get_id())\
           or id_textbox.text == ''\
           or id_textbox.text == '¡ERROR!':
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
                priority = None
            else:
                priority = int(priority)
                if priority <= 0 or priority > params.MAX_PRIORITY:
                    priority_textbox.text = '¡ERROR!'
                    return
        except ValueError:
            priority_textbox.text = '¡ERROR!'
            return

        past_service = multi_queue.get_current_service()
        try:
            front_client = multi_queue.get(0)
        except IndexError:
            front_client = None

        create_new_client(id_textbox.text, int(requests), priority)

        if multi_queue.get_current_service() != past_service and front_client is not None:
            client_row = expel_table_line(front_client)
            table_data.loc[client_row.name] = client_row
            new_table_line(front_client, client_row['T. Llegada'])
            table_data.iloc[-1, table_data.columns.get_loc('Estado')] = 'Esperando'

        id_textbox.text = ''
        requests_textbox.text = ''
        priority_textbox.text = ''

        print(multi_queue)

    addclient_button.action = addclient_button_action

    def block_button_action() -> None:
        """Bloquea o desbloquea un cliente dado."""
        
        global blocked_client, blocked_client_queue_index
        if blocked_client:
            new_state = 'Esperando'
            block_button.tag = 'Bloquear'
            queue_client = blocked_client
            blocked_client = None
            index = table_data[table_data['Proceso'] == queue_client.get_id()].iloc[-1].name
            multi_queue.enqueue(queue_client, queue_index=blocked_client_queue_index)

        else:
            new_state = 'Bloqueado'
            block_button.tag = 'Desbloquear Bloqueado'
            queue_client = multi_queue.get(0)
            blocked_client = queue_client
            blocked_client_queue_index = multi_queue.get_queue_index(queue_client)
            index = table_data[table_data['Proceso'] == queue_client.get_id()].iloc[-1].name
            if multi_queue.get_current_service() > 0:
                client_row = expel_table_line(queue_client)
                table_data.loc[client_row.name] = client_row
                new_table_line(queue_client, client_row['T. Llegada'])
                index = table_data.iloc[-1].name

            multi_queue.remove(queue_client)

        table_data.loc[index, 'Estado'] = new_state
        print(multi_queue)

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
                if multi_queue.get_size() >= 1:
                    queue_client = multi_queue.get(0)
                    grant.add_line(
                        current_tag=str(queue_client.get_id()),
                        blocked_tag=str(blocked_client.get_id()) if blocked_client else None
                    )
                    multi_queue.dequeue()

                    # Dando tiempo de llegada a proceso actual.
                    client_row = table_data[table_data['Proceso'] == str(queue_client.get_id())].iloc[-1]
                    client_row['Estado'] = 'En Ejecución'
                    if client_row['T. Comienzo'] is None:
                        client_row['T. Comienzo'] = time

                    # Actulizar la nueva fila en la tabla.
                    table_data.loc[client_row.name] = client_row

                    # Cuando se terminó de atender a un cliente.
                    if multi_queue.get_current_service() == 0 and multi_queue.get_size() == 0 or multi_queue.get(0) is not queue_client:
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
                multi_queue.age(params.MAX_AGE)
                print(multi_queue)

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

        if blocked_client or multi_queue.get_size() > 0:
            block_button.active = True
        else:
            block_button.active = False
            
        for button in button_list:
            button.update()

        # Simulación Semáforo
        time_tag.tag = f'Tiempo: {time}'
        if multi_queue.get_current_service() > 0 and multi_queue.get_size() > 0:
            queue_client = multi_queue.get(0)
            critical_section_tag.tag = f'En sección crítica: {queue_client.get_id()}'
            waiting_tag.tag = f'Procesos en espera: {multi_queue.get_size() - 1}'

        else:
            critical_section_tag.tag = f'En seccion crítica: -'
            waiting_tag.tag = f'Procesos en espera: {multi_queue.get_size()}'

        # Dibujando elementos.
        for tag in tag_list:
            tag.draw(screen)

        for textbox in textbox_list:
            textbox.draw(screen)

        for button in button_list:
            button.draw(screen)

        table.draw(screen)
        for queue_table in queue_tables:
            queue_table.draw(screen)
        grant.draw(screen)

        for name in queue_table_names:
            name.draw(screen)

        # Actualizar pantalla y esperar.
        pygame.display.update()
        clock.tick()
