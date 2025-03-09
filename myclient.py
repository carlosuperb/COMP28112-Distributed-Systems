"""
myclient.py - Chat Client Implementation

Usage:
    python3 myclient.py <server_ip> <server_port>

Description:
    1. The client connects to the server using the provided IP address and port.
    2. It prompts the user to enter a screen name, then sends a "register <screen_name>" command to the server.
       If the chosen screen name is already taken (the server sends an error message),
       the user should enter a different name by using "register <screem_name>" command.
    3. Once registered, the client repeatedly requests input from the user. The entered text is sent to the server,
       which processes it according to the defined protocol. The following commands are supported:
       
       Protocol Commands:
         - register %user%
             Register a new user with the specified screen name (e.g., "register Alice").
         - send_all %msg%
             Send a message to all connected users (e.g., "send_all Hello everyone").
         - send_to %user% %msg%
             Send a private message to a specific user (e.g., "send_to Bob How are you?").
         - online_users
             Get the list of all currently registered (connected) users.
         - close_connection
             Disconnect the current client from the server.
    
    4. To disconnect, the user types "close_connection". The client then sends the "close_connection"
       command to the server and will remain running until it receives "Client exiting"
       from the server, or until it encounters a connection error (e.g., server forcibly closed).

Testing:
    1. Start the server:
           python3 myserver.py localhost <port>

       - Example: python3 myserver.py localhost 8090
       - Expected:
           Server has started
           new client connected
           ...
    
    2. Start the client:
           python3 myclient.py localhost <port>

       OPEN THE FIRST CLIENT TERMINAL

       - Example: python3 myclient.py localhost 8090
       - Expected: "Enter your screen name: "
       You will be prompted to enter a screen name. Type one without spaces, e.g., "Alice".

       OPEN THE SECOND CLIENT TERMINAL

       - Example: python3 myclient.py localhost 8090
       - Expected: "Enter your screen name: "
       You will be prompted to enter a screen name. Type one without spaces, e.g., "Bob".

    3. Test the protocol in the following order to demonstrate all functionality:
       a) "register <username>"
          - Example: "register Alice"
          - Expected: Both server and client terminal showing "Alice registered"
          
          If you successfully register a username in the second step, 3a can be skipped.
          Otherwise, you cannot use command 3b to 3d, as the client terminal will show "not registered"

       b) "send_all <message>"
          - Example: "send_all Hello everyone"
          - Expected: All connected (registered) users see "message from Alice: Hello everyone".

       c) "online_users"
          - Lists all users currently registered (including yourself).

       d) "send_to <target_user> <message>"
          - Example: "send_to Bob Hi Bob!"
          - Expected: Only Bob receives "message from Alice: Hi Bob!".

       e) "close_connection"
          - Gracefully disconnects from the server. The client should stop after receiving "Client exiting".

    4. You can also start multiple clients to test private messages ("send_to") and broadcast messages ("send_all").
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
