import time
from PyQt5.QtWidgets import QDialog, QTextBrowser, QVBoxLayout, QLabel, QHBoxLayout, QLineEdit, QPushButton

from backend.chat_client import ChatClient
from backend.chat_fetching_utils import FetchMessage

"""
1:1 Chat window for users to chat to another user.
"""


class OneToOneChatDialog(QDialog):

    def __init__(self, other_client_nickname: str, other_client_port: int, client: ChatClient, parent=None) -> None:

        super().__init__(parent)

        self.setWindowTitle("1:1 Chat")

        self.other_client_nickname = other_client_nickname
        self.other_client_port = other_client_port
        self.client = client
        self.room_name = f"{self.client.connected_port}_to_{self.other_client_port}"

        self.chats = QTextBrowser()
        self.chat_inputs = QLineEdit()
        self.send_button = QPushButton("Send", self)
        self.send_image_button = QPushButton("Send Image", self)

        self.fetch_message_thread = FetchMessage(client=self.client, parent=self)
        self.fetch_message_thread.chat_fetched.connect(self.chats.append)
        self.fetch_message_thread.start()

        self.init_ui()

    def init_ui(self) -> None:

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        main_layout.addWidget(QLabel(f"Chat with {self.other_client_nickname}"))
        main_layout.addWidget(self.chats)

        chat_window = QHBoxLayout()

        self.send_button.clicked.connect(self.send)
        self.send_image_button.clicked.connect(self.send_image)
        chat_window.addWidget(self.chat_inputs, 15)
        chat_window.addWidget(self.send_button, 1)
        chat_window.addWidget(self.send_image_button, 2)
        main_layout.addLayout(chat_window)

        close_button = QPushButton("Close", self)
        close_button.clicked.connect(self.close_chat)
        main_layout.addWidget(close_button)

        self.setGeometry(900, 300, 400, 500)
        self.show()

    def close_chat(self) -> None:
        self.fetch_message_thread.stop_thread()
        self.client.leave_one_to_one()
        self.accept()

    def send(self) -> None:
        # Receive message, and clear the input.
        message: str = self.chat_inputs.text()
        self.chat_inputs.clear()

        # Send message when not empty.
        if message:
            self.client.send_message(self.room_name, message)
            current_time = time.strftime("%H:%M", time.localtime())
            self.chats.append(f"Me ({current_time}): {message}")

    def send_image(self) -> None:
        print("NOT IMPLEMENTED YET :(")
