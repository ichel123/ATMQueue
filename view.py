"""Representaciones gráficas para la simulación gráfica de una cola de cajero."""

import pygame, math
import logic, params
from typing import Callable

ALTO_GRAFICOS = 100

class ATM:
    """Representa gráficamente el cajero que atiende a los clientes.
    Señala quién es el siguiente cliente."""

    def __init__(self, x: int, y: int, font: pygame.font.Font, *args, **kwargs) -> None:
        """x: Posición en x de la esquina superior izquierda del cajero.
        y: Posición en y de la esquina superior izquierda del cajero.
        font: Letra con la cual escribir la etiqueta siguiente."""

        super().__init__(*args, **kwargs)
        self.image = pygame.image.load('atm.png').convert_alpha()
        self.image = pygame.transform.scale_by(self.image, ALTO_GRAFICOS/self.image.get_height())
        self.rect = self.image.get_rect(topleft=(x,y))
        self.font = font

    def draw(self, surface: pygame.Surface, queue: logic.ATM_Queue) -> None:
        """Dibuja el cajero en la superficie indicada.
        surface: Superficie sobre la cuál se dibujará el cajero.
        queue: Queue que contiene los clientes en espera."""

        try:
            next_value = list(queue)[1]
        except IndexError:
            next_value = list(queue)[0]

        next_text_surface = self.font.render(
            f'next: {next_value.get_id() if type(next_value) == logic.Queue_Client else next_value}',
            True,
            'Black'
        )

        surface.blit(self.image, self.rect)
        surface.blit(
            next_text_surface,
            (
                self.rect.centerx - next_text_surface.get_width()/2,
                self.rect.bottom + params.PADDING
            )
        )

class Client:
    """Representa gráficamente un cliente en la cola de espera.
    Señala su id, el número de solicitudes restantes y el siguiente cliente de la cola."""

    @classmethod
    def current_pos(cls, t: int, a: int, b: int, t_1: int) -> float:
        """Dado un tiempo actual, un destino, un origen y un tiempo final,
        calcula la posición actual de una partícula que recorre un espado unidimencional
        usando una función senosoidal."""

        if not 0 <= t:
            raise ValueError

        if t > t_1:
            t = t_1

        return (math.sin(math.pi * t / t_1 - math.pi / 2) + 1) * (b - a) / 2 + a

    def __init__(self, x: int, y: int, queue_client: logic.Queue_Client, font: pygame.font.Font, movement_time_total: int, *args, **kwargs) -> None:
        """x: Posición en x de la esquina superior izquierda del cliente.
        y: Posición en y de la esquina superior izquierda del cliente.
        queue_client: Representación lógica del cliente.
        font: Fuente con la que se escriben las etiquetas.
        movement_time_total: Tiempo en el que el cliente debe completar un movimiento."""

        super().__init__(*args, **kwargs)
        self.image = pygame.image.load('client.png').convert_alpha()
        self.image = pygame.transform.scale_by(self.image, ALTO_GRAFICOS/self.image.get_height())
        self.rect = self.image.get_rect(topleft=(x,y))
        self.queue_client = queue_client

        self.origin_point = x, y
        self.destination_point = x, y
        self.movement_time_initial = 0
        self.movement_instant = movement_time_total
        self.movement_time_total = movement_time_total
        self.movement_started = False

        self.font = font

    def move(self, instant: int) -> tuple[int, int]:
        """Mueve el cliente a su posición correspondiente para el instante ingresado.
        instant: Instante actual sobre el cual se calcula la posición actual."""

        if not self.movement_started:
            self.movement_time_initial = instant
            self.movement_started = True

        self.movement_instant = instant - self.movement_time_initial
        self.rect.x = Client.current_pos(
            self.movement_instant,
            self.origin_point[0],
            self.destination_point[0],
            self.movement_time_total
        )
        self.rect.y = Client.current_pos(
            self.movement_instant,
            self.origin_point[1],
            self.destination_point[1],
            self.movement_time_total
        )

        return self.rect.x, self.rect.y

    def move_done(self) -> bool:
        """Devuelve verdadero si se ha alcanzado la posición final
        después de llamar el método move()."""

        return self.movement_instant >= self.movement_time_total

    def set_destination_point(self, x: int, y: int) -> None:
        """Define la posición final del próximo movimeinto.
        x: Posición final en x al finalizar el movimiento.
        y: Posición final en y al finalizar el movimiento."""

        self.origin_point = self.rect.x, self.rect.y
        self.destination_point = x, y
        self.movement_started = False

    def draw(self, surface: pygame.Surface, queue: logic.ATM_Queue) -> None:
        """Dibuja el cliente en la superficie indicada.
        surface: Superficie sobre la cuál se dibujará el cliente.
        queue: Queue que contiene los clientes en espera."""

        id_text_surface = self.font.render(
            f'id: {self.queue_client.get_id()}',
            True,
            'Black'
        )
        n_requests_text_surface = self.font.render(
            f'n_requests: {self.queue_client.get_number_of_requests()}',
            True,
            'Black'
        )
        next_value = queue.next_value(self.queue_client)
        next_text_surface = self.font.render(
            f'next: {next_value.get_id() if type(next_value) == logic.Queue_Client else next_value}',
            True,
            'Black'
        )

        surface.blit(self.image, self.rect)

        y_pos = self.rect.bottom + params.PADDING
        surface.blit(
            id_text_surface,
            (
                self.rect.centerx - id_text_surface.get_width()/2,
                y_pos
            )    
        )

        y_pos += id_text_surface.get_height() + params.PADDING
        surface.blit(
            n_requests_text_surface,
            (
                self.rect.centerx - n_requests_text_surface.get_width()/2,
                y_pos
            )
        )

        y_pos += n_requests_text_surface.get_height() + params.PADDING
        surface.blit(
            next_text_surface,
            (
                self.rect.centerx - next_text_surface.get_width()/2,
                y_pos
            )
        )

