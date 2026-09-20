"""
Curated knowledge base used for retrieval-augmented tip generation.
Each entry is tagged by activity and by the severity level it best
answers ("high" = overuse/possible leak, "low" = good behaviour,
"normal" = general best practice).

retrieve_tip() in utils/classify.py does the lexical retrieval over
this list — swap this file out for a vector-store lookup later
without touching any of the calling code.
"""

KB = [
    {"tags": ["laundry"], "severity": "high",
     "text": "A running tap left on for 5 minutes can waste ~50L. Pre-soak clothes and shut the tap between rinses — this alone can cut laundry use by up to 30%."},
    {"tags": ["laundry"], "severity": "normal",
     "text": "Run washing machines only with a full load — half-loads use nearly the same water per kg of clothing."},
    {"tags": ["bathing"], "severity": "high",
     "text": "Switching from a bucket-and-mug to a low-flow showerhead, or timing showers to under 5 minutes, can cut bathing water use by 40%."},
    {"tags": ["bathing"], "severity": "normal",
     "text": "Turn the tap off while soaping or shampooing instead of letting it run."},
    {"tags": ["cooking"], "severity": "high",
     "text": "Rinsing vegetables under a running tap wastes far more water than washing them in a filled basin — try the basin method."},
    {"tags": ["cooking"], "severity": "normal",
     "text": "Reuse water used to rinse rice or vegetables to water plants instead of pouring it away."},
    {"tags": ["cleaning"], "severity": "high",
     "text": "Hosing down floors or vehicles with an open pipe can use 100+ litres in minutes. A bucket-and-mop approach uses a fraction of that."},
    {"tags": ["cleaning"], "severity": "normal",
     "text": "Sweep dry debris before mopping — less water is needed for the final clean."},
    {"tags": ["gardening"], "severity": "high",
     "text": "Watering during midday loses much of the water to evaporation. Water early morning or evening, and check for a stuck sprinkler valve if usage spiked."},
    {"tags": ["gardening"], "severity": "normal",
     "text": "Mulching garden beds reduces how often you need to water by retaining soil moisture."},
    {"tags": ["other", "general"], "severity": "normal",
     "text": "A dripping tap can waste over 15 litres a day — a quick washer replacement often pays for itself within a week."},
    {"tags": ["general"], "severity": "low",
     "text": "Great trend — usage below your usual baseline. Keep track of what changed this period so the habit sticks."},
]
