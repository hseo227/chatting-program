import socket

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QWidget, QLineEdit, QVBoxLayout, QGridLayout, QLabel, QHBoxLayout, QPushButton, QMessageBox

from backend.chat_client import ChatClient
from frontend.connected import ConnectedWidget

"""
A PyQT5 widget for connection screen.
"""


class ConnectionWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.ip_address_line_edit = QLineEdit()
        self.port_line_edit = QLineEdit()
        self.nickname_line_edit = QLineEdit()
        self.init_ui()

    def init_ui(self) -> None:

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        main_layout.addStretch(1)

        client_input_grid = QGridLayout()

        ip_address = QLabel("IP Address")
        port = QLabel("Port")
        nickname = QLabel("Nickname")

        client_input_grid.addWidget(ip_address, 0, 0)
        client_input_grid.addWidget(port, 1, 0)
        client_input_grid.addWidget(QLabel(), 2, 0)
        client_input_grid.addWidget(nickname, 3, 0)

        client_input_grid.addWidget(self.ip_address_line_edit, 0, 1)
        client_input_grid.addWidget(self.port_line_edit, 1, 1)
        client_input_grid.addWidget(self.nickname_line_edit, 3, 1)

        main_layout.addLayout(client_input_grid)
        main_layout.addStretch(1)

        buttons = QHBoxLayout()

        # connect client to server using connect method
        connect_button = QPushButton("Connect", self)
        connect_button.clicked.connect(self.connect)
        connect_button.setAutoDefault(True)

        cancel_button = QPushButton("Cancel", self)
        cancel_button.clicked.connect(QCoreApplication.instance().quit)

        buttons.addStretch(120)
        buttons.addWidget(connect_button)
        buttons.addWidget(cancel_button)
        buttons.addStretch(1)

        main_layout.addLayout(buttons)

        self.setWindowTitle("Chatting Program")
        self.setGeometry(600, 400, 500, 300)
        self.show()

    """
    Connects client to server with the provided inputs.
    On-click for the Connect button.
    """
    def connect(self) -> None:

        ip_address = self.ip_address_line_edit.text()
        port: int = int(self.port_line_edit.text())
        nickname = self.nickname_line_edit.text()

        # If any of input fields are empty
        if (nickname == "") or (ip_address == "") or (self.port_line_edit.text() == ""):
            empty_fields = QMessageBox()
            empty_fields.setText("Please make sure all fields are filled")
            empty_fields.exec()
            return

        try:
            client = ChatClient(nickname=nickname, host=ip_address, port=port)
            self.connected_widget = ConnectedWidget(client)
            self.connected_widget.show()
            self.close()
        except socket.error:
            notify_exit = QMessageBox()
            notify_exit.setText("Server could not be found!")
            notify_exit.setInformativeText(
                "Please start the server before the client, or change the server port and address.")
            notify_exit.exec()
