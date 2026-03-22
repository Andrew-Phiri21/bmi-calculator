import streamlit as st
import sqlite3
import pandas as pd
import hashlib


#--- Building a BMI Calculator with AI-Driven Health Protocols ---
#--- The goal is to create a user-friendly interface that not only calculates BMI but also provides personalized health advice based on the user's BMI category. The app will include secure user authentication, data storage, and visualization of progress over time.
#--- The app is lightweight and designed to run efficiently on Streamlit's free tier, ensuring accessibility for all users. The AI-driven advice is based on established health guidelines and is presented in a clear, actionable format.

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

# --- 3. LIBRARY & CALCULATION LOGIC ---
def get_ai_advice(bmi_val):
    if bmi_val < 18.5:
       return {
            "status": "Underweight", 
            "color": "blue",
            "advice": """
                **Protocol: Hypertrophy & Nutrient Density**
                Focus on 'Healthy Bulking' using complex African carbohydrates and high-protein legumes. 
                * **Key Focus**: Strength training 3x weekly to convert surplus calories into lean muscle.
                * **Tip**: Use healthy fats like Red Palm Oil (in moderation) or Peanut butter for extra calories.
            """,
            "meal_plan": """
                * **Breakfast**: Thick Millet or Sorghum porridge (Ugi/Pap) enriched with groundnut paste and milk / Nshima.
                * **Lunch**: Pounded Yam or Cassava (rich in protein/fats) and goat meat or fish.
                * **Snack**: Roasted Plantains with a handful of peanuts.
                * **Dinner**: Rice (parboiled rice) served with grilled chicken and a side of beans.
            """
        }
        
    elif 18.5 <= bmi_val <= 24.9:
        return {
            "status": "Normal (Optimal)", 
            "color": "green",
            "advice": """
                **Protocol: Maintenance & Metabolic Performance**
                You are in the optimal range. The goal is to maintain energy levels and prevent oxidative stress using indigenous antioxidants.
                * **Key Focus**: Diversify your intake of traditional greens (Lumanda, Spinach, or Cassava leaves).
                * **Tip**: Replace refined white rice with ancient brown rice.
            """,
            "meal_plan": """
                * **Breakfast**: Boiled Sweet Potato or Cassava with a boiled egg and black tea/coffee.
                * **Lunch**: Grilled Tilapia served with a side of Kachumbari or any salad and moderate Nshima.
                * **Snack**: Fresh fruit—Mango, Papaya, or Guava.
                * **Dinner**: Lean Beef stew with plenty of carrots and bell peppers, served with a small portion of Couscous or Rice.
            """
        }
        
    elif 25.0 <= bmi_val <= 29.9:
        return {
            "status": "Overweight", 
            "color": "orange",
            "advice": """
                **Protocol: Metabolic Optimization & Fiber Increase**
                Prioritize fat oxidation by swapping high-glycemic starches for high-fiber traditional options.
                * **Key Focus**: 10k steps daily + HIIT training. Increase vegetable-to-starch ratio to 2:1.
                * **Tip**: Drink Hibiscus tea (Zobo/Bissap) without sugar to help manage blood pressure and hydration.
            """,
            "meal_plan": """
                * **Breakfast**: A small bowl of watery Oats or Millet porridge or Oatmeal.
                * **Lunch**: Okra Soup (high fiber) with a small portion of Wheat - and steamed fish.
                * **Snack**: Garden eggs (Eggplant) with a small amount of spicy peanut dip.
                * **Dinner**: Grilled Chicken breast with a massive side of steamed Cabbage and beans, heavy on beans).
            """
        }
    else:
        return {
            "status": "Obese", 
            "color": "red",
            "advice": """
                **Protocol: Anti-Inflammatory & Therapeutic Intervention**
                Focus on reducing systemic inflammation and improving insulin sensitivity. 
                * **Key Focus**: Eliminate all soda and processed malt drinks. Focus on low-impact movement like brisk walking.
                * **Tip**: Use spices like Ginger, Turmeric, and Garlic heavily in cooking for their anti-inflammatory properties.
            """,
            "meal_plan": """
                * **Breakfast**: Garden egg sauce with two small slices of boiled Yam or a green smoothie with Moringa.
                * **Lunch**: Lean Vegetable Soup without oil, served with grilled fish (no swallow/starch).
                * **Snack**: Sliced cucumber or a few segments of Grapefruit.
                * **Dinner**: Pepper Soup (Chicken or Fish) loaded with herbs and spices, served with extra leafy greens on the side.
            """
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
                
                tab1, tab2 = st.tabs(["📋 Action Plan", "🍎 Sample Meal Plan"])
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
