import subprocess
import os
import time
import socket
from unittest import TestCase

from server import Server


class TestClient(object):

    def __init__(self, port):

        self.client_socket = socket.socket()
        self.client_socket.connect(("127.0.0.1", port))

        self.response = self.client_socket.recv(4096).decode();

    def send(self, message):

        self.client_socket.sendall(message.encode())
        self.response = self.client_socket.recv(4096).decode()


class ServerUnitTest(TestCase):

    def setUp(self):
        self.server = Server()

    def test_room_description(self):

        descriptions = [self.server.room_description(i) for i in range(4)]

        self.assertCountEqual(descriptions, set(descriptions))

    def test_say(self):

        for phrase in ["OK!", "Whazzzzzup?", "African or European?"]:
            self.server.say(phrase)
            self.assertEqual("You say, \"{}\"".format(phrase), self.server.output_buffer)


class AcceptanceTests(TestCase):

    @staticmethod
    def make_server(port):

        server = subprocess.Popen(
            [
                "python",
                os.path.join(
                    os.getcwd(),
                    "serve.py"
                ),
                str(port),
            ],
            stdout=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
        )

        time.sleep(3)
        return server

    @staticmethod
    def make_client(port):
        client = TestClient(port)
        return client

    def test_for_acceptance(self):

        self.make_server(50005)

        client = self.make_client(50005)

        room_descriptions = {}

        initial_response = client.response

        self.assertIn(
            "Welcome to Realms of Venture",
            initial_response,
            "The server provides the greeting message"
        )

        client.send("move south")
        client.send("move west")
        client.send("move west")  # We should now be in room 1

        room_descriptions[1] = client.response.split("OK! ")[1]  # Retrieve the room 1 description

        client.send("move east")
        room_descriptions[0] = client.response.split("OK! ")[1]  # Retrieve the room 0 description

        client.send("move east")
        room_descriptions[2] = client.response.split("OK! ")[1]  # Retrieve the room 2 description

        client.send("move west")
        client.send("move north")
        room_descriptions[3] = client.response.split("OK! ")[1]  # Retrieve the room 3 description

        client.send("move south")
        self.assertIn(room_descriptions[0], client.response, "Client can navigate through server's rooms.")

        client.send("move west")
        self.assertIn(room_descriptions[1], client.response, "Client can navigate through server's rooms.")

        client.send("move east")
        client.send("move east")
        self.assertIn(room_descriptions[2], client.response, "Client can navigate through server's rooms.")

        client.send("move west")
        client.send("move north")
        self.assertIn(room_descriptions[3], client.response, "Client can navigate through server's rooms.")

        self.assertEqual(4, len(set(room_descriptions.keys())), "Room descriptions are unique.")

        client.send("say Hello?")
        self.assertIn("You say, \"Hello?\"", client.response, "Client can see their speakings.")

        client.send("quit")
        self.assertEqual("OK! Goodbye!", client.response, "The server says goodbye.")





