import csv
import uuid
import tkinter as tk
from tkinter import ttk, messagebox

UNITS_FILE = "units.csv"
WEAPONS_FILE = "weapons.csv"
TAGS_FILE = "tags.csv"
KEYWORDS_FILE = "keywords.csv"

def load_csv(path):
    try:
        with open(path, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    except FileNotFoundError:
        if path == TAGS_FILE:
            return [{"uuid": "tag-"+str(uuid.uuid4())[:8], "name": tag} for tag in ["Infantry", "Vehicle", "Flying"]]
        elif path == KEYWORDS_FILE:
            return [{"uuid": "kw-"+str(uuid.uuid4())[:8], "name": kw} for kw in ["Melee", "Ranged", "Blast"]]
        return []


def save_csv(path, rows, fieldnames):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


units = load_csv(UNITS_FILE)
weapons = load_csv(WEAPONS_FILE)
tags = load_csv(TAGS_FILE)
keywords = load_csv(KEYWORDS_FILE)

# Save the tag and keyword files if they didn't exist
save_csv(TAGS_FILE, tags, ["uuid", "name"])
save_csv(KEYWORDS_FILE, keywords, ["uuid", "name"])

root = tk.Tk()
root.title("Unit & Weapon Editor")
root.geometry("800x600")

selected_item = tk.StringVar()
mode = tk.StringVar(value="units")
weapon_name_to_uuid = {}
tag_name_to_uuid = {}
keyword_name_to_uuid = {}

def generate_uuid(name, mode="units"):
    base = name.lower().replace(" ", "-")
    if mode == "weapons":
        # For weapons, append first keyword if available
        keywords_field = entries.get("keywords", None) if 'entries' in globals() else None
        if keywords_field and keywords_field.get():
            first_keyword = keywords_field.get().split(",")[0].strip()
            return f"{base}-{first_keyword}"
        return base
    return base  # For units, tags, and keywords, just use the base name

# GUI Layout
frame_left = ttk.Frame(root)
frame_left.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

frame_right = ttk.Frame(root)
frame_right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

# Mode Switch Button
def export_to_tex():
    # Create units.tex content
    tex_content = ""
    for unit in units:
        # Get unit's weapons
        unit_weapons = []
        if unit.get("weapons"):
            weapon_ids = unit["weapons"].split(",")
            unit_weapons = [w for w in weapons if w["uuid"] in weapon_ids]
        
        # Create weapon rows for the table
        weapon_rows = ""
        for w in unit_weapons:
            keywords_str = w.get("keywords", "").replace(",", ", ")
            weapon_rows += f"{w['name']} & {w.get('R', '-')} & {w.get('N', '-')} & {w.get('L', '-')} & {w.get('M', '-')} & {w.get('H', '-')} & {w.get('F', '-')} & {keywords_str} \\\\ \hline\n"
        
        # Get unit's tags
        tags_str = ""
        if unit.get("tags"):
            tag_ids = unit["tags"].split(",")
            tag_names = [t["name"] for t in tags if t["uuid"] in tag_ids]
            tags_str = ", ".join(tag_names)
        
        # Create unit card with weapon table
        tex_content += "\\unitcard{" + unit["name"] + "}{" + \
                      unit.get("subtitle", "") + "}{" + \
                      unit.get("M", "-") + "}{" + \
                      unit.get("A", "-") + "}{" + \
                      unit.get("C", "-") + "}{" + \
                      unit.get("H", "-") + "}{" + \
                      unit.get("MP", "-") + "}{" + \
                      unit.get("Mat", "-") + "}{" + \
                      tags_str + "}\n"

        # Prepare abilities injection: default to 'None' if empty; convert newlines to LaTeX linebreaks
        abilities_raw = unit.get("abilities", "") or ""
        abilities_text = abilities_raw.strip()
        if not abilities_text:
            abilities_text = "None"
        else:
            abilities_text = abilities_text.replace("\n", " \\\\ ")

        tex_content += "\\weapontable{" + weapon_rows + "}{" + abilities_text + "}\n\n"

    # Write to units.tex
    with open("units.tex", "w", encoding="utf-8") as f:
        f.write(tex_content)
    
    messagebox.showinfo("Export Complete", "Units have been exported to units.tex")

def toggle_mode():
    if mode.get() == "units":
        mode.set("weapons")
        mode_button.config(text="Switch to Units")
    else:
        mode.set("units")
        mode_button.config(text="Switch to Weapons")
    refresh_list()
    build_form()

mode_button = ttk.Button(frame_left, text="Switch to Weapons", command=toggle_mode)
mode_button.pack(pady=5)

export_button = ttk.Button(frame_left, text="Export to PDF", command=export_to_tex)
export_button.pack(pady=5)

listbox = tk.Listbox(frame_left, height=25)
listbox.pack(fill=tk.Y, expand=True)
listbox.bind("<<ListboxSelect>>", lambda e: load_selected())

form_frame = ttk.Frame(frame_right)
form_frame.pack(fill=tk.BOTH, expand=True)

entries = {}
weapon_vars = {}

def create_searchable_list(parent, items, name_to_uuid, selection_dict, title, height=6):
    frame = ttk.Frame(parent)
    frame.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
    
    # Header with title and selection display
    header_frame = ttk.Frame(frame)
    header_frame.pack(fill=tk.X, pady=(0,5))
    
    ttk.Label(header_frame, text=title, font=("Arial", 10, "bold")).pack(side=tk.LEFT, pady=(0,2))
    
    # Selection display
    selection_var = tk.StringVar(value="")
    selection_entry = ttk.Entry(frame, textvariable=selection_var, state='readonly')
    selection_entry.pack(fill=tk.X, pady=(0, 5))
    
    # Search entry
    search_var = tk.StringVar()
    search_entry = ttk.Entry(frame, textvariable=search_var)
    search_entry.pack(fill=tk.X, pady=(0, 5))
    
    # Listbox with scrollbar
    list_frame = ttk.Frame(frame)
    list_frame.pack(fill=tk.BOTH, expand=True)
    listbox = tk.Listbox(list_frame, selectmode=tk.MULTIPLE, height=height)
    scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=listbox.yview)
    listbox.configure(yscrollcommand=scrollbar.set)
    
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Store selection state and variables in the listbox
    # selection_state will map uuid -> bool so state is stable across renames/filters
    listbox.selection_state = {}
    listbox.uuid_to_name = {}
    listbox.items = items  # Store items reference
    listbox.selection_var = selection_var  # Store the selection display variable
    
    # Populate list and clear previous mappings
    name_to_uuid.clear()
    for item in items:
        name = item["name"]
        uuid = item["uuid"]
        listbox.insert(tk.END, name)
        name_to_uuid[name] = uuid
        selection_dict[uuid] = False
        listbox.selection_state[uuid] = False
        listbox.uuid_to_name[uuid] = name
    
    def update_selection_display():
        # Get all selected items by uuid and update the display with names
        selected_names = [listbox.uuid_to_name[uid] for uid, selected in listbox.selection_state.items() if selected]
        listbox.selection_var.set(", ".join(selected_names))
    
    def on_click_toggle(event):
        """Toggle selection for the clicked item only.

        Uses the event x/y to determine which index was clicked, toggles
        that item's stored selection state, updates the visual selection
        for currently visible items to reflect stored state, and updates
        the external selection_dict mapping. This avoids altering other
        listbox instances or non-visible item states.
        """
        # Prevent recursion from programmatic selection changes
        if hasattr(listbox, '_updating'):
            return

        # Calculate the clicked index from the y coordinate
        try:
            click_index = listbox.nearest(event.y)
        except Exception:
            return

        # If nothing visible, bail
        if click_index is None:
            return


        try:
            clicked_name = listbox.get(click_index)
        except Exception:
            return

        # Resolve uuid and toggle stored selection state for this item
        clicked_uuid = name_to_uuid.get(clicked_name)
        if not clicked_uuid:
            return

        current = listbox.selection_state.get(clicked_uuid, False)
        listbox.selection_state[clicked_uuid] = not current

        # Update external selection mapping for this uuid
        selection_dict[clicked_uuid] = listbox.selection_state[clicked_uuid]

        # Refresh visual selection for all visible items from stored state
        listbox._updating = True
        listbox.selection_clear(0, tk.END)
        for i in range(listbox.size()):
            name = listbox.get(i)
            uid = name_to_uuid.get(name)
            if uid and listbox.selection_state.get(uid, False):
                listbox.selection_set(i)
        delattr(listbox, '_updating')

        # Update the selection display
        update_selection_display()

        # Debug: log toggle
        try:
            print(f"Toggled {clicked_uuid} -> {listbox.selection_state[clicked_uuid]}")
            print("Current selection_dict snapshot:", {k: v for k, v in list(selection_dict.items())[:20]})
        except Exception:
            pass

        # Also refresh any sibling searchable lists in the same row (e.g. weapons/tags)
        try:
            # frame -> parent left/right container -> row_frame
            row_frame = frame.master.master
            for sibling in row_frame.winfo_children():
                # each sibling is a left_frame/right_frame; its first child is the searchable frame
                for child in sibling.winfo_children():
                    if hasattr(child, 'update_list') and child is not frame:
                        # call update_list to re-sync visual selection from stored state
                        try:
                            child.update_list()
                        except Exception:
                            pass
        except Exception:
            pass
                
    def update_list(*args):
        search_term = search_var.get().lower()
        
        # Set flag to prevent selection event handling
        listbox._updating = True
        
        listbox.delete(0, tk.END)
        for item in items:
            name = item["name"]
            uuid = item["uuid"]
            if search_term in name.lower():
                listbox.insert(tk.END, name)
                if listbox.selection_state.get(uuid, False):
                    idx = listbox.size() - 1
                    listbox.selection_set(idx)
        
        # Update selection display
        update_selection_display()
        
        # Remove flag
        delattr(listbox, '_updating')
    
    # Bind events: use click toggle to avoid cross-listbox side-effects
    listbox.bind('<ButtonRelease-1>', on_click_toggle)
    search_var.trace("w", update_list)
    
    # Store functions on the frame for external access
    frame.listbox = listbox
    frame.update_list = update_list
    
    return frame

