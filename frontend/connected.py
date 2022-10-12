from PyQt5.QtCore import Qt, QCoreApplication, pyqtSlot
from PyQt5.QtWidgets import QWidget, QListWidget, QVBoxLayout, QLabel, QHBoxLayout, QListWidgetItem, QPushButton, \
    QInputDialog, QMessageBox

from backend.chat_client import ChatClient
from backend.backend_utils import *
from frontend.frontend_utils import FetchServerUpdates
from frontend.group_chat import GroupChatDialog
from frontend.one_to_one_chat import OneToOneChatDialog


class ConnectedWidget(QWidget):

    def __init__(self, client: ChatClient) -> None:
        super().__init__()

        self.chat_rooms = QListWidget()
        self.connected_clients = QListWidget()
        self.port: int = -1
        self.client: ChatClient = client

        self.fetch = FetchServerUpdates(client=self.client, parent=self)
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

        main_layout.addLayout(connected_clients_layout)

        # Chat Rooms
        main_layout.addWidget(QLabel("Chat Rooms (Group Chat)"))

        chat_rooms_layout = QHBoxLayout()
        chat_rooms_layout.addWidget(self.chat_rooms)

        chat_room_buttons = QVBoxLayout()
        chat_rooms_layout.addLayout(chat_room_buttons)

        create_room_button = QPushButton("Create", self)
        chat_room_buttons.addWidget(create_room_button)

        join_chat_button = QPushButton("Join", self)
        chat_room_buttons.addWidget(join_chat_button)

        main_layout.addLayout(chat_rooms_layout)

        # Close Button
        close_button = QPushButton("Close", self)
        close_button.clicked.connect(self.close_program)
        main_layout.addWidget(close_button)

        self.setWindowTitle("Chatting Program")
        self.setGeometry(700, 300, 300, 400)
        self.show()

    def close_program(self) -> None:
        self.fetch.stop()
        self.fetch.wait()
        QCoreApplication.instance().quit()
