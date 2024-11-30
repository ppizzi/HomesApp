import streamlit as st
import sqlite3

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
                description TEXT,
                UNIQUE(house_id, name),
                FOREIGN KEY(house_id) REFERENCES houses(id)
            )
        ''')
        self.conn.commit()

    def get_houses(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name FROM houses")
        return cursor.fetchall()

    def get_appliances_by_house(self, house_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name, description FROM appliances WHERE house_id = ?", (house_id,))
        return cursor.fetchall()

    def add_appliance(self, house_id, name, description):
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO appliances 
                (house_id, name, description) 
                VALUES (?, ?, ?)
            """, (house_id, name, description))
            appliance_id = cursor.lastrowid
            self.conn.commit()
            return appliance_id
        except sqlite3.IntegrityError:
            st.error(f"An appliance named '{name}' already exists in this house.")
            return None

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
            if house_name:
                try:
                    cursor = manager.conn.cursor()
                    cursor.execute("INSERT INTO houses (name, address) VALUES (?, ?)", 
                                   (house_name, house_address))
                    manager.conn.commit()
                    st.success(f"House '{house_name}' added successfully!")
                except sqlite3.IntegrityError:
                    st.error(f"A house named '{house_name}' already exists.")
            else:
                st.warning("Please enter a house name.")

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
            appliance_name = st.text_input("Appliance Name *")
            appliance_description = st.text_area("Appliance Description")

            if st.button("Add Appliance"):
                if appliance_name:
                    appliance_id = manager.add_appliance(
                        selected_house_id, 
                        appliance_name, 
                        appliance_description
                    )
                    if appliance_id:
                        st.success(f"Appliance '{appliance_name}' added successfully!")
                else:
                    st.warning("Appliance Name is required.")

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
                st.write("Appliances in this house:")
                for appliance_id, name, description in appliances:
                    st.write(f"**{name}**")
                    if description:
                        st.write(f"*{description}*")

if __name__ == "__main__":
    main()
