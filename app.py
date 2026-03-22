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
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT PRIMARY KEY, password TEXT)')
    c.execute('''
        CREATE TABLE IF NOT EXISTS bmi_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            weight REAL,
            bmi REAL
        )
    ''')
    try:
        c.execute('ALTER TABLE bmi_history ADD COLUMN username TEXT')
        conn.commit()
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()

# --- 3. AI & CALCULATION LOGIC ---
def get_ai_advice(bmi_val):
    if bmi_val < 18.5:
        return {
            "status": "Underweight", "color": "blue",
            "advice": "**Protocol: Hypertrophy & Caloric Surplus**\nYour current mass is below optimal. Focus on nutrient density and strength training.",
            "meal_plan": "* **Breakfast**: 3-egg omelet\n* **Lunch**: Grilled salmon & quinoa\n* **Dinner**: Beef stir-fry."
        }
    elif 18.5 <= bmi_val <= 24.9:
        return {
            "status": "Normal (Optimal)", "color": "green",
            "advice": "**Protocol: Maintenance & Performance**\nYou are in the Goldilocks Zone. Maintain homeostasis and functional movement.",
            "meal_plan": "* **Breakfast**: Overnight oats\n* **Lunch**: Turkey spinach wrap\n* **Dinner**: Baked chicken & asparagus."
        }
    elif 25.0 <= bmi_val <= 29.9:
        return {
            "status": "Overweight", "color": "orange",
            "advice": "**Protocol: Metabolic Optimization**\nPrioritize fat oxidation and a slight caloric deficit. Aim for 10k steps daily.",
            "meal_plan": "* **Breakfast**: Scrambled egg whites\n* **Lunch**: Large green salad with chicken\n* **Dinner**: White fish & cauliflower rice."
        }
    else:
        return {
            "status": "Obese", "color": "red",
            "advice": "**Protocol: Therapeutic Intervention**\nReduce inflammation. Eliminate liquid sugars and focus on low-impact cardio.",
            "meal_plan": "* **Breakfast**: Chia pudding\n* **Lunch**: Lentil soup\n* **Dinner**: Grilled tofu & green beans."
        }

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
            c.execute('INSERT INTO userstable(username, password) VALUES (?,?)', (new_user, make_hashes(new_pass)))
            conn.commit()
            st.success("Account Forged! Proceed to Login.")
        except sqlite3.IntegrityError:
            st.error("This username already exists.")

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
            st.success(f"Welcome, {user}")
            
            col1, col2 = st.columns(2)
            with col1:
                weight = st.number_input("Weight (kg)", min_value=1.0, value=75.0)
            with col2:
                height = st.number_input("Height (m)", min_value=0.5, value=1.75)
            
            if st.button("Calculate & Save to History"):
                bmi = weight / (height**2)
                report = get_ai_advice(bmi)
                
                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()
                c.execute('INSERT INTO bmi_history(username, weight, bmi) VALUES (?,?,?)', (user, weight, bmi))
                conn.commit()
                conn.close()
                
                st.header(f"Health Analysis for {user}")
                st.subheader(f"BMI Score: {bmi:.2f}")
                st.markdown(f"### Current Standing: :{report['color']}[{report['status']}]")
                
                tab1, tab2 = st.tabs(["📋 AI Protocol", "🍎 Sample Meal Plan"])
                with tab1:
                    st.write(report['advice'])
                with tab2:
                    st.write(report['meal_plan'])

            # --- DATA VISUALIZATION ---
            st.markdown("---")
            st.write("### 📈 Your Personal Progress")
            conn = sqlite3.connect(DB_NAME)
            history_df = pd.read_sql(f"SELECT timestamp, weight, bmi FROM bmi_history WHERE username='{user}'", conn)
            
            if not history_df.empty:
                st.line_chart(history_df.set_index('timestamp')['weight'])
                st.dataframe(history_df)
            else:
                st.write("No data recorded yet.")
        else:
            if user and passwd:
                st.sidebar.error("Invalid Username or Password.")

# --- 5. THE FOOTER ---
st.markdown("---")
foot_col1, foot_col2, foot_col3 = st.columns([1, 2, 1])
with foot_col2:
    st.markdown(
        """<div style="text-align: center;"><p style="font-family: 'Courier New', Courier; color: #888; font-size: 0.9em;">
        Powered by <a href="https://dataamnis.netlify.app/?#" target="_blank" style="color: #00d4ff; text-decoration: none; font-weight: bold;">DataAmnis</a>
        </p></div>""", unsafe_allow_html=True)
