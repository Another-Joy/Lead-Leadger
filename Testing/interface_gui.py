# interface_gui.py
import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
import datetime
from playtest_db import ensure_tag

DB_FILE = "playtest_history.sqlite3"

def init_if_needed():
    """Initialize database if it doesn't exist"""
    import playtest_db
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Sessions'")
    if not cur.fetchone():
        playtest_db.init_db(conn)
    conn.close()

def load_sessions():
    """Load and display all sessions in the sessions treeview"""
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT s.id, s.date, s.version, s.notes,
               GROUP_CONCAT(p.name, ' vs ') as players
        FROM Sessions s
        LEFT JOIN SessionPlayers sp ON sp.session_id = s.id
        LEFT JOIN Players p ON p.id = sp.player_id
        GROUP BY s.id
        ORDER BY s.date DESC
    """)
    sessions = cur.fetchall()
    conn.close()
    
    # Clear existing items
    for item in sessions_tree.get_children():
        sessions_tree.delete(item)
    
    # Insert sessions
    for session in sessions:
        sessions_tree.insert("", "end", values=session)

def get_session_players(session_id):
    """Get players for a session for the player dropdown"""
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.id, p.name 
        FROM Players p 
        JOIN SessionPlayers sp ON sp.player_id = p.id 
        WHERE sp.session_id = ?
    """, (session_id,))
    players = cur.fetchall()
    conn.close()
    return players  # Updated to match playtest_db.py

def load_sessions():
    """Load and display all sessions in the sessions treeview"""
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT id, date, version, notes FROM Sessions ORDER BY date DESC")
    sessions = cur.fetchall()
    conn.close()
    
    # Clear existing items
    for item in sessions_tree.get_children():
        sessions_tree.delete(item)
    
    # Insert sessions
    for session in sessions:
        sessions_tree.insert("", "end", values=session)

def on_session_select(event):
    """Handle session selection to show its actions"""
    selected = sessions_tree.selection()
    if not selected:
        return
    
    # Get session id from selected item
    session_id = sessions_tree.item(selected[0])['values'][0]
    
    # Use playtest_db to get full action details
    conn = connect()
    import playtest_db
    actions = playtest_db.actions_for_session(conn, session_id)
    
    # Update player dropdown with session players
    players = playtest_db.get_session_players(conn, session_id)
    player_names = [p[1] for p in players]
    player_dropdown['values'] = player_names
    if player_names:
        player_var.set(player_names[0])
    
    conn.close()
    
    # Clear existing items
    for item in actions_tree.get_children():
        actions_tree.delete(item)
    
    # Insert actions with full details including participants and tags
    for action in actions:
        # Format participants
        participants_str = action['primary_participant'] or ''
        if action['secondary_participants']:
            if participants_str:
                participants_str += " → "
            participants_str += ", ".join(action['secondary_participants'])
        
        # Format tags
        tags_str = ", ".join(action['tags'])
        
        values = [
            action['id'],
            action['player'],
            action['type'],
            action['notes'],
            participants_str,
            tags_str
        ]
        actions_tree.insert("", "end", values=values)
        
    # Update selected session label and entry
    selected_session.set(f"Selected Session: {session_id}")
    entry_session.delete(0, tk.END)
    entry_session.insert(0, str(session_id))

# Modify add_session to refresh the list
def add_session():
    conn = connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO Sessions (date, version, notes) VALUES (?, ?, ?)",
                (datetime.date.today().isoformat(), entry_version.get(), entry_notes.get()))
    conn.commit()
    conn.close()
    messagebox.showinfo("Added", "Session added")
    load_sessions()  # Refresh the sessions list

# Action types available in the dropdown
ACTION_TYPES = ["Advance", "Embark", "Disembark", "Salvo", "Capture", "Move", "Consolidate", "Control", "Shot"]

def connect():
    return sqlite3.connect(DB_FILE)

def add_session():
    if not entry_player1.get() or not entry_player2.get():
        messagebox.showerror("Error", "Both players must be specified")
        return
        
    conn = connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO Sessions (date, version, notes) VALUES (?, ?, ?)",
                (datetime.date.today().isoformat(), entry_version.get(), entry_notes.get()))
    session_id = cur.lastrowid
    
    # Add players to session
    for player in [entry_player1.get(), entry_player2.get()]:
        # First ensure player exists
        cur.execute("INSERT OR IGNORE INTO Players (name) VALUES (?)", (player,))
        cur.execute("SELECT id FROM Players WHERE name = ?", (player,))
        player_id = cur.fetchone()[0]
        # Then link to session
        cur.execute("INSERT INTO SessionPlayers (session_id, player_id) VALUES (?, ?)",
                   (session_id, player_id))
    
    conn.commit()
    conn.close()
    messagebox.showinfo("Added", "Session added")
    load_sessions()

