"""
boot.py - Auto-start example for Interstate 75W

Copy this file to the Interstate 75W as 'boot.py' to automatically
start the Mosaic client when the device boots up.

Instructions:
    1. Upload this file to the Interstate 75W as 'boot.py'
    2. Configure settings in config.py first
    3. Reset the device - Mosaic client will start automatically

If you want to disable auto-start, rename or delete boot.py.
To interrupt the auto-start, press Ctrl+C during the first 2 seconds
after power-up while connected via USB/REPL.
"""

import sys
import time

# Give the user a chance to interrupt via REPL
print("\n🎨 Mosaic Client starting in 2 seconds...")
print("Press Ctrl+C to interrupt (requires REPL connection)")

try:
    # Wait 2 seconds for user to press Ctrl+C
    for i in range(20):
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nInterrupted! Mosaic client did not start.")
    print("Run 'import main' and 'main.main()' from the REPL to start manually.")
    sys.exit(0)

# If we get here, start the Mosaic client
print("\nStarting Mosaic Client...")

try:
    import main
    main.main()
except KeyboardInterrupt:
    print("\n\nMosaic Client interrupted by user")
except Exception as e:
    print(f"\nFATAL ERROR: {e}")
    import traceback
    traceback.print_exc()
    print("\nPlease check config.py and connection settings.")
    print("Connect via REPL for debugging.")
