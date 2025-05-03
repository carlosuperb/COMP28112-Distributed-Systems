#!/usr/bin/python3

import reservationapi
import configparser
import time
from exceptions import SlotUnavailableError

# Load the configuration file containing the URLs and keys
config = configparser.ConfigParser()
config.read("api.ini")

# Read the global configuration
retries   = int(config["global"]["retries"])
delay     = float(config["global"]["delay"])
cache_ttl = float(config["global"].get("cache_ttl", 90))

# Create an API object to communicate with the hotel API
hotel = reservationapi.ReservationApi(
    config["hotel"]["url"],
    config["hotel"]["key"],
    retries,
    delay,
    cache_ttl=cache_ttl
)

# Create an API object to communicate with the band API
band = reservationapi.ReservationApi(
    config["band"]["url"],
    config["band"]["key"],
    retries,
    delay,
    cache_ttl=cache_ttl
)


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
    print("7. Cancel unnecessary reservations")
    print("0. Exit")


def view_held_slots():
    """
    Retrieve and display the slots currently held by the hotel and the band.
    """
    try:
        hotel_held_slots = hotel.get_slots_held(service="Hotel")
        band_held_slots  = band.get_slots_held(service="Band")

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
        hotel_available_slots = hotel.get_slots_available(service="Hotel")
        band_available_slots  = band.get_slots_available(service="Band")

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
    Ask the user which service to book (hotel/band/both) or quit to menu,
    then attempt to reserve the specified slot.
    """
    # Prompt until the user enters a valid option or chooses to quit.
    target = ""
    while target not in {"h", "b", "a", "q"}:
        target = (
            input("Book for (h)otel, (b)and, (a)ll, or (q)uit to menu? ")
            .strip()
            .lower()
        )
        if target not in {"h", "b", "a", "q"}:
            print("Invalid choice. Please try again.")

    # Quit back to the main menu without booking anything.
    if target == "q":
        print("Returning to main menu...")
        return
    
    # Ask for the slot ID once the service choice is confirmed.
    slot = input("Enter the slot ID to book: ").strip()
    
    try:
        if target == "h":
            hotel.reserve_slot(slot, service="Hotel")
            print(f"Booking successful! Slot {slot} reserved for the hotel.")
        elif target == "b":
            band.reserve_slot(slot,  service="Band")
            print(f"Booking successful! Slot {slot} reserved for the band.")
        else:  # target == "a"
            hotel.reserve_slot(slot, service="Hotel")
            band.reserve_slot(slot,  service="Band")
            print(f"Booking successful! Slot {slot} reserved for both hotel and band.")

        # Ask the user whether to view current held slots
        while True:
            ans = input("View current held slots now? (y/n): ").strip().lower()
            if ans in {"y", "n"}:
                break
            print("Invalid choice. Please enter y or n.")

        if ans == "y":
            view_held_slots()

    except SlotUnavailableError:
        print(f"Slot {slot} is no longer available.")
        # Check the latest 20 slots immediately after invalidating the cache.
        hotel._slots_cache = None
        band._slots_cache  = None
        view_available_slots(20)

    except Exception as e:
        print("Error booking slot:", e)


def cancel_slot():
    """
    Ask the user which service to cancel (hotel/band/both) or quit to menu,
    then attempt to release the specified slot.
    """
    # Prompt until the user enters a valid option or chooses to quit.
    target = ""
    while target not in {"h", "b", "a", "q"}:
        target = (
            input("Cancel for (h)otel, (b)and, (a)ll, or (q)uit to menu? ")
            .strip()
            .lower()
        )
        if target not in {"h", "b", "a", "q"}:
            print("Invalid choice. Please try again.")

    # Quit back to the main menu without doing anything.
    if target == "q":
        print("Returning to main menu...")
        return

    # Ask for the slot ID once the service choice is confirmed.
    slot = input("Enter the slot ID to cancel: ").strip()

    try:
        if target == "h":
            hotel.release_slot(slot, service="Hotel")
            print(f"Cancellation successful! Slot {slot} has been cancelled for the hotel.")
        elif target == "b":
            band.release_slot(slot,  service="Band")
            print(f"Cancellation successful! Slot {slot} has been cancelled for the band.")
        else:  # target == "a"
            hotel.release_slot(slot, service="Hotel")
            band.release_slot(slot,  service="Band")
            print(f"Cancellation successful! Slot {slot} has been cancelled for both the hotel and the band.")
    
        # Ask the user whether to view current held slots
        while True:
            ans = input("View current held slots now? (y/n): ").strip().lower()
            if ans in {"y", "n"}:
                break
            print("Invalid choice. Please enter y or n.")

        if ans == "y":
            view_held_slots()

    except Exception as e:
        print("Error cancelling slot:", e)


def find_matching_slots(limit):
    """
    Retrieve the available slots for both hotel and band, find the intersection,
    sort them in ascending order, and display the first 'limit' matches.
    """
    try:
        hotel_available_slots = hotel.get_slots_available(service="Hotel")
        band_available_slots = band.get_slots_available(service="Band")

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
    Reserve the earliest slot that is common to both hotel and band.
    If a better (earlier) common slot later appears, swap to it and release
    the previous reservation pair.

    During the high-frequency checking loop, temporarily shrink cache_ttl
    to 5 seconds to reduce stale data, then restore the original TTL at the end.
    """
    max_retries = int(config['global']['retries'])
    delay = float(config['global']['delay'])

    # Shrink cache TTL for high-frequency polling
    original_ttl_h = hotel.cache_ttl
    original_ttl_b = band.cache_ttl
    hotel.cache_ttl = band.cache_ttl = 5.0

    try:
        # Get the earliest already-held common slot (if any)
        held_h = {s["id"] for s in hotel.get_slots_held(service="Hotel")}
        held_b = {s["id"] for s in band.get_slots_held(service="Band")}
        current_pair = sorted(held_h & held_b, key=lambda x: int(x))
        current_best = current_pair[0] if current_pair else None

        attempt = 0

        while True:
            if current_best:
                print("Checking for an earlier matching slot...")

            # Find the earliest available common slot available
            avail_h = {s["id"] for s in hotel.get_slots_available(service="Hotel")}
            avail_b = {s["id"] for s in band.get_slots_available(service="Band")}
            common  = sorted(avail_h & avail_b, key=lambda x: int(x))

            # No available common slot was founded
            if not common:
                if attempt < max_retries - 1:
                    attempt += 1
                    print(f"No matching slots (attempt {attempt}/{max_retries}). Retrying...")
                    continue
                else:
                    print(f"No matching slots found after {max_retries} retries.")
                    return
            else:
                attempt = 0  # Found common slot, reset the counter

            earliest = common[0]

            # Compare the new-retreived common slot with already-held common slot
            if current_best and int(earliest) >= int(current_best):
                print(f"Already holding the best available slot pair {current_best}. No earlier match than slot {current_best} was found.")
                break

            # Reserve the new slot pair
            print(f"Reserving improved common slot {earliest}")
            try:
                hotel.reserve_slot(earliest, service="Hotel")
                band.reserve_slot(earliest,  service="Band")
            except Exception:
                # If band slot reservation failed, roll back and keep original reservation
                hotel.release_slot(earliest, service="Hotel")
                print("Failed to reserve the new pair. Keeping previous reservation.")
                return

            # Release the old pair (if any)
            if current_best:
                hotel.release_slot(current_best)
                band.release_slot(current_best)
                print(f"Released previous common slot {current_best}.")

            # Update the 'current_best'
            current_best = earliest
            time.sleep(delay)

        # Ask the user whether to cancel unneeded reservations
        while True:
            ans = input("Cancel unnecessary reservations now? (y/n): ").strip().lower()
            if ans in {"y", "n"}:
                break
            print("Invalid choice. Please enter y or n.")
        if ans == "y":
            cancel_unneeded_reservations()

    except Exception as e:
        print("Error reserving earliest matching slot:", e)

    finally:
        # Restore original cache TTLs
        hotel.cache_ttl = original_ttl_h
        band.cache_ttl  = original_ttl_b


