"""
run_checkers_client.py
    - Main script for executing a local simulation with a PyGame GUI via Server Connection.

Anthony Trezza
26 Jan 2018

CHANGE LOG:
    - 1/26/2018 trezza - Software Birthday <(^.^)>
"""

from utils.jsonsocket import *
from msgs.messages import *


class CheckersClient:
    def __init__(self, name, host, port):
        self._host = host
        self._port = port
        self._name = name
        self._client = Client()

        self.state = "NOT_CONNECTED"

        # Game Rules
        self._timeout = -1
        self._color = 'none'
        self._board_size = -1

    def connect(self):
        # Try to connect to the server
        try:
            self._client.connect(self._host, self._port)
        except ...:
            raise Exception("Could not connect to the server...")

        print("[+] Connection established!")
        self.state = "CONNECTED"

        print("[.] Sending ConnectionRequest message...")
        # Send the connection request message
        connect_request = ConnectionRequest(self._name)
        data = dict(connect_request)

        try:
            self._client.send(data)
        except ...:
            raise Exception("Could not send the connection request message to the server...")

        print("[+] ConnectionRequest message sent and received!")

    def play(self):
        # Initialize the connection
        print("[.] Initializing Connection...")
        self.connect()

        # Loop until the game is over
        while self.state != "GAME_OVER":

            # If the state is connected but we aren't in a game yet,
            if self.state == "CONNECTED":
                response = self._client.recv()
                w4o = WaitingForOpponent()
                w4o.from_dict(response)

                if w4o.id != MESSAGE_IDS["WAITING_FOR_OPPONENT"] or w4o.flag is None:
                    raise Exception("INVALID MESSAGE")
                elif w4o.flag is True:
                    print("[.] Waiting for opponent...")
                    continue
                else:
                    print("[+] Opponent found!")
                    self.state = "FOUND_GAME"

            elif self.state == "FOUND_GAME":
                # Wait for the rules...
                response = self._client.recv()
                gr = GameRules()
                gr.from_dict(response)

                # TODO: More error checking...
                if gr.id != MESSAGE_IDS["GAME_RULES"]:
                    raise Exception("INVALID MESSAGE")

                self._color = gr.player_color
                self._timeout = gr.time_limit
                self._board_size = gr.board_size

                try:
                    self.player(self._board_size, self._timeout)
                except:
                    raise Exception("Could not launch AI Program")

                self.state = "GAME_LAUNCHED"

            elif self.state == "GAME_LAUNCHED":
                response = self._client.recv()
                bg = BeginGame()
                bg.from_dict(response)

                # TODO: More error checking...
                if bg.id != MESSAGE_IDS["BEGIN_GAME"]:
                    raise Exception("INVALID MESSAGE")

                self.state


def signal_handler(signal, frame):
    print("[-] Ctrl+C!  Shutting down...")
    gs.shutdown()
    sys.exit(0)

def main():
    """ main()
        -  Just launches the server
    :param: void
    :return: void
    """

    # Register the crl+c signal handler
    signal.signal(signal.SIGINT, signal_handler)

    # Instantiate the game server
    gs = GameServer(2004, 0.1, 10, 2)
    try:
        gs.open_socket()
        gs.run()
    finally:
        client.close()


if __name__ == '__main__':
    main()