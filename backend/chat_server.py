import select
import signal
import ssl
import sys

from backend.backend_utils import *


class ChatServer:

    def __init__(self, port, backlog=5):
        self.clients = 0
        self.client_map: dict[socket.socket, Client] = {}

        self.group_chat_rooms: dict[tuple[str, Client], list[socket.socket]] = {}
        self.one_to_one_chat_rooms: dict[socket.socket, socket.socket] = {}

        self.rooms: dict[str, list[socket.socket]] = {}
        self.outputs = []  # list output sockets

        self.context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        self.context.load_cert_chain(certfile="cert.pem", keyfile="cert.pem")
        self.context.load_verify_locations('cert.pem')
        self.context.set_ciphers('AES128-SHA')

        self.server_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((SERVER_HOST, port))
        self.server_socket.listen(backlog)
        self.server_socket = self.context.wrap_socket(self.server_socket, server_side=True)

        # For keyboard interrupts
        signal.signal(signal.SIGINT, self.sighandler)

        print(f'Server listening to port: {port} ...')

    def sighandler(self, signum, frame):
        """ Clean up client outputs"""
        print('Shutting down server...')

        # Close existing client sockets
        for output in self.outputs:
            output.close()

        self.server_socket.close()

    def get_client_name(self, client):
        """ Return the name of the client """
        return self.client_map[client][1]

    def get_client_socket(self, port_num: int) -> socket.socket:
        """
        Gets the socket instance of a client, given the port number.
        """
        for client_socket, client_info in self.client_map.items():
            if client_info[0][1] == port_num:
                return client_socket

    def run(self):
        inputs = [self.server_socket, sys.stdin]
        self.outputs = []
        running = True
        while running:
            try:
                readable, writeable, exceptional = select.select(
                    inputs, self.outputs, [])
            except select.error:
                break

            for sock in readable:
                sys.stdout.flush()
                if sock == self.server_socket:
                    # handle the server socket
                    client_socket, address = self.server_socket.accept()
                    print(
                        f'Chat server: got connection {client_socket.fileno()} from {address}')
                    # Read the login name
                    cname: str = receive(client_socket)[1]

                    # Compute client name and send back
                    self.clients += 1
                    client: Client = (address, cname, time.time())
                    print(f"newly connected client: {client}")
                    send(client_socket, "CLIENT", client)
                    inputs.append(client_socket)

                    self.client_map[client_socket] = client
                    self.outputs.append(client_socket)

                elif sock == sys.stdin:
                    cmd = sys.stdin.readline().strip()
                    if cmd == 'list':
                        print(self.client_map.values())
                    elif cmd == 'quit':
                        running = False
                else:
                    # handle all other messages into the server's socket.
                    try:
                        data = receive(sock)
                        # print(f"data: {data}")

                        if data == ():
                            print(f'Chat server: {sock.fileno()} hung up')

                            sock.close()
                            inputs.remove(sock)

                            self.outputs.remove(sock)
                            self.client_map.pop(sock)
                            self.clients -= 1

                        elif data[0] == "UPDATES":
                            send(sock, "CLIENTS", list(self.client_map.values()), "ROOMS", list(self.group_chat_rooms.keys()))

                        elif data[0] == "CONNECT":
                            _, chatting_client_port = data
                            return_code = "SUCCESS"
                            try:
                                _ = self.one_to_one_chat_rooms[sock]
                            except KeyError:
                                chatting_client_socket = self.get_client_socket(chatting_client_port)
                                self.one_to_one_chat_rooms[sock] = chatting_client_socket
                                self.one_to_one_chat_rooms[chatting_client_socket] = sock
                            finally:
                                send(sock, return_code)

                        elif data[0] == "END_ONE_TO_ONE":
                            try:
                                other_sock = self.one_to_one_chat_rooms.pop(sock)
                                self.one_to_one_chat_rooms.pop(other_sock)

                                message = f"<< Client {self.get_client_name(sock)} has left the chat. >>"

                                send(other_sock, message)
                            except KeyError as e:
                                # Connection has already been closed.
                                _ = e

                            send(sock, "EXIT")

                        elif data[0] == "CREATEROOM":
                            _, room_name, host = data
                            message = ""
                            return_code = ""
                            try:
                                _ = self.group_chat_rooms[(room_name, host)]
                                message = "The room name already exists. Please enter another name."
                                return_code = "ROOMEXISTS"
                            except KeyError:
                                self.group_chat_rooms[(room_name, host)] = []
                                message = f"Room: {room_name} has been created."
                                return_code = "SUCCESS"
                            finally:
                                print(message)
                                send(sock, return_code)

                        elif data[0] == "JOINROOM":
                            _, room_info = data
                            return_code = "UNKNOWN_ERROR"

                            try:
                                print(f"room to join: {room_info}")
                                print(f"list of rooms: {list(self.group_chat_rooms.keys())}")
                                self.group_chat_rooms[room_info].append(sock)
                                return_code = "SUCCESS"
                            except KeyError:
                                return_code = "NO_SUCH_ROOM"
                            finally:
                                print(return_code)
                                send(sock, return_code)

                        elif data[0] == "EXITROOM":
                            _, room_info = data
                            message = f"{self.get_client_name(sock)} has left the chat."

                            try:
                                connected_clients = self.group_chat_rooms[room_info]
                                connected_clients.remove(sock)

                                if connected_clients:
                                    for other_sock in connected_clients:
                                        send(other_sock, message)

                                else:
                                    # Remove room if no client is present.
                                    self.group_chat_rooms.pop(room_info)
                                    print(f"Room: {room_info[0]} by {room_info[1][1]} has been deleted.")

                            except KeyError:
                                print(f"Room: {room_info[0]} by {room_info[1][1]} does not exist.")

                            # A confirmation message. This closes fetch message thread waiting for incoming message.
                            send(sock, "EXIT")

                        elif data[0] == "CLIENTS_IN_ROOM":
                            _, room_info = data

                            clients: list[Client] = []

                            try:
                                clients = [self.client_map[member] for member in self.group_chat_rooms[room_info]]
                                print(f"clients: {clients}")
                                return_code = "SUCCESS"
                            except KeyError:
                                return_code = "NO_SUCH_ROOM"

                            send(sock, return_code, clients)

                        elif data[0] == "MESSAGE":
                            _, room_info, message = data
                            formatted_message = format_message(self.get_client_name(sock), message)

                            print(f"Trying to send the following message: \n"
                                  f"({message}) \n"
                                  f"to room {room_info[0]}")

                            try:
                                socket_to_send = self.one_to_one_chat_rooms[sock]
                                print(f"Socket found for one-to-one chat, sending to socket: {socket_to_send}")
                                send(socket_to_send, formatted_message)
                            except KeyError as e:
                                _ = e
                                print("Socket NOT found for one-to-one chat, trying group chat socket.")
                                for room in self.group_chat_rooms.values():
                                    print(f"Room: {room}")
                                    if sock in room:
                                        print("Room with sender socket found")
                                        for other_sock in room:
                                            print(f"other_sock: {other_sock}")
                                            if other_sock != sock:
                                                send(other_sock, formatted_message)
                                        break

                        else:
                            print("ERROR")

                    except socket.error:
                        inputs.remove(sock)
                        self.outputs.remove(sock)

        self.server_socket.close()
