# Mosaic Client — Interstate 75W MicroPython Implementation

A MicroPython client for Pimoroni's **Interstate 75W** that displays animations and content served by the **Mosaic** server.

## Overview

The Mosaic Client connects to a Mosaic server over WiFi, fetches LED matrix frames, and displays them on a 64×32 HUB75 LED matrix. It handles:

- 🌐 **WiFi connectivity** with configurable SSID/password
- 📡 **Frame streaming** from the Mosaic HTTP API
- 🎬 **Multi-frame animations** with automatic timing
- 🔄 **Automatic refresh** after dwell period
- 🛡️ **Graceful error handling** with visual error patterns
- 🎨 **Error patterns** (red checkerboard for connection, yellow for format, magenta for timeout)

## Hardware Requirements

- **Pimoroni Interstate 75W** (or compatible RP2040 board with HUB75 support)
- **64×32 HUB75 LED Matrix** (or any compatible size)
- **WiFi network** (2.4 GHz or 5 GHz)
- **USB power** (for the Interstate 75W)
- **LED power supply** (5V, 8A+ recommended for 64×32 matrix)

## Software Requirements

### Board Firmware

1. **MicroPython 1.20+** for RP2040
   - Download from [micropython.org](https://micropython.org/download/)
   - Use the **Raspberry Pi Pico RP2040** firmware
   - Flash using `ampy` or Thonny IDE

2. **Pimoroni HUB75 Library**
   ```bash
   # On your host machine, copy to the board:
   pimoroni-pico
   ├── libraries/
   │   └── hub75/
   │       └── hub75.py
   ```

### Python Libraries for MicroPython

The client uses these built-in MicroPython modules:

- `network` — WiFi connectivity
- `urequests` — HTTP requests (built-in or install via `upip`)
- `time` — Timing and delays

Most of these come pre-installed with MicroPython. If `urequests` is missing:

```python
import upip
upip.install('micropython-requests')
```

## Installation

### 1. Prepare the Interstate 75W

#### Flash MicroPython

```bash
# Download RP2040 MicroPython firmware
# Use Thonny IDE (recommended) or ampy:

ampy --port /dev/ttyACM0 put micropython.uf2
# (Reset the board in bootloader mode first)
```

#### Add Required Libraries

```bash
# Copy Pimoroni HUB75 library
ampy --port /dev/ttyACM0 put hub75.py /lib/hub75.py

# Or use Thonny IDE to upload files
```

### 2. Upload Client Files

Copy these files to the Interstate 75W:

```bash
ampy --port /dev/ttyACM0 put config.py /config.py
ampy --port /dev/ttyACM0 put network.py /network.py
ampy --port /dev/ttyACM0 put display.py /display.py
ampy --port /dev/ttyACM0 put main.py /main.py
```

Or use **Thonny IDE**:
1. Open Thonny
2. Open each `.py` file
3. Run → Save to device
4. Navigate to device folder and save

### 3. Configure Settings

Edit `config.py` with your settings:

```python
# WiFi
WIFI_SSID = "YourSSID"
WIFI_PASSWORD = "YourPassword"

# Mosaic Server
SERVER_URL = "http://192.168.1.100:5000"

# Display (if multi-display setup)
DISPLAY_ID = "kitchen"
```

Upload the updated `config.py` to the device.

### 4. Run the Client

**Option A: Using Thonny IDE**
1. Open `main.py`
2. Click "Run" (F5)
3. Watch the console for startup messages

**Option B: Using REPL**
```python
import main
main.main()
```

**Option C: Auto-start on boot**

Create `boot.py` on the device:

```python
# boot.py - Runs on startup
import main
main.main()
```

## Configuration

### Basic Settings (config.py)

```python
# WiFi connection
WIFI_SSID = "YourSSID"
WIFI_PASSWORD = "YourPassword"
WIFI_CONNECT_TIMEOUT = 30

# Mosaic server
SERVER_URL = "http://192.168.1.100:5000"
DISPLAY_ID = "kitchen"

# Display dimensions (don't change unless using different matrix size)
DISPLAY_WIDTH = 64
DISPLAY_HEIGHT = 32

# Error handling
FRAME_FETCH_RETRY_ATTEMPTS = 3
FRAME_FETCH_RETRY_DELAY = 2
ERROR_DISPLAY_TIME = 3

# Brightness (0-255)
BRIGHTNESS = 200

# Debug logging
DEBUG = True
```

### GPIO Pin Configuration

If your Interstate 75W uses different pins, modify `GPIO_CONFIG` in `config.py`:

```python
GPIO_CONFIG = {
    "R0": 2,   # Red high bit
    "R1": 3,   # Red low bit
    "G0": 4,   # Green high bit
    "G1": 17,  # Green low bit
    "B0": 27,  # Blue high bit
    "B1": 24,  # Blue low bit
    "A": 11,   # Row select A
    "B": 26,   # Row select B
    "C": 5,    # Row select C
    "D": 12,   # Row select D
    "E": 6,    # Row select E
    "CLK": 10, # Clock
    "STB": 8,  # Strobe/Latch
    "OE": 25,  # Output Enable
}
```

## API Communication

### Frame Endpoint

The client fetches frames from:

```
GET /frame?display=kitchen
```

**Response Headers:**
- `X-Frame-Width` — Frame width (pixels)
- `X-Frame-Height` — Frame height (pixels)
- `X-Frame-Count` — Number of frames (for animations)
- `X-Frame-Delay-Ms` — Delay between frames (milliseconds)
- `X-Dwell-Secs` — How long to show this frame before fetching next
- `X-Brightness` — Suggested brightness (0-255)
- `X-App-Name` — Name of the currently running app

**Response Body:**
Raw RGB bytes: `[R0 G0 B0 R1 G1 B1 ... RN GN BN]`

### Multi-Frame Animations

For animations, the server can send multiple frames:

```
Frame 1: pixels 0 to (width×height×3-1)
Frame 2: pixels (width×height×3) to (2×width×height×3-1)
...
```

The client displays each frame for `X-Frame-Delay-Ms` milliseconds.

## Troubleshooting

### WiFi Won't Connect

1. **Check SSID/password** in `config.py`
2. **Verify WiFi range** — Move closer to router
3. **Enable DEBUG** to see connection details:
   ```python
   DEBUG = True
   ```
4. **Check board antenna** — Ensure it's properly attached to Interstate 75W

### LED Matrix Not Displaying

1. **Check pin configuration** — Compare with Interstate 75W schematic
2. **Verify power supply** — HUB75 matrices draw significant current (2-5A)
3. **Test with simple pattern**:
   ```python
   from display import MosaicDisplay
   d = MosaicDisplay()
   # Should show a test pattern or error
   ```

### Server Connection Issues

1. **Verify server URL** in `config.py`:
   ```python
   SERVER_URL = "http://192.168.1.100:5000"
   ```
2. **Check firewall** — Ensure port 5000 is open
3. **Test connectivity**:
   ```python
   from network import check_server_health
   print(check_server_health())  # Should print True
   ```

### Frames Display Incorrectly

1. **Check frame dimensions** — Must be 64×32
2. **Verify X-Frame-Count header** — Should match actual data
3. **Check pixel data** — Must be RGB format (not BGR or other)

### Memory Issues

MicroPython on RP2040 has limited RAM (~252 KB). If you get memory errors:

1. **Disable DEBUG logging**:
   ```python
   DEBUG = False
   ```
2. **Reduce frame rate** if animations are memory-intensive
3. **Check board RAM usage**:
   ```python
   import gc
   gc.collect()
   print(gc.mem_free())
   ```

## Monitoring & Debugging

### Console Output

The client prints status messages to the REPL:

```
[DEBUG] Connecting to WiFi: YourSSID
[DEBUG] WiFi connected! IP: 192.168.1.100
[DEBUG] Fetching frame from http://192.168.1.100:5000/frame?display=kitchen
[DEBUG] Frame received: 1 frame(s), 64x32, app: weather
```

### Enable Full Debug Logging

```python
# In config.py
DEBUG = True
```

All modules will print detailed status messages.

### Error Patterns

| Pattern | Meaning |
|---------|---------|
| 🔴 Red checkerboard | Network/WiFi error |
| 🟡 Yellow horizontal lines | Frame format error |
| 🟣 Purple stripes | Timeout error |

## Examples

### Display Static Image

```python
from display import MosaicDisplay

d = MosaicDisplay()

# Create 64x32 RGB pixels (all black)
pixels = bytearray(64 * 32 * 3)

# Set a red pixel at (0, 0)
pixels[0] = 255  # R
pixels[1] = 0    # G
pixels[2] = 0    # B

d.display_frame(pixels)
```

### Fetch and Display Single Frame

```python
from network import fetch_frame
from display import MosaicDisplay

d = MosaicDisplay()

pixels, headers = fetch_frame()
if pixels:
    d.display_frame(pixels)
    print(f"Showing: {headers['app_name']}")
```

### Test WiFi Connection

```python
from network import connect_wifi, check_server_health

if connect_wifi():
    print("WiFi connected!")
    if check_server_health():
        print("Server is reachable!")
    else:
        print("Server not responding")
else:
    print("WiFi connection failed")
```

## Performance Considerations

### Bandwidth

A single frame requires:
- 64 × 32 × 3 = 6,144 bytes = ~6 KB
- Typical update: ~50 KB/min (with 10-second dwell)
- Over WiFi: Usually completes in <500 ms

### Power Consumption

- Interstate 75W: ~100 mA @ 5V
- LED Matrix: 500 mA - 2 A depending on brightness and content
- **Total: 0.6 - 2.1 W** (recommend 2-3 A supply)

### Refresh Rate

- Dwell time: 10 seconds (default)
- Animation frames: 100 ms each (configurable)
- Max useful frame rate: ~10 FPS (100 ms/frame)

## API Reference

### network.py

```python
connect_wifi()
    → bool: True if connected

fetch_frame()
    → (pixels_bytes, headers_dict) or (None, None)

check_server_health()
    → bool: True if server responding

register_display()
    → bool: True if registered
```

### display.py

```python
MosaicDisplay()
    display_frame(rgb_pixels)
    set_brightness(0-255)
    enable()
    disable()
    clear()
    show_error_pattern(error_type)
    cleanup()
```

## Architecture

```
┌─────────────────────┐
│   main.py           │ Event loop, frame scheduling
├─────────────────────┤
│   network.py        │ WiFi, HTTP requests
│   display.py        │ HUB75 rendering
│   config.py         │ Settings
└─────────────────────┘
         ↓
    Hub75 Library (Pimoroni)
         ↓
    HUB75 LED Matrix
```

## License

This project is provided as-is. Use freely with the Mosaic server and Interstate 75W.

## Support

For issues with:

- **Mosaic Server**: See `~/clawd/projects/mosaic/mosaic-addon/`
- **Pimoroni Libraries**: Visit [shop.pimoroni.com](https://shop.pimoroni.com)
- **MicroPython**: Visit [micropython.org](https://micropython.org)

## Changelog

### v1.0.0 (2026-02-08)
- Initial release
- WiFi connection with configurable credentials
- Frame streaming from Mosaic server
- Multi-frame animation support
- Error pattern display
- Retry logic with backoff
- Full debug logging

---

**Last updated:** 2026-02-08  
**Author:** Mosaic Development Team