def build_form():
    for widget in form_frame.winfo_children():
        widget.destroy()

    global entries, weapon_vars, tag_vars, keyword_vars
    entries = {}
    weapon_vars = {}
    tag_vars = {}
    keyword_vars = {}

    fields = []
    if mode.get() == "units":
        fields = ["name", "subtitle", "M", "A", "C", "H", "MP", "Mat"]
        # Add abilities field for units
        row = ttk.Frame(form_frame)
        row.pack(fill=tk.X, pady=2)
        ttk.Label(row, text="Abilities: ", width=12).pack(side=tk.LEFT)
        text_widget = tk.Text(row, height=4, width=50)
        text_widget.pack(side=tk.LEFT, fill=tk.X, expand=True)
        entries["abilities"] = text_widget
    else:
        fields = ["name", "R", "N", "L", "M", "H", "F"]

    for f in fields:
        row = ttk.Frame(form_frame)
        row.pack(fill=tk.X, pady=2)
        ttk.Label(row, text=f"{f}: ", width=12).pack(side=tk.LEFT)
        ent = ttk.Entry(row)
        ent.pack(side=tk.LEFT, fill=tk.X, expand=True)
        entries[f] = ent

    # Create scrollable frame for lists
    lists_frame = ttk.Frame(form_frame)
    lists_frame.pack(fill="both", expand=True, pady=(10,0))

    if mode.get() == "units":
        # Create a frame for holding lists side by side
        row_frame = ttk.Frame(lists_frame)
        row_frame.pack(fill="both", expand=True)
        
        # Left side - Weapons
        left_frame = ttk.Frame(row_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0,5))
        create_searchable_list(left_frame, weapons, weapon_name_to_uuid, weapon_vars, "Weapons:", 12)
        
        # Right side - Tags
        right_frame = ttk.Frame(row_frame)
        right_frame.pack(side="left", fill="both", expand=True, padx=(5,0))
        create_searchable_list(right_frame, tags, tag_name_to_uuid, tag_vars, "Tags:", 12)
    else:
        # Keywords selector - centered and full width
        create_searchable_list(lists_frame, keywords, keyword_name_to_uuid, keyword_vars, "Keywords:", 12)

    ttk.Button(form_frame, text="Save", command=save_item).pack(pady=5)

