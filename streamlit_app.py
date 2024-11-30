import streamlit as st
import qrcode
import pandas as pd
import sqlite3

class ApplianceManager:
    def __init__(self):
        # Initialize database connection
        self.conn = sqlite3.connect('appliance_manager.db')
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS houses (
                id INTEGER PRIMARY KEY,
                name TEXT,
                address TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS appliances (
                id INTEGER PRIMARY KEY,
                house_id INTEGER,
                name TEXT,
                brand TEXT,
                model TEXT,
                purchase_date DATE,
                FOREIGN KEY(house_id) REFERENCES houses(id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY,
                appliance_id INTEGER,
                manual_path TEXT,
                video_path TEXT,
                warranty_images TEXT,
                notes TEXT,
                serial_number TEXT,
                qr_code_path TEXT,
                FOREIGN KEY(appliance_id) REFERENCES appliances(id)
            )
        ''')
        self.conn.commit()

    def add_house(self, name, address):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO houses (name, address) VALUES (?, ?)", 
                       (name, address))
        self.conn.commit()
        return cursor.lastrowid

    def add_appliance(self, house_id, name, brand, model, purchase_date):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO appliances 
            (house_id, name, brand, model, purchase_date) 
            VALUES (?, ?, ?, ?, ?)
        """, (house_id, name, brand, model, purchase_date))
        self.conn.commit()
        return cursor.lastrowid

    def generate_qr_code(self, appliance_id):
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(f'appliance/{appliance_id}')
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        path = f'qr_codes/appliance_{appliance_id}.png'
        img.save(path)
        return path

def main():
    st.title("Appliance Management System")
    
    manager = ApplianceManager()

    menu = st.sidebar.selectbox("Menu", 
        ["Add House", "Add Appliance", "View Appliances"])

    if menu == "Add House":
        st.header("Add New House")
        house_name = st.text_input("House Name")
        house_address = st.text_input("House Address")
        
        if st.button("Add House"):
            house_id = manager.add_house(house_name, house_address)
            st.success(f"House added with ID: {house_id}")

    elif menu == "Add Appliance":
        st.header("Add New Appliance")
        # Additional form elements for appliance details

if __name__ == "__main__":
    main()
