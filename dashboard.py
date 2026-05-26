# ============================================================
#  dashboard.py  –  Web dashboard for the Premium Channel Bot
#  Run:  python dashboard.py
#  Then open:  http://localhost:5000
# ============================================================

from flask import Flask, jsonify, render_template, request, abort
from datetime import datetime, timedelta
import sqlite3
import os
import config

app = Flask(__name__)

DASHBOARD_TOKEN = os.environ.get("DASHBOARD_TOKEN", "admin1234")


def get_conn():
    conn = sqlite3.connect(config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def require_auth():
    token = request.headers.get("X-Dashboard-Token") or request.args.get("token")
    if token != DASHBOARD_TOKEN:
        abort(401)


@app.route("/api/overview")
def api_overview():
    require_auth()
    conn = get_conn()
    now  = datetime.now().isoformat()

    total   = conn.execute("SELECT COUNT(*) FROM subscribers").fetchone()[0]
    active  = conn.execute(
        "SELECT COUNT(*) FROM subscribers WHERE is_active=1 AND expiry_date > ?", (now,)
    ).fetchone()[0]
    expired = total - active

    rev_today = conn.execute(
        "SELECT COALESCE(SUM(amount),0) FROM payments WHERE paid_at >= ?",
        (datetime.now().date().isoformat(),)
    ).fetchone()[0]

    rev_week = conn.execute(
        "SELECT COALESCE(SUM(amount),0) FROM payments WHERE paid_at >= ?",
        ((datetime.now() - timedelta(days=7)).isoformat(),)
    ).fetchone()[0]

    rev_month = conn.execute(
        "SELECT COALESCE(SUM(amount),0) FROM payments WHERE paid_at >= ?",
        (datetime.now().replace(day=1).date().isoformat(),)
    ).fetchone()[0]

    total_payments = conn.execute("SELECT COUNT(*) FROM payments").fetchone()[0]

    new_today = conn.execute(
        "SELECT COUNT(*) FROM subscribers WHERE subscribed_at >= ?",
        (datetime.now().date().isoformat(),)
    ).fetchone()[0]

    expiring_soon = conn.execute("""
        SELECT COUNT(*) FROM subscribers
        WHERE is_active=1
          AND expiry_date > ?
          AND expiry_date <= ?
    """, (now, (datetime.now() + timedelta(hours=24)).isoformat())).fetchone()[0]

    conn.close()
    return jsonify({
        "total_subscribers":  total,
        "active_subscribers": active,
        "expired_subscribers": expired,
        "new_today":          new_today,
        "expiring_soon":      expiring_soon,
        "total_payments":     total_payments,
        "revenue_today":      rev_today,
        "revenue_week":       rev_week,
        "revenue_month":      rev_month,
    })


@app.route("/api/plan-breakdown")
def api_plan_breakdown():
    require_auth()
    conn = get_conn()
    now  = datetime.now().isoformat()
    rows = conn.execute("""
        SELECT plan, COUNT(*) as count,
               SUM(CASE WHEN is_active=1 AND expiry_date > ? THEN 1 ELSE 0 END) as active_count
        FROM subscribers GROUP BY plan
    """, (now,)).fetchall()
    conn.close()
    result = []
    for r in rows:
        plan_cfg = config.PLANS.get(r["plan"], {})
        result.append({
            "plan":   r["plan"],
            "label":  plan_cfg.get("label", r["plan"]),
            "emoji":  plan_cfg.get("emoji", "📋"),
            "price":  plan_cfg.get("price", 0),
            "total":  r["count"],
            "active": r["active_count"],
        })
    return jsonify(result)


@app.route("/api/revenue-chart")
def api_revenue_chart():
    require_auth()
    conn = get_conn()
    days = int(request.args.get("days", 14))
    labels, values = [], []
    for i in range(days - 1, -1, -1):
        day = (datetime.now() - timedelta(days=i)).date()
        rev = conn.execute(
            "SELECT COALESCE(SUM(amount),0) FROM payments WHERE DATE(paid_at)=?",
            (day.isoformat(),)
        ).fetchone()[0]
        labels.append(day.strftime("%d %b"))
        values.append(rev)
    conn.close()
    return jsonify({"labels": labels, "values": values})


@app.route("/api/subscribers-chart")
def api_subscribers_chart():
    require_auth()
    conn = get_conn()
    days = int(request.args.get("days", 14))
    labels, values = [], []
    for i in range(days - 1, -1, -1):
        day = (datetime.now() - timedelta(days=i)).date()
        cnt = conn.execute(
            "SELECT COUNT(*) FROM subscribers WHERE DATE(subscribed_at)=?",
            (day.isoformat(),)
        ).fetchone()[0]
        labels.append(day.strftime("%d %b"))
        values.append(cnt)
    conn.close()
    return jsonify({"labels": labels, "values": values})


@app.route("/api/recent-subscribers")
def api_recent_subscribers():
    require_auth()
    conn  = get_conn()
    limit = int(request.args.get("limit", 20))
    rows  = conn.execute("""
        SELECT s.user_id, s.first_name, s.username, s.plan,
               s.amount_paid, s.subscribed_at, s.expiry_date, s.is_active,
               p.mpesa_code
        FROM subscribers s
        LEFT JOIN payments p ON p.user_id = s.user_id
        ORDER BY s.subscribed_at DESC LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    result = []
    for r in rows:
        expiry    = datetime.fromisoformat(r["expiry_date"])
        days_left = (expiry - datetime.now()).days
        plan_cfg  = config.PLANS.get(r["plan"], {})
        result.append({
            "user_id":   r["user_id"],
            "name":      r["first_name"],
            "username":  f"@{r['username']}" if r["username"] else "—",
            "plan":      plan_cfg.get("label", r["plan"]),
            "emoji":     plan_cfg.get("emoji", "📋"),
            "amount":    r["amount_paid"],
            "paid_at":   r["subscribed_at"][:10],
            "expires":   expiry.strftime("%d %b %Y"),
            "days_left": days_left,
            "status":    "active" if r["is_active"] and days_left >= 0 else "expired",
            "mpesa":     r["mpesa_code"] or "—",
        })
    return jsonify(result)


@app.route("/api/recent-payments")
def api_recent_payments():
    require_auth()
    conn  = get_conn()
    limit = int(request.args.get("limit", 20))
    rows  = conn.execute("""
        SELECT p.*, s.first_name, s.username
        FROM payments p
        LEFT JOIN subscribers s ON s.user_id = p.user_id
        ORDER BY p.paid_at DESC LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    result = []
    for r in rows:
        plan_cfg = config.PLANS.get(r["plan"], {})
        result.append({
            "id":      r["id"],
            "name":    r["first_name"] or "Unknown",
            "username":f"@{r['username']}" if r["username"] else "—",
            "plan":    plan_cfg.get("label", r["plan"]),
            "emoji":   plan_cfg.get("emoji", "📋"),
            "amount":  r["amount"],
            "phone":   r["phone"],
            "mpesa":   r["mpesa_code"] or "—",
            "paid_at": r["paid_at"][:16].replace("T", " "),
        })
    return jsonify(result)


@app.route("/")
def dashboard():
    token = request.args.get("token", DASHBOARD_TOKEN)
    return render_template("dashboard.html", token=token)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