class Button:
    """Representa un botón que puede ser oprimido y ejecutar una acción."""

    def __init__(self, x: int, y: int, width: int, height: int, outline: int, tag: str, font_name: str = None, font_size: int = None, action: Callable = None) -> None:
        """Contruye un botón con la información indicada.
        x: Posición en x de la esquina superior izquierda del botón.
        y: Posición en y de la esquina superior izquierda del botón.
        width: Ancho del botón.
        height: Alto del botón.
        outline: Tamaño de la línea del botón.
        tag: Etiqueta del botón.
        font_name: Nombre de una fuente en el sistema para la etiqueta del botón.
        font_size: Tamaño de la letra de la etiqueta del botón.
        action: Función ejecutada cuando se oprime el botón."""

        self.rect = pygame.Rect(x, y, width, height)
        self.outline = outline
        self.tag = tag
        self.font = pygame.font.SysFont(
            font_name if font_name else 'Arial',
            font_size if font_size else 10
        )
        self.action = action

        self.active = True
        self.pressed = False

        self.outline_color_idle = 'Black'
        self.outline_color_hover = 'Black'
        self.outline_color_pressed = 'White'
        self.outline_color_inactive = 'White'

        self.box_color_idle = 'White'
        self.box_color_hover = 'Grey'
        self.box_color_pressed = 'DarkGrey'
        self.box_color_inactive = 'Black'

        self.font_color_idle = 'Black'
        self.font_color_hover = 'Black'
        self.font_color_pressed = 'White'
        self.font_color_inactive = 'White'

    def performAction(self) -> None:
        """Ejecuta la función asociada al botón."""

        if not self.active:
            return

        if self.action is not None:
            self.action()

    def update(self):
        """Ejecuta la lógica del botón."""

        self.hover = self.rect.collidepoint(pygame.mouse.get_pos())
        if pygame.mouse.get_pressed()[0]:
            if self.hover and not self.pressed:
                self.pressed = True
                self.performAction()
        else:
            self.pressed = False

    def draw(self, surface: pygame.Surface) -> None:
        """Dibuja el botón correspondientemente.
        surface: Superficie sobre la cual dibjar el botón."""

        if not self.active:
            outline_color = self.outline_color_inactive
            box_color = self.box_color_inactive
            font_color = self.font_color_inactive
        elif self.pressed:
            outline_color = self.outline_color_pressed
            box_color = self.box_color_pressed
            font_color = self.font_color_pressed
        else:
            outline_color = self.outline_color_hover if self.hover else self.outline_color_idle
            box_color = self.box_color_hover if self.hover else self.box_color_idle
            font_color = self.font_color_hover if self.hover else self.font_color_idle

        tag_surface = self.font.render(self.tag, True, font_color)

        pygame.draw.rect(surface, box_color, self.rect)
        pygame.draw.rect(surface, outline_color, self.rect, self.outline)
        surface.blit(
            tag_surface,
            (
                self.rect.centerx - tag_surface.get_width()/2,
                self.rect.centery - tag_surface.get_height()/2
            )
        )

