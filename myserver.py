import sys
import threading
from ex2utils import Server

class MyServer(Server):

    def onStart(self):
        # This method is called when the server starts
        self.clients = []  # List to store connected clients (wrapped sockets)
        self.lock = threading.Lock()
        print("Server has started")

    def onConnect(self, socket):
        # This method is called when a client connects
        # Initialize the client's username as None (not registered).
        socket.username = None
        with self.lock:
            self.clients.append(socket)
        print("new client connected")
        self.printActiveClients()

    def onMessage(self, socket, message):
        # This method is called when a message is received from a client.
        # Parse the message into command and parameters.
        parts = message.strip().split(" ", 1)
        command = parts[0].lower()  # Case-insensitive command matching
        parameters = parts[1] if len(parts) > 1 else ""

        # Process the commands according to the designed protocol.
        if command == "register":
            # Command: register <username>
            if parameters == "":
                print("Error: Missing username for registration")
            else:
                # Check if the username is already taken
                with self.lock:
                    for client in self.clients:
                        if client.username == parameters:
                            print("Error: Username already exists")
                            return True  # Keep connection alive even if error occurs
                    # If username is available, register the client.
                    socket.username = parameters
                print(f"{socket.username} registered")
                # Send registration confirmation to client
                socket.send(f"{socket.username} registered".encode())
        elif command == "send_all":
            # Command: send_all <message>
            if socket.username is None:
                print("not registered")
                # Inform client they are not registered
                socket.send("not registered".encode())
            else:
                # Prepare the message to broadcast.
                broadcast_message = f"message from {socket.username}: {parameters}"
                print(broadcast_message)
                # Broadcast message to all registered clients
                with self.lock:
                    for client in self.clients:
                        # Send only to registered clients.
                        if client.username is not None:
                            client.send(broadcast_message.encode())
        elif command == "send_to":
            # Command: send_to <target_username> <message>
            if socket.username is None:
                print("not registered")
                # Inform client they are not registered
                socket.send("not registered".encode())
            else:
                subparts = parameters.split(" ", 1)
                if len(subparts) < 2:
                    print("Error: Missing target username or message for private message")
                    # Inform client about the missing parameters
                    socket.send("Error: Missing target username or message for private message".encode())
                else:
                    target = subparts[0]
                    msg = subparts[1]
                    found = False
                    with self.lock:
                        for client in self.clients:
                            if client.username == target:
                                found = True
                                # Prepare private message.
                                private_message = f"message from {socket.username}: {msg}"
                                print(private_message)
                                # Send private message to target client
                                client.send(private_message.encode())
                                break
                    if not found:
                        print("Error: Target user not found")
                        # Inform sender that target user was not found
                        socket.send("Error: Target user not found".encode())
        elif command == "online_users":
            # Command: online_users - list all registered users.
            with self.lock:
                registered = [client.username for client in self.clients if client.username is not None]
            online_message = f"online users: {', '.join(registered)}"
            print(online_message)
            # Send online users list to the requesting client
            socket.send(online_message.encode())
        elif command == "close_connection":
            # Command: close_connection - client requested to close connection.
            return False
        else:
            # Unrecognized command.
            print("unknown command")
            # Inform client about unknown command
            socket.send("unknown command".encode())

        return True  # Keep the connection alive by default

    def onDisconnect(self, socket):
        # This method is called when a client disconnects.
        with self.lock:
            if socket in self.clients:
                self.clients.remove(socket)
        print("a client disconnected")
        self.printActiveClients()

    def printActiveClients(self):
        # Print the number of active clients in the required format.
        with self.lock:
            count = len(self.clients)
        print(f"{count} active clients")

# Parse command-line arguments for IP address and port
ip = sys.argv[1]
port = int(sys.argv[2])

# Create and start the server
server = MyServer()
server.start(ip, port)
