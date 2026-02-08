# Mosaic Client

MicroPython client for displaying Mosaic frames on HUB75 LED matrices.

## Supported Hardware

- Pimoroni Interstate 75 (W) with RP2350/RP2040
- 64x32 HUB75 LED matrix panels

## Quick Start

1. **Flash MicroPython** to your board (Pimoroni firmware recommended)

2. **Edit config.py** with your settings:
   ```python
   WIFI_SSID = "YourNetwork"
   WIFI_PASSWORD = "YourPassword"
   SERVER_URL = "http://192.168.1.100:8176"
   ```

3. **Upload to device:**
   ```bash
   mpremote cp config.py :
   mpremote cp display.py :
   mpremote cp main.py :
   ```

4. **Run:**
   ```bash
   mpremote run main.py
   ```

   Or reset the board — it runs `main.py` automatically.

## Files

| File | Purpose |
|------|---------|
| `main.py` | Entry point, WiFi + fetch loop |
| `display.py` | Hardware abstraction for LED matrix |
| `config.py` | Your settings (WiFi, server, brightness) |

## Boot Sequence

1. Rainbow gradient wipe (display is alive)
2. "MOSAIC booting..." text
3. "WiFi connecting..." → "WiFi OK" or "WiFi FAILED"
4. "Server connecting..." → frames displayed

## Adding Hardware Support

The `display.py` module abstracts hardware. To add support for other boards:

1. Add import detection at top of `display.py`
2. Update `_init_hardware()` with initialization
3. Ensure `update()`, `clear()`, `pixel()` methods work

## License

MIT
