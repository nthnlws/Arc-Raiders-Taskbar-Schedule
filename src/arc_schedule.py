import tkinter as tk
import requests
import time
from threading import Timer, Event
from pynput import keyboard

# --- CONFIGURATION ---
API_URL = "https://metaforge.app/api/arc-raiders/events-schedule"
REFRESH_RATE = 300.0  # Fetch API every 5 minutes
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

        self.setup_window()
        self.create_widgets()

        self.fetch_data()
        self.ui_timer = RepeatingTimer(60.0, self.process_data)
        self.ui_timer.start()

        self.listener = keyboard.Listener(on_press=self.on_key_press)
        self.listener.start()

    def setup_window(self):
        self.root.overrideredirect(True)  # Create a borderless window
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.config(bg='black') # This color will be made transparent
        self.root.attributes('-topmost', True)  # Keep the window on top
        # Make the window's background transparent
        self.root.attributes("-transparentcolor", "black")
        self.position_window()

    def create_widgets(self):
        # The black background of the labels will also become transparent
        self.header_label = tk.Label(self.root, text="", font=("Arial", 12, "bold"), fg="white", bg="black")
        self.header_label.pack(side=tk.LEFT, padx=10)

        self.content_label = tk.Label(self.root, text="Fetching data...", font=("Arial", 10), fg="white", bg="black")
        self.content_label.pack(side=tk.LEFT, padx=10)

    def position_window(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        # Position at the bottom right, over the taskbar
        x = screen_width - WINDOW_WIDTH - 250
        y = screen_height - WINDOW_HEIGHT - 4 # Small offset to sit nicely on the taskbar
        self.root.geometry(f"+{x}+{y}")

    def fetch_data(self):
        try:
            response = requests.get(API_URL)
            if response.status_code == 200:
                data = response.json()
                self.full_schedule = data.get("data", [])
                self.process_data()
            else:
                self.content_label.config(text="Error fetching data")
        except requests.RequestException:
            self.content_label.config(text="Connection error")

    def process_data(self):
        print("Processing data...")
        self.active_events = []
        self.upcoming_events = []
        now = time.time()

        for evt in self.full_schedule:
            start = evt["startTime"] / 1000.0
            end = evt["endTime"] / 1000.0

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
                    end_sec = float(evt["endTime"]) / 1000.0
                    mins_left = max(0, int((end_sec - now) / 60.0))
                    events_str.append(f"{evt['name']} ({evt['map']}, {mins_left}m)")
                text_str = " • ".join(events_str)
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
        
        self.content_label.config(text=text_str)

    def on_key_press(self, key):
        # Use 'F12' key to toggle between LIVE and NEXT views
        if key == keyboard.Key.f12:
            self.toggle_view()

    def on_close(self):
        print("Stopping threads...")
        self.api_timer.cancel()
        self.listener.stop()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = EventTracker(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()