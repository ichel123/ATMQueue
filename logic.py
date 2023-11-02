"""Módulo con las estructuras de datos para la simulación de una cola de cajero."""

from typing import TypeVar, Generic

T = TypeVar('T')

class Queue(Generic[T]):
    """Representa una cola y sus métodos por defecto siguen el orden de atención PEPS."""

    class __Node(Generic[T]):
        """Un nodo en la cola. Contiene información y apunta a otro nodo."""

        def __init__(self, data: T, prev_node=None, next_node=None) -> None:
            self.data = data
            self.prev = prev_node
            self.next = next_node

    def __init__(self, *args: T) -> None:
        """args: Lista de elementos en la cola."""

        self.__front = None
        self.__back = None
        self.__current = None
        self.__size = 0

        for data in args:
            self.enqueue(data)

    def front(self) -> T:
        """Devuelve el elemento en la primera posición de la cola."""

        if self.__front is None:
            return None

        return self.__front.data

    def back(self) -> T:
        """Devuelve el elemento en la última posición de la cola."""

        if self.__front is None:
            return None

        return self.__back.data

    def get(self, pos: int) -> T:
        """Devuelve el elemento de la cola en la posición indicada."""

        if not 0 <= pos < self.__size:
            raise IndexError

        aux_node = self.__front
        for _ in range(pos):
            aux_node = aux_node.next

        return aux_node.data

    def get_size(self) -> int:
        """Devuelve número de elementos en la cola."""

        return self.__size

    def next_value(self, data: T) -> T:
        """Devuelve el siguiente elemento en la cola al elemento dado si éste está en la cola, de lo contrario devuelve None.
        data: Elemento que precede al elemento buscado."""

        aux_node = self.__front
        while True:
            if aux_node.data is data:
                break

            if aux_node.next is self.__front:
                return None

            aux_node = aux_node.next

        return aux_node.next.data

    def index(self, data: T) -> int:
        """Devuelve la posición del elemento dado o None si el elemento no está en la cola.
        data: Elemento a buscar en la cola."""

        i = 0
        aux_node = self.__front
        while True:
            if aux_node.data is data:
                break

            if aux_node.next is self.__front:
                return None

            aux_node = aux_node.next
            i += 1

        return i

    def enqueue(self, data: T, pos: int = None) -> None:
        """Agrega a la cola el elemento indicado en la posición indicada.
        data: Elemento a agregar a la cola.
        pos: Posición en la cual insertar el elemento. Por defecto, al final."""

        if pos is not None and not 0 <= pos <= self.__size:
            raise IndexError

        if pos is None:
            pos = self.__size

        self.__size += 1

        if self.__front is None:
            self.__front = Queue.__Node(data)
            self.__front.prev = self.__front
            self.__front.next = self.__front
            self.__back = self.__front
            return

        aux_node = self.__front
        for _ in range(pos):
            aux_node = aux_node.next

        new_node = Queue.__Node(data, aux_node.prev, aux_node)
        aux_node.prev.next = new_node
        aux_node.prev = new_node

        if pos == 0:
            self.__front = new_node
        elif pos + 1 == self.__size:
            self.__back = new_node

    def dequeue(self, pos: int = 0) -> T:
        """Elimina de la cola y devuelve el elemento en la posición indicada.
        pos: Posición del elemento a eliminar de la cola, 0 por defecto."""

        if not 0 <= pos < self.__size:
            raise IndexError

        self.__size -= 1

        if pos == 0:
            out = self.__front.data
            if self.__size == 0:
                self.__front = self.__back = None
            else:
                self.__front = self.__front.next
                self.__front.prev = self.__back
                self.__back.next = self.__front

            return out

        aux_node = self.__front
        for _ in range(pos):
            aux_node = aux_node.next

        out = aux_node.data
        if aux_node is self.__back:
            self.__back = aux_node.prev

        aux_node.next.prev = aux_node.prev
        aux_node.prev.next = aux_node.next
        return out

    def __iter__(self):
        self.__current = self.__front
        return self

    def __next__(self) -> T:
        if self.__current is None:
            raise StopIteration

        out = self.__current.data
        if self.__current.next is not self.__front:
            self.__current = self.__current.next
        else:
            self.__current = None

        return out

    def __repr__(self) -> str:
        return f'{type(self).__name__}[{T}]({str(list(self))[1:-1]})'

