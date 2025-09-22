# COMP28112 Distributed Systems – Exercise 2: Multi-Client Chat System

## Overview
This project implements a multi-client chat system using Python socket programming.  
It provides a more robust solution than the simple PHP state store from Exercise 1, supporting:
- Multiple clients connecting concurrently
- Registration of usernames
- Broadcasting messages to all users
- Sending private messages to specific users
- Listing all online users
- Handling disconnections gracefully

## Project Structure
- myserver.py – Custom server implementation  
- myclient.py – Client program for interacting with the server  
- ex2utils.py – Provided utility module (base classes for Server/Client)  
- commands.json – Protocol description in JSON format  

## How to Run

### 1. Start the server
```bash
python3 myserver.py localhost 8090
```

### 2. Start a client
Open another terminal and run:
```bash
python3 myclient.py localhost 8090
```

### 3. Test with Telnet (optional)
You can also connect with:
```bash
telnet localhost 8090
```

## Protocol Commands
| Command              | Description                     | Example                   |
|----------------------|---------------------------------|---------------------------|
| register <name>      | Register a new username         | register Alice            |
| send_all <msg>       | Send message to all users       | send_all hello everyone   |
| send_to <user> <msg> | Send a private message          | send_to Bob hi there      |
| online_users         | List currently connected users  | online_users              |
| close_connection     | Disconnect from server          | close_connection          |


## Testing
1. Run the server in one terminal.
2. Start at least two clients in separate terminals.
3. Register unique usernames.
4. Try sending broadcast and private messages.
5. Use online_users to confirm active connections.
6. Test disconnection with close_connection and re-connection with a new username.

## Notes
Written in Python 3.
Uses the socket and threading libraries.
Follows coursework specification for COMP28112 Distributed Systems Exercise 2.