import select
import ssl

from backend.chat_utils import *


class ChatClient:

    def __init__(self, nickname, port, host=SERVER_HOST):
        self.nickname = nickname
        self.connected = False
        self.server_address: str = host
        self.server_port: int = port
        self.connected_address: str = ""
        self.connected_port: int = -1

        # SSL Context for a client.
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)

        self.prompt = f'[{nickname}@{socket.gethostname()}]> '

        # Connect to server at given port
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock = self.context.wrap_socket(self.sock, server_hostname=host)
            self.sock.connect((host, self.server_port))
            self.connected = True

            send(self.sock, "NAME", self.nickname)

            # Receive client address.
            self.client_from_server = receive(self.sock)[1]
            self.connected_address, self.connected_port = self.client_from_server[0]

        except socket.error:
            print(f'Failed to connect to chat server')
            raise socket.error

    def get_clients_in_server(self) -> tuple[list[Client], list[str, Client]]:
        client_info: str = ""
        clients: list[Client] = []
        rooms_info: str = ""
        chat_rooms: list[str, Client] = []

        while client_info != "CLIENTS" or rooms_info != "ROOMS":
            send(self.sock, "UPDATES")
            try:
                client_info, clients, rooms_info, chat_rooms = receive(self.sock)
            except ValueError:
                print("Error occurred while receiving updates from server.")
                continue

        return clients, chat_rooms

    def leave_one_to_one(self) -> None:
        send(self.sock, "END_ONE_TO_ONE")

    def join(self, room_info: tuple[str, Client]) -> None:
        counter = 0
        while counter < 5:
            send(self.sock, "JOINROOM", room_info)
            result, = receive(self.sock)

            if result == "SUCCESS":
                break
            else:
                counter += 1

    def leave(self, room_info: tuple[str, Client]) -> None:
        send(self.sock, "EXITROOM", room_info)

    def fetch_messages(self) -> list[str]:
        messages: list[str] = []

        readable, writeable, exceptional = select.select([self.sock], [], [])

        for sock in readable:
            data = receive(sock)[0]
            if data != "EXIT":
                messages.append(data)

        return messages

    def send_message(self, room_info: tuple[str, Client], message: str) -> None:
        send(self.sock, "MESSAGE", room_info, message)

    def get_clients_in_room(self, room_info: tuple[str, Client]) -> list[Client]:
        send(self.sock, "CLIENTS_IN_ROOM", room_info)
        result, clients_in_room = receive(self.sock)
        return clients_in_room
