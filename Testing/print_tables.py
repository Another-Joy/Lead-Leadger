#!/usr/bin/env python3
"""
print_tables.py

Dumps all tables from the playtest database into a formatted text file.
Includes table structure and contents.
"""

import sqlite3
from datetime import datetime

DB_PATH = "playtest_history.sqlite3"
OUTPUT_FILE = f"db_dump_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

def connect():
    return sqlite3.connect(DB_PATH)

def get_table_names(conn):
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    return [row[0] for row in cur.fetchall()]

def get_table_info(conn, table_name):
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table_name})")
    return cur.fetchall()

def get_table_contents(conn, table_name):
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table_name}")
    return cur.fetchall()

def format_value(value):
    if value is None:
        return "NULL"
    elif isinstance(value, bool):
        return "1" if value else "0"
    else:
        return str(value)

def main():
    conn = connect()
    tables = get_table_names(conn)
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(f"Database Dump - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        
        for table in tables:
            # Write table header
            f.write(f"Table: {table}\n")
            f.write("-" * 80 + "\n")
            
            # Get and write column info
            columns = get_table_info(conn, table)
            f.write("\nStructure:\n")
            for col in columns:
                col_id, name, type_, notnull, default, pk = col
                constraints = []
                if pk:
                    constraints.append("PRIMARY KEY")
                if notnull:
                    constraints.append("NOT NULL")
                if default is not None:
                    constraints.append(f"DEFAULT {default}")
                
                constraint_str = " ".join(constraints)
                f.write(f"  {name:15} {type_:10} {constraint_str}\n")
            
            # Get and write table contents
            rows = get_table_contents(conn, table)
            f.write(f"\nContents ({len(rows)} rows):\n")
            
            if rows:
                # Write column headers
                headers = [col[1] for col in columns]  # col[1] is column name
                f.write("  " + " | ".join(f"{h:15}" for h in headers) + "\n")
                f.write("  " + "-" * (17 * len(headers)) + "\n")
                
                # Write data rows
                for row in rows:
                    formatted_values = [format_value(val) for val in row]
                    f.write("  " + " | ".join(f"{val:15}" for val in formatted_values) + "\n")
            
            f.write("\n\n")
    
    conn.close()
    print(f"Database dump written to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()