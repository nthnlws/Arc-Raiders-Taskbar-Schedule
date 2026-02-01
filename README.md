# Event Tracker Overlay

A simple, borderless window that displays a schedule of events on top of your taskbar, fetching data from the MetaForge API.
<img width="1911" height="44" alt="image" src="https://github.com/user-attachments/assets/fd81f6ec-c2c6-4d3b-823b-0fa173f7e826" />

## Features

*   Displays live and upcoming events.
*   Borderless, transparent window that sits over the taskbar.
*   Toggle between "LIVE" and "NEXT" views using the `F12` key.
*   Automatically refreshes data every minute.

## Data Source & Attribution

This project uses the Unofficial Arc Raiders API provided by MetaForge. The data is subject to change and is not affiliated with Embark Studios.

In accordance with the API's terms, attribution is provided below:

> All data is sourced from the [MetaForge API for Arc Raiders](https://metaforge.app/arc-raiders).
> Program icon from https://cdn.metaforge.app/arc-raiders/custom/matriarch.webp (Returned in API request)

## Installation and Usage

### For End-Users (Recommended)

1.  Go to the Releases page
2.  Download the latest `arc_schedule.exe` file.
3.  Run the executable. No installation is required.

## How to Build the .exe

If you want to build the executable yourself, you'll need PyInstaller.

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --noconsole --icon=app.ico src/arc_schedule.py
