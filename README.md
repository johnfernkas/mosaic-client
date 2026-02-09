# Mosaic Client

MicroPython client for displaying frames from a Mosaic LED display server on HUB75 LED matrices. Communicates with the Mosaic add-on to fetch and render app animations in real-time.

## Features

- **Real-time frame fetching** — Pulls animated frames from Mosaic server every 10 seconds
- **Multi-display ready** — Register with server using unique display ID
- **Brightness control** — Server-side brightness applied to frames
- **Hardware abstraction** — Easy to add support for other boards
- **Status screens** — Boot animations, WiFi status, error feedback
- **Lightweight** — Minimal dependencies, ~50KB total code
- **Automatic reconnect** — Handles WiFi drops and connection issues

## Supported Hardware

- **Pimoroni Interstate 75 (W)** — 64x32 HUB75 matrix controller with RP2350/RP2040 (primary)
- 64x32 HUB75 LED matrix panels
- 5V power supply for LED matrix

### Tested Configurations

- Interstate 75W + RP2350
- Interstate 75W + RP2040
- Custom HUB75 boards with PicoGraphics support

## Installation

### 1. Flash MicroPython

Use Pimoroni's firmware (includes PicoGraphics):

```bash
# Download latest .uf2 from:
# https://github.com/pimoroni/pimoroni-pico/releases

# Put board in bootloader mode (hold BOOTSEL, press RESET)
# Drag .uf2 file onto RPI-RP2 drive
```

Alternatively, use the installer:

```bash
pip install pimoroni-pico
pimoroni-pico --board=interstate75w
```

### 2. Configure Settings

Edit `config.py` with your environment:

```python
# WiFi
WIFI_SSID = "YourWiFiNetwork"
WIFI_PASSWORD = "YourPassword"
WIFI_CONNECT_TIMEOUT = 30  # seconds

# Mosaic Server
SERVER_URL = "http://192.168.1.100:8176"  # Add-on URL
DISPLAY_ID = "kitchen_display"  # Unique ID for this display
DISPLAY_NAME = "Kitchen"  # Human-readable name

# Display
BRIGHTNESS = 80  # 0-100, can be overridden by server
```

### 3. Upload Files

Use `mpremote` (comes with Pimoroni firmware):

```bash
# Copy files to device
mpremote cp config.py :
mpremote cp display.py :
mpremote cp main.py :
```

Or mount the device as USB and drag files:

```bash
# MacOS/Linux
cp config.py /Volumes/RPI-RP2/
cp display.py /Volumes/RPI-RP2/
cp main.py /Volumes/RPI-RP2/
```

### 4. Run the Client

The client starts automatically on board power or reset:

```bash
# Or manually start
mpremote run main.py

# Watch the serial output
mpremote repl
```

## Boot Sequence

1. **Display initialization** — Shows rainbow mosaic tile animation
2. **WiFi connecting** — Animated status screen with server logo
3. **WiFi OK** — Brief success flash
4. **Server connecting** — Status screen while registering with add-on
5. **Frame fetching** — Main loop fetches and displays frames

### Status Screens

| Screen | Meaning | Next Step |
|--------|---------|-----------|
| Mosaic boot anim | System initializing | — |
| "WiFi" (animated dots) | Connecting to network | Check SSID/password |
| "WiFi OK" | Connected to WiFi | Proceeding to server |
| "Server" (dots) | Registering with add-on | Check SERVER_URL |
| Frames displaying | Connected! | Normal operation |
| "No WiFi" (red) | Failed to connect | Check WiFi settings, range, password |
| "ERROR" (orange pattern) | Server connection lost | Server may be down; auto-retries |

## Configuration Reference

### config.py

```python
# WiFi Configuration
WIFI_SSID = "YourNetwork"          # Your WiFi network name
WIFI_PASSWORD = "password123"      # Your WiFi password
WIFI_CONNECT_TIMEOUT = 30          # Seconds to wait for connection

# Server Configuration
SERVER_URL = "http://192.168.1.100:8176"  # Mosaic add-on URL
DISPLAY_ID = "kitchen"             # Unique ID for this display
DISPLAY_NAME = "Kitchen Display"   # Human-readable name

# Display Configuration
BRIGHTNESS = 80                    # Default brightness (0-100)
                                   # Can be overridden by server
```

### Finding Your Server URL

For **Home Assistant add-on**:
- Local network: `http://a0d7b954-mosaic:8176` (default HA DNS)
- Or by IP: `http://192.168.1.100:8176`

For **Standalone server**:
- Wherever you deployed it, e.g., `http://192.168.1.100:8075`

Test the connection:

```bash
curl http://192.168.1.100:8176/api/status
# Should return: {"status":"ok","version":"0.2.0",...}
```

## Architecture

### Boot & Status System (`display.py`)

- **Boot animation** — Procedural mosaic tile fill with random shuffle
- **Logo screen** — "MOSAIC" branding with corner tiles
- **Status screens** — WiFi connecting, WiFi OK, WiFi failed, Server connecting, Server error
- **Hardware abstraction** — Pluggable display drivers

