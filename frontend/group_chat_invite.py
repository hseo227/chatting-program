from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QWidget, QListWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton

from backend.chat_client import ChatClient
from backend.chat_fetching_utils import FetchCurrentServer


class GroupChatInviteWidget(QWidget):

    def __init__(self) -> None:
        super().__init__()
        self.init_ui()

    def init_ui(self) -> None:

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        main_layout.addWidget(QLabel("Connected Clients"))

        # Connected Clients
        # main_layout.addWidget(self.connected_clients)

        buttons = QHBoxLayout()

        # connect client to server using connect method
        invite_button = QPushButton("Invite", self)
        # connect_button.clicked.connect(self.connect)
        # connect_button.setAutoDefault(True)

        cancel_button = QPushButton("Cancel", self)
        cancel_button.clicked.connect(QCoreApplication.instance().quit)

        buttons.addWidget(invite_button)
        buttons.addWidget(cancel_button)

        main_layout.addLayout(buttons)