import tkinter as tk
from tkinter import ttk
import investpy
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import logging
import pytz

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Country-to-code mapping (ISO 3166-1 alpha-2)
country_codes = {
    "united states": "US",
    "United States": "US",
    "euro zone": "EU",
    "Euro Zone": "EU",
    "united kingdom": "GB",
    "United Kingdom": "GB",
    "japan": "JP",
    "Japan": "JP",
    "germany": "DE",
    "Germany": "DE",
    "france": "FR",
    "France": "FR",
    "china": "CN",
    "China": "CN",
    "australia": "AU",
    "Australia": "AU",
    "canada": "CA",
    "Canada": "CA",
    "new zealand": "NZ",
    "New Zealand": "NZ",
    "switzerland": "CH",
    "Switzerland": "CH",
    "italy": "IT",
    "Italy": "IT",
    "spain": "ES",
    "Spain": "ES",
    "russia": "RU",
    "Russia": "RU",
    "india": "IN",
    "India": "IN",
    "brazil": "BR",
    "Brazil": "BR",
}

# Scrape Economic Calendar with investpy
def scrape_economic_calendar(start_date, end_date):
    try:
        df = investpy.economic_calendar(from_date=start_date.strftime("%d/%m/%Y"), to_date=end_date.strftime("%d/%m/%Y"))
        event_list = []
        for _, row in df.iterrows():
            try:
                event_date = datetime.strptime(row["date"], "%d/%m/%Y")
                event_time = row["time"]
                event_title = row["event"]
                country = row["zone"] if pd.notna(row["zone"]) else "Unknown"
                code = country_codes.get(country, country_codes.get(country.capitalize(), "??"))
                importance = row["importance"] if pd.notna(row["importance"]) else "low"
                impact = {
                    "low": "Low Volatility Expected",
                    "medium": "Moderate Volatility Expected",
                    "high": "High Volatility Expected"
                }.get(importance.lower(), "Low Volatility Expected")
                if "holiday" in event_title.lower():
                    event_type = "Holiday"
                elif pd.isna(row["importance"]) or pd.isna(row["event"]):
                    event_type = "Other"
                else:
                    event_type = "Event"
                event_list.append((event_date, event_time, event_title, impact, event_type, code))
            except Exception as e:
                logging.warning(f"Error parsing economic event: {e}")
                continue
        logging.info(f"Scraped {len(event_list)} economic calendar events")
        return event_list
    except Exception as e:
        logging.error(f"Failed to scrape economic calendar with investpy: {e}")
        return []

# Scrape Earnings with requests
def scrape_earnings_calendar(start_date, end_date):
    url = "https://www.investing.com/earnings-calendar/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        events = soup.select("tr.js-earnings-row")
        event_list = []
        for event in events:
            try:
                event_date_str = event.get("data-earnings-date", "")
                if not event_date_str:
                    continue
                event_date = datetime.strptime(event_date_str[:10], "%Y-%m-%d")
                if start_date <= event_date <= end_date:
                    event_time = "N/A"
                    event_title = event.select_one(".earningsName").text.strip()
                    country_span = event.select_one(".flag")
                    country = country_span.get("title", "Unknown") if country_span else "Unknown"
                    code = country_codes.get(country, country_codes.get(country.capitalize(), "??"))
                    impact = "Moderate Volatility Expected"
                    event_type = "Earnings"
                    event_list.append((event_date, event_time, event_title, impact, event_type, code))
            except Exception as e:
                logging.warning(f"Error parsing earnings event: {e}")
                continue
        logging.info(f"Scraped {len(event_list)} earnings events")
        return event_list
    except Exception as e:
        logging.error(f"Failed to scrape earnings calendar: {e}")
        return []

# Combine all calendars
def scrape_all_calendars():
    today = datetime.now()
    start_date = today - timedelta(days=today.weekday())
    end_date = start_date + timedelta(days=6)
    economic_events = scrape_economic_calendar(start_date, end_date)
    earnings_events = scrape_earnings_calendar(start_date, end_date)
    return economic_events + earnings_events

# Function to get date range
def get_date_range():
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    return yesterday, today, tomorrow, start_of_week, end_of_week

# Function to filter events based on timeframe
def filter_events(events, timeframe, yesterday, today, tomorrow, start_of_week, end_of_week):
    filtered = []
    for event in events:
        event_datetime = event[0]
        if timeframe == "Yesterday" and event_datetime.date() == yesterday.date():
            filtered.append(event)
        elif timeframe == "Today" and event_datetime.date() == today.date():
            filtered.append(event)
        elif timeframe == "Tomorrow" and event_datetime.date() == tomorrow.date():
            filtered.append(event)
        elif timeframe == "This Week" and start_of_week <= event_datetime <= end_of_week:
            filtered.append(event)
    return filtered

# Function to parse event time to datetime (EST, UTC-5)
def parse_event_time(event_date, event_time_str):
    est = pytz.FixedOffset(-300)  # EST is UTC-5, no DST
    if event_time_str == "N/A" or not event_time_str or event_time_str == "All Day":
        logging.debug(f"Defaulting {event_date} {event_time_str} to midnight EST")
        return event_date.replace(hour=0, minute=0, tzinfo=est)
    try:
        event_time = datetime.strptime(event_time_str, "%H:%M").time()
        full_time = datetime.combine(event_date, event_time).replace(tzinfo=est)
        logging.debug(f"Parsed {event_date} {event_time_str} to {full_time}")
        return full_time
    except ValueError as e:
        logging.warning(f"Failed to parse time '{event_time_str}': {e}")
        return event_date.replace(hour=0, minute=0, tzinfo=est)

