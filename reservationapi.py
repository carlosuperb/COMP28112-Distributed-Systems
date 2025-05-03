""" Reservation API wrapper

This class implements a simple wrapper around the reservation API. It
provides automatic retries for server-side errors, delays to prevent
server overloading, and produces sensible exceptions for the different
types of client-side error that can be encountered.
"""

# This file contains areas that need to be filled in with your own
# implementation code. They are marked with "Your code goes here".
# Comments are included to provide hints about what you should do.

import requests
import simplejson
import warnings
import time

from requests.exceptions import HTTPError
from exceptions import (
    BadRequestError, InvalidTokenError, BadSlotError, NotProcessedError,
    SlotUnavailableError,ReservationLimitError)

class ReservationApi:
    def __init__(self, base_url: str, token: str, retries: int, delay: float, cache_ttl: float):
        """ Create a new ReservationApi to communicate with a reservation
        server.

        Args:
            base_url: The URL of the reservation API to communicate with.
            token: The user's API token obtained from the control panel.
            retries: The maximum number of attempts to make for each request.
            delay: A delay to apply to each request to prevent server overload.
            cache_ttl: seconds the available-slot list stays valid in memory.
        """
        self.base_url = base_url
        self.token    = token
        self.retries  = retries
        self.delay    = delay

        # cache for /reservation/available
        self._slots_cache      = None
        self._slots_cache_time = 0.0
        self.cache_ttl         = cache_ttl


    def _reason(self, req: requests.Response) -> str:
        """Obtain the reason associated with a response"""
        reason = ''

        # Try to get the JSON content, if possible, as that may contain a
        # more useful message than the status line reason
        try:
            json = req.json()
            reason = json['message']

        # A problem occurred while parsing the body - possibly no message
        # in the body (which can happen if the API really does 500,
        # rather than generating a "fake" 500), so fall back on the HTTP
        # status line reason
        except simplejson.errors.JSONDecodeError:
            if isinstance(req.reason, bytes):
                try:
                    reason = req.reason.decode('utf-8')
                except UnicodeDecodeError:
                    reason = req.reason.decode('iso-8859-1')
            else:
                reason = req.reason

        return reason


    def _headers(self) -> dict:
        """Create the authorization token header needed for API requests"""
        # Your code goes here
        return {"Authorization": f"Bearer {self.token}"}


    def _send_request(self, method: str, endpoint: str, service: str = "") -> dict:
        """Send a request to the reservation API and convert errors to
           appropriate exceptions"""
        # Your code goes here
        # Allow for multiple retries if needed
        for attempt in range(1, self.retries + 1):
            # Perform the request.
            try:
                response = requests.request(method, endpoint, headers=self._headers())
            except Exception as e:
                if attempt < self.retries:
                    prefix = f"[{service}] " if service else ""
                    print(f"{prefix}Attempt {attempt}/{self.retries}: Unable to connect to the server. Retrying...")
                else:
                    print("We are unable to process your request. Please try again later.")
                time.sleep(self.delay)
                continue

            # Delay before processing the response to avoid swamping server.
            time.sleep(self.delay)

            # 200 response indicates all is well - send back the json data.
            if response.status_code == 200:
                return response.json()
            
            # 5xx responses indicate a server-side error, show a warning
            # (including the try number).
            elif 500 <= response.status_code <= 599:
                prefix = f"[{service}] " if service else ""
                if attempt < self.retries:
                    print(f"{prefix}Attempt {attempt}/{self.retries}: Server is currently unavailable. Retrying...")
                else:
                    print("We are unable to process your request due to server issues. Please try again later.")
                continue

            # 400 errors are client problems that are meaningful, so convert
            # them to separate exceptions that can be caught and handled by
            # the caller.
            elif 400 <= response.status_code < 500:
                reason = self._reason(response)
                # Bad request
                if response.status_code == 400:
                    raise BadRequestError(reason)
                # The API token was invalid or missing
                elif response.status_code == 401:
                    raise InvalidTokenError(reason)
                # SlotId does not exist
                elif response.status_code == 403:
                    raise BadSlotError(reason)
                # The request has not been processed
                elif response.status_code == 404:
                    raise NotProcessedError(reason)
                # Slot is not available
                elif response.status_code == 409:
                    raise SlotUnavailableError(reason)
                # The client already holds the maximum number of reservations
                elif response.status_code == 451:
                    raise ReservationLimitError(reason)
                # Unexpected status code
                else:
                    print("An error occurred with your request. Please try again.")
                    raise HTTPError("Client error")
                
            # Anything else is unexpected and may need to kill the client.
            else:
                print("An unexpected error occurred. Please try again later.")
                raise HTTPError("Unexpected error")
        
        # Get here and retries have been exhausted, throw an appropriate
        # exception.
        raise NotProcessedError(f"Failed to process request after {self.retries} attempts.")


    def get_slots_available(self, service: str = ""):
        """
        Return cached slots if still fresh, 
        otherwise query API for slots currently available in the system.
        """
        # Your code goes here
        now = time.time()

        # Serve cached data when it is still within the time‑to‑live window.
        if self._slots_cache and now - self._slots_cache_time < self.cache_ttl:
            return self._slots_cache
        
        # Cache expired (or empty), then query the API.
        data = self._send_request("GET", f"{self.base_url}/reservation/available", service=service)

        # Update the in‑memory cache.
        self._slots_cache      = data
        self._slots_cache_time = now
        return data


    def get_slots_held(self, service: str = ""):
        """
        Obtain the list of slots currently held by the client.
        (No caching — always obtain the exact up‑to‑date list.)
        """
        # Your code goes here
        return self._send_request("GET", f"{self.base_url}/reservation", service=service)


    def release_slot(self, slot_id, service: str = ""):
        """
        Release a slot that is currently held by the client, 
        then invalidate the cached available‑slot list.
        """
        # Your code goes here
        data = self._send_request("DELETE", f"{self.base_url}/reservation/{slot_id}", service=service)

        # Invalidate cache because availability has changed.
        self._slots_cache = None
        self._slots_cache_time = 0.0
        return data


    def reserve_slot(self, slot_id, service: str = ""):
        """
        Attempt to reserve the specified slot for the client, 
        then invalidate the cached available‑slot list.
        """
        # Your code goes here
        data = self._send_request("POST", f"{self.base_url}/reservation/{slot_id}", service=service)

        # Invalidate cache because availability has changed.
        self._slots_cache = None
        self._slots_cache_time = 0.0
        return data

