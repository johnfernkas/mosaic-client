"""
Mosaic Client

Fetches and displays frames from a Mosaic server on HUB75 LED matrices.
"""

import time
import network
import urequests
from config import (
    WIFI_SSID, WIFI_PASSWORD, WIFI_CONNECT_TIMEOUT,
    SERVER_URL, DISPLAY_ID, BRIGHTNESS
)
try:
    from config import DISPLAY_NAME
except:
    DISPLAY_NAME = DISPLAY_ID or "Mosaic Display"
from display import Display


class MosaicClient:
    """Main client controller."""
    
    def __init__(self):
        # Initialize display immediately for visual feedback
        self.display = Display(brightness=BRIGHTNESS)
        self.display.boot_screen()
        
        # State
        self.frames = None
        self.frame_count = 1
        self.frame_delay = 100
        self.dwell_secs = 10
        self.last_fetch = 0
        self.current_frame = 0
        self.last_frame_time = 0
    
    def connect_wifi(self):
        """Connect to WiFi network."""
        self.display.wifi_connecting()
        
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        
        if wlan.isconnected():
            ip = wlan.ifconfig()[0]
            self.display.wifi_connected(ip)
            time.sleep(0.5)
            return True
        
        wlan.disconnect()
        time.sleep(0.5)
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        
        start = time.time()
        while not wlan.isconnected():
            if time.time() - start > WIFI_CONNECT_TIMEOUT:
                self.display.wifi_failed()
                return False
            time.sleep(0.5)
        
        ip = wlan.ifconfig()[0]
        self.display.wifi_connected(ip)
        time.sleep(0.5)
        return True
    
    def register_display(self):
        """Register this display with the server."""
        if not DISPLAY_ID:
            return True  # Skip if no display ID configured
        
        try:
            url = f"{SERVER_URL}/api/displays"
            data = {
                "id": DISPLAY_ID,
                "name": DISPLAY_NAME,
                "width": self.display.width,
                "height": self.display.height
            }
            
            # MicroPython urequests needs json as string
            import json
            response = urequests.post(url, 
                data=json.dumps(data),
                headers={"Content-Type": "application/json"},
                timeout=10)
            response.close()
            return True
        except Exception as e:
            print(f"Registration failed: {e}")
            return False
    
    def fetch_frame(self):
        """Fetch frame data from server."""
        try:
            url = f"{SERVER_URL}/frame"
            if DISPLAY_ID:
                url += f"?display={DISPLAY_ID}"
            
            response = urequests.get(url, timeout=10)
            
            if response.status_code != 200:
                return False
            
            # Parse headers (MicroPython uses lowercase)
            h = response.headers
            self.frame_count = int(h.get("x-frame-count") or h.get("X-Frame-Count") or "1")
            self.frame_delay = int(h.get("x-frame-delay-ms") or h.get("X-Frame-Delay-Ms") or "100")
            self.dwell_secs = int(h.get("x-dwell-secs") or h.get("X-Dwell-Secs") or "10")
            
            # Update brightness from server
            brightness = h.get("x-brightness") or h.get("X-Brightness")
            if brightness:
                self.display.brightness = int(brightness)
            
            self.frames = response.content
            self.last_fetch = time.time()
            self.current_frame = 0
            
            response.close()
            return True
            
        except Exception as e:
            print(f"Fetch error: {e}")
            return False
    
    def should_fetch(self):
        """Check if we need new frame data."""
        if self.frames is None:
            return True
        return (time.time() - self.last_fetch) >= self.dwell_secs
    
    def display_current_frame(self):
        """Display the current animation frame."""
        if self.frames is None:
            return
        
        frame_size = self.display.width * self.display.height * 3
        offset = self.current_frame * frame_size
        
        if offset + frame_size <= len(self.frames):
            frame_data = self.frames[offset:offset + frame_size]
            self.display.show_frame(frame_data)
    
    def run(self):
        """Main loop."""
        # Connect to WiFi
        if not self.connect_wifi():
            time.sleep(5)
            return  # Will restart via main.py loop
        
        # Register with server
        self.display.server_connecting()
        self.register_display()
        
        # Main loop
        while True:
            # Fetch new frame if needed
            if self.should_fetch():
                if not self.fetch_frame():
                    self.display.server_error()
                    time.sleep(3)
                    continue
            
            # Display animation frame
            now = time.ticks_ms()
            if time.ticks_diff(now, self.last_frame_time) >= self.frame_delay:
                self.display_current_frame()
                self.current_frame = (self.current_frame + 1) % self.frame_count
                self.last_frame_time = now
            
            time.sleep_ms(10)


# Entry point
if __name__ == "__main__":
    while True:
        try:
            client = MosaicClient()
            client.run()
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