# Function to update Treeview with filtered events and highlight
def update_tree(tree, events, timeframe, yesterday, today, tomorrow, start_of_week, end_of_week):
    tree.delete(*tree.get_children())
    est = pytz.FixedOffset(-300)  # EST
    now = datetime.now(est)
    one_hour_later = now + timedelta(hours=1)
    logging.info(f"Highlight window: {now.strftime('%H:%M')} to {one_hour_later.strftime('%H:%M')} EST")
    
    filtered_events = filter_events(events, timeframe, yesterday, today, tomorrow, start_of_week, end_of_week)
    for event_datetime, event_time, event_title, impact, event_type, code in filtered_events:
        date_str = event_datetime.strftime("%Y-%m-%d")
        event_full_time = parse_event_time(event_datetime, event_time)
        iid = tree.insert("", tk.END, values=(date_str, event_time, code, event_title, impact, event_type))
        if impact == "High Volatility Expected":
            logging.info(f"Critical event: {date_str} {event_time} - {event_title}")
            tree.item(iid, tags=("critical",))
        elif now <= event_full_time <= one_hour_later:
            logging.info(f"Highlighting: {date_str} {event_time} - {event_title}")
            tree.item(iid, tags=("highlight",))
    
    tree.tag_configure("critical", background="#FF9999")  # Red for critical
    tree.tag_configure("highlight", background="#FFFF99")  # Yellow for next hour

# Function to update market time and highlights
def update_market_time(label, tree, events, timeframe, yesterday, today, tomorrow, start_of_week, end_of_week):
    est = pytz.FixedOffset(-300)  # EST
    now = datetime.now(est)
    time_str = now.strftime("Market Time (EST): %Y-%m-%d %H:%M")
    label.config(text=time_str)
    update_tree(tree, events, timeframe, yesterday, today, tomorrow, start_of_week, end_of_week)
    label.after(60000, update_market_time, label, tree, events, timeframe, yesterday, today, tomorrow, start_of_week, end_of_week)

# Function to display events in GUI
def display_calendar():
    yesterday, today, tomorrow, start_of_week, end_of_week = get_date_range()
    events = scrape_all_calendars()
    
    root = tk.Tk()
    root.title("InvestingBot Calendar")
    root.geometry("1000x700")
    
    filter_frame = tk.Frame(root)
    filter_frame.pack(pady=5, anchor="nw")
    
    market_time_label = tk.Label(filter_frame, text="", font=("Arial", 10))
    market_time_label.pack(side=tk.LEFT, padx=5)
    
    tk.Label(filter_frame, text="Filter by:").pack(side=tk.LEFT, padx=5)
    timeframe_var = tk.StringVar(value="Today")
    timeframe_options = ["Yesterday", "Today", "Tomorrow", "This Week"]
    timeframe_menu = tk.OptionMenu(filter_frame, timeframe_var, *timeframe_options)
    timeframe_menu.pack(side=tk.LEFT, padx=5)
    
    tree = ttk.Treeview(root, columns=("Date", "Time", "Code", "Event", "Impact", "Type"), show="headings")
    tree.heading("Date", text="Date")
    tree.heading("Time", text="Time")
    tree.heading("Code", text="CC")
    tree.heading("Event", text="Event")
    tree.heading("Impact", text="Impact")
    tree.heading("Type", text="Type")
    tree.column("Date", width=100)
    tree.column("Time", width=80)
    tree.column("Code", width=30)
    tree.column("Event", width=350)
    tree.column("Impact", width=150)
    tree.column("Type", width=100)
    tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    
    style = ttk.Style()
    style.configure("Treeview", rowheight=25)
    
    if events:
        events.sort(key=lambda x: (x[0], x[1]))
        update_tree(tree, events, timeframe_var.get(), yesterday, today, tomorrow, start_of_week, end_of_week)
        update_market_time(market_time_label, tree, events, timeframe_var.get(), yesterday, today, tomorrow, start_of_week, end_of_week)
    else:
        tree.insert("", tk.END, values=("N/A", "N/A", "??", "No events scraped. Check logs or network.", "N/A", "Error"))
    
    def on_filter_change(*args):
        update_tree(tree, events, timeframe_var.get(), yesterday, today, tomorrow, start_of_week, end_of_week)
    
    timeframe_var.trace("w", on_filter_change)
    
    refresh_button = tk.Button(root, text="Refresh", command=lambda: refresh_tree(tree, events, timeframe_var, yesterday, today, tomorrow, start_of_week, end_of_week))
    refresh_button.pack(pady=5)
    
    root.mainloop()

# Function to refresh the Treeview
def refresh_tree(tree, events, timeframe_var, yesterday, today, tomorrow, start_of_week, end_of_week):
    new_events = scrape_all_calendars()
    if new_events:
        events.clear()
        events.extend(new_events)
        events.sort(key=lambda x: (x[0], x[1]))
    update_tree(tree, events, timeframe_var.get(), yesterday, today, tomorrow, start_of_week, end_of_week)

# Main execution
if __name__ == "__main__":
    display_calendar()