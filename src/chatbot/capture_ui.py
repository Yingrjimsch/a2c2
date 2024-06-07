import mss
import mss.tools
from io import BytesIO

"""
This module is used to capture the screen 
"""

# Function to capture the screen
def capture() -> dict[str, list[tuple[str, any]]]:
    with mss.mss() as sct:
        screens = []
        #Iterate over every monitor and make screenshot
        for i in range(1, len(sct.monitors)):
            
            monitor_number = i
            mon = sct.monitors[monitor_number]

            # The screen part to capture
            monitor = {
                "top": mon["top"],
                "left": mon["left"],
                "width": mon["width"],
                "height": mon["height"],
                "mon": monitor_number,
            }
            # Save Path
            screen_name = f"screen_{monitor_number}.png"
            print(screen_name)
            # Grab the data
            sct_img = sct.grab(monitor)
            raw_bytes = mss.tools.to_png(sct_img.rgb, sct_img.size)
            image_byte = BytesIO(raw_bytes)
            image_byte.name = screen_name
            img = ("screens", image_byte)
            screens.append(img)
        return screens
