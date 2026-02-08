"""
Network Management Module

Handles WiFi connection, HTTP requests, and server communication.
"""

import network
import urequests
import time
from config import (
    WIFI_SSID,
    WIFI_PASSWORD,
    WIFI_CONNECT_TIMEOUT,
    SERVER_URL,
    DISPLAY_ID,
    DEBUG,
)


def debug_print(msg):
    """Print debug messages if debugging is enabled."""
    if DEBUG:
        print(f"[DEBUG] {msg}")


def connect_wifi():
    """
    Connect to WiFi network.

    Returns:
        bool: True if connected successfully, False otherwise
    """
    debug_print(f"Connecting to WiFi: {WIFI_SSID}")

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    # Disconnect any existing connections
    wlan.disconnect()
    time.sleep(0.5)

    # Start connection
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)

    # Wait for connection with timeout
    start_time = time.time()
    while not wlan.isconnected():
        if time.time() - start_time > WIFI_CONNECT_TIMEOUT:
            debug_print("WiFi connection timeout")
            return False

        print(".", end="", flush=True)
        time.sleep(0.5)

    print()  # New line after dots
    ifconfig = wlan.ifconfig()
    debug_print(f"WiFi connected! IP: {ifconfig[0]}")
    return True


def fetch_frame():
    """
    Fetch frame data from Mosaic server.

    Returns:
        tuple: (pixels_bytes, headers_dict) on success, (None, None) on failure
               headers contains: width, height, frame_count, delay_ms, dwell_secs, etc.
    """
    try:
        url = f"{SERVER_URL}/frame"
        if DISPLAY_ID:
            url += f"?display={DISPLAY_ID}"

        debug_print(f"Fetching frame from {url}")

        response = urequests.get(url, timeout=10)

        # Parse response headers
        headers = {
            "width": int(response.headers.get("X-Frame-Width", 64)),
            "height": int(response.headers.get("X-Frame-Height", 32)),
            "frame_count": int(response.headers.get("X-Frame-Count", 1)),
            "delay_ms": int(response.headers.get("X-Frame-Delay-Ms", 100)),
            "dwell_secs": int(response.headers.get("X-Dwell-Secs", 10)),
            "brightness": int(response.headers.get("X-Brightness", 200)),
            "app_name": response.headers.get("X-App-Name", "unknown"),
        }

        # Read the pixel data
        pixels = response.content
        response.close()

        debug_print(f"Frame received: {headers['frame_count']} frame(s), "
                   f"{headers['width']}x{headers['height']}, "
                   f"app: {headers['app_name']}")

        return pixels, headers

    except Exception as e:
        print(f"Error fetching frame: {e}")
        return None, None


def register_display():
    """
    Register this display with the Mosaic server (optional).

    This endpoint is for multi-display support, allowing the server
    to track connected displays.

    Returns:
        bool: True if registration was successful, False otherwise
    """
    try:
        from config import DISPLAY_WIDTH, DISPLAY_HEIGHT

        url = f"{SERVER_URL}/api/displays"
        payload = {
            "id": DISPLAY_ID or "interstate75w",
            "name": f"Interstate 75W - {DISPLAY_ID or 'Main'}",
            "width": DISPLAY_WIDTH,
            "height": DISPLAY_HEIGHT,
            "client_type": "interstate75w",
        }

        debug_print(f"Registering display: {payload['id']}")

        response = urequests.post(url, json=payload, timeout=10)
        success = response.status_code == 200
        response.close()

        return success

    except Exception as e:
        debug_print(f"Display registration failed (non-critical): {e}")
        # Don't fail the entire startup if registration fails
        return False


def check_server_health():
    """
    Check if the Mosaic server is reachable.

    Returns:
        bool: True if server is responding, False otherwise
    """
    try:
        url = f"{SERVER_URL}/api/status"
        response = urequests.get(url, timeout=5)
        success = response.status_code == 200
        response.close()
        return success

    except Exception as e:
        debug_print(f"Server health check failed: {e}")
        return False