def refresh_list():
    listbox.delete(0, tk.END)
    if mode.get() == "units":
        for u in units:
            listbox.insert(tk.END, f"{u['name']}")
    else:
        for w in weapons:
            listbox.insert(tk.END, f"{w['name']}")

def load_selected():
    if not listbox.curselection():
        return
    index = listbox.curselection()[0]
    item = units[index] if mode.get() == "units" else weapons[index]
    selected_item.set(item["uuid"])

    # Fill entries
    for key, entry in entries.items():
        if key == "abilities" and isinstance(entry, tk.Text):
            entry.delete("1.0", tk.END)
            entry.insert("1.0", item.get(key, ""))
        else:
            entry.delete(0, tk.END)
            entry.insert(0, item.get(key, ""))

    # Update selections for weapons, tags, and keywords
    if mode.get() == "units":
        # Reset all selection states
        for uuid in weapon_vars:
            weapon_vars[uuid] = False
        for uuid in tag_vars:
            tag_vars[uuid] = False
            
        lists_frame = form_frame.winfo_children()[-2]  # Get the lists frame
        row_frame = lists_frame.winfo_children()[0]  # Get the row frame
        weapons_frame = row_frame.winfo_children()[0]  # Left frame
        tags_frame = row_frame.winfo_children()[1]  # Right frame
        
        # Get the listboxes
        weapons_list = weapons_frame.winfo_children()[0]
        tags_list = tags_frame.winfo_children()[0]
        weapons_listbox = weapons_list.listbox
        tags_listbox = tags_list.listbox
        
        # Clear all selections first (visual)
        weapons_listbox._updating = True
        tags_listbox._updating = True

        weapons_listbox.selection_clear(0, tk.END)
        tags_listbox.selection_clear(0, tk.END)

        # Reset selection_state (keys are uuids)
        for uid in list(weapons_listbox.selection_state.keys()):
            weapons_listbox.selection_state[uid] = False
        for uid in list(tags_listbox.selection_state.keys()):
            tags_listbox.selection_state[uid] = False

        # Update weapons from unit data (uuids)
        if item.get("weapons"):
            selected_weapon_ids = [s for s in item["weapons"].split(",") if s]
            for uid in selected_weapon_ids:
                if uid in weapons_listbox.selection_state:
                    weapons_listbox.selection_state[uid] = True
                    # map uuid to displayed name and select index if visible
                    name = weapons_listbox.uuid_to_name.get(uid)
                    if name:
                        try:
                            idx = weapons_listbox.get(0, tk.END).index(name)
                            weapons_listbox.selection_set(idx)
                        except ValueError:
                            pass
                    weapon_vars[uid] = True

        # Force update of weapons display (use uuid_to_name)
        selected_weapons = [weapons_listbox.uuid_to_name[uid] for uid, sel in weapons_listbox.selection_state.items() if sel and uid in weapons_listbox.uuid_to_name]
        weapons_listbox.selection_var.set(", ".join(selected_weapons))

        # Update tags from unit data (uuids)
        if item.get("tags"):
            selected_tag_ids = [s for s in item["tags"].split(",") if s]
            for uid in selected_tag_ids:
                if uid in tags_listbox.selection_state:
                    tags_listbox.selection_state[uid] = True
                    name = tags_listbox.uuid_to_name.get(uid)
                    if name:
                        try:
                            idx = tags_listbox.get(0, tk.END).index(name)
                            tags_listbox.selection_set(idx)
                        except ValueError:
                            pass
                    tag_vars[uid] = True

        # Force update of tags display
        selected_tags = [tags_listbox.uuid_to_name[uid] for uid, sel in tags_listbox.selection_state.items() if sel and uid in tags_listbox.uuid_to_name]
        tags_listbox.selection_var.set(", ".join(selected_tags))

        # Remove update flags
        try:
            delattr(weapons_listbox, '_updating')
        except Exception:
            pass
        try:
            delattr(tags_listbox, '_updating')
        except Exception:
            pass
        # Debug: log loaded selections
        try:
            print(f"Loaded unit {item.get('name')} - weapons:", selected_weapons)
            print(f"Loaded unit {item.get('name')} - tags:", selected_tags)
        except Exception:
            pass
        
    else:
        # Handle keywords for weapons
        lists_frame = form_frame.winfo_children()[-2]  # Get the lists frame
        keywords_frame = lists_frame.winfo_children()[0].winfo_children()[0]  # Get the inner frame that contains the listbox
        keywords_listbox = None
        
        # Find the listbox within the frame's children
        for child in keywords_frame.winfo_children():
            if isinstance(child, tk.Listbox):
                keywords_listbox = child
                break
        
        if keywords_listbox:
            # Clear all selections first
            keywords_listbox._updating = True
            keywords_listbox.selection_clear(0, tk.END)
            
            # Reset selection states (keys are uuids)
            for uid in list(keywords_listbox.selection_state.keys()):
                keywords_listbox.selection_state[uid] = False
                if uid in keyword_vars:
                    keyword_vars[uid] = False

            # Update keywords from item data (uuids)
            if item.get("keywords"):
                selected_keyword_ids = [s for s in item["keywords"].split(",") if s]
                for uid in selected_keyword_ids:
                    if uid in keywords_listbox.selection_state:
                        keywords_listbox.selection_state[uid] = True
                        name = keywords_listbox.uuid_to_name.get(uid)
                        if name:
                            try:
                                idx = keywords_listbox.get(0, tk.END).index(name)
                                keywords_listbox.selection_set(idx)
                                keyword_vars[uid] = True
                            except ValueError:
                                pass  # Item might be filtered out
                        
            # Remove update flag
            delattr(keywords_listbox, '_updating')

