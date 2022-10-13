import time

from PyQt5.QtCore import QThread, pyqtSignal

from backend.chat_client import ChatClient
from backend.chat_utils import Client


class FetchGroupChat(QThread):

    chat_fetched = pyqtSignal(object)
    members_fetched = pyqtSignal(object)

    def __init__(self, client: ChatClient, room_info: tuple[str, Client] = None, parent=None):
        super(FetchGroupChat, self).__init__(parent)
        self.client = client
        self.room_info = room_info
        self.thread_alive = False

    def run(self):

        self.thread_alive = True

        # Iterate until the thread is dead.
        while self.thread_alive:
            # Fetch messages and emit each message to the connected listener.
            # Merge them to both.
            chat_client_list: list[Client] = self.client.get_clients_in_room(self.room_info)
            self.members_fetched.emit(chat_client_list)

            messages: list[str] = self.client.fetch_messages()
            [self.chat_fetched.emit(message) for message in messages]

    def stop_thread(self):
        self.thread_alive = False


class FetchMessage(QThread):

    chat_fetched = pyqtSignal(object)

    def __init__(self, client: ChatClient, parent=None):
        super(FetchMessage, self).__init__(parent)
        self.client = client
        self.thread_alive = False

    def run(self):

        self.thread_alive = True

        # Iterate until the thread is dead.
        while self.thread_alive:
            # Fetch messages and emit each message to the connected listener.
            messages: list[str] = self.client.fetch_messages()
            [self.chat_fetched.emit(message) for message in messages]

    def stop_thread(self):
        self.thread_alive = False


class FetchCurrentServer(QThread):

    updates_fetched = pyqtSignal(object)

    def __init__(self, client: ChatClient, parent=None):
        super(FetchCurrentServer, self).__init__(parent)
        self.client = client
        self.thread_alive = False

    def run(self):
        self.thread_alive = True

        # Iterate until the thread is dead.
        while self.thread_alive:
            clients: list[tuple[str, tuple[str, int]]] = []

            # Retrieve a list of clients currently connected.
            connected_clients, group_chat_rooms = self.client.get_clients_in_server()

            current_time = time.time()

            for client in connected_clients:

                seconds_elapsed = current_time - client[2]
                hours, rest = divmod(seconds_elapsed, 3600)
                minutes, seconds = divmod(rest, 60)

                # Add appropriate time elapsed label.
                if hours > 0:
                    time_passed = f"{int(hours)} hour ago"
                elif minutes > 0:
                    time_passed = f"{int(minutes)} min ago"
                elif seconds > 1:
                    time_passed = f"{int(seconds)} sec ago"
                else:
                    time_passed = "now"

                me_notifier = " [me]" if client[0][1] == self.client.connected_port else ""

                clients.append((f"{client[1]}{me_notifier} ({time_passed})", (client[1], client[0][1])))

            self.updates_fetched.emit((clients, group_chat_rooms))

            time.sleep(1)

    def stop_thread(self):
        self.thread_alive = False
