from dataclasses import dataclass
from typing import Optional, List
import db


@dataclass
class Room:
    id: Optional[int]
    number: str
    type: str
    price: float
    available: bool
    notes: Optional[str]


def add_room(number: str, room_type: str, price: float, available: bool = True, notes: Optional[str] = None) -> Room:
    conn = db.get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO rooms (number, type, price, available, notes) VALUES (?, ?, ?, ?, ?)",
        (number, room_type, price, 1 if available else 0, notes),
    )
    conn.commit()
    room_id = cur.lastrowid
    conn.close()
    return Room(room_id, number, room_type, price, available, notes)


def get_room_by_number(number: str) -> Optional[Room]:
    conn = db.get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM rooms WHERE number = ?", (number,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return Room(row["id"], row["number"], row["type"], row["price"], bool(row["available"]), row["notes"])


def list_rooms() -> List[Room]:
    conn = db.get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM rooms ORDER BY number")
    rows = cur.fetchall()
    conn.close()
    return [Room(r["id"], r["number"], r["type"], r["price"], bool(r["available"]), r["notes"]) for r in rows]


def update_room(number: str, **fields) -> Optional[Room]:
    allowed = {"type", "price", "available", "notes"}
    set_parts = []
    params = []
    for k, v in fields.items():
        if k not in allowed:
            continue
        if k == "available":
            v = 1 if v else 0
        set_parts.append(f"{k} = ?")
        params.append(v)
    if not set_parts:
        return get_room_by_number(number)
    params.append(number)
    conn = db.get_conn()
    cur = conn.cursor()
    cur.execute(f"UPDATE rooms SET {', '.join(set_parts)} WHERE number = ?", params)
    conn.commit()
    conn.close()
    return get_room_by_number(number)


def delete_room(number: str) -> bool:
    conn = db.get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM rooms WHERE number = ?", (number,))
    changed = cur.rowcount
    conn.commit()
    conn.close()
    return changed > 0


def set_availability(number: str, available: bool) -> Optional[Room]:
    return update_room(number, available=available)


def list_by_type(room_type: str) -> List[Room]:
    conn = db.get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM rooms WHERE type = ? ORDER BY number", (room_type,))
    rows = cur.fetchall()
    conn.close()
    return [Room(r["id"], r["number"], r["type"], r["price"], bool(r["available"]), r["notes"]) for r in rows]