def export_to_tex():
    # Create units.tex content
    tex_content = ""
    for unit in units:
        # Get unit's weapons
        unit_weapons = []
        if unit.get("weapons"):
            weapon_ids = unit["weapons"].split(",")
            unit_weapons = [w for w in weapons if w["uuid"] in weapon_ids]
        
        # Create weapon rows for the table
            weapon_rows = ""
            for w in unit_weapons:
                # Convert keyword uuids to names
                kw_field = w.get("keywords", "")
                if kw_field:
                    kw_ids = [k for k in kw_field.split(",") if k]
                    kw_names = [kobj["name"] for kobj in keywords if kobj["uuid"] in kw_ids]
                    keywords_str = ", ".join(kw_names)
                else:
                    keywords_str = ""

                # Append row and ensure a \hline after each weapon
                weapon_rows += f"{w['name']} & {w.get('R', '-')} & {w.get('N', '-')} & {w.get('L', '-')} & {w.get('M', '-')} & {w.get('H', '-')} & {w.get('F', '-')} & {keywords_str} \\\\\\hline \n"
        
        # Get unit's tags
        tags_str = ""
        if unit.get("tags"):
            tag_ids = unit["tags"].split(",")
            tag_names = [t["name"] for t in tags if t["uuid"] in tag_ids]
            tags_str = ", ".join(tag_names)
        
        # Create unit card with weapon table
        tex_content += "\\unitcard{" + unit["name"] + "}{" + \
                      unit.get("subtitle", "") + "}{" + \
                      unit.get("M", "-") + "}{" + \
                      unit.get("A", "-") + "}{" + \
                      unit.get("C", "-") + "}{" + \
                      unit.get("H", "-") + "}{" + \
                      unit.get("MP", "-") + "}{" + \
                      unit.get("Mat", "-") + "}{" + \
                      tags_str + "}\n"
        
        tex_content += "\\weapontable{" + weapon_rows + "}\n\n"

    # Write to units.tex
    with open("units.tex", "w", encoding="utf-8") as f:
        f.write(tex_content)
    
    messagebox.showinfo("Export Complete", "Units have been exported to units.tex")

