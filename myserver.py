import sys
from ex2utils import Server

class MyServer(Server):

    def onStart(self):
        """
        This is called when the server starts - i.e. shortly after the start() method is
        executed. Any server-wide variables should be created here.
        """
        # Initialize a list to store connected clients (wrapped sockets).
        self.clients = []

        # Indicate in the console that the server has started.
        self.printOutput("Server has started")

    def onStop(self):
        """
        This is called just before the server stops, allowing you
        to clean up any server-wide variables you may still have set.
        """
        # Notify that the server is stopping.
        self.printOutput("Server is stopping...")

        # Iterate through all connected clients.
        for client in self.clients:
            try:
                # Send a shutdown message to the client.
                client.send("Server is shutting down. Disconnecting...\n".encode())
                # Close the client's connection.
                client.close()
            except:
                # If an error occurs (e.g., the client is already closed), ignore it.
                pass
        
        # Clear the list of clients to free up resources.
        self.clients.clear()
        
        self.printOutput("All client connections have been closed. Resources cleaned up.")

    def onConnect(self, socket):
        """
        This is called when a client starts a new connection with the server, with that
        connection's socket being provided as a parameter. You may store connection-
        specific variables directly in this socket object.
        e.g. socket.myNewVariableName = myNewVariableValue
        """
        # Initialize the client's username as None (nindicating the client has not registered yet).
        socket.username = None

        # Add the new client's socket to the server's list of connected clients.
        self.clients.append(socket)

        # Output a message to the server to indicate that a new client has connected.
        self.printOutput("new client connected")

        # Print the updated number of active clients.
        number = len(self.clients)
        self.printOutput(f"{number} active clients")

    def onMessage(self, socket, message):
        """
        This is called when a client sends a new-line delimited message to the server.
        The message parameter DOES NOT include the new-line character.
        """
        # Parse the message into command and parameters.
        parts = message.strip().split(" ", 1)
        command = parts[0].lower()
        parameters = parts[1] if len(parts) > 1 else ""

        # Process the commands according to the designed protocol.
        # Command: register <username>
        if command == "register":
            # Check if user already registered
            if socket.username is not None:
                socket.send("Error: You have already registered".encode())
                return True
            
            # Check if username is empty
            if parameters == "":
                self.printOutput("Error: Missing username for registration")
                socket.send("Error: Missing username for registration".encode())
                return True

            # Check if username contains space
            if " " in parameters:
                self.printOutput("Error: Username cannot contain spaces")
                socket.send("Error: Username cannot contain spaces".encode())
                return True
            
            # Check if username is taken
            for client in self.clients:
                if client.username == parameters:
                    self.printOutput("Error: Username already exists")
                    socket.send("Error: Username already exists".encode())
                    return True
                    
            # If username is available, register the client.
            socket.username = parameters
            self.printOutput(f"{socket.username} registered")
            socket.send(f"{socket.username} registered\n".encode())

        # Command: send_all <message>
        elif command == "send_all":
            if socket.username is None:
                socket.send("not registered".encode())
            else:
                # Prepare the message for clients.
                broadcast_message = f"message from {socket.username}: {parameters}"

                # Log the broadcast message on the server for tracking
                self.printOutput(f"[BROADCAST] {socket.username} => ALL: {parameters}")

                # Send the broadcast message to all registered clients.
                for client in self.clients:
                    if client.username is not None:
                        client.send(broadcast_message.encode())

        # Command: send_to <target_username> <message>
        elif command == "send_to":
            if socket.username is None:
                socket.send("not registered".encode())
            else:
                # Split the parameters into target username and the message text.
                subparts = parameters.split(" ", 1)

                # Check if both target username and message text are provided.
                if len(subparts) < 2:
                    # If either is missing, send an error message to the sender.
                    socket.send("Error: Missing target username or message for private message".encode())        
                else:
                    # Extract target username and message.
                    target = subparts[0]
                    msg = subparts[1]
                    found = False   # Flag to indicate if the target user was found.

                    # Iterate through all connected clients to find the target user.
                    for client in self.clients:
                        # Compare the client's username with the target username.
                        if client.username == target:
                            found = True

                            # Prepare the private message in the required format.
                            private_message = f"message from {socket.username}: {msg}"

                            # Log the private message action on the server for tracking.
                            self.printOutput(f"[PRIVATE] {socket.username} => {target}: {msg}")

                            # Send the private message to target client
                            client.send(private_message.encode())

                            # Stop iterating once the target is found.
                            break
                    
                    # If no client with the target username was found, notify the sender.
                    if not found:
                        socket.send("Error: Target user not found".encode())

        # Command: online_users - list all registered users.
        elif command == "online_users":
            if socket.username is None:
                socket.send("not registered".encode())
            else:
                # Create a list of usernames for all clients that have registered.
                registered = [client.username for client in self.clients if client.username is not None]
                # Construct the online users message in the required format.
                online_message = f"online users: {', '.join(registered)}"
                # Send the online users list back to the requesting client.
                socket.send(online_message.encode())
        
        # Command: close_connection - client requested to close connection.
        elif command == "close_connection":
            return False
        
        # Unknown command
        else:
            # Inform client about unrecognized command
            socket.send("unknown command".encode())

        return True  # Keep the connection alive by default

    def onDisconnect(self, socket):
        """
        This is called when a client's connection is terminated. As with onConnect(),
        the connection's socket is provided as a parameter. This is called regardless
        of who closed the connection.

        This function safely removes the disconnected client's socket from the list of
        active clients and then prints a message indicating that a client has disconnected.
        It also prints the updated number of active clients.
        """
        # Check if the socket exists in the clients list and remove it if found.
        if socket in self.clients:
            self.clients.remove(socket)
        
        # Output a message to the server to indicate that a client has disconnected.
        self.printOutput("a client disconnected")

        # Print the updated number of active clients.
        number = len(self.clients)
        self.printOutput(f"{number} active clients")

# Parse command-line arguments for IP address and port
ip = sys.argv[1]
port = int(sys.argv[2])

# Create and start the server
server = MyServer()
server.start(ip, port)
