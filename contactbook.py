import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo, showwarning, showerror
import csv
import re
import sqlite3

class ContactBookApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Contact Book App")
        self.root.geometry("1090x555+300+25")

        # Create an SQLite database and table
        self.conn = sqlite3.connect("contacts.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY,
                name TEXT,
                phone TEXT,
                email TEXT,
                address TEXT
            )
        ''')
        self.conn.commit()

        # Define keyboard shortcuts
        self.root.bind("<Control-n>", self.add_contact)  # Ctrl + N to add a contact
        self.root.bind("<Delete>", self.delete_contact)   # Delete key to delete a contact
        self.root.bind("<Control-f>", self.focus_search_entry)  # Ctrl + F to focus on the search entry

        self.notebook = ttk.Notebook(self.root)
        self.tab1 = tk.Frame(self.notebook, bg="darkturquoise")
        self.tab2 = tk.Frame(self.notebook, bg="darkturquoise")
        self.notebook.add(self.tab1, text="Add Contact")
        self.notebook.add(self.tab2, text="View Contacts")
        self.notebook.pack()

        self.init_add_contact_tab()
        self.init_view_contacts_tab()
        self.update_contacts_treeview()  # Load contacts initially

    def init_add_contact_tab(self):
        label = tk.Label(self.tab1, text="Add Contact", font=("Arial", 20), bg="#FF9912")
        label.pack(pady=10)

        name_label = tk.Label(self.tab1, text="Name:", font=("Arial", 15), bg="lawngreen")
        name_label.pack()
        self.name_entry = tk.Entry(self.tab1, font=("Arial", 15))
        self.name_entry.pack(pady=10)

        phone_label = tk.Label(self.tab1, text="Phone:", font=("Arial", 15), bg="lawngreen")
        phone_label.pack()
        self.phone_entry = tk.Entry(self.tab1, font=("Arial", 15))
        self.phone_entry.pack(pady=10)

        email_label = tk.Label(self.tab1, text="Email:", font=("Arial", 15), bg="lawngreen")
        email_label.pack()
        self.email_entry = tk.Entry(self.tab1, font=("Arial", 15))
        self.email_entry.pack(pady=10)

        address_label = tk.Label(self.tab1, text="Address:", font=("Arial", 15), bg="lawngreen")
        address_label.pack()
        self.address_entry = tk.Entry(self.tab1, font=("Arial", 15))
        self.address_entry.pack(pady=10)

        add_button = tk.Button(self.tab1, text="Add Contact", command=self.add_contact, font=("Arial", 15), bg="lawngreen")
        add_button.pack(pady=10)

    def init_view_contacts_tab(self):
        label = tk.Label(self.tab2, text="View Contacts", font=("Arial", 20), bg="#FF9912")
        label.pack(pady=10)

        search_label = tk.Label(self.tab2, text="Search:", font=("Arial", 15), bg="lawngreen")
        search_label.pack()
        self.search_entry = tk.Entry(self.tab2, font=("Arial", 15))
        self.search_entry.pack(pady=10)

        search_button = tk.Button(self.tab2, text="Search", command=self.search_contacts, font=("Arial", 15), bg="lawngreen")
        search_button.pack(pady=5)

        self.contacts_treeview = ttk.Treeview(self.tab2, columns=("Name", "Phone", "Email", "Address"), show="headings")
        self.contacts_treeview.heading("Name", text="Name")
        self.contacts_treeview.heading("Phone", text="Phone")
        self.contacts_treeview.heading("Email", text="Email")
        self.contacts_treeview.heading("Address", text="Address")
        self.contacts_treeview.pack(padx=10, pady=10)

        button_frame = tk.Frame(self.tab2, bg="darkturquoise")
        button_frame.pack(pady=10)

        edit_button = tk.Button(button_frame, text="Edit Contact", command=self.edit_contact, font=("Arial", 15), bg="lawngreen")
        edit_button.pack(side=tk.LEFT, padx=10)

        delete_button = tk.Button(button_frame, text="Delete Contact", command=self.delete_contact, font=("Arial", 15), bg="lawngreen")
        delete_button.pack(side=tk.LEFT, padx=10)

        merge_button = tk.Button(button_frame, text="Merge Contacts", command=self.merge_contacts, font=("Arial", 15), bg="lawngreen")
        merge_button.pack(side=tk.LEFT, padx=10)

        export_csv_button = tk.Button(button_frame, text="Export Contacts (CSV)", command=self.export_contacts_to_csv, font=("Arial", 15), bg="lawngreen")
        export_csv_button.pack(side=tk.LEFT, padx=10)

        load_csv_button = tk.Button(button_frame, text="Load Contacts", command=self.load_contacts_from_csv, font=("Arial", 15), bg="lawngreen")
        load_csv_button.pack(side=tk.LEFT, padx=10)

        stats_button = tk.Button(button_frame, text="Contact Statistics", command=self.display_contact_statistics,
                              font=("Arial", 15), bg="lawngreen")
        stats_button.pack(side=tk.LEFT, padx=10)

        self.stats_label = tk.Label(self.tab2, text="", font=("Arial", 15), bg="darkturquoise")
        self.stats_label.pack(pady=10)

    def display_contact_statistics(self):
        num_contacts = len(self.contacts)
        stats_text = f"Number of Contacts: {num_contacts}"
        self.stats_label.config(text=stats_text)

    def add_contact(self, event=None):
        name = self.name_entry.get()
        phone = self.phone_entry.get()
        email = self.email_entry.get()
        address = self.address_entry.get()

        if not name:
            showwarning("Validation Error", "Name is required.")
        elif not phone:
            showwarning("Validation Error", "Phone is required.")
        elif not self.is_valid_phone(phone):
            showwarning("Validation Error", "Phone number should only contain digits.")
        elif email and not self.is_valid_email(email):
            showwarning("Validation Error", "Invalid email format.")
        else:
            # Insert contact data into the SQLite database
            self.cursor.execute("INSERT INTO contacts (name, phone, email, address) VALUES (?, ?, ?, ?)",
                            (name, phone, email, address))
            self.conn.commit()
            
            self.update_contacts_treeview()
            self.clear_add_contact_fields()
            showinfo("Success", "Contact added successfully!")

    def clear_add_contact_fields(self):
        self.name_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.address_entry.delete(0, tk.END)

    def update_contacts_treeview(self):
        self.contacts_treeview.delete(*self.contacts_treeview.get_children())
        self.cursor.execute("SELECT * FROM contacts")
        self.contacts = []  # Initialize the contacts list
        for row in self.cursor.fetchall():
            contact = {"ID": row[0], "Name": row[1], "Phone": row[2], "Email": row[3], "Address": row[4]}
            self.contacts.append(contact)  # Append contact data to the list
            self.contacts_treeview.insert("", "end", values=(contact["Name"], contact["Phone"], contact["Email"], contact["Address"]))

    def search_contacts(self):
        search_text = self.search_entry.get().strip().lower()
        found_match = False
        for item in self.contacts_treeview.get_children():
            values = self.contacts_treeview.item(item, 'values')
            name_match = values[0].lower() == search_text
            phone_match = values[1].lower() == search_text
            if name_match or phone_match:
                self.contacts_treeview.selection_set(item)
                self.contacts_treeview.focus(item)
                found_match = True
        if not found_match:
            showinfo("Info", f"No contact with '{search_text}' found.")

    def edit_contact(self):
        selected_item = self.contacts_treeview.selection()
        if selected_item:
            selected_contact = self.contacts[self.contacts_treeview.index(selected_item)]
            edit_window = tk.Toplevel(self.root)
            edit_window.title("Edit Contact")
            edit_window.geometry("300x300")
            edit_window.config(bg="darkturquoise")

            edit_name_label = tk.Label(edit_window, text="Name:", font=("Arial", 15), bg="lawngreen")
            edit_name_label.pack()
            edit_name_entry = tk.Entry(edit_window, font=("Arial", 15), width=40)
            edit_name_entry.pack()
            edit_name_entry.insert(0, selected_contact["Name"])

            edit_phone_label = tk.Label(edit_window, text="Phone:", font=("Arial", 15), bg="lawngreen")
            edit_phone_label.pack()
            edit_phone_entry = tk.Entry(edit_window, font=("Arial", 15), width=40)
            edit_phone_entry.pack()
            edit_phone_entry.insert(0, selected_contact["Phone"])

            edit_email_label = tk.Label(edit_window, text="Email:", font=("Arial", 15), bg="lawngreen")
            edit_email_label.pack()
            edit_email_entry = tk.Entry(edit_window, font=("Arial", 15), width=40)
            edit_email_entry.pack()
            edit_email_entry.insert(0, selected_contact["Email"])

            edit_address_label = tk.Label(edit_window, text="Address:", font=("Arial", 15), bg="lawngreen")
            edit_address_label.pack()
            edit_address_entry = tk.Entry(edit_window, font=("Arial", 15), width=40)
            edit_address_entry.pack()
            edit_address_entry.insert(0, selected_contact["Address"])

            def save_edited_contact():
                edited_name = edit_name_entry.get()
                edited_phone = edit_phone_entry.get()
                edited_email = edit_email_entry.get()
                edited_address = edit_address_entry.get()

                if not edited_name:
                    showwarning("Validation Error", "Name is required.")
                elif not edited_phone:
                    showwarning("Validation Error", "Phone is required.")
                elif not self.is_valid_phone(edited_phone):
                    showwarning("Validation Error", "Phone number should only contain digits.")
                elif edited_email and not self.is_valid_email(edited_email):
                    showwarning("Validation Error", "Invalid email format.")
                else:
                    # Update the contact in the SQLite database
                    self.cursor.execute("UPDATE contacts SET name=?, phone=?, email=?, address=? WHERE id=?",
                                        (edited_name, edited_phone, edited_email, edited_address, selected_contact["ID"]))
                    self.conn.commit()

                    # Update the contact in the contacts list
                    selected_contact["Name"] = edited_name
                    selected_contact["Phone"] = edited_phone
                    selected_contact["Email"] = edited_email
                    selected_contact["Address"] = edited_address
                    self.update_contacts_treeview()
                    edit_window.destroy()

            save_button = tk.Button(edit_window, text="Save", command=save_edited_contact, font=("Arial", 15), bg="lawngreen")
            save_button.pack(pady=10)

    def delete_contact(self, event=None):
        selected_item = self.contacts_treeview.selection()
        if selected_item:
            selected_contact = self.contacts[self.contacts_treeview.index(selected_item)]
            # Delete the contact from the SQLite database
            self.cursor.execute("DELETE FROM contacts WHERE id=?", (selected_contact["ID"],))
            self.conn.commit()
            # Update the contacts list
            self.contacts.remove(selected_contact)
            self.update_contacts_treeview()
            showinfo("Success", "Contact deleted successfully!")

    def focus_search_entry(self, event=None):
        self.search_entry.focus()

    def merge_contacts(self):
        # Create a dictionary to store merged contacts
        merged_contacts = {}

        for contact in self.contacts:
            name = contact["Name"]
            email = contact["Email"]

            # Create a unique key based on name and email
            key = (name, email)

            # Check if the key already exists in merged_contacts
            if key in merged_contacts:
                # Merge the contact's information into the existing contact
                merged_contacts[key].update(contact)
            else:
                # If the key doesn't exist, add the contact to merged_contacts
                merged_contacts[key] = contact

        # Update the contacts list with the merged contacts
        self.contacts = list(merged_contacts.values())

        # Update the SQLite database with the merged contacts
        self.cursor.execute("DELETE FROM contacts")
        for contact in self.contacts:
            self.cursor.execute("INSERT INTO contacts (name, phone, email, address) VALUES (?, ?, ?, ?)",
                                (contact["Name"], contact["Phone"], contact["Email"], contact["Address"]))
        self.conn.commit()

        self.update_contacts_treeview()
        showinfo("Success", "Duplicate contacts merged.")

    def load_contacts_from_csv(self):
        try:
            with open("contacts.csv", mode="r", newline="") as file:
                reader = csv.DictReader(file)
                self.contacts = list(reader)
                # Add the loaded contacts to the SQLite database
                self.cursor.executemany("INSERT INTO contacts (name, phone, email, address) VALUES (?, ?, ?, ?)",
                                        [(contact["Name"], contact["Phone"], contact["Email"], contact["Address"]) for contact in self.contacts])
                self.conn.commit()
            self.update_contacts_treeview()
            showinfo("Success", "Contacts loaded from CSV file.")
        except FileNotFoundError:
            showerror("Error", "CSV file not found.")

    def export_contacts_to_csv(self):
        try:
            with open("contacts.csv", mode="w", newline="") as file:
                fieldnames = ["Name", "Phone", "Email", "Address"]
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                for contact in self.contacts:
                    # Exclude the 'ID' field when writing to the CSV file
                    contact_without_id = {key: value for key, value in contact.items() if key != 'ID'}
                    writer.writerow(contact_without_id)
            showinfo("Success", "Contacts exported to CSV file.")
        except Exception as e:
            showerror("Error", f"An error occurred: {str(e)}")

    def is_valid_phone(self, phone):
        phone_pattern = r'^\d+$'  # Regular expression for digits only
        return re.match(phone_pattern, phone) is not None

    def is_valid_email(self, email):
        email_pattern = r'^\S+@\S+\.\S+'
        return re.match(email_pattern, email) is not None

if __name__ == "__main__":
    root = tk.Tk()
    app = ContactBookApp(root)
    root.mainloop()
