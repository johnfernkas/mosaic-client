# File Inventory

## Application Code

### `main.py` (223 lines)
**Entry point and event loop**

Main application that orchestrates the entire system:
- Startup sequence (display init → WiFi → server check)
- Main event loop (fetch → validate → render → retry)
- Frame animation handling with timing
- Error recovery and retry logic
- Graceful shutdown

**Key functions:**
- `main()` — Main event loop
- `parse_frame_data()` — Parse multi-frame RGB data

**Start here:** Run `import main; main.main()`

---

### `config.py` (88 lines)
**Configuration hub - single source of truth**

All user-facing settings in one place:
- WiFi credentials and timeouts
- Mosaic server URL and display ID
- GPIO pin assignments
- LED matrix dimensions
- Timing parameters (frame delays, dwell, retries)
- Brightness settings
- Debug logging flag

**Edit this file first** to match your setup.

---

### `network.py` (156 lines)
**WiFi and HTTP communication**

Handles all network operations:
- WiFi connection with timeout handling
- HTTP frame fetching from server
- Response header parsing
- Server health checking
- Optional display registration
- Debug logging helper

**Key functions:**
- `connect_wifi()` → Connect to configured network
- `fetch_frame()` → Get frame data and headers
- `check_server_health()` → Verify server is reachable
- `register_display()` → Register with server (optional)
- `debug_print()` → Conditional debug logging

---

### `display.py` (222 lines)
**HUB75 LED matrix control**

Hardware abstraction for the LED display:
- Pimoroni Hub75 library wrapper
- Pixel rendering from RGB bytes
- Brightness control
- Error pattern generation
- Power on/off management

**Key class:**
- `MosaicDisplay`
  - `display_frame()` — Show RGB pixel data
  - `set_brightness()` — Control LED brightness
  - `show_error_pattern()` — Visual error indicators
  - `enable()` / `disable()` — Power control
  - `cleanup()` — Shutdown resources

**Error patterns:**
- `connection` → Red checkerboard (network error)
- `format` → Yellow horizontal lines (data error)
- `timeout` → Purple stripes (timing error)

---

## Testing & Utilities

### `test_basic.py` (263 lines)
**Component testing and diagnostics**

Isolated tests for debugging without running full app:

**Test functions:**
- `test_display()` — Rainbow pattern on LED matrix
- `test_error_patterns()` — All error patterns
- `test_wifi()` — Connection and IP info
- `test_server()` — Server health check
- `test_frame_fetch()` — Full frame cycle
- `test_full()` — Complete test suite

**Usage:**
```python
from test_basic import test_display
test_display()
```

---

### `boot_example.py` (46 lines)
**Auto-start example for boot.py**

Rename to `boot.py` on device for auto-start on power-up.

Features:
- 2-second delay to cancel via Ctrl+C
- Graceful fallback if startup fails
- Clear error messages

---

## Documentation

### `README.md` (456 lines)
**Complete user guide**

Comprehensive documentation covering:
- Overview and features
- Hardware requirements
- Software requirements and installation
- Configuration guide
- Troubleshooting
- API reference
- Examples and usage patterns
- Performance considerations

**Read this for:** Complete setup and usage guide

---

### `QUICKSTART.md` (~100 lines)
**5-minute setup guide**

Fast track to get running:
- Upload files (Thonny or ampy)
- Edit configuration
- Test components
- Run the client
- Auto-start setup
- Quick troubleshooting

**Read this for:** Quick setup without details

---

### `ARCHITECTURE.md` (346 lines)
**Technical design document**

Deep dive into design and implementation:
- Module structure and responsibilities
- Data flow diagrams
- Error handling strategy
- Memory management
- Timing model
- Configuration hierarchy
- Testing strategy
- Future extensions
- Code style guidelines

**Read this for:** Understanding how it works

---

### `PROJECT_SUMMARY.md` (280 lines)
**Project overview and statistics**

Summary of what was built:
- Feature list
- Project structure
- Technical details
- Implementation statistics
- Testing checklist
- Known limitations
- Success criteria

**Read this for:** High-level project overview

---

### `FILES.md` (this file)
**File inventory and descriptions**

Quick reference for all files in the project.

---

## Total Project Size

```
Python Code:    ~1,000 lines
Documentation:  ~1,300 lines
Total:          ~2,300 lines

Code:           ~55 KB
Docs:           ~50 KB
Total:          ~105 KB
```

## Getting Started

1. **First time?** Read `QUICKSTART.md`
2. **Setting up?** Follow `README.md`
3. **Debugging?** Use `test_basic.py`
4. **Understanding design?** Read `ARCHITECTURE.md`
5. **Reference?** Check `PROJECT_SUMMARY.md`

## File Dependencies

```
main.py
  ├─ imports: network.py, display.py, config.py
  └─ runs: Event loop, calls network/display functions

network.py
  ├─ imports: config.py
  └─ uses: MicroPython network, urequests

display.py
  ├─ imports: config.py
  └─ uses: Pimoroni hub75 library, MicroPython time

config.py
  └─ imports: None (configuration data only)

test_basic.py
  ├─ imports: config.py
  └─ imports: network.py, display.py (only for specific tests)

boot_example.py
  └─ imports: main.py
  └─ runs: main.main() on startup
```

## Deployment Checklist

- [ ] Upload all `.py` files to Interstate 75W
- [ ] Edit `config.py` with your WiFi and server details
- [ ] Run test suite: `from test_basic import test_full; test_full()`
- [ ] Run main client: `import main; main.main()`
- [ ] (Optional) Copy `boot_example.py` as `boot.py` for auto-start

---

**Created:** 2026-02-08  
**Status:** Complete  
**Version:** 1.0.0
