import streamlit as st
import sqlite3
import qrcode
from datetime import date

class ApplianceManager:
    def __init__(self):
        # Initialize database connection
        self.conn = sqlite3.connect('appliance_manager.db', check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS houses (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
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

    def get_houses(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name FROM houses")
        return cursor.fetchall()

    def get_appliances_by_house(self, house_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name FROM appliances WHERE house_id = ?", (house_id,))
        return cursor.fetchall()

    def add_house(self, name, address):
        cursor = self.conn.cursor()
        try:
            cursor.execute("INSERT INTO houses (name, address) VALUES (?, ?)", 
                           (name, address))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            st.error(f"A house named '{name}' already exists.")
            return None

    def add_appliance(self, house_id, name, brand, model, purchase_date):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO appliances 
            (house_id, name, brand, model, purchase_date) 
            VALUES (?, ?, ?, ?, ?)
        """, (house_id, name, brand, model, purchase_date))
        appliance_id = cursor.lastrowid
        self.conn.commit()
        return appliance_id

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
        ["Add House", "Add Appliance", "View Appliances", "Manage Appliance"])

    if menu == "Add House":
        st.header("Add New House")
        house_name = st.text_input("House Name")
        house_address = st.text_input("House Address")
        
        if st.button("Add House"):
            if house_name and house_address:
                house_id = manager.add_house(house_name, house_address)
                if house_id:
                    st.success(f"House added successfully!")
            else:
                st.warning("Please enter both house name and address.")

    elif menu == "Add Appliance":
        st.header("Add New Appliance")
        
        # Get list of houses
        houses = manager.get_houses()
        if not houses:
            st.warning("Please add a house first.")
        else:
            # Create house selection dropdown
            house_options = {name: id for id, name in houses}
            selected_house_name = st.selectbox("Select House", list(house_options.keys()))
            selected_house_id = house_options[selected_house_name]

            # Appliance details
            appliance_name = st.text_input("Appliance Name")
            brand = st.text_input("Brand")
            model = st.text_input("Model")
            purchase_date = st.date_input("Purchase Date", date.today())

            if st.button("Add Appliance"):
                if appliance_name and brand and model:
                    appliance_id = manager.add_appliance(
                        selected_house_id, 
                        appliance_name, 
                        brand, 
                        model, 
                        purchase_date
                    )
                    st.success(f"Appliance added successfully! ID: {appliance_id}")
                else:
                    st.warning("Please fill in all appliance details.")

    elif menu == "View Appliances":
        st.header("View Appliances")
        
        # Get list of houses
        houses = manager.get_houses()
        if not houses:
            st.warning("Please add a house first.")
        else:
            # Create house selection dropdown
            house_options = {name: id for id, name in houses}
            selected_house_name = st.selectbox("Select House", list(house_options.keys()))
            selected_house_id = house_options[selected_house_name]

            # Get appliances for selected house
            appliances = manager.get_appliances_by_house(selected_house_id)
            
            if not appliances:
                st.warning("No appliances found for this house.")
            else:
                # Create a radio button for appliance selection
                appliance_names = [name for _, name in appliances]
                selected_appliance_name = st.radio("Select Appliance", appliance_names)
                
                # Find the ID of the selected appliance
                selected_appliance_id = next(
                    id for id, name in appliances if name == selected_appliance_name
                )

                # Manage button becomes active when an appliance is selected
                if st.button("Manage Selected Appliance"):
                    st.write(f"Managing Appliance: {selected_appliance_name}")
                    # Here you would add the logic for managing the specific appliance

    elif menu == "Manage Appliance":
        st.header("Manage Appliance")
        st.write("Future functionality for detailed appliance management")

if __name__ == "__main__":
    main()
