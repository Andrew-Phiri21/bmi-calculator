import streamlit as st
import sqlite3
import pandas as pd
import hashlib

# --- 1. GLOBAL CONSTANTS ---
DB_NAME = "andrew_fitness.db"
SALT = "DataAmnis_2026" 

# --- 2. SECURITY & DATABASE LOGIC ---
def make_hashes(password):
    salted_pass = password + SALT
    return hashlib.sha256(str.encode(salted_pass)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

def init_db():
    """Forges the tables and performs 'Self-Healing' migrations."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Create User Table
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT PRIMARY KEY, password TEXT)')
    
    # Create History Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS bmi_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            weight REAL,
            bmi REAL
        )
    ''')
    
    # --- SELF-HEALING MIGRATION ---
    # This checks if the 'username' column exists, and adds it if it's missing
    try:
        c.execute('ALTER TABLE bmi_history ADD COLUMN username TEXT')
        conn.commit()
    except sqlite3.OperationalError:
        # This error happens if the column already exists, so we just ignore it
        pass
        
    conn.commit()
    conn.close()

# --- 3. AI & CALCULATION LOGIC ---
def get_ai_advice(bmi_val):
    if bmi_val < 18.5:
        return "Underweight", "blue", "Increase protein intake and focus on resistance training."
    elif 18.5 <= bmi_val <= 24.9:
        return "Normal", "green", "You are in the safe zone. Keep it up!"
    else:
        return "Overweight", "orange", "Focus on a caloric deficit and steady cardio."

# --- 4. THE INTERFACE ---
st.set_page_config(page_title="BMI Calculator", page_icon="⚖️")
init_db()

st.title("⚖️ BMI Calculator")

menu = ["Login", "SignUp"]
choice = st.sidebar.selectbox("Access Level", menu)

if choice == "SignUp":
    st.subheader("Create a New Identity")
    new_user = st.text_input("Choose Username")
    new_pass = st.text_input("Choose Password", type='password')
    
    if st.button("Initialize Account"):
        try:
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute('INSERT INTO userstable(username, password) VALUES (?,?)', 
                      (new_user, make_hashes(new_pass)))
            conn.commit()
            st.success("Account Forged! Proceed to Login.")
        except sqlite3.IntegrityError:
            st.error("This username already exists in my database.")

elif choice == "Login":
    st.sidebar.subheader("Login Credentials")
    user = st.sidebar.text_input("Username")
    passwd = st.sidebar.text_input("Password", type='password')
    
    if st.sidebar.checkbox("Login"):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('SELECT password FROM userstable WHERE username =?', (user,))
        data = c.fetchone()
        
        if data and check_hashes(passwd, data[0]):
            st.success(f"Welcome, Commander {user}")
            
            # --- MAIN APP LOGIC ---
            col1, col2 = st.columns(2)
            with col1:
                weight = st.number_input("Weight (kg)", min_value=1.0, value=75.0)
            with col2:
                height = st.number_input("Height (m)", min_value=0.5, value=1.75)
            
            if st.button("Calculate & Save to History"):
                bmi = weight / (height**2)
                status, color, advice = get_ai_advice(bmi)
                
                # Save specifically for this user
                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()
                c.execute('INSERT INTO bmi_history(username, weight, bmi) VALUES (?,?,?)', (user, weight, bmi))
                conn.commit()
                
                st.subheader(f"BMI Result: {bmi:.2f}")
                st.write(f"Status: :{color}[{status}]")
                st.info(f"**AI Advice:** {advice}")

            # --- DATA VISUALIZATION ---
            st.markdown("---")
            st.write("### 📈 Your Personal Progress")
            conn = sqlite3.connect(DB_NAME)
            # Fetching data only for current user
            history_df = pd.read_sql(f"SELECT timestamp, weight, bmi FROM bmi_history WHERE username='{user}'", conn)
            
            if not history_df.empty:
                st.line_chart(history_df.set_index('timestamp')['weight'])
                st.dataframe(history_df)
            else:
                st.write("No data recorded yet. Take your first measurement!")
        else:
            if user and passwd: # Only show error if they actually tried to log in
                st.sidebar.error("Invalid Username or Password.")

st.markdown("---")
st.caption("Poered by DataAmnis ⚡")