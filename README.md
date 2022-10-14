# SOFTENG 364 Assignment 2: Chatting Program

## Description

This is a chatting program, written in Python, which allows chatting between clients connected to a server.
The connection between the server and the clients is encrypted.

The program incliudes following functionalities:
- prompt the client to connect to the server
- 1:1 chatting
- create/join group chats between multiple clients

## To get you started

### Dependencies

- Python 3.7 or above (RECOMMENDED: Python 3.9)
- PyQt5

### Installing

You can access the source code through the submitted zip file, or by cloning from github repository:

```bash
git clone https://github.com/hseo227/chatting-program.git
```

### Executing program

Open terminal and run `server.py` and `client.py` from the root directory of this repository **(i.e. `hseo227_source_code`)**.
Make sure to run `server.py` prior to running `client.py`.

A reminder to check the python version before running the program.
You can do this by running the following command:
```bash
python --version
```

Run the server first, then the client
```bash
python server.py --name=NAME --port=PORT
```
(For example: --name=localhost --port=9988)

and
```bash
python client.py
```
When client.py is run, make sure to enter the correct, or corresponding, IP address and Port number to the server.

**On Mac, python 3 can be run by using the command `python3` rather than `python`.
And consequently, use `python3` to check and run python 3 version.*