class Textbox:
    """Caja de texto en la que es posible ingresar texto."""

    def __init__(self, x: int, y: int, width: int, height: int, outline: int, font_name: str = None, font_size: int = None) -> None:
        """Construye la caja de texto con la información indicada.
        x: Posición en x de la esquina superior izquierda de la caja de texto.
        y: Posición en y de la esquina superior izquierda de la caja de texto.
        width: Ancho de la caja de texto.
        height: Alto de la caja de texto.
        outline: Tamaño de la línea de la caja de texto.
        font_name: Nombre de una fuente en el sistema para la caja de texto.
        font_size: Tamaño de la letra de la etiqueta de la caja de texto."""

        self.rect = pygame.Rect(x, y, width, height)
        self.outline = outline
        self.font = pygame.font.SysFont(
            font_name if font_name else 'Arial',
            font_size if font_size else 10
        )

        self.text = ''
        self.active = False

        self.outline_color_active = 'Black'
        self.outline_color_inactive = 'Black'

        self.box_color_active = 'White'
        self.box_color_inactive = 'White'

        self.font_color_active = 'Black'
        self.font_color_inactive = 'Black'

    def check_active(self) -> None:
        """Revisa si el mouse está encima de la cada de texto y, de ser así, la pone activa.
        De lo contrario, la desactiva."""

        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.active = True
        else:
            self.active = False

    def add_text(self, unicode: str) -> str:
        """Añade el texto indicado a la cadena de la caja de texto.
        unicode: Texto a añadir."""

        if unicode == '\b':
            self.text = self.text[:-1]
        elif unicode in ''.join([chr(char) for char in range(1, 32)]):
            return
        else:
            self.text += unicode

        return self.text

    def draw(self, surface: pygame.Surface) -> None:
        """Dibuja la caja de texto correspondientemente.
        surface: Superficie sobre la cual dibujar la caja de texto."""

        if not self.active:
            outline_color = self.outline_color_inactive
            box_color = self.box_color_inactive
            font_color = self.font_color_inactive
        else:
            outline_color = self.outline_color_active
            box_color = self.box_color_active
            font_color = self.font_color_active

        text_surface = self.font.render(self.text + ('_' if self.active else ''), True, font_color)

        pygame.draw.rect(surface, box_color, self.rect)
        pygame.draw.rect(surface, outline_color, self.rect, self.outline)
        surface.blit(
            text_surface,
            (
                self.rect.x + 5,
                self.rect.centery - text_surface.get_height()/2
            ),
            pygame.Rect(
                max(0, text_surface.get_width() - self.rect.width + 10),
                0,
                min(text_surface.get_width(), self.rect.width - 10),
                self.rect.height - 10
            )
        )

class Table:
    """Clase que permite imprimir tablas dentro de Pygame."""

    def __init__(self, x: int, y: int, cell_widht: int, cell_height: int, rows: int, cols: int, font_name: str = None, font_size: int = None):
        """Construye la tabla con las propiedades indicadas.
        x: Posición en x de la esquina superior izquierda de la tabla.
        y: Posición en y de la esquina superior izquierda de la tabla.
        cell_width: Ancho de todas las columnas.
        cell_height: Ancho de todas las filas.
        rows: Número de filas.
        cols: Número de columnas.
        font_name: Nombre de una fuente en el sistema para el texto de la tabla.
        font_size: Tamaño de la fuente para el texto de la tabla."""

        self.pos = pygame.math.Vector2(x, y)
        self.col_widths = [cell_widht for i in range(cols)]
        self.row_heights = [cell_height for i in range(rows)]
        self.cell_values = [['' for j in range(cols)] for i in range(rows)]
        self.font = pygame.font.SysFont(font_name if font_name else 'Arial', font_size if font_size else 10)

    def set_value(self, value: str, row: int, col: int) -> None:
        """Asigna el valor a la celda indicada.
        value: Valor a asignar a la celda.
        row: Fila de la celda.
        col: Columna de la celda."""

        self.cell_values[row][col] = value

    def set_width(self, width: int, col: int) -> None:
        """Modifica el ancho de una columna.
        width: Nuevo ancho.
        col: Columna a modificar."""

        self.col_widths[col] = width

    def set_height(self, height: int, row: int) -> None:
        """Modifica el alto de una fila.
        height: Nuevo alto.
        row: Fila a modificar."""

        self.row_heights[row] = height

    def add_col(self, width: int) -> None:
        """Añade una nueva columna al final de la tabla.
        width: Ancho de la nueva columna."""

        for row in len(self.row_heights):
            self.cell_values[row].append('')
        self.col_widths.append(width)

    def add_row(self, height: int) -> None:
        """Añade una nueva fila al final de la tabla.
        height: Alto de la nueva columna."""

        self.cell_values.append(['' for j in range(self.col_widths)])
        self.row_heights.append(height)

    def draw(self, surface: pygame.Surface) -> None:
        """Dibuja la tabla correspondientemente.
        surface: Superficie sobre la que se debe dibujar la tabla."""

        y = self.pos[1]
        for row_index, row in enumerate(self.cell_values):
            x = self.pos[0]
            for col_index, value in enumerate(row):
                rect = pygame.Rect(x, y, self.col_widths[col_index], self.row_heights[row_index])
                x += rect.width - 1
                pygame.draw.rect(surface, 'Black', rect, 2)
                text_surface = self.font.render(value, True, 'Black')
                surface.blit(
                    text_surface,
                    (
                        rect.centerx - text_surface.get_width() / 2,
                        rect.centery - text_surface.get_height() / 2
                    )
                )
            y += self.row_heights[row_index] - 1
