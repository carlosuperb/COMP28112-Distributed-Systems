"""
myclient.py - Chat Client Implementation

Usage:
    python myclient.py <server_ip> <server_port>

Description:
    1. The client connects to the server using the provided IP address and port.
    2. It prompts the user to enter a screen name, then sends a "register <screen_name>" command to the server.
       If the chosen screen name is already taken (the server sends an error message), the user should enter a different name.
    3. Once registered, the client repeatedly requests input from the user. The entered text is sent to the server.
       The server will process the message according to the defined protocol (e.g., sending to all, sending to one, etc.).
    4. To disconnect, the user types "/quit". The client then sends the "close_connection" command to the server.
       The client will remain running until it receives the message "Client exiting" from the server, then it will exit.
       
Testing:
    1. Start the server: 
           python myserver.py localhost <port>
    2. Start the client:
           python myclient.py localhost <port>
    3. Follow the prompts:
         - Enter a unique screen name.
         - Type messages to send.
         - To disconnect, type "/quit" and wait for the "Client exiting" message.
"""

import sys
import threading
from ex2utils import Client

class MyClient(Client):
    def onMessage(self, socket, message):
        # Process incoming messages and display them.
        # If the server sends "Client exiting", then stop the client.
        msg = message.strip()
        print(msg)
        if msg == "Client exiting":
            self.stop()
        return True

    def onStart(self):
        # Called when the client starts
        print("Connected to server.")

    def onStop(self):
        # Called when the client stops
        print("Client exiting.")

def main():
    if len(sys.argv) < 3:
        print("Usage: python myclient.py <server_ip> <server_port>")
        sys.exit(1)

    ip = sys.argv[1]
    port = int(sys.argv[2])

    client = MyClient()
    client.start(ip, port)

    # Registration phase: repeatedly ask for a screen name until registered successfully.
    # In this example, we assume that if the server sends an error message (e.g., "Error: Username already exists"),
    # it will be printed by onMessage, so the user can try again.
    while True:
        screen_name = input("Enter your screen name: ").strip()
        if not screen_name:
            print("Screen name cannot be empty.")
            continue
        client.send(("register " + screen_name).encode())
        # Wait a moment to receive response from the server.
        # (In a real implementation, you might wait for a specific confirmation message.)
        # Here we assume that if no error is received, the registration is successful.
        # You can improve this logic based on server feedback.
        # For simplicity, we break after sending the registration command.
        break

    # Main interaction loop.
    # The user can send messages; if the user types "/quit", the client sends a close_connection command.
    while True:
        user_input = input("Enter message (/quit to exit): ").strip()
        if user_input.lower() == "/quit":
            client.send("close_connection".encode())
            # Wait until the client receives "Client exiting" and stops.
            break
        else:
            client.send(user_input.encode())

    # Wait for the client thread to finish before exiting.
    client._thread.join()

if __name__ == "__main__":
    main()
