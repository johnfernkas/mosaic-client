# Mosaic Client Architecture

## Overview

The Mosaic Client is a lightweight MicroPython application for the Pimoroni Interstate 75W that streams LED matrix frames from a Mosaic server and displays them on a 64×32 HUB75 display.

## Module Structure

```
mosaic-client/
├── main.py                # Main event loop
├── config.py              # All user-facing configuration
├── network.py             # WiFi & HTTP communication
├── display.py             # HUB75 LED matrix control
├── test_basic.py          # Component testing utilities
├── boot_example.py        # Auto-start script example
├── README.md              # User documentation
├── ARCHITECTURE.md        # This file
└── LICENSE                # License file
```

## Module Responsibilities

### `config.py` — Configuration Hub

Single source of truth for all settings:
- WiFi credentials
- Server URL and display ID
- GPIO pin mappings
- Timing and retry parameters
- Debug logging flag

**Design principle:** All configuration in one place, no hardcoded values elsewhere.

### `network.py` — Connectivity Layer

Handles all network operations:

```python
connect_wifi()              # Connect to configured WiFi network
fetch_frame()              # Fetch frame data and headers from server
check_server_health()      # Test server reachability
register_display()         # Register display with server (optional)
debug_print()              # Conditional debug logging
```

**Error handling:**
- Timeouts on WiFi and HTTP operations
- Graceful degradation if server is unreachable
- Retry logic in main loop (not in network module)

**Dependencies:**
- `network` — MicroPython WiFi
- `urequests` — HTTP requests

### `display.py` — Hardware Abstraction

Encapsulates all HUB75 matrix operations:

```python
class MosaicDisplay:
    __init__()              # Initialize display with GPIO pins
    display_frame()         # Show RGB pixel frame
    set_brightness()        # Control LED brightness
    enable() / disable()    # Power control
    clear()                 # Blank the display
    show_error_pattern()    # Display diagnostic patterns
    cleanup()              # Shutdown gracefully
```

**Error patterns:**
- `connection` → Red checkerboard (network errors)
- `format` → Yellow horizontal lines (data format errors)
- `timeout` → Purple stripes (timing issues)

**Dependencies:**
- `hub75` — Pimoroni library for HUB75 control
- `time` — Timing functions

### `main.py` — Application Logic

Main event loop orchestrating the system:

1. **Startup phase**
   - Initialize display
   - Connect to WiFi
   - Check server health
   - Register display (optional)

2. **Main loop**
   - Track time since last frame fetch
   - When dwell time expires:
     - Fetch new frame from server
     - Parse multi-frame data
     - Validate dimensions
   - Render frames to display
   - Handle animations (frame delays)
   - Handle errors (show patterns, retry)

3. **Shutdown phase**
   - Clear display
   - Disable output
   - Clean up resources

**Flow diagram:**

```
┌─────────────────┐
│  main()         │
├─────────────────┤
│  Initialize     │
│  • Display      │
│  • WiFi         │
│  • Server check │
└────────┬────────┘
         │
    ┌────▼────────────────────────────┐
    │  Event Loop                      │
    │  Track time since last fetch     │
    │                                  │
    │  ┌──────────────────────────┐    │
    │  │ Dwell timeout? (async)   │    │
    │  └──────────────────────────┘    │
    │         YES    │    NO            │
    │         │      │                  │
    │         ▼      │                  │
    │    Fetch frame │                  │
    │    Parse data  │                  │
    │    Validate    │                  │
    │         │      │                  │
    │         └──┬───┘                  │
    │            │                      │
    │         ┌──▼──────┐               │
    │         │ Display  │              │
    │         │ Animation│              │
    │         └──────────┘              │
    │            │                      │
    │            └──────┬───────────────┤
    │                   │               │
    │                   ▼               │
    │            ┌──────────────┐       │
    │            │ Error?       │       │
    │            └──────────────┘       │
    │              YES  │  NO           │
    │              │    │               │
    │         ┌────▼──┐└──┐             │
    │         │ Retry │   │             │
    │         │ Wait  │   │             │
    │         └───┬───┘   │             │
    │             └───┬───┘             │
    │                 │                 │
    │                 └────────────┬────┘
    │                              │
    │                         Loop
    │
    └──────────────────────────────────┘
```

## Data Flow

### Frame Retrieval and Display