def handle_enter(event):
    widget = event.widget
    
    # Define the widget sequence for Enter key navigation
    sequence = [primary_participant, secondary_participants, entry_tags, entry_notes]
    
    try:
        # Get the next widget in sequence
        next_idx = sequence.index(widget) + 1
        if next_idx < len(sequence):
            sequence[next_idx].focus()
        else:
            # If we're on the last widget (notes), trigger add action
            add_action()
            # Move focus back to first field
            primary_participant.focus()
    except ValueError:
        pass  # Widget not in sequence
    
    return "break"  # Prevent default Enter behavior

def add_action(event=None):
    if not entry_session.get():
        messagebox.showerror("Error", "Please select a session first")
        return
        
    # Get primary and secondary participants
    primary = primary_participant.get().strip() or None
    secondary = [p.strip() for p in secondary_participants.get().split(',') if p.strip()] if secondary_participants.get() else None
        
    # Collect tags
    tags = [t.strip() for t in entry_tags.get().split(',')] if entry_tags.get() else None
        
    conn = connect()
    try:
        # Use the playtest_db function to add the action with all details
        import playtest_db
        playtest_db.add_action(
            conn,
            int(entry_session.get()),
            player_var.get(),
            action_type_var.get(),
            entry_notes.get(),
            primary_participant=primary,
            secondary_participants=secondary,
            tags=tags
        )
        
        # Only clear notes field, keep the rest. NOT ANYMORE
        entry_notes.delete(0, tk.END)
        primary_participant.delete(0, tk.END)
        secondary_participants.delete(0, tk.END)
        
        # Refresh the actions list if this action belongs to the currently selected session
        selected = sessions_tree.selection()
        if selected and str(sessions_tree.item(selected[0])['values'][0]) == entry_session.get():
            on_session_select(None)
        
        messagebox.showinfo("Added", "Action added")
        # Set focus back to primary participant field
        primary_participant.focus()
    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        conn.close()

# GUI setup
root = tk.Tk()
root.title("Playtest History")

# Configure default button for message boxes
root.option_add('*Dialog.msg.button.default', 'active')

# Initialize database if needed
init_if_needed()

# Add a refresh button at the top
refresh_btn = tk.Button(root, text="Refresh Lists", command=lambda: load_sessions())
refresh_btn.pack(fill="x", padx=5, pady=5)

# Create frames for lists
lists_frame = tk.Frame(root)
lists_frame.pack(fill="both", expand=True, padx=5, pady=5)

# Sessions list
sessions_frame = tk.LabelFrame(lists_frame, text="Sessions")
sessions_frame.pack(side="left", fill="both", expand=True, padx=5)

sessions_tree = ttk.Treeview(sessions_frame, columns=("ID", "Date", "Version", "Notes", "Players"), show="headings")
sessions_tree.heading("ID", text="ID")
sessions_tree.heading("Date", text="Date")
sessions_tree.heading("Version", text="Version")
sessions_tree.heading("Notes", text="Notes")
sessions_tree.heading("Players", text="Players")

# Configure column widths
sessions_tree.column("ID", width=50, minwidth=50)
sessions_tree.column("Date", width=100, minwidth=100)
sessions_tree.column("Version", width=70, minwidth=70)
sessions_tree.column("Notes", width=150, minwidth=100)
sessions_tree.column("Players", width=150, minwidth=100)

sessions_tree.pack(fill="both", expand=True)
sessions_tree.bind("<Double-1>", on_session_select)

# Add Delete Session button
def delete_session():
    selected = sessions_tree.selection()
    if not selected:
        messagebox.showerror("Error", "Please select a session to delete")
        return
    
    if not messagebox.askyesno("Confirm Delete", "Delete this session and all its actions?"):
        return
        
    session_id = sessions_tree.item(selected[0])['values'][0]
    conn = connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM Sessions WHERE id = ?", (session_id,))
    conn.commit()
    conn.close()
    load_sessions()
    
    # Clear session-related fields
    entry_session.delete(0, tk.END)
    selected_session.set("Selected Session: None")
    # Clear actions tree
    for item in actions_tree.get_children():
        actions_tree.delete(item)

delete_session_btn = tk.Button(sessions_frame, text="Delete Session", command=delete_session)
delete_session_btn.pack(pady=5)

