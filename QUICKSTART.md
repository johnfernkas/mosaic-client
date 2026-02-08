# Quick Start Guide

Get your Interstate 75W running with Mosaic in 5 minutes.

## Prerequisites

- Interstate 75W with MicroPython installed
- 64×32 HUB75 LED matrix
- WiFi network (SSID and password ready)
- Mosaic server running on your network
- Pimoroni HUB75 library

## Step 1: Upload Files to Device

Using **Thonny IDE** (easiest):

1. Open each file in Thonny:
   - `config.py`
   - `network.py`
   - `display.py`
   - `main.py`

2. Click **Run → Save to device** for each file

Or using **ampy** (command line):

```bash
ampy --port /dev/ttyACM0 put config.py
ampy --port /dev/ttyACM0 put network.py
ampy --port /dev/ttyACM0 put display.py
ampy --port /dev/ttyACM0 put main.py
```

## Step 2: Edit Configuration

Edit `config.py` on the device with your settings:

```python
WIFI_SSID = "YourWiFiName"
WIFI_PASSWORD = "YourPassword"
SERVER_URL = "http://192.168.1.100:5000"  # Mosaic server IP
DISPLAY_ID = "kitchen"                     # Or any name
```

## Step 3: Test Components

In Thonny REPL, run individual tests:

```python
# Test the display
from test_basic import test_display
test_display()

# Test WiFi
from test_basic import test_wifi
test_wifi()

# Test server
from test_basic import test_server
test_server()

# Fetch a real frame
from test_basic import test_frame_fetch
test_frame_fetch()
```

## Step 4: Run the Client

In REPL:

```python
import main
main.main()
```

You should see:
```
============================================================
  MOSAIC CLIENT for Interstate 75W
============================================================

[DEBUG] Connecting to WiFi: YourWiFiName
[DEBUG] WiFi connected! IP: 192.168.1.100
[DEBUG] Fetching frame from http://192.168.1.100:5000/frame
[DEBUG] Frame received: 1 frame(s), 64x32, app: weather
```

The LED matrix should light up with content from your Mosaic server!

## Step 5: Auto-start on Boot (Optional)

To automatically run the client on power-up:

1. Copy `boot_example.py` to the device
2. Rename it to `boot.py` on the device
3. Power cycle the Interstate 75W

The client will start automatically (with a 2-second window to cancel via Ctrl+C).

## Troubleshooting

### WiFi won't connect

- Check SSID and password in `config.py`
- Ensure 2.4 GHz network (5 GHz may not be supported)
- Look for error messages in REPL

### LED matrix not showing anything

- Verify GPIO pins in `config.py` match your wiring
- Check LED matrix power supply (should be 5V, 5A+)
- Test with: `from test_basic import test_display; test_display()`

### Server not responding

- Verify SERVER_URL in `config.py`
- Check server is running on port 5000
- Test: `from network import check_server_health; check_server_health()`

### Red checkerboard error pattern

- WiFi or server connection lost
- Check network connectivity
- Verify server is still running

## Getting Help

- See **README.md** for full documentation
- See **ARCHITECTURE.md** for technical details
- Check **test_basic.py** for diagnostic examples

---

**Good luck! 🎨**
