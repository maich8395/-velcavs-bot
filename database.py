# ============================================================
#  database.py  –  SQLite subscriber management
# ============================================================

import sqlite3
import logging
from datetime import datetime, timedelta
from contextlib import contextmanager
import config

logger = logging.getLogger(__name__)


@contextmanager
def get_conn():
    conn = sqlite3.connect(config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Create all tables on first run."""
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS subscribers (
                user_id        INTEGER PRIMARY KEY,
                username       TEXT,
                first_name     TEXT,
                phone          TEXT,
                plan           TEXT,
                amount_paid    INTEGER,
                subscribed_at  TEXT,
                expiry_date    TEXT,
                is_active      INTEGER DEFAULT 1,
                expiry_notified INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS payments (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id        INTEGER,
                plan           TEXT,
                amount         INTEGER,
                phone          TEXT,
                mpesa_code     TEXT,
                paid_at        TEXT,
                FOREIGN KEY(user_id) REFERENCES subscribers(user_id)
            );

            CREATE TABLE IF NOT EXISTS auto_post_log (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                posted_at  TEXT,
                channel_id TEXT
            );
        """)
    logger.info("Database initialised.")


# ─── Subscribers ─────────────────────────────────────────────

def upsert_subscriber(user_id: int, username: str, first_name: str,
                      phone: str, plan: str, amount: int, expiry: datetime):
    """Insert or update a subscriber record."""
    now = datetime.now().isoformat()
    with get_conn() as conn:
        existing = conn.execute(
            "SELECT 1 FROM subscribers WHERE user_id = ?", (user_id,)
        ).fetchone()

        if existing:
            conn.execute("""
                UPDATE subscribers SET
                    username=?, first_name=?, phone=?, plan=?,
                    amount_paid=?, subscribed_at=?, expiry_date=?,
                    is_active=1, expiry_notified=0
                WHERE user_id=?
            """, (username, first_name, phone, plan, amount, now,
                  expiry.isoformat(), user_id))
        else:
            conn.execute("""
                INSERT INTO subscribers
                    (user_id, username, first_name, phone, plan,
                     amount_paid, subscribed_at, expiry_date, is_active, expiry_notified)
                VALUES (?,?,?,?,?,?,?,?,1,0)
            """, (user_id, username, first_name, phone, plan,
                  amount, now, expiry.isoformat()))


def log_payment(user_id: int, plan: str, amount: int,
                phone: str, mpesa_code: str = "PENDING"):
    """Record a payment transaction."""
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO payments (user_id, plan, amount, phone, mpesa_code, paid_at)
            VALUES (?,?,?,?,?,?)
        """, (user_id, plan, amount, phone, mpesa_code,
              datetime.now().isoformat()))


def get_subscriber(user_id: int):
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM subscribers WHERE user_id=?", (user_id,)
        ).fetchone()


def get_active_subscriber(user_id: int):
    with get_conn() as conn:
        return conn.execute("""
            SELECT * FROM subscribers
            WHERE user_id=? AND is_active=1
              AND expiry_date > ?
        """, (user_id, datetime.now().isoformat())).fetchone()


def get_expiring_soon(hours: int = 24):
    """Return active subs expiring within `hours` hours."""
    cutoff = (datetime.now() + timedelta(hours=hours)).isoformat()
    now    = datetime.now().isoformat()
    with get_conn() as conn:
        return conn.execute("""
            SELECT * FROM subscribers
            WHERE is_active=1
              AND expiry_date <= ?
              AND expiry_date > ?
              AND expiry_notified=0
        """, (cutoff, now)).fetchall()


def get_expired_subscribers():
    """Return all subs whose time has passed and haven't been deactivated."""
    with get_conn() as conn:
        return conn.execute("""
            SELECT * FROM subscribers
            WHERE is_active=1 AND expiry_date <= ?
        """, (datetime.now().isoformat(),)).fetchall()


def deactivate_subscriber(user_id: int):
    with get_conn() as conn:
        conn.execute(
            "UPDATE subscribers SET is_active=0 WHERE user_id=?", (user_id,)
        )


def mark_expiry_notified(user_id: int):
    with get_conn() as conn:
        conn.execute(
            "UPDATE subscribers SET expiry_notified=1 WHERE user_id=?", (user_id,)
        )


# ─── Stats ───────────────────────────────────────────────────

def get_stats() -> dict:
    today = datetime.now().date().isoformat()
    month_start = datetime.now().replace(day=1).date().isoformat()

    with get_conn() as conn:
        total   = conn.execute("SELECT COUNT(*) FROM subscribers").fetchone()[0]
        active  = conn.execute(
            "SELECT COUNT(*) FROM subscribers WHERE is_active=1 AND expiry_date > ?",
            (datetime.now().isoformat(),)
        ).fetchone()[0]
        expired = total - active

        rev_today = conn.execute(
            "SELECT COALESCE(SUM(amount),0) FROM payments WHERE paid_at >= ?",
            (today,)
        ).fetchone()[0]
        rev_month = conn.execute(
            "SELECT COALESCE(SUM(amount),0) FROM payments WHERE paid_at >= ?",
            (month_start,)
        ).fetchone()[0]

        plan_breakdown = {}
        for row in conn.execute("""
            SELECT plan, COUNT(*) as cnt FROM subscribers
            WHERE is_active=1 AND expiry_date > ?
            GROUP BY plan
        """, (datetime.now().isoformat(),)):
            plan_breakdown[row['plan']] = row['cnt']

    return {
        "total":         total,
        "active":        active,
        "expired":       expired,
        "revenue_today": rev_today,
        "revenue_month": rev_month,
        "plan_breakdown": plan_breakdown,
    }