```
┌─────────────┐
│   Server    │ GET /frame
└──────┬──────┘ ← Response headers:
       │          • X-Frame-Width
       │          • X-Frame-Height
       │          • X-Frame-Count
       │          • X-Frame-Delay-Ms
       │          • X-Dwell-Secs
       │          • X-App-Name
       │        Body: Raw RGB bytes
       │
       ▼
┌──────────────┐
│  network.py  │ Parse response
│ fetch_frame()│ Return (pixels, headers)
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│   main.py        │ Parse multi-frame data
│ parse_frame_data │ Check dimensions
└────────┬─────────┘ Split into frame list
         │
         ├─→ Validate (width×height match)
         │
         ├─→ For each frame:
         │   ├─ display.display_frame()
         │   └─ sleep(delay_ms)
         │
         ▼
┌──────────────┐
│  display.py  │ Set GPIO pins
│display_frame │ Update HUB75 matrix
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│ HUB75 LED Matrix │
└──────────────────┘
```

## Error Handling Strategy

### Network Errors
1. **Transient errors** (connection drops)
   - Show red error pattern
   - Retry up to N times with backoff
   - Resume normal operation on success

2. **Persistent errors** (server down)
   - Display error pattern continuously
   - Keep retrying with long delays
   - Automatic recovery when server comes back online

3. **Timeout errors**
   - Show purple error pattern
   - Retry sooner (network might be congested)

### Data Format Errors
1. **Size mismatch** (frame dimensions don't match display)
   - Show yellow error pattern
   - Fetch new frame (app might have changed)
   - Log error for debugging

2. **Incomplete data** (truncated response)
   - Show yellow error pattern
   - Fetch again (might be network corruption)

### Display Errors
- **Initialization failure** → Fatal error, exit
- **Runtime errors** → Log, show error pattern, recover
- **Pixel data errors** → Log and skip that frame

## Memory Management

### RP2040 Constraints
- **Total RAM:** ~252 KB
- **Available for app:** ~200 KB
- **Frame buffer needed:** 64×32×3 = 6,144 bytes (one frame)
- **Two frames (animation):** 12,288 bytes

### Optimization Strategies
1. **Minimal buffering** — Process frames one at a time
2. **Stream parsing** — Don't load entire response in memory
3. **Garbage collection** — Explicit `gc.collect()` after frame processing
4. **No frame caching** — Fetch and display immediately

## Timing Model

### Dwell Time
- **Concept:** How long to display a frame before fetching a new one
- **Source:** `X-Dwell-Secs` header from server
- **Fallback:** `DEFAULT_DWELL_SECS` from config (10 seconds)
- **Use case:** Show an app/content for a fixed duration, then rotate

### Frame Delay
- **Concept:** Time between frames within an animation
- **Source:** `X-Frame-Delay-Ms` header from server
- **Default:** 100 ms
- **Use case:** Multi-frame animations (e.g., scrolling text, animated icons)

### Combined Example
```
[0ms] Server says: "Show weather app" (8 frames, 50ms each, dwell 10 sec)

[0ms]  Show frame 0
[50ms] Show frame 1
[100ms] Show frame 2
[150ms] Show frame 3
[200ms] Show frame 4
[250ms] Show frame 5
[300ms] Show frame 6
[350ms] Show frame 7
[400ms] Animation done, keep showing frame 7

[10000ms] Dwell time expired, fetch next frame from server
```

## Configuration Hierarchy

1. **Default values** (hardcoded in config.py)
2. **Server overrides** (X-Brightness, X-Dwell-Secs headers)
3. **User adjustments** (edit config.py)

This allows the server to suggest brightness/timing while users can override locally.

## Testing Strategy

### Unit Testing (test_basic.py)

Isolated component tests:
- **Display test** — Rainbow pattern to HUB75
- **WiFi test** — Connection and IP info
- **Server test** — Health check
- **Frame test** — Full fetch cycle
- **Error patterns** — Visual validation

### Integration Testing

Full main loop with real server and display.

## Future Extensions

### Potential Features
- **mDNS auto-discovery** — Find Mosaic server on network
- **WebSocket push** — Real-time updates instead of polling
- **Over-the-air updates** — Download new client code from server
- **Local app storage** — Run apps without server connection
- **Brightness sensor** — Auto-adjust for ambient lighting
- **Status API** — Report uptime, frame count, errors to server

### Backward Compatibility
- New features added to `network.py` and `display.py`
- `main.py` evolves to use new modules
- Old code removed in major versions
- Config always forward-compatible

## Security Considerations

### Current Implementation
- **No authentication** — Server runs on trusted local network
- **HTTP only** — Acceptable for local use
- **No input validation** — Assumes server responses are correct

### Production Deployment
- Add API key support (already designed in Mosaic server)
- Use HTTPS if server has certificate
- Validate frame dimensions and data size
- Timeout on hung connections

## Code Style

- **Python 3 syntax** (MicroPython compatible)
- **Type hints** in docstrings (not code, for RP2040 compatibility)
- **Detailed comments** for complex logic
- **Descriptive names** (avoid cryptic abbreviations)
- **Error messages** for debugging
- **Modular functions** (single responsibility)

---

**Last updated:** 2026-02-08  
**Version:** 1.0.0
