from PyQt5.QtCore import Qt, QCoreApplication, pyqtSlot
from PyQt5.QtWidgets import QWidget, QListWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QListWidgetItem

from backend.chat_client import ChatClient
from backend.chat_fetching_utils import FetchCurrentServer
from backend.chat_utils import Client


class GroupChatInviteWidget(QWidget):

    def __init__(self, client: ChatClient) -> None:
        super().__init__()

        self.connected_clients = QListWidget()
        # self.port: int = -1
        self.client: ChatClient = client
        #
        self.fetch = FetchCurrentServer(client=self.client, parent=self)
        # self.fetch.updates_fetched.connect(self.server_updates)
        # self.fetch.start()

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
        # connect_button.setAutoDefault(True)

        close_button = QPushButton("Cancel", self)
        close_button.clicked.connect(self.close_program)

        buttons.addWidget(invite_button)
        buttons.addWidget(close_button)

        main_layout.addLayout(buttons)

        self.setGeometry(1050, 350, 300, 400)

    # @pyqtSlot(object)
    # def server_updates(self, updates: tuple[list[tuple[str, tuple[str, int]]], list[tuple[str, Client]]]) -> None:
    #
    #     clients, group_chat_rooms = updates
    #
    #     port_numbers: list[int] = [self.connected_clients.item(i).data(Qt.UserRole)[1]
    #                                for i in range(self.connected_clients.count())]
    #
    #     for c in clients:
    #         if c[1][1] in port_numbers:
    #             # Set texts to corresponding clients.
    #             self.connected_clients.item(port_numbers.index(c[1][1])).setText(c[0])
    #             port_numbers[port_numbers.index(c[1][1])] = -1
    #         else:
    #             new_client = QListWidgetItem(c[0])
    #             new_client.setData(Qt.UserRole, c[1])
    #             self.connected_clients.addItem(new_client)
    #
    #     removed = 0
    #     for i, port in enumerate(port_numbers):
    #         if port != -1:
    #             self.connected_clients.takeItem(i - removed)
    #             removed += 1

    def close_program(self):
        self.fetch.stop_thread()
        self.fetch.wait()
        self.hide()

    def invite(self) -> None:
        print("NOT IMPLEMENTED YET :(")
