import time

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog, QTextBrowser, QLabel, QLineEdit, QPushButton, QGridLayout

from backend.chat_client import ChatClient
from backend.backend_utils import Client
from frontend.frontend_utils import FetchGroupMessage


class GroupChatDialog(QDialog):
    """
    This is a group chat window which allows users to chat with a single person.
    """

    def __init__(self, client: ChatClient, room_info: tuple[str, Client], parent=None) -> None:
        super().__init__(parent)

        self.setWindowTitle("Group Chat")

        self.client = client
        self.room_info = room_info
        self.room_name, self.room_host = self.room_info

        self.members = QTextBrowser()
        self.chats = QTextBrowser()
        self.chats_input = QLineEdit()

        self.send_button = QPushButton("Send", self)
        self.send_image_button = QPushButton("Send Image", self)

        self.fetch_message_thread = FetchGroupMessage(client=self.client, room_info=self.room_info, parent=self)
        self.fetch_message_thread.chat_fetched.connect(self.chats.append)
        self.fetch_message_thread.members_fetched.connect(self.update_members)
        self.fetch_message_thread.start()

        self.init_ui()

    def init_ui(self) -> None:

        main_layout = QGridLayout()
        main_layout.setColumnStretch(0, 4)
        main_layout.setColumnStretch(1, 1)
        main_layout.setColumnStretch(2, 1)
        main_layout.setColumnStretch(3, 2)
        self.setLayout(main_layout)

        main_layout.addWidget(QLabel(f"{self.room_name} by {self.room_host[1]}"), 0, 0, 1, 3)
        main_layout.addWidget(QLabel("Members"), 0, 3)
        main_layout.addWidget(self.chats, 1, 0, 1, 3)
        main_layout.addWidget(self.members, 1, 3, 2, 1)

        main_layout.addWidget(self.chats_input, 2, 0)

        self.send_button.clicked.connect(self.send)
        main_layout.addWidget(self.send_button, 2, 1)

        self.send_image_button.clicked.connect(self.send_image)
        main_layout.addWidget(self.send_image_button, 2, 2)

        close_button = QPushButton("Close", self)
        close_button.clicked.connect(self.close_chat)
        main_layout.addWidget(close_button, 3, 0, 1, 3)

        invite_button = QPushButton("Invite", self)
        invite_button.clicked.connect(self.invite)
        main_layout.addWidget(invite_button, 3, 3)

        self.setGeometry(900, 300, 600, 500)
        self.show()

    @pyqtSlot(object)
    def update_members(self, members: list[Client]) -> None:

        self.members.clear()

        for member in members:
            member_name = member[1]
            if member == self.room_host:
                member_name += " (Host)"
            if member == self.client.client_from_server:
                member_name += " (me)"
            self.members.append(member_name)

    def close_chat(self) -> None:
        # When host closes group chat, chat gets removed from server.
        self.fetch_message_thread.stop()
        self.client.leave_room(self.room_info)
        self.accept()

    def send(self) -> None:
        # Receive message, and clear the input.
        message: str = self.chats_input.text()
        self.chats_input.clear()

        # Send message when not empty.
        if message:
            self.client.send_message(self.room_info, message)
            current_time = time.strftime("%H:%M", time.localtime())
            self.chats.append(f"Me ({current_time}): {message}")

    def send_image(self) -> None:
        print("NOT IMPLEMENTED YET :(")

    def invite(self):
        print("NOT IMPLEMENTED YET :(")
