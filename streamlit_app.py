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

def add_appliance_page(manager):
    st.header("Add New Appliance")
    
    # Get list of houses
    houses = manager.get_houses()
    if not houses:
        st.warning("Please add a house first.")
        return

    # Create house selection dropdown
    house_options = {name: id for id, name in houses}
    selected_house_name = st.selectbox("Select House", list(house_options.keys()))
    selected_house_id = house_options[selected_house_name]

    # Use st.form to manage input and submission
    with st.form("add_appliance_form", clear_on_submit=True):
        # Appliance details
        appliance_name = st.text_input("Appliance Name *")
        appliance_description = st.text_area("Appliance Description")

        # Submit button
        submitted = st.form_submit_button("Add Appliance")

        # Handle form submission
        if submitted:
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

# Rest of the code remains the same as in the previous implementation
def main():
    # Initialize session state for page navigation
    if 'page' not in st.session_state:
        st.session_state.page = 'Add House'

    # Create a manager instance
    manager = ApplianceManager()

    # Sidebar navigation
    st.sidebar.title("Navigation")
    pages = ["Add House", "Add Appliance", "View Appliances", "Manage Appliance"]
    selected_page = st.sidebar.radio("Go to", pages, index=pages.index(st.session_state.page))
    
    # Page routing
    if selected_page == "Add House":
        add_house_page(manager)
    elif selected_page == "Add Appliance":
        add_appliance_page(manager)
    elif selected_page == "View Appliances":
        view_appliances_page(manager)
    elif selected_page == "Manage Appliance":
        manage_appliance_page(manager)

    # Update session state
    st.session_state.page = selected_page

if __name__ == "__main__":
    main()
