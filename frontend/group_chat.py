import time
import socket

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog, QTextBrowser, QLabel, QLineEdit, QPushButton, QGridLayout, QListWidget, \
    QListWidgetItem, QWidget, QMessageBox
from PyQt5.QtCore import Qt

from backend.chat_client import ChatClient
from backend.chat_fetching_utils import FetchGroupChat, FetchCurrentServer
from backend.chat_utils import Client, send, receive
from frontend.group_chat_invite import GroupChatInviteWidget


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
        # self.chat_rooms = QListWidget()
        # self.connected_clients = QListWidget()

        self.members = QTextBrowser()
        self.chats = QTextBrowser()
        self.chats_input = QLineEdit()

        self.send_button = QPushButton("Send", self)
        self.send_image_button = QPushButton("Send Image", self)

        self.fetch_message_thread = FetchGroupChat(client=self.client, room_info=self.room_info, parent=self)
        self.fetch_message_thread.chat_fetched.connect(self.chats.append)
        self.fetch_message_thread.members_fetched.connect(self.update_members)
        self.fetch_message_thread.start()

        # self.fetch = FetchCurrentServer(client=self.client, parent=self)
        # # self.fetch.updates_fetched.connect(self.server_updates)
        # self.fetch.start()

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
    #
    #     existing_group_chats: list[tuple[str, Client]] = [self.chat_rooms.item(i).data(Qt.UserRole)
    #                                                       for i in range(self.chat_rooms.count())]
    #
    #     rooms_to_add = list(set(group_chat_rooms) - set(existing_group_chats))
    #     rooms_to_remove = list(set(existing_group_chats) - set(group_chat_rooms))
    #
    #     for room in rooms_to_add:
    #         new_room = QListWidgetItem(f"{room[0]} by {room[1][1]}")
    #         new_room.setData(Qt.UserRole, room)
    #         self.chat_rooms.addItem(new_room)
    #
    #     for removed_rooms, room in enumerate(rooms_to_remove):
    #         self.chat_rooms.takeItem(existing_group_chats.index(room) - removed_rooms)

    def close_chat(self) -> None:
        # When host closes group chat, chat gets removed from server.
        self.fetch_message_thread.stop_thread()
        self.client.leave(self.room_info)
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
        # # print("NOT IMPLEMENTED YET :(")
        #
        # # self.fetch.stop_thread()
        # # self.fetch.wait()
        # #
        # # chat_info = self.chat_rooms.currentItem().data(Qt.UserRole)
        # # self.client.join(chat_info)
        # #
        # group_chat_invite = GroupChatInviteWidget(self.client)
        # group_chat_invite.show()
        # # group_chat_invite.exec()
        # #
        # # # Start updating client list again.
        # # self.fetch.start()

        try:
            self.group_chat_invite = GroupChatInviteWidget(self.client)
            self.group_chat_invite.show()
        except socket.error:
            notify_exit = QMessageBox()
            notify_exit.setText("Server could not be found!")
            notify_exit.setInformativeText(
                "Please start the server before the client, or change the server port and address.")
            notify_exit.exec()
