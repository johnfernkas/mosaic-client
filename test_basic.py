"""
Basic test script for Mosaic Client

Use this to test individual components without running the full main loop.
Run from the REPL to diagnose setup issues.

Examples:
    from test_basic import test_display
    test_display()

    from test_basic import test_wifi
    test_wifi()

    from test_basic import test_server
    test_server()
"""

import time
from config import (
    DISPLAY_WIDTH,
    DISPLAY_HEIGHT,
    WIFI_SSID,
    WIFI_PASSWORD,
    SERVER_URL,
    DEBUG,
)


def test_display():
    """Test the LED matrix display by showing a test pattern."""
    print("\n" + "="*60)
    print("  DISPLAY TEST")
    print("="*60)

    try:
        from display import MosaicDisplay

        print("Initializing display...")
        d = MosaicDisplay()

        print("Creating rainbow pattern...")
        pixels = bytearray(DISPLAY_WIDTH * DISPLAY_HEIGHT * 3)

        # Rainbow gradient
        for y in range(DISPLAY_HEIGHT):
            for x in range(DISPLAY_WIDTH):
                idx = (y * DISPLAY_WIDTH + x) * 3
                pixels[idx] = (x * 255) // DISPLAY_WIDTH      # Red gradient
                pixels[idx + 1] = (y * 255) // DISPLAY_HEIGHT  # Green gradient
                pixels[idx + 2] = 128                          # Blue constant

        print("Displaying pattern (10 seconds)...")
        for i in range(10):
            d.display_frame(pixels)
            time.sleep(1)
            print(".", end="", flush=True)

        print("\n✓ Display test passed!")
        d.cleanup()

    except Exception as e:
        print(f"✗ Display test failed: {e}")
        import traceback
        traceback.print_exc()


def test_error_patterns():
    """Test all error pattern displays."""
    print("\n" + "="*60)
    print("  ERROR PATTERN TEST")
    print("="*60)

    try:
        from display import MosaicDisplay

        d = MosaicDisplay()
        patterns = ["connection", "format", "timeout"]

        for pattern in patterns:
            print(f"\nShowing {pattern} error pattern (2 seconds)...")
            d.show_error_pattern(pattern)
            time.sleep(2)

        print("✓ Error pattern test passed!")
        d.cleanup()

    except Exception as e:
        print(f"✗ Error pattern test failed: {e}")
        import traceback
        traceback.print_exc()


def test_wifi():
    """Test WiFi connection."""
    print("\n" + "="*60)
    print("  WiFi TEST")
    print("="*60)

    try:
        from network import connect_wifi

        print(f"SSID: {WIFI_SSID}")
        print(f"Attempting to connect...")

        if connect_wifi():
            print("✓ WiFi connected!")

            # Get IP info
            import network
            wlan = network.WLAN(network.STA_IF)
            ifconfig = wlan.ifconfig()
            print(f"  IP Address: {ifconfig[0]}")
            print(f"  Netmask: {ifconfig[1]}")
            print(f"  Gateway: {ifconfig[2]}")
            print(f"  DNS: {ifconfig[3]}")

            return True
        else:
            print("✗ WiFi connection failed")
            return False

    except Exception as e:
        print(f"✗ WiFi test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_server():
    """Test connection to Mosaic server."""
    print("\n" + "="*60)
    print("  SERVER CONNECTIVITY TEST")
    print("="*60)

    try:
        from network import check_server_health

        print(f"Server URL: {SERVER_URL}")
        print("Checking health...")

        if check_server_health():
            print("✓ Server is reachable!")
            return True
        else:
            print("✗ Server is not responding")
            return False

    except Exception as e:
        print(f"✗ Server test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_frame_fetch():
    """Test fetching a frame from the server."""
    print("\n" + "="*60)
    print("  FRAME FETCH TEST")
    print("="*60)

    try:
        from network import fetch_frame

        print("Fetching frame...")
        pixels, headers = fetch_frame()

        if pixels is None:
            print("✗ Failed to fetch frame")
            return False

        print("✓ Frame fetched successfully!")
        print(f"  App: {headers['app_name']}")
        print(f"  Dimensions: {headers['width']}x{headers['height']}")
        print(f"  Frame Count: {headers['frame_count']}")
        print(f"  Delay: {headers['delay_ms']} ms")
        print(f"  Dwell: {headers['dwell_secs']} sec")
        print(f"  Brightness: {headers['brightness']}")
        print(f"  Pixel Data Size: {len(pixels)} bytes")

        return True

    except Exception as e:
        print(f"✗ Frame fetch test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_full():
    """Run all tests in sequence."""
    print("\n" + "="*60)
    print("  MOSAIC CLIENT - FULL TEST SUITE")
    print("="*60)

    results = {}

    # Display test
    try:
        test_display()
        results["Display"] = "✓ PASS"
    except Exception as e:
        results["Display"] = f"✗ FAIL: {e}"

    # Error patterns
    try:
        test_error_patterns()
        results["Error Patterns"] = "✓ PASS"
    except Exception as e:
        results["Error Patterns"] = f"✗ FAIL: {e}"

    # WiFi test
    try:
        if test_wifi():
            results["WiFi"] = "✓ PASS"

            # Only test server if WiFi works
            try:
                if test_server():
                    results["Server"] = "✓ PASS"

                    # Only test frame fetch if server works
                    try:
                        if test_frame_fetch():
                            results["Frame Fetch"] = "✓ PASS"
                        else:
                            results["Frame Fetch"] = "✗ FAIL"
                    except Exception as e:
                        results["Frame Fetch"] = f"✗ FAIL: {e}"
                else:
                    results["Server"] = "✗ FAIL"
                    results["Frame Fetch"] = "⊘ SKIP"
            except Exception as e:
                results["Server"] = f"✗ FAIL: {e}"
                results["Frame Fetch"] = "⊘ SKIP"
        else:
            results["WiFi"] = "✗ FAIL"
            results["Server"] = "⊘ SKIP"
            results["Frame Fetch"] = "⊘ SKIP"
    except Exception as e:
        results["WiFi"] = f"✗ FAIL: {e}"
        results["Server"] = "⊘ SKIP"
        results["Frame Fetch"] = "⊘ SKIP"

    # Summary
    print("\n" + "="*60)
    print("  TEST SUMMARY")
    print("="*60)
    for test_name, result in results.items():
        print(f"{test_name:.<40} {result}")

    print("\n")


if __name__ == "__main__":
    # Uncomment the test you want to run:

    # test_display()
    # test_error_patterns()
    # test_wifi()
    # test_server()
    # test_frame_fetch()

    test_full()  # Run all tests
