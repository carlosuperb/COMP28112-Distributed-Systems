# COMP28112 Distributed Systems – Exercise 3: Wedding Planner

## Overview
This project implements a **distributed booking system** (Wedding Planner) that coordinates hotel and band reservations through RESTful web APIs.  
The client application interacts with two external services (hotel and band), ensuring both reservations are made for the same slot.  
It handles concurrency, retries, caching, and error management, while following the one-request-per-second constraint.

Key features:
- View current held slots for hotel and band
- View first 20 available slots for both services
- Book slots (hotel, band, or both)
- Cancel reservations (hotel, band, or both)
- Find first 5 matching available slots
- Reserve the earliest matching slot, upgrading if a better one appears
- Cancel unnecessary reservations, keeping at most one per service
- Retry failed operations with delay, while respecting API limits

## Project Structure
- `booking.py` – Main Wedding Planner client application (menu-driven)  
- `reservationapi.py` – API wrapper for hotel and band services (with retries, caching, and error handling)  
- `exceptions.py` – Custom exceptions for API error codes  
- `api.ini` – Configuration file containing API URLs, tokens, and global parameters  

## How to Run

### 1. Prepare the environment
Make sure you have **Python 3** installed. Install required dependencies:

```bash
pip install requests simplejson
```
### 2. Configure API keys
Open api.ini and insert your hotel and band API tokens:
```ini
[global]
retries = 3
delay = 1
cache_ttl = 90

[hotel]
url = https://web.cs.manchester.ac.uk/hotel
key = YOUR_HOTEL_API_KEY

[band]
url = https://web.cs.manchester.ac.uk/band
key = YOUR_BAND_API_KEY
```

### 3. Run the Wedding Planner client
```bash
python3 booking.py
```
You will see the menu displayed:
----- Wedding Planner Application Menu -----
1. View current held slots
2. View first 20 available slots
3. Book a specified slot
4. Cancel a booking for a specified slot
5. View first 5 matching available slots
6. Reserve the earliest matching slot
7. Cancel unnecessary reservations
0. Exit

## Menu Options
| Option | Description |
|--------|-------------|
| 1 | View current held slots (hotel and band) |
| 2 | View first 20 available slots for hotel and band |
| 3 | Book a specified slot (hotel / band / both) |
| 4 | Cancel a booking for a specified slot (hotel / band / both) |
| 5 | View first 5 matching available slots (intersection) |
| 6 | Reserve the earliest matching slot, upgrading if a better one appears |
| 7 | Cancel unnecessary reservations, keeping at most one per service |
| 0 | Exit the application |

## Testing
Start the client with python3 booking.py.
The application will automatically display current held slots.
Use option 2 to view available slots.
Use option 3 to book slots; test invalid IDs to trigger error handling.
Use option 5 or 6 to test matching logic and automatic upgrades.
Use option 7 to cancel redundant reservations.
Confirm one request per second rate limit is respected.

## Notes
Written in Python 3
Uses requests and simplejson libraries
Respects API usage rules (retry logic, one request per second)
Follows coursework specification for COMP28112 Distributed Systems Exercise 3