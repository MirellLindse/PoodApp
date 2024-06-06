import sqlite3
import customtkinter as ctk
from tkinter import ttk
from tkinter import simpledialog, messagebox

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

def create_table(conn):
    try:
        sql_create_products_table = """
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            allergens TEXT
        );
        """
        cursor = conn.cursor()
        cursor.execute(sql_create_products_table)
    except sqlite3.Error as e:
        print(e)

def add_product(conn, product):
    sql = '''INSERT INTO products(name, price, allergens) VALUES(?, ?, ?)'''
    cursor = conn.cursor()
    cursor.execute(sql, product)
    conn.commit()
    return cursor.lastrowid

def update_product(conn, product):
    sql = '''UPDATE products SET name = ?, price = ?, allergens = ? WHERE id = ?'''
    cursor = conn.cursor()
    cursor.execute(sql, product)
    conn.commit()

def delete_product(conn, product_id):
    sql = 'DELETE FROM products WHERE id = ?'
    cursor = conn.cursor()
    cursor.execute(sql, (product_id,))
    conn.commit()

def get_products(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()
    return rows

class StoreApp:
    def __init__(self, root):
        self.conn = create_connection("store.db")
        create_table(self.conn)

        self.root = root
        self.root.title("Pood")
        self.root.geometry("1150x600")  # Увеличим ширину окна

        # Настройка стиля Treeview
        style = ttk.Style()
        style.configure("Custom.Treeview", background="#333333", fieldbackground="#333333", foreground="white")

        # Установка цвета фона для окна
        self.root.configure(bg="#2c2c2c")

        # Левое окно для управления продуктами
        self.left_frame = ctk.CTkFrame(root, width=600)
        self.left_frame.grid(row=0, column=0, padx=10, pady=10)

        self.name_label = ctk.CTkLabel(self.left_frame, text="Nimi")
        self.name_label.grid(row=0, column=0, padx=10, pady=10)
        self.name_entry = ctk.CTkEntry(self.left_frame)
        self.name_entry.grid(row=0, column=1, padx=10, pady=10)

        self.price_label = ctk.CTkLabel(self.left_frame, text="Hind")
        self.price_label.grid(row=1, column=0, padx=10, pady=10)
        self.price_entry = ctk.CTkEntry(self.left_frame)
        self.price_entry.grid(row=1, column=1, padx=10, pady=10)

        self.allergens_label = ctk.CTkLabel(self.left_frame, text="Allergeeenid")
        self.allergens_label.grid(row=2, column=0, padx=10, pady=10)
        self.allergens_entry = ctk.CTkEntry(self.left_frame)
        self.allergens_entry.grid(row=2, column=1, padx=10, pady=10)

        self.add_button = ctk.CTkButton(self.left_frame, text="Lisa", command=self.add_product)
        self.add_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        self.tree = ttk.Treeview(self.left_frame, columns=("id", "name", "price", "allergens"), show='headings', style="Custom.Treeview")
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Nimi")
        self.tree.heading("price", text="Hind (€)")
        self.tree.heading("allergens", text="Allergeenid")
        self.tree.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

        self.load_products()

        self.update_button = ctk.CTkButton(self.left_frame, text="Uuenda", command=self.update_product)
        self.update_button.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

        self.delete_button = ctk.CTkButton(self.left_frame, text="Kustuta", command=self.delete_product)
        self.delete_button.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

        self.tree.bind('<ButtonRelease-1>', self.select_product)

        # Правое окно для оплаты
        self.right_frame = ctk.CTkFrame(root, width=300)
        self.right_frame.grid(row=0, column=1, padx=10, pady=10)

        self.id_label = ctk.CTkLabel(self.right_frame, text="Kaupa ID")
        self.id_label.grid(row=0, column=0, padx=10, pady=10)
        self.id_entry = ctk.CTkEntry(self.right_frame)
        self.id_entry.grid(row=0, column=1, padx=10, pady=10)

        self.quantity_label = ctk.CTkLabel(self.right_frame, text="Kogus")
        self.quantity_label.grid(row=1, column=0, padx=10, pady=10)
        self.quantity_entry = ctk.CTkEntry(self.right_frame)
        self.quantity_entry.grid(row=1, column=1, padx=10, pady=10)

        self.add_to_cart_button = ctk.CTkButton(self.right_frame, text="Lisa ostule", command=self.add_to_cart)
        self.add_to_cart_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

        self.cart_label = ctk.CTkLabel(self.right_frame, text="Ost")
        self.cart_label.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        self.payment_frame = ctk.CTkFrame(root, width=300)
        self.payment_frame.grid(row=1, column=1, padx=10, pady=10)

        self.pay_cash_button = ctk.CTkButton(self.payment_frame, text="Sularaha", command=self.pay_cash)
        self.pay_cash_button.grid(row=0, column=0, padx=10, pady=10)

        self.pay_card_button = ctk.CTkButton(self.payment_frame, text="Kaardimakse", command=self.pay_card)
        self.pay_card_button.grid(row=0, column=1, padx=10, pady=10)

        self.cart_listbox = ctk.CTkTextbox(self.right_frame, width=250, height=150)
        self.cart_listbox.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

        self.total_label = ctk.CTkLabel(self.right_frame, text="Kokku: €0.00")
        self.total_label.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

        self.cart = []
        self.total = 0.0

    def load_products(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for row in get_products(self.conn):
            formatted_row = (row[0], row[1], f"{row[2]:.2f} €", row[3])
            self.tree.insert("", "end", values=formatted_row)

    def add_product(self):
        name = self.name_entry.get()
        price = float(self.price_entry.get())
        allergens = self.allergens_entry.get()
        add_product(self.conn, (name, price, allergens))
        self.load_products()

    def update_product(self):
        selected_item = self.tree.selection()[0]
        item = self.tree.item(selected_item, 'values')
        product_id = item[0]
        name = self.name_entry.get()
        price = float(self.price_entry.get())
        allergens = self.allergens_entry.get()
        update_product(self.conn, (name, price, allergens, product_id))
        self.load_products()

    def delete_product(self):
        selected_item = self.tree.selection()[0]
        item = self.tree.item(selected_item, 'values')
        product_id = item[0]
        delete_product(self.conn, product_id)
        self.load_products()

    def select_product(self, event):
        selected_item = self.tree.selection()[0]
        item = self.tree.item(selected_item, 'values')
        self.name_entry.delete(0, ctk.END)
        self.name_entry.insert(0, item[1])
        self.price_entry.delete(0, ctk.END)
        # Убираем знак евро для ввода в поле
        self.price_entry.insert(0, item[2].replace(" €", ""))
        self.allergens_entry.delete(0, ctk.END)
        self.allergens_entry.insert(0, item[3])

    def add_to_cart(self):
        product_id = int(self.id_entry.get())
        quantity = int(self.quantity_entry.get())
        cursor = self.conn.cursor()
        cursor.execute("SELECT name, price FROM products WHERE id = ?", (product_id,))
        product = cursor.fetchone()
        if product:
            name, price = product
            self.cart.append((name, quantity, price * quantity))
            self.total += price * quantity
            self.update_cart_display()

    def update_cart_display(self):
        self.cart_listbox.delete("1.0", ctk.END)
        for item in self.cart:
            self.cart_listbox.insert(ctk.END, f"{item[0]} x {item[1]}: €{item[2]:.2f}\n")
        self.total_label.configure(text=f"Kokku: €{self.total:.2f}")

    def pay_cash(self):
        cash_given = float(simpledialog.askstring("Sisestage sularahasumma", "Sisestage summa sularahas, mille klient andis:"))
        if cash_given is not None:
            change = cash_given - self.total
            if change >= 0:
                messagebox.showinfo("Tagasimakse", f"Tagasimakse: €{change:.2f}")
                self.cart = []
                self.total = 0.0
                self.update_cart_display()
            else:
                messagebox.showerror("Viga", "Maksmiseks pole piisavalt sularaha.")

    def pay_card(self):
        messagebox.showinfo("Maksmine", "Kaardimakse oli edukas.")
        self.cart = []
        self.total = 0.0
        self.update_cart_display()



if __name__ == "__main__":
    ctk.set_appearance_mode("dark")  # "dark" or "light"
    ctk.set_default_color_theme("blue")  # "blue" or "green"
    root = ctk.CTk()
    app = StoreApp(root)
    root.mainloop()
