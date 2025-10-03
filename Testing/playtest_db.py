#!/usr/bin/env python3
"""
playtest_db.py

Lightweight playtest history manager using SQLite (local file).
No hosting required.

Features:
- Sessions (date, version, notes)
- Players (2 per session)
- Actions (session, player, type, notes)
- ActionParticipants (primary and secondary participants)
- Tags (many-to-many via ActionTags)
- Querying and basic stats

Run as a script to exercise demo usage at bottom.
"""

import sqlite3
import datetime
import csv
from collections import Counter
from typing import List, Optional, Iterable, Tuple, Dict, Any

DB_PATH = "playtest_history.sqlite3"


def connect(db_path=DB_PATH):
    return sqlite3.connect(db_path)


def clear_db(conn: sqlite3.Connection):
    """Drops all user tables from the database."""
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = OFF;")
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT IN ('sqlite_sequence');")
    tables = c.fetchall()
    for table in tables:
        c.execute(f"DROP TABLE IF EXISTS {table[0]};")
    conn.commit()
    c.execute("PRAGMA foreign_keys = ON;")

def init_db(conn: sqlite3.Connection):
    c = conn.cursor()
    # Enable foreign keys
    c.execute("PRAGMA foreign_keys = ON;")

    # Sessions
    c.execute("""
    CREATE TABLE IF NOT EXISTS Sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        version TEXT NOT NULL,
        notes TEXT
    );
    """)

    # Players
    c.execute("""
    CREATE TABLE IF NOT EXISTS Players (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    );
    """)

    # SessionPlayers junction table
    c.execute("""
    CREATE TABLE IF NOT EXISTS SessionPlayers (
        session_id INTEGER NOT NULL REFERENCES Sessions(id) ON DELETE CASCADE,
        player_id INTEGER NOT NULL REFERENCES Players(id) ON DELETE CASCADE,
        PRIMARY KEY(session_id, player_id)
    );
    """)

    # Actions
    c.execute("""
    CREATE TABLE IF NOT EXISTS Actions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL REFERENCES Sessions(id) ON DELETE CASCADE,
        player_id INTEGER REFERENCES Players(id),
        type TEXT,
        notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Action participants (flexible: unit names, tile ids, free text)
    c.execute("""
    CREATE TABLE IF NOT EXISTS ActionParticipants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action_id INTEGER NOT NULL REFERENCES Actions(id) ON DELETE CASCADE,
        is_primary BOOLEAN NOT NULL,  -- True for primary participant, False for secondary
        name_text TEXT NOT NULL       -- e.g. "Unit A" or "Tile 5"
    );
    """)

    # Tags table + junction
    c.execute("""
    CREATE TABLE IF NOT EXISTS Tags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    );
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS ActionTags (
        action_id INTEGER NOT NULL REFERENCES Actions(id) ON DELETE CASCADE,
        tag_id INTEGER NOT NULL REFERENCES Tags(id) ON DELETE CASCADE,
        PRIMARY KEY(action_id, tag_id)
    );
    """)

    conn.commit()


# CRUD helpers

def add_session(conn: sqlite3.Connection, version: str, player1_name: str, player2_name: str, date: Optional[str] = None, notes: Optional[str] = None) -> int:
    date = date or datetime.date.today().isoformat()
    cur = conn.cursor()
    cur.execute("INSERT INTO Sessions (date, version, notes) VALUES (?, ?, ?)", (date, version, notes))
    session_id = cur.lastrowid

    # Add players to session
    player1_id = add_player(conn, player1_name)
    player2_id = add_player(conn, player2_name)
    
    cur.executemany("INSERT INTO SessionPlayers (session_id, player_id) VALUES (?, ?)",
                    [(session_id, player1_id), (session_id, player2_id)])
    
    conn.commit()
    return session_id


def add_player(conn: sqlite3.Connection, name: str) -> int:
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO Players (name) VALUES (?)", (name,))
        conn.commit()
        return cur.lastrowid
    except sqlite3.IntegrityError:
        # player exists, return existing id
        cur.execute("SELECT id FROM Players WHERE name = ?", (name,))
        r = cur.fetchone()
        return r[0]


def get_session_players(conn: sqlite3.Connection, session_id: int) -> List[Tuple[int, str]]:
    """Returns list of (player_id, player_name) tuples for a session"""
    cur = conn.cursor()
    cur.execute("""
        SELECT p.id, p.name 
        FROM Players p 
        JOIN SessionPlayers sp ON sp.player_id = p.id 
        WHERE sp.session_id = ?
    """, (session_id,))
    return cur.fetchall()

def find_player_id(conn: sqlite3.Connection, name: str) -> Optional[int]:
    cur = conn.cursor()
    cur.execute("SELECT id FROM Players WHERE name = ?", (name,))
    r = cur.fetchone()
    return r[0] if r else None


def ensure_tag(conn: sqlite3.Connection, tag_name: str) -> int:
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO Tags (name) VALUES (?)", (tag_name,))
        conn.commit()
        return cur.lastrowid
    except sqlite3.IntegrityError:
        cur.execute("SELECT id FROM Tags WHERE name = ?", (tag_name,))
        return cur.fetchone()[0]


def add_action(conn: sqlite3.Connection,
               session_id: int,
               player_name: Optional[str],
               type: Optional[str],
               notes: Optional[str],
               primary_participant: Optional[str] = None,
               secondary_participants: Optional[List[str]] = None,
               tags: Optional[Iterable[str]] = None) -> int:
    """
    Add an action with optional primary and secondary participants.
    
    Args:
        primary_participant: The main unit/tile involved in the action
        secondary_participants: List of additional units/tiles involved
        tags: List of tag strings
    """
    cur = conn.cursor()
    
    # Get player id
    player_id = None
    if player_name:
        cur.execute("SELECT id FROM Players WHERE name = ?", (player_name,))
        player = cur.fetchone()
        if not player:
            raise ValueError(f"Player {player_name} not found in session {session_id}")
        player_id = player[0]
    
    # Create action
    cur.execute(
        "INSERT INTO Actions (session_id, player_id, type, notes) VALUES (?, ?, ?, ?)",
        (session_id, player_id, type, notes)
    )
    action_id = cur.lastrowid

    # Add primary participant if provided
    if primary_participant:
        cur.execute(
            "INSERT INTO ActionParticipants (action_id, is_primary, name_text) VALUES (?, ?, ?)",
            (action_id, True, primary_participant)
        )
    
    # Add secondary participants if provided
    if secondary_participants:
        cur.executemany(
            "INSERT INTO ActionParticipants (action_id, is_primary, name_text) VALUES (?, ?, ?)",
            [(action_id, False, name) for name in secondary_participants]
        )

    if tags:
        for t in tags:
            tag_id = ensure_tag(conn, t)
            try:
                cur.execute("INSERT INTO ActionTags (action_id, tag_id) VALUES (?, ?)", (action_id, tag_id))
            except sqlite3.IntegrityError:
                pass

    conn.commit()
    return action_id


# Query / filter helpers

def actions_for_session(conn: sqlite3.Connection, session_id: int) -> List[Dict[str, Any]]:
    cur = conn.cursor()
    cur.execute("""
    SELECT a.id, p.name as player_name, a.type, a.notes
    FROM Actions a
    LEFT JOIN Players p ON p.id = a.player_id
    WHERE a.session_id = ?
    ORDER BY a.id ASC
    """, (session_id,))
    rows = cur.fetchall()
    actions = []
    for r in rows:
        aid = r[0]
        # Get participants
        cur.execute("""
            SELECT is_primary, name_text 
            FROM ActionParticipants 
            WHERE action_id = ?
            ORDER BY is_primary DESC, id ASC
        """, (aid,))
        participants = cur.fetchall()
        
        # Split into primary and secondary
        primary = next((p[1] for p in participants if p[0]), None)
        secondary = [p[1] for p in participants if not p[0]]
        
        # Get tags
        cur.execute("""
            SELECT t.name 
            FROM Tags t 
            JOIN ActionTags at ON t.id = at.tag_id 
            WHERE at.action_id = ?
        """, (aid,))
        tags = [t[0] for t in cur.fetchall()]
        
        actions.append({
            "id": aid,
            "player": r[1],
            "type": r[2],
            "notes": r[3],
            "primary_participant": primary,
            "secondary_participants": secondary,
            "tags": tags
        })
    return actions


def actions_filter(conn: sqlite3.Connection,
                   session_id: Optional[int] = None,
                   player_name: Optional[str] = None,
                   action_type: Optional[str] = None,
                   tag: Optional[str] = None,
                   participant_name: Optional[str] = None,
                   version: Optional[str] = None
                   ) -> List[Dict[str, Any]]:
    """
    Flexible ad-hoc filter. Any argument can be None (ignored).
    participant_name matches ActionParticipants.name_text (substring match).
    """
    cur = conn.cursor()
    params = []
    where_clauses = []

    if session_id is not None:
        where_clauses.append("a.session_id = ?")
        params.append(session_id)

    if player_name is not None:
        where_clauses.append("p.name = ?")
        params.append(player_name)

    if action_type is not None:
        where_clauses.append("a.type = ?")
        params.append(action_type)

    if tag is not None:
        where_clauses.append("t.name = ?")
        params.append(tag)

    if participant_name is not None:
        where_clauses.append("ap.name_text LIKE ?")
        params.append(f"%{participant_name}%")

    if version is not None:
        where_clauses.append("s.version = ?")
        params.append(version)

    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
    query = f"""
    SELECT a.id, a.turn_order, p.name as player_name, a.type, a.notes, s.version
    FROM Actions a
    LEFT JOIN Players p ON p.id = a.player_id
    LEFT JOIN Sessions s ON s.id = a.session_id
    LEFT JOIN ActionTags at ON at.action_id = a.id
    LEFT JOIN Tags t ON t.id = at.tag_id
    LEFT JOIN ActionParticipants ap ON ap.action_id = a.id
    {where_sql}
    GROUP BY a.id
    ORDER BY a.turn_order ASC, a.id ASC
    """
    cur.execute(query, params)
    rows = cur.fetchall()
    # reuse actions_for_session-like population
    results = []
    for r in rows:
        aid = r[0]
        participants = cur.execute("SELECT role, name_text FROM ActionParticipants WHERE action_id = ?", (aid,)).fetchall()
        tags = cur.execute("SELECT t.name FROM Tags t JOIN ActionTags at ON t.id = at.tag_id WHERE at.action_id = ?", (aid,)).fetchall()
        results.append({
            "id": aid,
            "turn_order": r[1],
            "player": r[2],
            "type": r[3],
            "notes": r[4],
            "version": r[5],
            "participants": [{"role": pr[0], "name": pr[1]} for pr in participants],
            "tags": [t[0] for t in tags]
        })
    return results


# Stats / aggregations

def count_actions_by_participant(conn: sqlite3.Connection, participant_name: str, filter_type: Optional[str] = None) -> int:
    cur = conn.cursor()
    params = [f"%{participant_name}%"]
    sql = """
    SELECT COUNT(DISTINCT a.id)
    FROM Actions a
    JOIN ActionParticipants ap ON ap.action_id = a.id
    WHERE ap.name_text LIKE ?
    """
    if filter_type:
        sql += " AND a.type = ?"
        params.append(filter_type)
    cur.execute(sql, params)
    return cur.fetchone()[0]


def count_actions_by_type(conn: sqlite3.Connection, session_id: Optional[int] = None) -> Dict[str, int]:
    cur = conn.cursor()
    params = []
    where = ""
    if session_id:
        where = "WHERE a.session_id = ?"
        params.append(session_id)
    cur.execute(f"""
    SELECT a.type, COUNT(*) FROM Actions a
    {where}
    GROUP BY a.type
    """, params)
    return {row[0] if row[0] else "(none)": row[1] for row in cur.fetchall()}


def tag_frequency(conn: sqlite3.Connection, session_id: Optional[int] = None) -> Counter:
    cur = conn.cursor()
    params = []
    where = ""
    if session_id:
        where = "WHERE a.session_id = ?"
        params.append(session_id)
    cur.execute(f"""
    SELECT t.name, COUNT(*) FROM Tags t
    JOIN ActionTags at ON at.tag_id = t.id
    JOIN Actions a ON a.id = at.action_id
    {where}
    GROUP BY t.name
    """, params)
    return Counter({row[0]: row[1] for row in cur.fetchall()})


# Export helpers

def export_session_actions_csv(conn: sqlite3.Connection, session_id: int, out_path: str):
    actions = actions_for_session(conn, session_id)
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["action_id", "player", "type", "notes", "primary", "secondary", "tags"])
        for a in actions:
            secondary_str = ";".join(a["secondary_participants"])
            tags_str = ";".join(a["tags"])
            writer.writerow([
                a["id"], 
                a["player"], 
                a["type"], 
                a["notes"],
                a["primary_participant"] or "",
                secondary_str,
                tags_str
            ])


# Convenience demo / REPL-like functions

def demo_seed(conn: sqlite3.Connection):
    s1 = add_session(conn, "v0.9", "Alice", "Bob", "2025-09-25", "Testing economy")
    s2 = add_session(conn, "v1.0", "Bob", "Clara", "2025-09-28", "Combat rebalance")
    
    # Actions for session 1
    add_action(conn, s1, "Alice", "Move", "Moved to zone 5",
              primary_participant="A", secondary_participants=["5"], tags=["move"])
    add_action(conn, s1, "Bob", "Attack", "Attacked A",
              primary_participant="X", secondary_participants=["A"], tags=["critical"])
    add_action(conn, s1, "Clara", "Consolidate", "Merged B and C into D",
              primary_participant="D", secondary_participants=["B", "C"], tags=["uncommon"])
    
    # Session 2
    add_action(conn, s2, "Bob", "Move", "Flank",
              primary_participant="X", secondary_participants=["L"])
    add_action(conn, s2, "Alice", "Attack", "Damaged X",
              primary_participant="A", secondary_participants=["X"], tags=["hit"])
    
    conn.commit()
    return s1, s2


def print_actions_list(actions: List[Dict[str, Any]]):
    for a in actions:
        print(f"#{a['id']} [{a['type']}] by {a['player']}")
        if a['primary_participant']:
            print("  primary:", a['primary_participant'])
        if a['secondary_participants']:
            print("  secondary:", ", ".join(a['secondary_participants']))
        if a['tags']:
            print("  tags:", ", ".join(a['tags']))
        if a['notes']:
            print("  notes:", a['notes'])
        print("")


def demo_queries(conn: sqlite3.Connection):
    print("=== actions session 1 ===")
    s1 = 1
    print_actions_list(actions_for_session(conn, s1))

    print("=== how many times unit A attacked? ===")
    print(count_actions_by_participant(conn, "A", filter_type="Attack"))

    print("=== count by action type (session 1) ===")
    print(count_actions_by_type(conn, session_id=1))

    print("=== tag frequency overall ===")
    print(tag_frequency(conn))


if __name__ == "__main__":
    conn = connect()
    clear_db(conn)
    init_db(conn)
    # Demo seed only if DB empty (simple heuristic)
    """     cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM Actions")
    if cur.fetchone()[0] == 0:
        s1, s2 = demo_seed(conn)
        print("Demo data created. Sessions:", s1, s2)
"""
    # Run demo queries
    #demo_queries(conn)

    # Example export
    #export_session_actions_csv(conn, 1, "session_1_actions.csv")
    #print("Exported session 1 actions to session_1_actions.csv")

    conn.close()
