import sqlite3
from pathlib import Path
# front end was made with tkinter, copilot was used to help with the code, especially with the front end

DATABASE_FOLDER = Path(__file__).parent
def get_fields(database_name):

    if database_name == "Teams":
        return ["name", "location"]

    if database_name == "Players":
        return ["name", "age", "team"]


    return ["team_1", "team_2", "winner"]


def get_records(database_name):

    if database_name == "Teams":

        database_file = DATABASE_FOLDER / "teams.db"
        query = "SELECT rowid, name, location FROM teams"

    elif database_name == "Players":

        database_file = DATABASE_FOLDER / "players.db"
        query = "SELECT rowid, name, age, team FROM players"

    else:
        database_file = DATABASE_FOLDER / "matches.db"
        query = "SELECT rowid, team_1, team_2, winner FROM matches"

    with sqlite3.connect(database_file) as connection:

        return connection.execute(query).fetchall()


def add_record(database_name, values):

    if database_name == "Teams":
        database_file = DATABASE_FOLDER / "teams.db"
        query = "INSERT INTO teams (name, location) VALUES (?, ?)"

    elif database_name == "Players":
        database_file = DATABASE_FOLDER / "players.db"
        query = "INSERT INTO players (name, age, team) VALUES (?, ?, ?)"

    else:
        database_file = DATABASE_FOLDER / "matches.db"
        query = "INSERT INTO matches (team_1, team_2, winner) VALUES (?, ?, ?)"

    with sqlite3.connect(database_file) as connection:
        connection.execute(query, values)


def update_record(database_name, record_rowid, values):

    if database_name == "Teams":

        database_file = DATABASE_FOLDER / "teams.db"
        query = "UPDATE teams SET name = ?, location = ? WHERE rowid = ?"

    elif database_name == "Players":
        database_file = DATABASE_FOLDER / "players.db"
        query = "UPDATE players SET name = ?, age = ?, team = ? WHERE rowid = ?"

    else:
        database_file = DATABASE_FOLDER / "matches.db"
        query = "UPDATE matches SET team_1 = ?, team_2 = ?, winner = ? WHERE rowid = ?"

    with sqlite3.connect(database_file) as connection:
        connection.execute(query, [*values, record_rowid])


def delete_record(database_name, record_rowid):

    if database_name == "Teams":

        database_file = DATABASE_FOLDER / "teams.db"
        query = "DELETE FROM teams WHERE rowid = ?"

    elif database_name == "Players":

        database_file = DATABASE_FOLDER / "players.db"
        query = "DELETE FROM players WHERE rowid = ?"

    else:
        database_file = DATABASE_FOLDER / "matches.db"
        query = "DELETE FROM matches WHERE rowid = ?"

    with sqlite3.connect(database_file) as connection:
        connection.execute(query, [record_rowid])


