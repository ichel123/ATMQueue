import logic, params

class Server_Enqueuer:
    def __init__(self):
        self.queues = [
            logic.FIFO_Server_Queue(params.SERVER_CAPACITY, 5),
            logic.FIFO_Server_Queue(params.SERVER_CAPACITY),
            logic.Priority_Server_Queue(params.SERVER_CAPACITY)
        ]

    def queued_clients(self):
        total_clients = 0
        for queue in self.queues:
            total_clients += queue.get_size()
        return total_clients
        
    def enqueue(self, client: logic.Queue_Client):
        """Ubica cada cliente en la cola que le corresponde."""

        if client.get_queue_id() is not None and  client.get_queue_id() <= len(self.queues):
            self.queues[client.get_queue_id()-1].enqueue(client)
        else:
            queue_id = 1
            self.queues[queue_id].enqueue(client)
        
    def get_client_data(self, client_id: str) -> dict:
        """Obtiene los datos de un cliente específico a partir de su id."""
        for queue in self.queues:
            for client in queue:
                if isinstance(client, logic.Queue_Client) and client.get_id() == client_id:
                    return {
                        "id": client.get_id(),
                        "requests": client.get_number_of_requests(),
                        "arrival_time": client.get_arrival_time(),
                        "priority": client.get_priority(),
                        "queue_id": client.get_queue_id()
                    }
        return None
    
    def get_clients_in_queue(self, queue_number: int) -> list:
        """Obtiene todos los clientes de una cola específica."""
        if 0 <= queue_number < len(self.queues):
            return [
                {
                    "id": client.get_id(),
                    "requests": client.get_number_of_requests(),
                    "arrival_time": client.get_arrival_time(),
                    "priority": client.get_priority(),
                    "queue_id": client.get_queue_id()
                }
                for client in self.queues[queue_number]
                if isinstance(client, logic.Queue_Client)
            ]
