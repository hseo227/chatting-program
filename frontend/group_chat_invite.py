from PyQt5.QtWidgets import QWidget, QListWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QListWidgetItem

from backend.chat_client import ChatClient
from backend.chat_fetching_utils import FetchCurrentServer


class GroupChatInviteWidget(QWidget):

    def __init__(self, client: ChatClient) -> None:
        super().__init__()

        self.connected_clients = QListWidget()

        self.client: ChatClient = client

        self.fetch = FetchCurrentServer(client=self.client, parent=self)

        self.init_ui()

    def init_ui(self) -> None:

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        main_layout.addWidget(QLabel("Connected Clients"))

        # Connected Clients
        main_layout.addWidget(self.connected_clients)

        buttons = QHBoxLayout()

        # connect client to server using connect method
        invite_button = QPushButton("Invite", self)
        invite_button.clicked.connect(self.invite)

        close_button = QPushButton("Cancel", self)
        close_button.clicked.connect(self.close_program)

        buttons.addWidget(invite_button)
        buttons.addWidget(close_button)

        main_layout.addLayout(buttons)

        self.setGeometry(1050, 350, 300, 400)

    def close_program(self):
        self.fetch.stop_thread()
        self.fetch.wait()
        self.hide()

    def invite(self) -> None:
        print("NOT IMPLEMENTED YET :(")