def save_item():
    # Get all form field values, stripped of whitespace
    data = {}
    for k, v in entries.items():
        if k == "abilities" and isinstance(v, tk.Text):
            data[k] = v.get("1.0", tk.END).strip()
        else:
            data[k] = v.get().strip()
    
    # Handle Units mode
    if mode.get() == "units":
        # Fill empty unit stats with "0"
        for field in ["M", "A", "C", "H", "MP", "Mat"]:
            if not data[field]:
                data[field] = "0"
                entries[field].delete(0, tk.END)
                entries[field].insert(0, "0")
        
        # Get selected weapons and tags
        selected_weapons = [wid for wid, selected in weapon_vars.items() if selected]
        selected_tags = [tid for tid, selected in tag_vars.items() if selected]
        data["weapons"] = ",".join(selected_weapons)
        data["tags"] = ",".join(selected_tags)
        
        # Update existing unit or create new one
        existing = next((u for u in units if u["name"] == data["name"]), None)
        if existing:
            existing.update(data)
        else:
            new_row = {"uuid": generate_uuid(data["name"]), **data}
            units.append(new_row)
        # Ensure abilities is the last editable field in the CSV before weapons/tags
        # Build header: uuid, then all entry keys with abilities moved to the end, then weapons/tags
        entry_keys = [k for k in entries.keys() if k != 'abilities'] + (['abilities'] if 'abilities' in entries else [])
        save_csv(UNITS_FILE, units, ["uuid"] + entry_keys + ["weapons", "tags"])
        
    # Handle Weapons mode
    else:
        # Fill empty weapon stats with "NA"
        for field in ["R", "N", "L", "M", "H", "F"]:
            if not data[field]:
                data[field] = "NA"
                entries[field].delete(0, tk.END)
                entries[field].insert(0, "NA")
        
        # Get selected keywords
        selected_keywords = [kid for kid, selected in keyword_vars.items() if selected]
        data["keywords"] = ",".join(selected_keywords)
        
        # Update existing weapon or create new one
        existing = next((w for w in weapons if w["name"] == data["name"]), None)
        if existing:
            existing.update(data)
        else:
            new_row = {"uuid": generate_uuid(data["name"], "weapons"), **data}
            weapons.append(new_row)
        save_csv(WEAPONS_FILE, weapons, ["uuid"] + list(entries.keys()) + ["keywords"])

    refresh_list()
    messagebox.showinfo("Saved", f"{mode.get().capitalize()} saved successfully.")

build_form()
refresh_list()
root.mainloop()
