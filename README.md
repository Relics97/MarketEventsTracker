# MarketEventsTracker
Hey there! This is my little Python project, MarketEventsTracker, a handy tool that pulls economic and earnings calendars into a neat window on your screen. I made it to keep an eye on what’s shaking up the markets—think big rate decisions or company earnings—without drowning in browser tabs. It’s got some cool highlighting tricks and runs in EST time, so you know exactly when stuff’s happening.

What It Does
Grabs Events: Snags economic stuff (like Fed announcements) and earnings reports for the week.
Sorts Them Out: Labels things as “Event” (most stuff), “Holiday” (like bank closures), “Earnings”, or “Other” if it’s weird.
Highlights the Big Stuff:
Red Rows: High-impact events that could rock the market—think “High Volatility Expected”—no matter when they are.
Yellow Rows: Stuff happening right now or in the next hour, so you don’t miss it (only if it’s not red).
EST Time: Keeps everything in Eastern Standard Time (UTC-5, no daylight savings mess).
Updates Live: Checks the time every minute to keep those highlights fresh.
Simple Window: Shows it all in a clean table with a filter for “Yesterday”, “Today”, “Tomorrow”, or “This Week”.
Why I Made It
I wanted something quick to see what’s coming up in the markets without digging through websites. The red and yellow highlights are my way of saying, “Hey, pay attention to this!” It’s not fancy, but it gets the job done.

How to Use It
Get Python: You’ll need Python 3 on your computer (I use 3.9, but newer should work).
Grab the Code: Download Investingbot.py from this repo.
Install Some Stuff: Open a terminal (like PowerShell or CMD) where the file is and run:
bash

Collapse

Wrap

Copy
pip install investpy pandas requests beautifulsoup4 pytz
Run It: Fire it up with:
bash

Collapse

Wrap

Copy
python Investingbot.py
Play Around: A window pops up—click the filter to switch days, hit “Refresh” if you want the latest scoop.
What You’ll See
A table with columns: Date, Time, Country Code (like “US” or “CA”), Event, Impact, and Type.
Red rows for the big, market-moving events.
Yellow rows for what’s up next in the hour (EST time).
A clock at the top ticking in EST.
Heads Up
Internet Needed: It pulls data live from investpy and Investing.com.
Earnings Glitches: Sometimes the earnings part doesn’t grab anything—website quirks, you know?
Logs: You’ll see some chatter in the terminal about what’s happening—helps if something’s off.
Want to Tweak It?
Go for it! Fork this repo, mess with the code, and let me know what you come up with. Maybe add more event types or switch the timezone—whatever vibes with you.

Thanks For Checking It Out!
- Relics97
