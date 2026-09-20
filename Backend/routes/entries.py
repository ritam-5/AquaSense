from datetime import date as ddate

from flask import Blueprint, jsonify, request

from data import store
from utils.classify import classify, retrieve_tip
from utils.forecast import day_total, forecast_month_total, month_total

entries_bp = Blueprint("entries", __name__)

VALID_ACTIVITIES = ["laundry", "bathing", "cooking", "cleaning", "gardening", "other"]


# GET /api/entries — list all logged readings, most recent first
@entries_bp.route("/", methods=["GET"])
def list_entries():
    entries = store.read_all()
    sorted_entries = sorted(entries, key=lambda e: e["date"], reverse=True)
    return jsonify({"entries": sorted_entries})


# POST /api/entries — log a new reading, returns classification + a retrieved tip
# body: { "activity": ..., "litres": ..., "date": optional }
@entries_bp.route("/", methods=["POST"])
def add_entry():
    body = request.get_json(silent=True) or {}
    activity = body.get("activity")
    litres_raw = body.get("litres")
    date = body.get("date")

    if not activity or activity not in VALID_ACTIVITIES:
        return jsonify({"error": f"activity must be one of: {', '.join(VALID_ACTIVITIES)}"}), 400

    try:
        litres = float(litres_raw)
    except (TypeError, ValueError):
        litres = 0
    if not litres or litres <= 0:
        return jsonify({"error": "litres must be a positive number"}), 400

    entries = store.read_all()
    result = classify(entries, activity, litres)
    entry = {"date": date or ddate.today().isoformat(), "activity": activity, "litres": litres}
    store.add_entry(entry)

    tip = retrieve_tip(activity, result["level"])
    updated = store.read_all()

    return jsonify({
        "entry": entry,
        "classification": result,
        "tip": tip,
        "stats": {
            "today": day_total(updated),
            "month": month_total(updated),
            "forecast": forecast_month_total(updated),
        },
    }), 201


# DELETE /api/entries — clear all logged data
@entries_bp.route("/", methods=["DELETE"])
def clear_entries():
    store.clear_all()
    return jsonify({"cleared": True})
