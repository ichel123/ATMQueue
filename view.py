"""Representaciones gráficas para la simulación gráfica de una cola de cajero."""

import pygame, math, pandas, numpy
import logic, params
from typing import Callable

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
        self.outline_color_inactive = 'Black'

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

        self.padding = params.TEXTBOX_PADDING

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

        if not self.active:
            return

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
                self.rect.x + self.padding,
                self.rect.centery - text_surface.get_height()/2
            ),
            pygame.Rect(
                max(0, text_surface.get_width() - self.rect.width + 2 * self.padding),
                0,
                min(text_surface.get_width(), self.rect.width - 2 * self.padding),
                self.rect.height - 2 * self.padding
            )
        )

class Table:
    """Clase contenedora que imprime DataFrames en Pygame."""

    def __init__(self, df: pandas.DataFrame, x: int, y: int, cell_widht: int, cell_height: int, rows: int, cols: int, outline: int, font_name: str = None, font_size: int = None):
        """Construye la tabla con las propiedades indicadas.
        df: El data frame contenido a mostrar.
        x: Posición en x de la esquina superior izquierda de la tabla.
        y: Posición en y de la esquina superior izquierda de la tabla.
        cell_width: Ancho de todas las columnas.
        cell_height: Ancho de todas las filas.
        rows: Número de filas.
        cols: Número de columnas.
        outline: Grosor de línea.
        font_name: Nombre de una fuente en el sistema para el texto de la tabla.
        font_size: Tamaño de la fuente para el texto de la tabla."""

        self.df = df
        self.pos = pygame.math.Vector2(x, y)
        self.default_cell_width = cell_widht
        self.default_cell_height = cell_height
        self.col_widths = {}
        self.row_heights = {}
        self.outline = outline
        self.font = pygame.font.SysFont(font_name if font_name else 'Arial', font_size if font_size else 10)

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

    def draw(self, surface: pygame.Surface) -> None:
        """Dibuja la tabla correspondientemente.
        surface: Superficie sobre la que se debe dibujar la tabla."""

        y_pos = self.pos[1]
        x_pos = self.pos[0]
        row_height = self.default_cell_height

        for col_index, column in enumerate(self.df.columns):
            col_width = self.default_cell_width

            rect = pygame.Rect(x_pos, y_pos, col_width, row_height)
            x_pos += rect.width - self.outline
            pygame.draw.rect(surface, 'Black', rect, self.outline)
            text_surface = self.font.render(str(column), True, 'Black')
            surface.blit(
                text_surface,
                (
                    rect.centerx - text_surface.get_width() / 2,
                    rect.centery - text_surface.get_height() / 2
                )
            )

        y_pos += row_height - self.outline

        for row_index, (_, row) in enumerate(self.df.iterrows()):
            x_pos = self.pos[0]
            try:
                row_height = self.row_heights[row_index]
            except:
                row_height = self.default_cell_height

            for col_index, value in enumerate(row):
                try:
                    col_width = self.col_widths[col_index]
                except:
                    col_width = self.default_cell_width

                rect = pygame.Rect(x_pos, y_pos, col_width, row_height)
                x_pos += rect.width - self.outline
                pygame.draw.rect(surface, 'Black', rect, self.outline)
                text_surface = self.font.render(str(value), True, 'Black')
                if value is not None:
                    surface.blit(
                        text_surface,
                        (
                            rect.centerx - text_surface.get_width() / 2,
                            rect.centery - text_surface.get_height() / 2
                        )
                    )

            y_pos += row_height - self.outline

class Tag:
    """Clase que permite colocar etiquetas dentro de Pygame."""

    def __init__(self, x: int, y: int, tag: str, font_name: str, font_size: int, font_color: str) -> None:
        """Construye la etiqueta con la información correspondiente.
        x: Posición en x de la esquina superior izquierda de la etiqueta.
        y: Posición en y de la esquina superior izquierda de la etiqueta.
        tag: Texto de la etiqueta.
        font_name: Nombre de una fuente en el sistema para escribir la etiqueta.
        font_size: Tamaño de la fuente para escribir la etiqueta.
        font_color: Color de la fuente para escribir la etiqueta."""

        self.pos = pygame.math.Vector2(x, y)
        self.tag = tag
        self.font = pygame.font.SysFont(font_name if font_name else 'Arial', font_size if font_size else 10)
        self.font_color = font_color

    def draw(self, surface: pygame.Surface) -> None:
        """Dibuja la etiqueta correspondientemente.
        surface: Superficie sobre la que se imprimirá la etiqueta."""

        surface.blit(self.font.render(self.tag, True, self.font_color), self.pos)

