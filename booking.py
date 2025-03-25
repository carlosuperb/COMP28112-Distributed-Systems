#!/usr/bin/python3

import reservationapi
import configparser
import time

# Load the configuration file containing the URLs and keys
config = configparser.ConfigParser()
config.read("api.ini")

# Create an API object to communicate with the hotel API
hotel = reservationapi.ReservationApi(config['hotel']['url'],
                                      config['hotel']['key'],
                                      int(config['global']['retries']),
                                      float(config['global']['delay']))

# Create an API object to communicate with the band API
band = reservationapi.ReservationApi(config['band']['url'],
                                     config['band']['key'],
                                     int(config['global']['retries']),
                                     float(config['global']['delay']))

def display_menu():
    """
    Display the menu options for the Wedding Planner Application.
    """
    print("\n----- Wedding Planner Application Menu -----")
    print("1. View current held slots")
    print("2. View first 20 available slots")
    print("3. Book a specified slot")
    print("4. Cancel a booking for a specified slot")
    print("5. View first 5 matching available slots")
    print("6. Reserve the earliest matching slot")
    print("7. Cancel unnecessary reservations (keep earliest one)")
    print("0. Exit")

def view_held_slots():
    """
    Retrieve and display the slots currently held by the hotel and the band.
    """
    try:
        hotel_held_slots = hotel.get_slots_held()
        band_held_slots = band.get_slots_held()

        # Extract the slot IDs from each reservation entry.
        hotel_slot_ids = [slot["id"] for slot in hotel_held_slots]
        band_slot_ids = [slot["id"] for slot in band_held_slots]

        # Format the slot IDs as a comma-separated list for display.
        hotel_slots_str = ", ".join(hotel_slot_ids) if hotel_slot_ids else "No slots"
        band_slots_str = ", ".join(band_slot_ids) if band_slot_ids else "No slots"

        print("Hotel held slots:", hotel_slots_str)
        print("Band held slots:", band_slots_str)
    except Exception as e:
        print("Error viewing held slots:", e)

def view_available_slots(limit):
    """
    Retrieve and display the first 'limit' available slots for both hotel and band.
    """
    try:
        hotel_available_slots = hotel.get_slots_available()
        band_available_slots = band.get_slots_available()

        # Extract the slot IDs from the first 'limit' available entries.
        hotel_slot_ids = [slot['id'] for slot in hotel_available_slots[:limit]]
        band_slot_ids = [slot['id'] for slot in band_available_slots[:limit]]

        # Format the slot IDs as a comma-separated list for display.
        hotel_slots_str = ", ".join(hotel_slot_ids) if hotel_slot_ids else "No slots"
        band_slots_str = ", ".join(band_slot_ids) if band_slot_ids else "No slots"

        print(f"Hotel available slots (first {limit}): {hotel_slots_str}")
        print(f"Band available slots (first {limit}): {band_slots_str}")
    except Exception as e:
        print("Error viewing available slots:", e)

def book_slot():
    """
    Prompt the user for a slot ID and attempt to book that slot for both hotel and band.
    """
    slot = input("Please enter the slot ID to book: ")
    try:
        hotel.reserve_slot(slot)
        band.reserve_slot(slot)
        print(f"Booking successful! Slot {slot} has been reserved for both the hotel and the band.")
    except Exception as e:
        print("Error booking slot:", e)

def cancel_slot():
    """
    Prompt the user for a slot ID and attempt to cancel that booking for both hotel and band.
    """
    slot = input("Please enter the slot ID to cancel: ")
    try:
        hotel.release_slot(slot)
        band.release_slot(slot)
        print(f"Cancellation successful! Slot {slot} has been cancelled for both the hotel and the band.")
    except Exception as e:
        print("Error cancelling slot:", e)

def find_matching_slots(limit):
    """
    Retrieve the available slots for both hotel and band, find the intersection,
    sort them in ascending order, and display the first 'limit' matches.
    """
    try:
        hotel_available_slots = hotel.get_slots_available()
        band_available_slots = band.get_slots_available()

        # Extract slot IDs and determine the common slots
        hotel_ids = {slot["id"] for slot in hotel_available_slots}
        band_ids = {slot["id"] for slot in band_available_slots}

        # Find the intersection and sort the IDs numerically
        matching = sorted(hotel_ids & band_ids, key=lambda x: int(x))

        # Select the first 'limit' slots from the sorted list
        matching_limited = matching[:limit]

        # Format the slot IDs as a comma-separated string for display
        if matching_limited:
            matching_str = ", ".join(matching_limited)
        else:
            matching_str = "No matching slots"

        print(f"First {limit} matching slots: {matching_str}")
    except Exception as e:
        print("Error finding matching slots:", e)

def reserve_earliest_matching_slot():
    """
    Find the earliest matching available slot for both hotel and band, and book it.
    """
    try:
        hotel_available_slots = hotel.get_slots_available()
        band_available_slots = band.get_slots_available()

        # Extract the slot IDs from each service's available slots.
        hotel_ids = {slot["id"] for slot in hotel_available_slots}
        band_ids = {slot["id"] for slot in band_available_slots}

        # Determine the common slots and sort them numerically.
        matching = sorted(hotel_ids & band_ids, key=lambda x: int(x))
        if matching:
            # Use the earliest (first) matching slot.
            slot = matching[0]
            print("Reserving the earliest matching slot:", slot)
            hotel.reserve_slot(slot)
            band.reserve_slot(slot)
            print("Booking successful! Slot {slot} has been reserved for both the hotel and the band.")
        else:
            print("No matching slots available.")
    except Exception as e:
        print("Error reserving earliest matching slot:", e)

def cancel_unneeded_reservations():
    """
    Cancel any extra reservations for both hotel and band,
    keeping only the earliest slot for each.
    """
    try:
        reservations = hotel.get_slots_held()

        if reservations:
            # Sort the reservations by slot ID (converted to integer)
            sorted_reservations = sorted(reservations, key=lambda s: int(s["id"]))

            # The earliest reservation
            remaining_reservation = sorted_reservations[0]["id"]

            # All reservations after the first one will be cancelled
            cancelled_reservations = [slot["id"] for slot in sorted_reservations[1:]]
            
            # Cancel extra reservations for both hotel and band
            for slot in sorted_reservations[1:]:
                hotel.release_slot(slot["id"])
                band.release_slot(slot["id"])
            
            # Display cancellation and remaining information to the user
            if cancelled_reservations:
                print("Cancelled extra reservations for slot: " + ", ".join(cancelled_reservations))
            else:
                print("No extra reservations to cancel.")
            print("Remaining reservation: " + remaining_reservation)
        else:
            print("No reservations found.")
    except Exception as e:
        print("Error cancelling extra reservations. Please try again later.")

def main():
    """
    Main function to run the Wedding Planner Application.
    """
    print("----- Welcome to the Wedding Planner Application! -----")
    view_held_slots()
    while True:
        display_menu()
        choice = input("Please select an option: ")
        if choice == '1':
            view_held_slots()
        elif choice == '2':
            view_available_slots(20)
        elif choice == '3':
            book_slot()
        elif choice == '4':
            cancel_slot()
        elif choice == '5':
            find_matching_slots(5)
        elif choice == '6':
            reserve_earliest_matching_slot()
        elif choice == '7':
            cancel_unneeded_reservations()
        elif choice == '0':
            print("Exiting application.")
            break
        else:
            print("Invalid option, please try again.")
        time.sleep(1)

if __name__ == '__main__':
    main()