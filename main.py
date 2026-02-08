"""
Mosaic Client for Interstate 75W

Main entry point and event loop for the Mosaic LED display client.
Connects to WiFi, fetches frames from the Mosaic server, and displays them.
"""

import time
import sys

# Import our modules
from network import connect_wifi, fetch_frame, check_server_health, register_display
from display import MosaicDisplay, debug_print
from config import (
    FRAME_FETCH_RETRY_ATTEMPTS,
    FRAME_FETCH_RETRY_DELAY,
    ERROR_DISPLAY_TIME,
    DEFAULT_DWELL_SECS,
    DISPLAY_WIDTH,
    DISPLAY_HEIGHT,
)


def parse_frame_data(pixel_bytes, frame_count, width, height):
    """
    Parse raw RGB bytes into individual frames.

    Args:
        pixel_bytes: Raw RGB bytes from server
        frame_count: Number of frames in the data
        width: Frame width in pixels
        height: Frame height in pixels

    Returns:
        list: List of frame byte objects, or None if parsing fails
    """
    try:
        bytes_per_frame = width * height * 3
        total_expected = bytes_per_frame * frame_count

        if len(pixel_bytes) < total_expected:
            print(f"ERROR: Received only {len(pixel_bytes)} bytes, "
                  f"expected {total_expected} for {frame_count} frame(s)")
            return None

        frames = []
        for i in range(frame_count):
            start = i * bytes_per_frame
            end = start + bytes_per_frame
            frames.append(pixel_bytes[start:end])

        return frames

    except Exception as e:
        print(f"ERROR: Failed to parse frame data: {e}")
        return None


def main():
    """
    Main application loop.

    1. Connect to WiFi
    2. Continuously fetch and display frames from Mosaic server
    3. Handle animations (multiple frames with delays)
    4. Handle errors gracefully
    """

    print("\n" + "="*60)
    print("  MOSAIC CLIENT for Interstate 75W")
    print("="*60 + "\n")

    # Initialize display
    try:
        display = MosaicDisplay()
    except Exception as e:
        print(f"FATAL: Cannot initialize display: {e}")
        sys.exit(1)

    # Connect to WiFi
    if not connect_wifi():
        print("\nERROR: Failed to connect to WiFi")
        display.show_error_pattern("connection")
        time.sleep(5)
        display.cleanup()
        sys.exit(1)

    # Check server connectivity
    print("Checking Mosaic server...")
    if not check_server_health():
        print("WARNING: Mosaic server is not responding")
        display.show_error_pattern("connection")
        time.sleep(5)

    # Attempt to register display (optional, non-fatal if it fails)
    register_display()

    # Main event loop
    try:
        print("\n" + "="*60)
        print("  RUNNING - Fetching frames from Mosaic server")
        print("="*60 + "\n")

        retry_count = 0
        last_frame_time = 0
        current_dwell_secs = DEFAULT_DWELL_SECS

        while True:
            try:
                # Time to fetch a new frame
                current_time = time.time()

                if current_time - last_frame_time >= current_dwell_secs:
                    # Fetch frame from server with retries
                    pixel_data = None
                    headers = None

                    for attempt in range(FRAME_FETCH_RETRY_ATTEMPTS):
                        pixel_data, headers = fetch_frame()

                        if pixel_data is not None:
                            break

                        if attempt < FRAME_FETCH_RETRY_ATTEMPTS - 1:
                            print(f"Retry {attempt + 1}/{FRAME_FETCH_RETRY_ATTEMPTS - 1} "
                                  f"in {FRAME_FETCH_RETRY_DELAY}s...")
                            time.sleep(FRAME_FETCH_RETRY_DELAY)

                    # Handle fetch failure
                    if pixel_data is None:
                        print("ERROR: Failed to fetch frame after all retries")
                        display.show_error_pattern("connection")
                        time.sleep(ERROR_DISPLAY_TIME)
                        retry_count += 1
                        current_dwell_secs = DEFAULT_DWELL_SECS
                        last_frame_time = current_time
                        continue

                    # Parse frame data
                    frame_count = headers.get("frame_count", 1)
                    frame_delay_ms = headers.get("delay_ms", 100)
                    current_dwell_secs = headers.get("dwell_secs", DEFAULT_DWELL_SECS)

                    # Validate dimensions match
                    server_width = headers.get("width", DISPLAY_WIDTH)
                    server_height = headers.get("height", DISPLAY_HEIGHT)

                    if server_width != DISPLAY_WIDTH or server_height != DISPLAY_HEIGHT:
                        print(f"ERROR: Server frame size {server_width}x{server_height} "
                              f"does not match display {DISPLAY_WIDTH}x{DISPLAY_HEIGHT}")
                        display.show_error_pattern("format")
                        time.sleep(ERROR_DISPLAY_TIME)
                        current_dwell_secs = DEFAULT_DWELL_SECS
                        last_frame_time = current_time
                        continue

                    # Parse frames
                    frames = parse_frame_data(
                        pixel_data,
                        frame_count,
                        server_width,
                        server_height
                    )

                    if frames is None:
                        print("ERROR: Failed to parse frame data")
                        display.show_error_pattern("format")
                        time.sleep(ERROR_DISPLAY_TIME)
                        current_dwell_secs = DEFAULT_DWELL_SECS
                        last_frame_time = current_time
                        continue

                    # Display animation frames
                    debug_print(f"Displaying {frame_count} frame(s) "
                               f"from app: {headers.get('app_name', 'unknown')}")

                    animation_start = time.time()
                    frame_index = 0

                    while True:
                        # Display current frame
                        display.display_frame(frames[frame_index])

                        # Timing for next frame
                        frame_index += 1
                        if frame_index >= frame_count:
                            # Animation complete, will fetch new frame next time
                            break

                        # Wait for frame delay (in milliseconds)
                        delay_seconds = frame_delay_ms / 1000.0
                        time.sleep(delay_seconds)

                    # Update dwell timer after showing animation
                    last_frame_time = time.time()
                    retry_count = 0  # Reset retry counter on success

                else:
                    # Still in dwell period, just sleep a bit
                    time.sleep(0.1)

            except KeyboardInterrupt:
                print("\n\nInterrupted by user")
                break

            except Exception as e:
                print(f"Unexpected error in main loop: {e}")
                import traceback
                traceback.print_exc()
                display.show_error_pattern("connection")
                time.sleep(ERROR_DISPLAY_TIME)
                current_dwell_secs = DEFAULT_DWELL_SECS
                last_frame_time = time.time()

    finally:
        # Cleanup on exit
        print("\n\nShutting down...")
        display.cleanup()
        print("Done!")


if __name__ == "__main__":
    main()
