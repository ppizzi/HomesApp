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

def add_house_page(manager):
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

def view_appliances_page(manager):
    st.header("View Appliances")
    
    # Get list of houses
    houses = manager.get_houses()
    if not houses:
        st.warning("Please add a house first.")
        return

    # Create house selection dropdown
    house_options = {name: id for id, name in houses}
    selected_house_name = st.selectbox("Select House", list(house_options.keys()))
    selected_house_id = house_options[selected_house_name]

    # Get appliances for selected house
    appliances = manager.get_appliances_by_house(selected_house_id)
    
    if not appliances:
        st.warning("No appliances found for this house.")
        return

    # Create a radio button for appliance selection
    appliance_options = {name: (id, description) for id, name, description in appliances}
    selected_appliance_name = st.radio("Select Appliance", list(appliance_options.keys()))
    
    # Get details of selected appliance
    selected_appliance_id, selected_appliance_description = appliance_options[selected_appliance_name]

    # Display appliance description
    if selected_appliance_description:
        st.write("Description:", selected_appliance_description)

    # Manage button
    if st.button("Manage Appliance"):
        # Store selected appliance in session state for use in manage page
        st.session_state.selected_appliance = {
            'id': selected_appliance_id,
            'name': selected_appliance_name,
            'house_id': selected_house_id,
            'house_name': selected_house_name
        }
        # Navigate to Manage Appliance page
        st.experimental_set_query_params(page="Manage Appliance")
def manage_appliance_page(manager):
    st.header("Manage Appliance")
    
    # Check if an appliance is selected
    if 'selected_appliance' not in st.session_state:
        st.warning("Please select an appliance first.")
        return

    appliance = st.session_state.selected_appliance
    st.write(f"Managing Appliance: **{appliance['name']}**")
    st.write(f"In House: **{appliance['house_name']}**")

    # Placeholder for future functionality
    st.write("Appliance management features coming soon...")

def main():
    # Initialize session state for page navigation
    if 'page' not in st.session_state:
        st.session_state.page = 'Add House'

    # Create a manager instance
    manager = ApplianceManager()

    # Sidebar navigation
    st.sidebar.title("Navigation")
    pages = ["Add House", "Add Appliance", "View Appliances", "Manage Appliance"]
    query_params = st.experimental_get_query_params()
    if 'page' in query_params:
        selected_page = query_params['page'][0]
    else:
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
