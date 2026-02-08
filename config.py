"""
Mosaic Client Configuration

All configurable settings for the Interstate 75W Mosaic client.
Edit these values to match your setup.
"""

# ============================================================================
# WiFi Configuration
# ============================================================================
WIFI_SSID = "YourSSID"
WIFI_PASSWORD = "YourPassword"

# WiFi connection timeout in seconds
WIFI_CONNECT_TIMEOUT = 30

# ============================================================================
# Mosaic Server Configuration
# ============================================================================
# Server URL (e.g., "http://192.168.1.100:8000" or "http://mosaic.local:8000")
SERVER_URL = "http://192.168.1.100:5000"

# Display ID to register with the server (optional, for multi-display support)
# If not set, defaults to "interstate75w"
DISPLAY_ID = "kitchen"

# ============================================================================
# LED Matrix Display Configuration
# ============================================================================
# Physical dimensions of the HUB75 matrix
DISPLAY_WIDTH = 64
DISPLAY_HEIGHT = 32

# GPIO pin configuration for Interstate 75W
# These are the standard Pimoroni Interstate 75W pins
GPIO_CONFIG = {
    "R0": 2,
    "R1": 3,
    "G0": 4,
    "G1": 17,
    "B0": 27,
    "B1": 24,
    "A": 11,
    "B": 26,
    "C": 5,
    "D": 12,
    "E": 6,
    "CLK": 10,
    "STB": 8,
    "OE": 25,
}

# ============================================================================
# Animation & Timing Configuration
# ============================================================================
# Default dwell time if server doesn't specify (seconds)
DEFAULT_DWELL_SECS = 10

# Maximum frame delay to enforce (milliseconds, prevents too-fast animations)
MAX_FRAME_DELAY_MS = 500

# ============================================================================
# Network Error Handling
# ============================================================================
# Retry attempts when fetching frames fails
FRAME_FETCH_RETRY_ATTEMPTS = 3

# Delay between retry attempts (seconds)
FRAME_FETCH_RETRY_DELAY = 2

# Error pattern display time (seconds) before retrying
ERROR_DISPLAY_TIME = 3

# ============================================================================
# Debug & Logging
# ============================================================================
# Enable debug logging to console
DEBUG = True

# ============================================================================
# System Configuration
# ============================================================================
# Brightness adjustment (0-255, affects the PWM values sent to the matrix)
# Set this lower if the display is too bright for your environment
BRIGHTNESS = 200

# Enable/disable the display on startup
DISPLAY_ENABLED = True