### Main Loop (`main.py`)

```
┌─────────────────────────────────┐
│  Boot & Display Initialization  │
└────────────────┬────────────────┘
                 │
        ┌────────▼─────────────┐
        │  Connect to WiFi     │
        │  (show status)       │
        └────────┬─────────────┘
                 │
        ┌────────▼──────────────┐
        │ Register with Server  │
        │ (POST /api/displays)  │
        └────────┬──────────────┘
                 │
        ┌────────▼────────────────────────┐
        │  Main Loop (every 10 seconds)   │
        │  ┌─────────────────────────┐    │
        │  │ Fetch frame from server │    │
        │  │ (GET /frame)            │    │
        │  └──────────────┬──────────┘    │
        │                 │               │
        │  ┌──────────────▼────────────┐  │
        │  │ Display animation frames  │  │
        │  │ (every X milliseconds)    │  │
        │  └───────────────────────────┘  │
        └────────────────────────────────┘
```

### Frame Fetching

The client fetches frames from `/frame` endpoint:

```bash
GET /frame?display={DISPLAY_ID}
```

Response headers:
- `X-Frame-Count` — Number of animation frames
- `X-Frame-Delay-Ms` — Milliseconds between frames
- `X-Dwell-Secs` — How long to display this app (10s)
- `X-Brightness` — Brightness % from server (overrides config)
- `X-App-Name` — Current app name (for logging)

Response body: Raw RGB pixel data (width × height × 3 bytes per frame)

## Hardware Support

### Interstate 75W (Default)

Works out-of-the-box. Uses `PicoGraphics` from `interstate75` library.

```python
# Automatic initialization in display.py
from interstate75 import Interstate75, DISPLAY_INTERSTATE75_64X32
```

### Adding Other Hardware

To support a different board:

1. **Add import detection** in `display.py`:
   ```python
   try:
       from your_hardware import YourDisplay
       HARDWARE = "your_hardware"
   except ImportError:
       HARDWARE = None
   ```

2. **Implement `_init_hardware()`**:
   ```python
   if HARDWARE == "your_hardware":
       self.display = YourDisplay()
       self.graphics = self.display.get_graphics()
       bounds = self.graphics.get_bounds()
       self.width = bounds[0]
       self.height = bounds[1]
   ```

3. **Implement required methods**:
   - `update()` — Push buffer to display
   - `clear(color)` — Fill with color
   - `pixel(x, y, r, g, b)` — Set pixel
   - `text(msg, x, y, color)` — Draw text

See `display.py` for a complete example.

## Troubleshooting

### Won't connect to WiFi

1. Verify SSID and password in `config.py`
2. Check WiFi signal strength
3. Ensure board is powered correctly
4. Try static IP if using WPA-Enterprise networks

Monitor via serial:
```bash
mpremote repl
# Ctrl+D to soft reset, watch output
```

### Can't reach server

1. Ping the server from another device on the network
2. Verify `SERVER_URL` in `config.py`
3. Check firewall rules
4. Try URL by IP instead of hostname

Test from the board:
```python
import urequests
resp = urequests.get("http://192.168.1.100:8176/api/status", timeout=10)
print(resp.json())
resp.close()
```

### Display not updating

1. Check that server is responding
2. Verify display is registered (check Mosaic dashboard)
3. Check that apps are in rotation
4. Look for "Server error" screen — indicates connection issue

### MicroPython syntax errors

Ensure you're using compatible syntax:
- No type hints in function signatures
- Use `except:` not `except Exception:`
- Use `print()` not f-strings for logging

### Out of memory

1. Don't open too many files at once
2. Use `urequests.Response.close()` after each request (code does this)
3. Avoid large JSON parsing

## Performance

- **Memory:** ~80KB (config + code)
- **WiFi latency:** 100-300ms per request
- **Frame refresh:** Every 10 seconds (configurable)
- **Power draw:** ~1A at full brightness (64x32 matrix)

## Development

### Serial REPL

```bash
# Connect to board via USB and open REPL
mpremote repl
```

Useful commands:
```python
# Check files
import os
os.listdir()

# Test WiFi
import network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
print(wlan.scan())

# Test server
import urequests
resp = urequests.get("http://SERVER:PORT/api/status")
print(resp.json())
```

### Logging

Add debug output in main loop:
```python
print(f"Fetching frame {self.current_frame}")
```

### Custom boot animation

Edit `display.py` `boot_screen()` method to customize:
```python
def boot_screen(self):
    # Your animation here
    self.clear((0, 0, 0))
    self.text("CUSTOM", 10, 10, (255, 0, 0))
    self.update()
```

## License

MIT — See LICENSE file

## References

- [Pimoroni Interstate 75W](https://shop.pimoroni.com/products/interstate-75-w)
- [MicroPython Docs](https://docs.micropython.org/)
- [Mosaic Add-on](https://github.com/johnfernkas/mosaic-addon)
- [Tidbyt App Framework](https://tidbyt.dev/)

---

**Mosaic Client** — MicroPython LED display client | [GitHub](https://github.com/johnfernkas/mosaic-client)
