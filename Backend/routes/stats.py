import random
from datetime import date as ddate, timedelta

from flask import Blueprint, jsonify, request

from data import store
from utils.classify import retrieve_tip
from utils.forecast import day_total, forecast_month_total, month_total

stats_bp = Blueprint("stats", __name__)


# GET /api/stats — today / this month / last month / forecast totals
@stats_bp.route("/stats", methods=["GET"])
def stats():
    entries = store.read_all()
    now = ddate.today()
    if now.month == 1:
        last_month_ref = ddate(now.year - 1, 12, 1)
    else:
        last_month_ref = ddate(now.year, now.month - 1, 1)

    return jsonify({
        "today": day_total(entries, now),
        "month": month_total(entries, now),
        "lastMonth": month_total(entries, last_month_ref),
        "forecast": forecast_month_total(entries, now),
    })


# GET /api/tips?activity=laundry&level=high — retrieval-augmented tip lookup
@stats_bp.route("/tips", methods=["GET"])
def tips():
    activity = request.args.get("activity", "general")
    level = request.args.get("level", "normal")
    return jsonify({"tip": retrieve_tip(activity, level)})


# POST /api/seed — load 30 days of demo data (for quick evaluation / demos)
@stats_bp.route("/seed", methods=["POST"])
def seed():
    acts = ["laundry", "bathing", "cooking", "cleaning", "gardening"]
    base = {"laundry": 35, "bathing": 55, "cooking": 20, "cleaning": 25, "gardening": 30}
    today = ddate.today()
    demo = []

    for d in range(29, -1, -1):
        day = today - timedelta(days=d)
        for a in acts:
            if random.random() < 0.55:
                litres = base[a] * (0.75 + random.random() * 0.5)
                if d == 3 and a == "laundry":
                    litres = base[a] * 1.8  # one intentional anomaly
                demo.append({"date": day.isoformat(), "activity": a, "litres": round(litres)})

    store.write_all(demo)
    return jsonify({"seeded": len(demo)})
