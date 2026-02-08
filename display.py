"""
LED Matrix Display Module

Manages the HUB75 display using Pimoroni's Hub75 library.
Handles pixel rendering, color conversion, and error patterns.
"""

from hub75 import Hub75
import time
from config import (
    DISPLAY_WIDTH,
    DISPLAY_HEIGHT,
    GPIO_CONFIG,
    BRIGHTNESS,
    DISPLAY_ENABLED,
    DEBUG,
)


def debug_print(msg):
    """Print debug messages if debugging is enabled."""
    if DEBUG:
        print(f"[DISPLAY] {msg}")


class MosaicDisplay:
    """
    HUB75 LED matrix display controller.
    """

    def __init__(self):
        """Initialize the display with configured GPIO pins."""
        debug_print(f"Initializing {DISPLAY_WIDTH}x{DISPLAY_HEIGHT} HUB75 display")

        try:
            # Create the hub75 display with configured GPIO pins
            self.display = Hub75(
                width=DISPLAY_WIDTH,
                height=DISPLAY_HEIGHT,
                r0=GPIO_CONFIG["R0"],
                r1=GPIO_CONFIG["R1"],
                g0=GPIO_CONFIG["G0"],
                g1=GPIO_CONFIG["G1"],
                b0=GPIO_CONFIG["B0"],
                b1=GPIO_CONFIG["B1"],
                a=GPIO_CONFIG["A"],
                b=GPIO_CONFIG["B"],
                c=GPIO_CONFIG["C"],
                d=GPIO_CONFIG["D"],
                e=GPIO_CONFIG["E"],
                clk=GPIO_CONFIG["CLK"],
                stb=GPIO_CONFIG["STB"],
                oe=GPIO_CONFIG["OE"],
            )

            # Set brightness
            self.set_brightness(BRIGHTNESS)

            # Enable/disable the display
            if DISPLAY_ENABLED:
                self.display.start()
                debug_print("Display enabled and started")
            else:
                debug_print("Display initialized but disabled")

            self.enabled = DISPLAY_ENABLED
            self.current_brightness = BRIGHTNESS

        except Exception as e:
            print(f"ERROR: Failed to initialize display: {e}")
            print("Ensure the Hub75 library is installed and GPIO pins are correct.")
            raise

    def set_brightness(self, brightness):
        """
        Set the display brightness (0-255).

        Args:
            brightness: Brightness value from 0 (off) to 255 (full)
        """
        try:
            # Clamp to valid range
            brightness = max(0, min(255, brightness))

            # The Hub75 library uses 0-255 range
            self.display.set_brightness(brightness)
            self.current_brightness = brightness

            debug_print(f"Brightness set to {brightness}")

        except Exception as e:
            print(f"Warning: Failed to set brightness: {e}")

    def enable(self):
        """Enable the display."""
        if not self.enabled:
            try:
                self.display.start()
                self.enabled = True
                debug_print("Display enabled")
            except Exception as e:
                print(f"Warning: Failed to enable display: {e}")

    def disable(self):
        """Disable the display (blank screen, lower power)."""
        if self.enabled:
            try:
                self.display.stop()
                self.enabled = False
                debug_print("Display disabled")
            except Exception as e:
                print(f"Warning: Failed to disable display: {e}")

    def clear(self):
        """Clear the display (fill with black)."""
        try:
            # Create a black frame (all zeros)
            black_frame = bytearray(DISPLAY_WIDTH * DISPLAY_HEIGHT * 3)
            self.display_frame(black_frame)
            debug_print("Display cleared")
        except Exception as e:
            print(f"Warning: Failed to clear display: {e}")

    def display_frame(self, rgb_pixels):
        """
        Display a frame of RGB pixel data.

        Args:
            rgb_pixels: Bytes object containing RGB pixel data (width*height*3 bytes)
                       in format: [R0G0B0, R1G1B1, R2G2B2, ...]
        """
        if not self.enabled:
            return

        try:
            # Ensure we have the right amount of data
            expected_size = DISPLAY_WIDTH * DISPLAY_HEIGHT * 3
            if len(rgb_pixels) < expected_size:
                print(f"Warning: Received only {len(rgb_pixels)} bytes, expected {expected_size}")
                return

            # Convert RGB bytes to pixel data for the display
            # The Hub75 library expects pixels to be set via indexing
            pixels = self.display
            pixel_idx = 0

            for y in range(DISPLAY_HEIGHT):
                for x in range(DISPLAY_WIDTH):
                    r = rgb_pixels[pixel_idx]
                    g = rgb_pixels[pixel_idx + 1]
                    b = rgb_pixels[pixel_idx + 2]
                    pixel_idx += 3

                    # Set the pixel (RGB values are 0-255)
                    pixels.set_pixel(x, y, r, g, b)

            # Update the display with the new frame
            self.display.update()

        except Exception as e:
            print(f"Error displaying frame: {e}")

    def show_error_pattern(self, error_type="connection"):
        """
        Display an error pattern on the LED matrix.

        Args:
            error_type: Type of error ("connection", "format", "timeout")
        """
        if not self.enabled:
            return

        try:
            pixels = self.display

            if error_type == "connection":
                # Red checkerboard pattern for connection errors
                for y in range(DISPLAY_HEIGHT):
                    for x in range(DISPLAY_WIDTH):
                        if (x + y) % 2 == 0:
                            pixels.set_pixel(x, y, 255, 0, 0)  # Red
                        else:
                            pixels.set_pixel(x, y, 0, 0, 0)  # Black

            elif error_type == "format":
                # Yellow horizontal lines for format errors
                for y in range(DISPLAY_HEIGHT):
                    for x in range(DISPLAY_WIDTH):
                        if y % 2 == 0:
                            pixels.set_pixel(x, y, 255, 255, 0)  # Yellow
                        else:
                            pixels.set_pixel(x, y, 0, 0, 0)  # Black

            elif error_type == "timeout":
                # Purple scrolling pattern for timeout
                for y in range(DISPLAY_HEIGHT):
                    for x in range(DISPLAY_WIDTH):
                        if x % 4 == 0:
                            pixels.set_pixel(x, y, 255, 0, 255)  # Magenta
                        else:
                            pixels.set_pixel(x, y, 0, 0, 0)  # Black

            else:
                # Default: flashing red
                for y in range(DISPLAY_HEIGHT):
                    for x in range(DISPLAY_WIDTH):
                        pixels.set_pixel(x, y, 255, 0, 0)  # Red

            self.display.update()
            debug_print(f"Error pattern displayed: {error_type}")

        except Exception as e:
            print(f"Error displaying error pattern: {e}")

    def cleanup(self):
        """Clean up display resources."""
        try:
            self.clear()
            self.disable()
            debug_print("Display cleaned up")
        except Exception as e:
            print(f"Warning: Error during cleanup: {e}")
