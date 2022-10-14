from PyQt5.QtCore import Qt, QCoreApplication, pyqtSlot
from PyQt5.QtWidgets import QWidget, QListWidget, QVBoxLayout, QLabel, QHBoxLayout, QListWidgetItem, QPushButton, \
    QInputDialog, QMessageBox

from backend.chat_client import ChatClient
from backend.chat_utils import *
from backend.chat_fetching_utils import FetchCurrentServer
from frontend.group_chat import GroupChatDialog
from frontend.one_to_one_chat import OneToOneChatDialog


class ConnectedWidget(QWidget):

    def __init__(self, client: ChatClient) -> None:
        super().__init__()

        self.chat_rooms = QListWidget()
        self.connected_clients = QListWidget()
        self.port: int = -1
        self.client: ChatClient = client
        self.one_to_one_chat_widgets = []

        self.fetch = FetchCurrentServer(client=self.client, parent=self)
        self.fetch.updates_fetched.connect(self.server_updates)
        self.fetch.start()

        self.init_ui()

    def init_ui(self) -> None:

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        main_layout.addWidget(QLabel("Connected Clients"))

        # Connected Clients
        connected_clients_layout = QHBoxLayout()

        connected_clients_layout.addWidget(self.connected_clients)
        chat_button = QPushButton("1:1 Chat", self)
        connected_clients_layout.addWidget(chat_button)
        #
        chat_button.clicked.connect(self.one_to_one_chat)

        main_layout.addLayout(connected_clients_layout)

        # Chat Rooms
        main_layout.addWidget(QLabel("Chat Rooms (Group Chat)"))

        chat_rooms_layout = QHBoxLayout()
        chat_rooms_layout.addWidget(self.chat_rooms)

        chat_room_buttons = QVBoxLayout()
        chat_rooms_layout.addLayout(chat_room_buttons)

        create_room_button = QPushButton("Create", self)
        create_room_button.clicked.connect(self.create_chat_room)
        chat_room_buttons.addWidget(create_room_button)

        join_chat_button = QPushButton("Join", self)
        join_chat_button.clicked.connect(self.join_group_chat)
        chat_room_buttons.addWidget(join_chat_button)

        main_layout.addLayout(chat_rooms_layout)

        # Close Button
        close_button = QPushButton("Close", self)
        close_button.clicked.connect(self.close_program)
        main_layout.addWidget(close_button)

        self.setWindowTitle("Chatting Program")
        self.setGeometry(450, 300, 400, 500)
        self.show()

    @pyqtSlot(object)
    def server_updates(self, updates: tuple[list[tuple[str, tuple[str, int]]], list[tuple[str, Client]]]) -> None:

        clients, group_chat_rooms = updates

        port_numbers: list[int] = [self.connected_clients.item(i).data(Qt.UserRole)[1]
                                   for i in range(self.connected_clients.count())]

        for c in clients:
            if c[1][1] in port_numbers:
                # Set texts to corresponding clients.
                self.connected_clients.item(port_numbers.index(c[1][1])).setText(c[0])
                port_numbers[port_numbers.index(c[1][1])] = -1
            else:
                new_client = QListWidgetItem(c[0])
                new_client.setData(Qt.UserRole, c[1])
                self.connected_clients.addItem(new_client)

        removed = 0
        for i, port in enumerate(port_numbers):
            if port != -1:
                self.connected_clients.takeItem(i - removed)
                removed += 1

        existing_group_chats: list[tuple[str, Client]] = [self.chat_rooms.item(i).data(Qt.UserRole)
                                                          for i in range(self.chat_rooms.count())]

        rooms_to_add = list(set(group_chat_rooms) - set(existing_group_chats))
        rooms_to_remove = list(set(existing_group_chats) - set(group_chat_rooms))

        for room in rooms_to_add:
            new_room = QListWidgetItem(f"{room[0]} by {room[1][1]}")
            new_room.setData(Qt.UserRole, room)
            self.chat_rooms.addItem(new_room)

        for removed_rooms, room in enumerate(rooms_to_remove):
            self.chat_rooms.takeItem(existing_group_chats.index(room) - removed_rooms)

    def one_to_one_chat(self) -> None:

        if self.connected_clients.currentItem() is None:
            notify_non_empty_nickname = QMessageBox()
            notify_non_empty_nickname.setText("Please select a user to chat.")
            notify_non_empty_nickname.exec()
            return
        else:
            self.fetch.stop_thread()
            self.fetch.wait()

        # Setting and changing a variable (status) for use in backend.
        status = ""
        chat_room_created = False
        other_client_nickname, other_client_port = self.connected_clients.currentItem().data(Qt.UserRole)

        while not chat_room_created:
            if status == "":
                send(self.client.sock, "CONNECT", other_client_port)
                status = receive(self.client.sock)[0]

            if status == "SUCCESS":
                chat_room_created = True
            elif status == "ROOMEXISTS":
                send(self.client.sock, "JOINROOM", f"{self.client.connected_port}_to_{other_client_port}")
                status = receive(self.client.sock)[0]

        # Link connected screen to 1:1 chat.
        one_to_one_chat = OneToOneChatDialog(other_client_nickname=other_client_nickname,
                                             other_client_port=other_client_port,
                                             client=self.client,
                                             parent=self)
        one_to_one_chat.exec()

        # Start updating client list again.
        self.fetch.start()

    def create_chat_room(self) -> None:

        chat_room_name, ready = QInputDialog.getText(self, '', "Enter a name for your chat room: ")

        if ready:
            room_created = False
            while not room_created:
                send(self.client.sock, "CREATEROOM", chat_room_name, self.client.client_from_server)
                status = receive(self.client.sock)[0]
                if status == "SUCCESS":
                    room_created = True
                else:
                    room_name, create_room = QInputDialog.getText(self, "Create Chat Room",
                                                                  "Provided chat room name already exists.\n"
                                                                  "Enter another chat room name: ")
                    if not create_room:
                        return

            new_chat_room = QListWidgetItem(f"{chat_room_name} by {self.client.nickname}")
            new_chat_room.setData(Qt.UserRole, (chat_room_name, self.client.client_from_server))
            self.chat_rooms.addItem(new_chat_room)

    def join_group_chat(self) -> None:

        self.fetch.stop_thread()
        self.fetch.wait()

        # Alert user that a room needs to be selected.
        if self.chat_rooms.currentItem() is None:
            notify_unselected_chat_room = QMessageBox()
            notify_unselected_chat_room.setText("Please select a chat room you wish to join.")
            notify_unselected_chat_room.exec()
            self.fetch.start()
            return

        chat_info = self.chat_rooms.currentItem().data(Qt.UserRole)

        self.client.join(chat_info)

        one_to_one_chat = GroupChatDialog(client=self.client, room_info=chat_info, parent=self)
        one_to_one_chat.exec()

        # Start updating client list again.
        self.fetch.start()

    def close_program(self) -> None:
        self.fetch.stop_thread()
        self.fetch.wait()
        QCoreApplication.instance().quit()
