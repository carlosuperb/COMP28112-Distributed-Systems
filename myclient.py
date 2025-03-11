"""
myclient.py - Chat Client Implementation

Description:
    1. The client connects to the server using the provided IP address and port.
    2. It prompts the user to enter a screen name, then sends a "register <screen_name>" command to the server.
       If the chosen screen name is already taken (the server sends an error message),
       then user should enter a different name by using "register <screem_name>" command.
    3. Once registered, the client repeatedly requests input from the user. The entered text is sent to the server,
       which processes it according to the defined protocol.
    4. To disconnect, the user types "close_connection". The client then sends the "close_connection"
       command to the server and will remain running until it receives "Client exiting"
       from the server, or until it encounters a connection error (e.g., server forcibly closed).

Testing:
    1. Start the server:
        - Example: "python3 myserver.py localhost 8090"

        - Expected (Server Terminal): Server has started
    
    2. Start the client:
        2.1. OPEN THE FIRST CLIENT TERMINAL
        - Example: "python3 myclient.py localhost 8090"

        - Expected (Server Termianl): new client connected
                                      1 active clients
        - Expected (Client Terminal): Connected to server.
                                      Enter your screen name: 

        2.2 ENTER THE FIRST SCREEN NAME
        - Example: Enter your screen name: Carlos

        - Expected (Server & Client Terminal): Carlos registered

        2.3 OPEN THE SECOND CLIENT TERMINAL
        -Example: "python3 myclient.py localhost 8090"

        - Expected (Server Termianl): new client connected
                                      2 active clients
        - Expected (Client Terminal): Connected to server.
                                      Enter your screen name: 

        2.4 ENTER THE SECOND SCREEN NAME (with existing name)
        - Example: "Enter your screen name: Carlos"

        - Expected (Client Terminal): Error: Username already exists

    3. Test the protocol in the following order to demonstrate all functionality:
        a) "register <username>" in the second client (unregistered) termianl
            - Example: "register Bob"

            - Expected (Server & Client Terminal): Bob registered

        b) "send_all <message>" in the first client (Carlos) terminal
            - Example: "send_all Hello everyone"

            - Expected (Carlos & Bob Client Terminal): message from Carlos: Hello everyone
            - Expected (Server Terminal): [BROADCAST] Carlos => ALL: Hello everyone
        
        c) "send_to <target_user> <message>" in the second client (Bob) terminal
            - Example: "send_to Carlos Good morning"

            - Expected (Carlos Client Terminal): message from Bob: Good morning
            - Expected (Server Terminal): [PRIVATE] Bob => Carlos: Good morning

        d) "online_users" in the second client (Bob) terminal
            - Example: "online_users"

            - Expected (Bob Client Terminal): online users: Carlos, Bob

        e) "close_connection" in the first client (Carlos) terminal
            - Example: "close_connection"

            - Expected (Carlos Client Terminal): Client exiting.
            - Expected (Server Terminal): a client disconnected
                                          1 active clients

        f) "close_connection" in the second client (Bob) terminal
            - Example: "close_connection"

            - Expected (Bob Client Terminal): Client exiting.
            - Expected (Server Terminal): a client disconnected
                                          0 active clients
        
    4. Close the server
        - Example: <Ctrl+C>
        - Expected (Server Terminal): Server is stopping...
                                      All client connections have been closed. Resources cleaned up.
"""
import sys
from ex2utils import Client

class MyClient(Client):
    def __init__(self):
        """
        Constructor for MyClient.
        Initializes a flag (has_printed_exiting) to track whether the
        "Client exiting" message has already been printed.
        """
        super().__init__()
        self.has_printed_exiting = False

    def onMessage(self, socket, message):
        """
        Called whenever the client receives a newline-delimited message from the server.
        The 'message' parameter does not include the newline character.

        This method checks if the server has sent a "Client exiting" message.
        If so, it ensures that "Client exiting" is printed only once by checking
        the has_printed_exiting flag. Then it calls self.stop() to halt the client.
        Otherwise, it simply prints the server's message.
        """
        # Move cursor to the beginning of the line to avoid overlapping with user input
        sys.stdout.write("\r")

        msg = message.strip()

        # If the server indicates that the client should exit,
        # print "Client exiting" only once and then stop the client.
        if msg == "Client exiting":
            if not self.has_printed_exiting:
                print(msg)
                self.has_printed_exiting = True
            self.stop()
        else:
            print(msg)

        return True
    
    def onStart(self):
        """
        Called when the client starts.

        Prints a simple message indicating that the client has connected to the server.
        """
        print("Connected to server.")

    def onStop(self):
        """
        Called when the client stops.

        If the "Client exiting" message hasn't been printed yet (e.g., the server
        didn't send it or the client stopped for another reason), print it here
        to ensure the user sees an exit message.
        """
        if not self.has_printed_exiting:
            print("Client exiting.")
            self.has_printed_exiting = True

def run_client(ip, port):
    """
    Runs the client logic:
      1. Create and start MyClient.
      2. Prompt for screen name and send register command.
      3. Enter main interaction loop until user requests close_connection or server forcibly closes.
    """
    client = MyClient()
    client.start(ip, port)

    # Registration phase
    while True:
        screen_name = input("Enter your screen name: ").strip()
        if not screen_name:
            print("Screen name cannot be empty.")
            continue
        if " " in screen_name:
            print("Screen name cannot contain spaces.")
            continue

        # Send the registration command
        try:
            client.send(f"register {screen_name}".encode())
        except OSError:
            # If server is already closed
            print("Connection error: The server might be closed.")
            client.stop()
        break

    # Main interaction loop
    while client.isRunning():
        user_input = input().strip()

        # If the user wants to close the connection gracefully
        if user_input.lower() == "close_connection":
            try:
                client.send("close_connection".encode())
            except OSError:
                # Server might be closed already
                print("Connection error: The server might be closed.")
                client.stop()
            break
        else:
            # Send the user input to the server
            try:
                client.send(user_input.encode())
            except OSError:
                print("Connection error: The server might be closed.")
                client.stop()
                break

    # Once the loop ends, if client is still running, stop it and join
    if client.isRunning():
        client.stop()
    client._thread.join()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python myclient.py <server_ip> <server_port>")
        sys.exit(1)

    ip = sys.argv[1]
    port = int(sys.argv[2])
    run_client(ip, port)
