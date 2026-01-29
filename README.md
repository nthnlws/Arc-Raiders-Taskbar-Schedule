# Event Tracker Overlay

A simple, borderless window that displays a schedule of events on top of your taskbar, fetching data from the MetaForge API.

## Features

*   Displays live and upcoming events.
*   Borderless, transparent window that sits over the taskbar.
*   Toggle between "LIVE" and "NEXT" views using the `F12` key.
*   Automatically refreshes data every 5 minutes.

## Installation and Usage

### For End-Users (Recommended)

1.  Go to the Releases page
2.  Download the latest `arc_schedule_taskbar.exe` file.
3.  Run the executable. No installation is required.

## How to Build the .exe

If you want to build the executable yourself, you'll need PyInstaller.

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole src/arc_schedule.py