# Edit Action Dialog
class EditActionDialog:
    def __init__(self, parent, action_data):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Edit Action")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.result = None
        self.action_data = action_data
        
        # Create widgets
        tk.Label(self.dialog, text="Type").grid(row=0, column=0)
        self.type_var = tk.StringVar(value=action_data['type'])
        self.type_combo = ttk.Combobox(self.dialog, textvariable=self.type_var, values=ACTION_TYPES, state="readonly")
        self.type_combo.grid(row=0, column=1)
        
        tk.Label(self.dialog, text="Primary Participant").grid(row=1, column=0)
        self.primary = tk.Entry(self.dialog)
        self.primary.insert(0, action_data['primary_participant'] or '')
        self.primary.grid(row=1, column=1)
        
        tk.Label(self.dialog, text="Secondary Participants").grid(row=2, column=0)
        self.secondary = tk.Entry(self.dialog)
        if action_data['secondary_participants']:
            self.secondary.insert(0, ', '.join(action_data['secondary_participants']))
        self.secondary.grid(row=2, column=1)
        
        tk.Label(self.dialog, text="Tags").grid(row=3, column=0)
        self.tags = tk.Entry(self.dialog)
        if action_data['tags']:
            self.tags.insert(0, ', '.join(action_data['tags']))
        self.tags.grid(row=3, column=1)
        
        tk.Label(self.dialog, text="Notes").grid(row=4, column=0)
        self.notes = tk.Entry(self.dialog)
        self.notes.insert(0, action_data['notes'] or '')
        self.notes.grid(row=4, column=1)
        
        btn_frame = tk.Frame(self.dialog)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        tk.Button(btn_frame, text="Save", command=self.save).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cancel", command=self.cancel).pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key to save
        self.dialog.bind("<Return>", lambda e: self.save())
        self.dialog.bind("<Escape>", lambda e: self.cancel())
        
        # Center the dialog
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (width // 2)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (height // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def save(self):
        self.result = {
            'type': self.type_var.get(),
            'primary_participant': self.primary.get().strip() or None,
            'secondary_participants': [p.strip() for p in self.secondary.get().split(',')] if self.secondary.get().strip() else None,
            'tags': [t.strip() for t in self.tags.get().split(',')] if self.tags.get().strip() else None,
            'notes': self.notes.get().strip() or None
        }
        self.dialog.destroy()
    
    def cancel(self):
        self.dialog.destroy()

# Actions list
actions_frame = tk.LabelFrame(lists_frame, text="Actions")
actions_frame.pack(side="right", fill="both", expand=True, padx=5)

selected_session = tk.StringVar(value="Selected Session: None")
tk.Label(actions_frame, textvariable=selected_session).pack()

actions_tree = ttk.Treeview(actions_frame, columns=("ID", "Player", "Type", "Participants", "Tags", "Notes"), show="headings")
actions_tree.heading("ID", text="ID")
actions_tree.heading("Player", text="Player")
actions_tree.heading("Type", text="Type")
actions_tree.heading("Participants", text="Participants")
actions_tree.heading("Tags", text="Tags")
actions_tree.heading("Notes", text="Notes")

# Configure column widths
actions_tree.column("ID", width=50, minwidth=50)
actions_tree.column("Player", width=80, minwidth=80)
actions_tree.column("Type", width=80, minwidth=80)
actions_tree.column("Participants", width=150, minwidth=100)
actions_tree.column("Tags", width=100, minwidth=80)
actions_tree.column("Notes", width=150, minwidth=100)

actions_tree.pack(fill="both", expand=True)

# Add double-click handler for action editing
def on_action_double_click(event):
    selected = actions_tree.selection()
    if not selected:
        return
        
    action = actions_tree.item(selected[0])['values']
    action_data = {
        'id': action[0],
        'player': action[1],
        'type': action[2],
        'notes': action[3],
        'primary_participant': None,
        'secondary_participants': [],
        'tags': []
    }
    
    # Parse participants from the participants string
    if action[4]:  # participants column
        parts = action[4].split(' → ')
        if parts[0]:  # primary participant
            action_data['primary_participant'] = parts[0]
        if len(parts) > 1:  # secondary participants
            action_data['secondary_participants'] = [p.strip() for p in parts[1].split(',')]
    
    # Parse tags
    if action[5]:  # tags column
        action_data['tags'] = [t.strip() for t in action[5].split(',')]
    
    dialog = EditActionDialog(root, action_data)
    root.wait_window(dialog.dialog)
    
    if dialog.result:
        conn = connect()
        cur = conn.cursor()
        
        # Update the action
        cur.execute("""
            UPDATE Actions 
            SET type = ?, notes = ?
            WHERE id = ?
        """, (dialog.result['type'], dialog.result['notes'], action_data['id']))
        
        # Delete old participants
        cur.execute("DELETE FROM ActionParticipants WHERE action_id = ?", (action_data['id'],))
        
        # Add new primary participant
        if dialog.result['primary_participant']:
            cur.execute(
                "INSERT INTO ActionParticipants (action_id, is_primary, name_text) VALUES (?, ?, ?)",
                (action_data['id'], True, dialog.result['primary_participant'])
            )
        
        # Add new secondary participants
        if dialog.result['secondary_participants']:
            cur.executemany(
                "INSERT INTO ActionParticipants (action_id, is_primary, name_text) VALUES (?, ?, ?)",
                [(action_data['id'], False, name) for name in dialog.result['secondary_participants']]
            )
            
        # Delete old tags
        cur.execute("DELETE FROM ActionTags WHERE action_id = ?", (action_data['id'],))
        
        # Add new tags
        if dialog.result['tags']:
            for tag in dialog.result['tags']:
                tag_id = ensure_tag(conn, tag)
                cur.execute("INSERT INTO ActionTags (action_id, tag_id) VALUES (?, ?)", 
                          (action_data['id'], tag_id))
        
        conn.commit()
        conn.close()
        
        # Refresh the actions list
        on_session_select(None)

def delete_action():
    selected = actions_tree.selection()
    if not selected:
        messagebox.showerror("Error", "Please select an action to delete")
        return
    
    if not messagebox.askyesno("Confirm Delete", "Delete this action?"):
        return
        
    action_id = actions_tree.item(selected[0])['values'][0]
    conn = connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM Actions WHERE id = ?", (action_id,))
    
    # Reset the sequence to the maximum ID
    cur.execute("SELECT MAX(id) FROM Actions")
    max_id = cur.fetchone()[0] or 0
    cur.execute("UPDATE SQLITE_SEQUENCE SET seq = ? WHERE name = 'Actions'", (max_id,))
    
    conn.commit()
    conn.close()
    
    # Refresh actions list
    selected = sessions_tree.selection()
    if selected:
        on_session_select(None)

delete_action_btn = tk.Button(actions_frame, text="Delete Action", command=delete_action)
delete_action_btn.pack(pady=5)

# Bind double-click for editing
actions_tree.bind("<Double-1>", on_action_double_click)

# Add Session frame
frame1 = tk.LabelFrame(root, text="Add Session")
frame1.pack(fill="x", padx=5, pady=5)

tk.Label(frame1, text="Version").grid(row=0, column=0)
entry_version = tk.Entry(frame1)
entry_version.grid(row=0, column=1)

tk.Label(frame1, text="Player 1").grid(row=1, column=0)
entry_player1 = tk.Entry(frame1)
entry_player1.grid(row=1, column=1)

tk.Label(frame1, text="Player 2").grid(row=2, column=0)
entry_player2 = tk.Entry(frame1)
entry_player2.grid(row=2, column=1)

tk.Label(frame1, text="Notes").grid(row=3, column=0)
entry_notes = tk.Entry(frame1)
entry_notes.grid(row=3, column=1)

tk.Button(frame1, text="Add Session", command=add_session).grid(row=4, columnspan=2, pady=5)

# Add Action frame
frame2 = tk.LabelFrame(root, text="Add Action")
frame2.pack(fill="x", padx=5, pady=5)

# Session ID (hidden but needed)
entry_session = tk.Entry(frame2)
entry_session.grid_remove()  # Hide it, it's set automatically when selecting a session

# Player dropdown
tk.Label(frame2, text="Player").grid(row=0, column=0)
player_var = tk.StringVar()
player_dropdown = ttk.Combobox(frame2, textvariable=player_var, state="readonly")
player_dropdown.grid(row=0, column=1)

# Action type dropdown
tk.Label(frame2, text="Action Type").grid(row=1, column=0)
action_type_var = tk.StringVar(value=ACTION_TYPES[0])
action_type_dropdown = ttk.Combobox(frame2, textvariable=action_type_var, values=ACTION_TYPES, state="readonly")
action_type_dropdown.grid(row=1, column=1)

# Participants frame
participants_frame = ttk.LabelFrame(frame2, text="Participants")
participants_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=5)

# Primary participant
tk.Label(participants_frame, text="Primary").grid(row=0, column=0)
primary_participant = tk.Entry(participants_frame)
primary_participant.grid(row=0, column=1)
primary_participant.bind("<Return>", handle_enter)

# Secondary participants
tk.Label(participants_frame, text="Secondary (comma-separated)").grid(row=1, column=0)
secondary_participants = tk.Entry(participants_frame)
secondary_participants.grid(row=1, column=1)
secondary_participants.bind("<Return>", handle_enter)

# Tags
tk.Label(frame2, text="Tags (comma-separated)").grid(row=3, column=0)
entry_tags = tk.Entry(frame2)
entry_tags.grid(row=3, column=1)
entry_tags.bind("<Return>", handle_enter)

# Notes
tk.Label(frame2, text="Notes").grid(row=4, column=0)
entry_notes = tk.Entry(frame2)
entry_notes.grid(row=4, column=1)
entry_notes.bind("<Return>", handle_enter)

tk.Button(frame2, text="Add Action", command=add_action).grid(row=5, columnspan=2, pady=5)

# Initial load
load_sessions()

root.mainloop()