def cancel_unneeded_reservations():
    """
    Keep at most one reservation per service.
    - If hotel and band share at least one slot, keep the earliest common slot
      and release every other reservation (matching or not).
    - If no common slot exists, keep each service's earliest slot and release
      all other reservations on that service.
    """
    try:
        # Get the already-held slot for hotel and band
        hotel_slots = hotel.get_slots_held(service="Hotel")
        band_slots  = band.get_slots_held(service="Band")

        hotel_ids = sorted([s["id"] for s in hotel_slots], key=int)
        band_ids  = sorted([s["id"] for s in band_slots],  key=int)

        if not hotel_ids and not band_ids:
            print("No reservations found.")
            return

        # Get common already-held slot
        common = sorted(set(hotel_ids) & set(band_ids), key=int)

        # If have common already-held slot,
        # keep the earliest common slot and release others later on
        if common:
            keep_h = keep_b = common[0]
            print(f"Keeping earliest common slot {keep_h}.")
        # Otherwise, keep the earliest slot for each service and release others later on
        else:
            keep_h = hotel_ids[0] if hotel_ids else None
            keep_b = band_ids[0]  if band_ids else None
            if keep_h:
                print(f"Keeping earliest hotel slot {keep_h}.")
            if keep_b:
                print(f"Keeping earliest band slot {keep_b}.")

        # Release unneeded slots
        cancelled_h, cancelled_b = [], []

        for slot_id in hotel_ids:
            if slot_id != keep_h:
                hotel.release_slot(slot_id, service="Hotel")
                cancelled_h.append(slot_id)

        for slot_id in band_ids:
            if slot_id != keep_b:
                band.release_slot(slot_id, service="Band")
                cancelled_b.append(slot_id)

        # Print output
        if cancelled_h:
            print("Cancelled extra hotel slot: " + ", ".join(cancelled_h))
        if cancelled_b:
            print("Cancelled extra band slot: " + ", ".join(cancelled_b))
        if not cancelled_h and not cancelled_b:
            print("No extra reservations to cancel.")
    except Exception:
        print("Failed to cancel extra reservations. Please try again later.")


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
