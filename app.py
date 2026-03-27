import os
import requests
from flask import Flask, render_template_string

app = Flask(__name__)

API_KEY = os.environ.get("TM_API_KEY", "")

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>UniEvent - University Events</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f4f6f8; margin: 0; padding: 20px; }
        h1 { background: #003366; color: white; padding: 20px; margin: -20px -20px 20px -20px; }
        .event { background: white; border-radius: 8px; padding: 15px; margin-bottom: 15px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); overflow: auto; }
        .event img { width: 180px; float: right; margin-left: 15px; border-radius: 6px; }
        .event h3 { margin-top: 0; color: #003366; }
        .meta { color: #555; margin: 5px 0; }
    </style>
</head>
<body>
    <h1>🎓 UniEvent - University Events</h1>
    {% for event in events %}
    <div class="event">
        {% if event.image %}<img src="{{ event.image }}" alt="Event Image">{% endif %}
        <h3>{{ event.name }}</h3>
        <div class="meta">📅 {{ event.date }}</div>
        <div class="meta">📍 {{ event.venue }}</div>
        <p>{{ event.description }}</p>
    </div>
    {% endfor %}
</body>
</html>
"""

@app.route("/")
def index():
    if not API_KEY:
        return "Ticketmaster API key is missing.", 500

    url = f"https://app.ticketmaster.com/discovery/v2/events.json?apikey={API_KEY}&size=10&countryCode=US"
    events = []

    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()

        for e in data.get("_embedded", {}).get("events", []):
            venue = "TBD"
            if "_embedded" in e and "venues" in e["_embedded"] and len(e["_embedded"]["venues"]) > 0:
                venue = e["_embedded"]["venues"][0].get("name", "TBD")

            image = ""
            if e.get("images"):
                image = e["images"][0].get("url", "")

            events.append({
                "name": e.get("name", "N/A"),
                "date": e.get("dates", {}).get("start", {}).get("localDate", "TBD"),
                "venue": venue,
                "description": e.get("info", "Official university event"),
                "image": image
            })

        if not events:
            events = [{
                "name": "No events found",
                "date": "",
                "venue": "",
                "description": "The API returned no events at the moment.",
                "image": ""
            }]

    except Exception as ex:
        events = [{
            "name": "Error fetching events",
            "date": "",
            "venue": "",
            "description": str(ex),
            "image": ""
        }]

    return render_template_string(HTML, events=events)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