class Queue_Client:
    """Representa un cliente que espera en una cola de cajero."""
    
    def __init__(self, id_client: str, n_requests: int, arrival_time: int, priority: int = None):
        """Crea el cliente con la información correspondiente.
        id_client: Id del cliente.
        n_requests: Número de solicitudes del cliente.
        arrival_time: Momento en el que llega el cliente.
        priority: Prioridad del cliente."""

        if n_requests < 0:
            raise ValueError

        self.__id_client = id_client
        self.__n_requests = n_requests
        self.__arrival_time = arrival_time
        self.__current_time = arrival_time
        self.__priority = priority

    def get_id(self) -> str:
        """Devuelve el id del cliente."""

        return self.__id_client

    def get_number_of_requests(self) -> int:
        """Devuelve el número de solicitudes restantes del cliente."""

        return self.__n_requests

    def respond_requests(self, quantity: int):
        """Disminuye el número de solicitudes del cliente según el número indicado.
        quantity: Número de solicitudes a atender."""

        if quantity < 0:
            raise ValueError

        if quantity > self.__n_requests:
            quantity = self.__n_requests

        self.__n_requests -= quantity
        self.__current_time += 1

    def is_done(self):
        """Verdadero si el cliente no tiene solicitudes pendientes. Falso de lo contrario."""

        return self.__n_requests == 0

    def get_arrival_time(self):
        """Devuelve el tiempo en el que fue creado."""

        return self.__arrival_time

    def get_priority(self):
        """Devuelve la prioridad del cliente."""

        return self.__priority
    
    def get_final_time(self):
        """Devuelve el tiempo en el que el cliente terminó o -1 si no ha terminado."""

        if not self.is_done():
            return -1

        return self.__current_time - self.__arrival_time

    def __repr__(self):
        return f'{type(self).__name__}({self.__id_client}, {self.__n_requests}{"" if self.__priority is None else f", {self.__priority}"})'

class FIFO_Server_Queue(Queue[Queue_Client]):
    """Representa una cola donde al frente hay un cajero."""

    def __init__(self, capacity: int, *args: Queue_Client):
        """capacity: Número de solicitudes que el cajero puede atender por turno.
                     Si es exactamente 0, se atenderá hasta terminar.
        args: Clientes en la cola."""

        if capacity < 0:
            raise ValueError

        super().__init__()
        self._Queue__front = Queue._Queue__Node("Servidor")
        self._Queue__front.prev = self._Queue__front
        self._Queue__front.next = self._Queue__front
        self._Queue__back = self._Queue__front

        self._Queue__size = 1

        self.__capacity = capacity
        self.__current_service = 0

        for arg in args:
            self.enqueue(arg)

    def enqueue(self, client: Queue_Client) -> None:
        """Agrega un cliente al final de la cola.
        client: Cliente a agregar a la cola."""

        if type(client) is not Queue_Client:
            raise ValueError

        super().enqueue(client)

    def dequeue(self) -> Queue_Client:
        """Atiende al cliente en la segunda posición de la cola.
        Si el cliente ha terminado todas sus solicitudes, lo saca de la cola y lo devuelve. Si no, devuelve None."""

        if self._Queue__size <= 1:
            raise IndexError

        self._Queue__front.next.data.respond_requests(1)
        self.__current_service += 1
        if (   self.__current_service < self.__capacity\
            or self.__capacity == 0)\
           and not self._Queue__front.next.data.is_done():
            return None
        
        self.__current_service = 0
        if self._Queue__front.next.data.is_done():
            return super().dequeue(1)

        self.enqueue(super().dequeue(1))
        return None

    def get_current_service(self) -> int:
        """Devuelve el número de servicios que se han hecho con el cliente actual."""

        return self.__current_service

    def remove(self, queue_client: Queue_Client) -> None:
        """Elimina el cliente indicado de la lista."""

        index = list(self).index(queue_client)
        if index == 1:
            self.__current_service = 0

        super().dequeue(index)

    def __repr__(self) -> str:
        return f'{type(self).__name__}({str(list(self))[1:-1]})'

class Priority_Server_Queue(FIFO_Server_Queue):
    """Representa una cola donde al frente hay un cajero,
    pero los clientes son atendidos según su prioridad más baja."""

    def enqueue(self, client: Queue_Client):
        """Añade al cliente a la cola y lo coloca en la posición indicada según su prioridad."""
        
        if type(client) is not Queue_Client:
            raise ValueError
        
        if client.get_priority() is None:
            raise ValueError
        
        self._Queue__size += 1
        
        new_node = Queue._Queue__Node(client)
        aux_node = self._Queue__front.next

        while aux_node is not self._Queue__front:
            if  client.get_priority() < aux_node.data.get_priority():
                break
            
            aux_node = aux_node.next

        if self.get_current_service() > 0 and aux_node is self._Queue__front.next:
            aux_node = aux_node.next

        new_node.next = aux_node
        new_node.prev = aux_node.prev

        aux_node.prev.next = new_node
        aux_node.prev = new_node

        if aux_node is self._Queue__front:
            self._Queue__back = new_node

        return
        