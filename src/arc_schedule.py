import tkinter as tk
import requests
import time
from threading import Timer
from pynput import keyboard
import ctypes

# --- CONFIGURATION ---
API_URL = "https://metaforge.app/api/arc-raiders/events-schedule"
REFRESH_RATE = 300.0       # Retry rate if the API fails (5 mins)
DATA_REFRESH_RATE = 3600.0 # How often to grab fresh data (1 hour)
WINDOW_WIDTH = 675
WINDOW_HEIGHT = 40

class RepeatingTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

class EventTracker:
    def __init__(self, root):
        self.full_schedule = []
        self.root = root
        self.active_events = []
        self.upcoming_events = []
        self.showing_live = True
        
        # Timer placeholders
        self.retry_timer = None
        self.ui_timer = None

        self.setup_window()
        self.create_widgets()

        # Initial Fetch
        self.fetch_data()
        
        # UI Update Timer (updates countdowns every minute)
        self.ui_timer = RepeatingTimer(60.0, self.process_data)
        self.ui_timer.start()

        self.listener = keyboard.Listener(on_press=self.on_key_press)
        self.listener.start()

    def setup_window(self):
        self.root.overrideredirect(True)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.config(bg='black')
        self.root.attributes('-topmost', True)
        self.root.attributes("-transparentcolor", "black")
        self.position_window()

        # --- MAKE CLICK-THROUGH ---
        # GWL_EXSTYLE = -20
        # WS_EX_TRANSPARENT = 0x20
        # WS_EX_LAYERED = 0x80000
        
        hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
        style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
        style = style | 0x20 | 0x80000
        ctypes.windll.user32.SetWindowLongW(hwnd, -20, style)

    def create_widgets(self):
        self.header_label = tk.Label(self.root, text="", font=("Arial", 12, "bold"), fg="white", bg="black")
        self.header_label.pack(side=tk.LEFT, padx=10)

        self.content_label = tk.Label(self.root, text="Fetching data...", font=("Arial", 10), fg="white", bg="black")
        self.content_label.pack(side=tk.LEFT, padx=10)

    def position_window(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = screen_width - WINDOW_WIDTH - 250
        y = screen_height - WINDOW_HEIGHT - 4
        self.root.geometry(f"+{x}+{y}")

    def fetch_data(self):
        if self.retry_timer and self.retry_timer.is_alive():
            self.retry_timer.cancel()

        try:
            response = requests.get(API_URL)
            if response.status_code == 200:
                data = response.json()
                if data.get('data'):
                    self.full_schedule = data.get("data", [])
                    self.process_data()
                    
                    # --- Schedule the next fetch even on success ---
                    print(f"Data refreshed. Next refresh in {DATA_REFRESH_RATE}s")
                    self.retry_timer = Timer(DATA_REFRESH_RATE, self.fetch_data)
                    self.retry_timer.daemon = True
                    self.retry_timer.start()
                    return 
                else:
                    self.schedule_retry("No Metaforge data available")
            else:
                self.schedule_retry(f"HTTP Error {response.status_code}")
        except requests.RequestException:
            self.schedule_retry("Connection error")

    def schedule_retry(self, error_message):
        """Updates UI with error and schedules fetch_data again."""
        self.content_label.config(text=error_message, fg="OrangeRed1", font=("Arial", 12, "bold"))
        print(f"{error_message}. Retrying in {REFRESH_RATE} seconds...")
        
        # Schedule the retry on a background thread
        self.retry_timer = Timer(REFRESH_RATE, self.fetch_data)
        self.retry_timer.start()

    def process_data(self):
        self.active_events = []
        self.upcoming_events = []
        now = time.time()

        for evt in self.full_schedule:
            # Convert ms to seconds
            start = float(evt["startTime"]) / 1000.0
            end = float(evt["endTime"]) / 1000.0

            if start <= now < end:
                self.active_events.append(evt)
            elif now < start:
                self.upcoming_events.append(evt)

        self.upcoming_events.sort(key=lambda x: x["startTime"])
        self.update_display()

    def toggle_view(self):
        self.showing_live = not self.showing_live
        self.update_display()

    def update_display(self):
        text_str = ""
        now = time.time()

        if self.showing_live:
            self.header_label.config(text="LIVE", fg="green yellow")
            if not self.active_events:
                text_str = "No Active Events"
            else:
                events_str = []
                for evt in self.active_events:
                    if evt['name'] == "Electromagnetic Storm":
                        evt['name'] = "EMS"
                    end_sec = float(evt["endTime"]) / 1000.0
                    mins_left = max(0, int((end_sec - now) / 60.0))
                    events_str.append(f"{evt['name']} ({evt['map']})")
                text_str = " • ".join(events_str)
                text_str += f" • {mins_left}m"
        else:
            self.header_label.config(text="NEXT", fg="cyan")
            if not self.upcoming_events:
                text_str = "No Upcoming Data"
            else:
                events_str = []
                for evt in self.upcoming_events[:3]:
                    start_sec = float(evt["startTime"]) / 1000.0
                    mins_to_start = int((start_sec - now) / 60.0)
                    events_str.append(f"{evt['name']} ({evt['map']}, {mins_to_start}m)")
                text_str = " • ".join(events_str)
        
        self.content_label.config(text=text_str, fg="white", font=("Arial", 10))

    def on_key_press(self, key):
        if key == keyboard.Key.f12:
            self.toggle_view()

    def on_close(self):
        print("Stopping threads...")
        # Cancel the UI timer
        if self.ui_timer:
            self.ui_timer.cancel()
        
        # Cancel the retry timer if it's counting down
        if self.retry_timer:
            self.retry_timer.cancel()
            
        self.listener.stop()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = EventTracker(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()