def run_app():
    import tkinter as tk
    from tkinter import ttk

    class MolkkyApp:
        def __init__(self, window):
            self.window = window
            self.window.title("Mölkky Game Records")
            self.window.geometry("750x450")

            self.selected_database = tk.StringVar(value="Teams")
            self.selected_record_rowid = None
            self.input_fields = {}

            database_row = ttk.Frame(window, padding=10)
            database_row.pack(fill="x")

            ttk.Label(database_row, text="Show:").pack(side="left", padx=(0, 8))

            database_menu = ttk.Combobox(
                database_row,
                textvariable=self.selected_database,
                values=["Teams", "Players", "Matches"],
                state="readonly",
            )
            database_menu.pack(side="left")
            database_menu.bind("<<ComboboxSelected>>", self.show_database)

            self.form = ttk.Frame(window, padding=10)
            self.form.pack(fill="x")

            self.table_area = ttk.Frame(window, padding=10)
            self.table_area.pack(fill="both", expand=True)

            self.status_message = tk.StringVar()
            ttk.Label(window, textvariable=self.status_message, padding=10).pack(
                anchor="w"
            )

            self.show_database()

        def show_database(self, _event=None):
            for widget in self.form.winfo_children():
                widget.destroy()

            for widget in self.table_area.winfo_children():
                widget.destroy()

            self.selected_record_rowid = None
            self.input_fields = {}
            database_name = self.selected_database.get()
            fields = get_fields(database_name)

            for column, field in enumerate(fields):
                field_label = field.replace("_", " ").title()
                ttk.Label(self.form, text=field_label).grid(
                    row=0, column=column, sticky="w", padx=4
                )

                input_box = ttk.Entry(self.form, width=20)
                input_box.grid(row=1, column=column, padx=4, pady=(0, 8))
                self.input_fields[field] = input_box

            buttons = ttk.Frame(self.form)
            buttons.grid(row=2, column=0, columnspan=len(fields), sticky="w", padx=4)

            ttk.Button(buttons, text="Add", command=self.add).pack(side="left", padx=3)
            self.update_button = ttk.Button(
                buttons, text="Update", command=self.update, state="disabled"
            )
            self.update_button.pack(side="left", padx=3)

            self.delete_button = ttk.Button(
                buttons, text="Delete", command=self.delete, state="disabled"
            )
            self.delete_button.pack(side="left", padx=3)

            self.records_table = ttk.Treeview(
                self.table_area,
                columns=fields,
                show="headings",
                height=12,
            )

            for field in fields:
                field_label = field.replace("_", " ").title()
                self.records_table.heading(field, text=field_label)
                self.records_table.column(field, width=180)

            scrollbar = ttk.Scrollbar(
                self.table_area,
                orient="vertical",
                command=self.records_table.yview,
            )
            self.records_table.configure(yscrollcommand=scrollbar.set)
            self.records_table.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            self.records_table.bind("<<TreeviewSelect>>", self.select_record)
            self.refresh_records()

        def refresh_records(self):
            for row in self.records_table.get_children():
                self.records_table.delete(row)

            database_name = self.selected_database.get()

            for record in get_records(database_name):
                record_rowid = record[0]
                record_values = record[1:]
                self.records_table.insert(
                    "",
                    "end",
                    iid=str(record_rowid),
                    values=record_values,
                )

        def select_record(self, _event=None):
            selected_rows = self.records_table.selection()

            if not selected_rows:
                return

            selected_row = selected_rows[0]
            self.selected_record_rowid = int(selected_row)
            record_values = self.records_table.item(selected_row)["values"]
            fields = get_fields(self.selected_database.get())

            for field, value in zip(fields, record_values):
                self.input_fields[field].delete(0, tk.END)
                self.input_fields[field].insert(0, value)

            self.update_button.configure(state="normal")
            self.delete_button.configure(state="normal")

        def reset_form(self):
            self.selected_record_rowid = None

            for input_box in self.input_fields.values():
                input_box.delete(0, tk.END)

            for row in self.records_table.selection():
                self.records_table.selection_remove(row)

            self.update_button.configure(state="disabled")
            self.delete_button.configure(state="disabled")

        def get_input_values(self):
            values = []

            for input_box in self.input_fields.values():
                values.append(input_box.get())

            return values

        def add(self):
            database_name = self.selected_database.get()
            add_record(database_name, self.get_input_values())
            self.refresh_records()
            self.reset_form()
            self.status_message.set("Record added.")

        def update(self):
            database_name = self.selected_database.get()
            values = self.get_input_values()
            update_record(database_name, self.selected_record_rowid, values)
            self.refresh_records()
            self.reset_form()
            self.status_message.set("Record updated.")

        def delete(self):
            database_name = self.selected_database.get()
            delete_record(database_name, self.selected_record_rowid)
            self.refresh_records()
            self.reset_form()
            self.status_message.set("Record deleted.")

    window = tk.Tk()
    MolkkyApp(window)
    window.mainloop()


if __name__ == "__main__":
    run_app()
