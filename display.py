"""
Mosaic Display Module

Hardware-abstracted LED matrix display controller.
"""

import time

try:
    import random
except:
    random = None

try:
    from interstate75 import Interstate75, DISPLAY_INTERSTATE75_64X32
    HARDWARE = "interstate75"
except ImportError:
    HARDWARE = None


class Display:
    """LED matrix display controller."""

    def __init__(self, width=64, height=32, brightness=80):
        self.width = width
        self.height = height
        self.brightness = brightness
        self._init_hardware()
        
    def _init_hardware(self):
        """Initialize display hardware."""
        if HARDWARE == "interstate75":
            self.i75 = Interstate75(display=DISPLAY_INTERSTATE75_64X32)
            self.graphics = self.i75.display
            bounds = self.graphics.get_bounds()
            self.width = bounds[0]
            self.height = bounds[1]
        else:
            raise RuntimeError("No supported display hardware found")
    
    def update(self):
        """Push buffer to display."""
        if HARDWARE == "interstate75":
            self.i75.update()
    
    def clear(self, color=(0, 0, 0)):
        """Fill display with solid color."""
        pen = self.graphics.create_pen(color[0], color[1], color[2])
        self.graphics.set_pen(pen)
        self.graphics.clear()
    
    def pixel(self, x, y, r, g, b):
        """Set a single pixel."""
        scale = self.brightness / 100.0
        pen = self.graphics.create_pen(
            int(r * scale),
            int(g * scale),
            int(b * scale)
        )
        self.graphics.set_pen(pen)
        self.graphics.pixel(x, y)
    
    def rect(self, x, y, w, h, r, g, b):
        """Draw filled rectangle."""
        for py in range(y, y + h):
            for px in range(x, x + w):
                if 0 <= px < self.width and 0 <= py < self.height:
                    self.pixel(px, py, r, g, b)
    
    def text(self, message, x, y, color=(255, 255, 255)):
        """Draw text on display."""
        scale = self.brightness / 100.0
        pen = self.graphics.create_pen(
            int(color[0] * scale),
            int(color[1] * scale),
            int(color[2] * scale)
        )
        self.graphics.set_pen(pen)
        self.graphics.text(message, x, y, -1, 1)
    
    def show_frame(self, rgb_data):
        """Display RGB frame data."""
        expected = self.width * self.height * 3
        if len(rgb_data) < expected:
            return False
        
        idx = 0
        for y in range(self.height):
            for x in range(self.width):
                self.pixel(x, y, rgb_data[idx], rgb_data[idx+1], rgb_data[idx+2])
                idx += 3
        
        self.update()
        return True
    
    # -------------------------------------------------------------------------
    # Boot & Status Screens
    # -------------------------------------------------------------------------
    
    def boot_screen(self):
        """Mosaic tile animation on boot."""
        # Tile colors - vibrant mosaic palette
        colors = [
            (0, 200, 255),   # cyan
            (255, 0, 150),   # magenta
            (255, 200, 0),   # gold
            (0, 255, 100),   # green
            (150, 0, 255),   # purple
            (255, 100, 0),   # orange
        ]
        
        tile_size = 4
        tiles_x = self.width // tile_size
        tiles_y = self.height // tile_size
        
        # Create list of all tile positions
        tiles = [(x, y) for y in range(tiles_y) for x in range(tiles_x)]
        
        # Shuffle if random available, otherwise use diagonal pattern
        if random:
            try:
                random.shuffle(tiles)
            except:
                pass
        
        # Fill tiles one by one with animation
        self.clear()
        for i, (tx, ty) in enumerate(tiles):
            color = colors[i % len(colors)]
            self.rect(tx * tile_size, ty * tile_size, tile_size, tile_size, *color)
            if i % 8 == 0:  # Update every 8 tiles for speed
                self.update()
                time.sleep_ms(10)
        
        self.update()
        time.sleep(0.3)
        
        # Fade to show "MOSAIC" branding
        self._show_logo()
    
    def _show_logo(self):
        """Show MOSAIC logo screen."""
        self.clear((10, 10, 20))
        
        # Draw decorative mosaic tiles in corners
        colors = [(0, 200, 255), (255, 0, 150), (255, 200, 0), (0, 255, 100)]
        
        # Top-left corner tiles
        self.rect(0, 0, 3, 3, *colors[0])
        self.rect(4, 0, 3, 3, *colors[1])
        self.rect(0, 4, 3, 3, *colors[2])
        
        # Top-right corner tiles
        self.rect(57, 0, 3, 3, *colors[1])
        self.rect(61, 0, 3, 3, *colors[0])
        self.rect(61, 4, 3, 3, *colors[3])
        
        # Bottom-left corner tiles
        self.rect(0, 25, 3, 3, *colors[3])
        self.rect(0, 29, 3, 3, *colors[0])
        self.rect(4, 29, 3, 3, *colors[2])
        
        # Bottom-right corner tiles
        self.rect(57, 29, 3, 3, *colors[2])
        self.rect(61, 29, 3, 3, *colors[1])
        self.rect(61, 25, 3, 3, *colors[0])
        
        # Center text "MOSAIC"
        self.text("MOSAIC", 11, 12, (255, 255, 255))
        
        self.update()
        time.sleep(0.8)
    
    def wifi_connecting(self):
        """Show WiFi connecting screen."""
        self._status_screen("WiFi", (255, 200, 0), dots=True)
    
    def wifi_connected(self, ip):
        """Show WiFi connected."""
        self._status_screen("WiFi OK", (0, 255, 100))
        time.sleep(0.3)
    
    def wifi_failed(self):
        """Show WiFi error."""
        self._status_screen("No WiFi", (255, 50, 50))
    
    def server_connecting(self):
        """Show server connecting."""
        self._status_screen("Server", (255, 200, 0), dots=True)
    
    def server_error(self):
        """Show server error with mosaic pattern."""
        self.clear((20, 0, 0))
        
        # Draw warning mosaic pattern
        for y in range(0, self.height, 4):
            for x in range(0, self.width, 4):
                if (x + y) % 8 == 0:
                    self.rect(x, y, 3, 3, 255, 100, 0)
        
        self.text("ERROR", 17, 12, (255, 255, 255))
        self.update()
    
    def _status_screen(self, message, color, dots=False):
        """Generic status screen with centered text."""
        self.clear((10, 10, 20))
        
        # Draw accent bar at top
        self.rect(0, 0, self.width, 2, *color)
        
        # Draw small mosaic accent in corners
        self.rect(0, 0, 4, 4, *color)
        self.rect(60, 0, 4, 4, *color)
        
        # Center the message (approximate - 6px per char)
        text_width = len(message) * 6
        x = (self.width - text_width) // 2
        
        self.text(message, x, 13, color)
        
        if dots:
            # Animated dots below
            self.text("...", 28, 22, (100, 100, 100))
        
        self.update()
    
    def _hsv_to_rgb(self, h, s, v):
        """Convert HSV to RGB (h: 0-255, s: 0-255, v: 0-255)."""
        if s == 0:
            return v, v, v
        
        region = h // 43
        remainder = (h - (region * 43)) * 6
        
        p = (v * (255 - s)) >> 8
        q = (v * (255 - ((s * remainder) >> 8))) >> 8
        t = (v * (255 - ((s * (255 - remainder)) >> 8))) >> 8
        
        if region == 0:
            return v, t, p
        elif region == 1:
            return q, v, p
        elif region == 2:
            return p, v, t
        elif region == 3:
            return p, q, v
        elif region == 4:
            return t, p, v
        else:
            return v, p, q