class Grant:
    """Clase para la impresión de un diagrama de Grant."""

    def __init__(self, x: int, y: int, width: int, height: int, font_name: str, font_size: int) -> None:
        """Construye el Diagrama de Grant con la información indicada.
        x: Posición en x de la esquina superior izquierda del diagrama.
        y: Posición en y de la esquina superior izquierda del diagrama.
        width: Ancho del diagrama.
        height: Alto del diagrama.
        font_name: Nombre de una fuente en el sistema para usar en el diagrama.
        font_size: Tamaño de la fuente para usar en el diagrama."""

        self.rect = pygame.Rect(x, y, width, height)
        self.font = pygame.font.SysFont(font_name if font_name else 'Arial', font_size if font_size else 10)
        self.tags: list[str] = []
        self.tags_rects: list[pygame.Rect] = []
        self.tags_surface = pygame.Surface((0,0))
        self.tags_active: list[bool] = []
        self.lines_surface = pygame.Surface((0, 0))
        self.numbers_surface = pygame.Surface((0, 0))
        self.current_time = 1

        self.padding = params.GRANT_PADDING

    def add_tag(self, tag: str) -> None:
        """Añade o regresa una etiqueta al diagrama.
        tag: Etiqueta a agregar."""

        try:
            index = self.tags.index(tag)
        except ValueError:
            index = -1

        if index >= 0:
            self.tags_active[index] = True
            return

        self.tags.append(tag)
        self.tags_active.append(True)

        tag_surface = self.font.render(tag, True, 'Black')
        tag_rect = tag_surface.get_rect(
            topleft = (
                self.padding,
                self.tags_surface.get_height() + self.padding
            )
        )
        self.tags_rects.append(tag_rect)

        tags_surface = pygame.Surface(
            (
                max(self.tags_surface.get_width(), tag_rect.right + self.padding),
                tag_rect.bottom
            )
        )
        tags_surface.fill('White')
        tags_surface.blit(self.tags_surface, (0, 0))
        tags_surface.blit(tag_surface, tag_rect)
        self.tags_surface = tags_surface

        lines_surface = pygame.Surface(
            (
                self.lines_surface.get_width(),
                self.tags_surface.get_height()
            )
        )
        lines_surface.fill('White')
        lines_surface.blit(self.lines_surface, (0, 0))
        self.lines_surface = lines_surface

    def remove_tag(self, tag: str) -> None:
        """Deja de imprimir líneas para la etiqueta indicada.
        tag: Etiqueta para la cual dejar de imprimir líneas."""

        index = self.tags.index(tag)
        self.tags_active[index] = False

    def add_line(self, tag: str = None) -> None:
        """Añade una nueva sección al diagrama con línea gruesa para la etiqueta indicada.
        tag: Etiqueta a la cual dar línea gruesa."""

        if tag is not None:
            index = self.tags.index(tag)
        else:
            index = -1

        lines_surface = pygame.Surface(
            (
                self.lines_surface.get_width() + params.GRANT_TIME_WIDTH,
                self.lines_surface.get_height()
            )
        )
        lines_surface.fill('White')
        lines_surface.blit(self.lines_surface, (0, 0))

        number_text_surface = self.font.render(str(self.current_time), True, 'Black')
        number_text_surface = pygame.transform.scale_by(number_text_surface, 2/3)
        numbers_surface = pygame.Surface(
            (
                self.numbers_surface.get_width() + params.GRANT_TIME_WIDTH,
                max(self.numbers_surface.get_height(), number_text_surface.get_height())
            )
        )
        numbers_surface.fill('White')
        numbers_surface.blit(self.numbers_surface, (0, 0))
        numbers_surface.blit(number_text_surface,
            (
                self.numbers_surface.get_width(),
                numbers_surface.get_height() / 2 - number_text_surface.get_height() / 2
            )
        )
        self.numbers_surface = numbers_surface
        self.current_time += 1
        
        for i, tag_rect in enumerate(self.tags_rects):
            if not self.tags_active[i]:
                continue

            line_rect = pygame.Rect(
                self.lines_surface.get_width(),
                tag_rect.top,
                params.GRANT_TIME_WIDTH,
                tag_rect.height
            )
            line_surface = pygame.Surface(
                (
                    params.GRANT_TIME_WIDTH,
                    tag_rect.height / (1 if i == index else 5)
                )
            )
            line_surface.fill('Red' if i == index else 'Black')

            lines_surface.blit(
                line_surface,
                (
                    line_rect.x,
                    line_rect.y + tag_rect.height / 2 - line_surface.get_height() / 2
                )
            )

        self.lines_surface = lines_surface

    def draw(self, surface: pygame.Surface) -> None:
        """Dibuja el diagrama correspondientemente.
        surface: Superificie en la cual dibujar el diagrama."""

        surface.blit(self.numbers_surface, (self.rect.x + self.tags_surface.get_width() + self.padding, self.rect.y),
            (
                max(0, self.numbers_surface.get_width() - self.rect.width + self.tags_surface.get_width() + self.padding),
                0,
                min(self.numbers_surface.get_width(), self.rect.width - self.tags_surface.get_width() - self.padding),
                self.numbers_surface.get_height()
            )
        )

        surface.blit(self.tags_surface, (self.rect.x + self.padding, self.rect.y + self.numbers_surface.get_height()),
            pygame.Rect(
                max(0, self.tags_surface.get_width() - self.rect.width + self.padding),
                max(0, self.tags_surface.get_height() - self.rect.height + self.numbers_surface.get_height()),
                min(self.tags_surface.get_width(), self.rect.width - self.padding),
                min(self.tags_surface.get_height(), self.rect.height - self.numbers_surface.get_height())
            )
        )

        surface.blit(self.lines_surface, (self.rect.x + self.tags_surface.get_width() + self.padding, self.rect.y + self.numbers_surface.get_height()),
            pygame.Rect(
                max(0, self.lines_surface.get_width() - self.rect.width + self.tags_surface.get_width() + self.padding),
                max(0, self.lines_surface.get_height() - self.rect.height + self.numbers_surface.get_height()),
                min(self.lines_surface.get_width(), self.rect.width - self.tags_surface.get_width() - self.padding),
                min(self.lines_surface.get_height(), self.rect.height - self.numbers_surface.get_height())
            )
        )

        pygame.draw.rect(surface, 'Black', self.rect, 2)
