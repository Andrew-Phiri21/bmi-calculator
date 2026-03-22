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
    """The AI engine providing deep nutritional and lifestyle protocols."""
    
    if bmi_val < 18.5:
        return {
            "status": "Underweight",
            "color": "blue",
            "advice": """
                **Protocol: Hypertrophy & Caloric Surplus**
                Your current mass is below the optimal threshold. We need to focus on **Nutrient Density**. 
                Avoid 'dirty bulking' (junk food); instead, aim for complex carbs and high protein to build lean muscle tissue.
                * **Key Focus**: Strength training 3-4 times a week.
                * **Hydration**: Drink calories (protein shakes, smoothies) if solid meals are difficult.
            """,
            "meal_plan": """
                * **Breakfast**: 3-egg omelet with avocado and whole-grain toast.
                * **Lunch**: Grilled salmon with a double serving of quinoa and roasted sweet potatoes.
                * **Snack**: Greek yogurt with honey, walnuts, and chia seeds.
                * **Dinner**: Lean beef stir-fry with broccoli and brown rice, sautéed in olive oil.
            """
        }
        
    elif 18.5 <= bmi_val <= 24.9:
        return {
            "status": "Normal (Optimal)",
            "color": "green",
            "advice": """
                **Protocol: Maintenance & Performance**
                You are in the 'Goldilocks Zone.' Your objective is to maintain this homeostasis while improving athletic performance or body composition.
                * **Key Focus**: Functional movement and cardiovascular endurance.
                * **Micronutrients**: Ensure a diverse intake of colorful vegetables for recovery.
            """,
            "meal_plan": """
                * **Breakfast**: Overnight oats with berries and a scoop of whey protein.
                * **Lunch**: Turkey breast wrap with spinach, tomatoes, and hummus.
                * **Snack**: An apple with a small handful of almonds.
                * **Dinner**: Baked chicken breast with asparagus and a small portion of couscous.
            """
        }
        
    elif 25.0 <= bmi_val <= 29.9:
        return {
            "status": "Overweight",
            "color": "orange",
            "advice": """
                **Protocol: Metabolic Optimization**
                Your BMI indicates a need for a slight caloric deficit. We want to prioritize **Fat Oxidation** while preserving muscle mass.
                * **Key Focus**: High-Intensity Interval Training (HIIT) combined with steady-state walking (10k steps).
                * **Fiber**: Increase fiber intake to stay satiated longer.
            """,
            "meal_plan": """
                * **Breakfast**: Scrambled egg whites with spinach and mushrooms.
                * **Lunch**: Large green salad with grilled chicken, lemon vinaigrette (no mayo).
                * **Snack**: Celery sticks with a tablespoon of almond butter.
                * **Dinner**: White fish (Cod or Tilapia) with steamed zucchini and cauliflower rice.
            """
        }
    else:
        return {
            "status": "Obese",
            "color": "red",
            "advice": """
                **Protocol: Therapeutic Intervention**
                It is vital to reduce systemic inflammation and improve insulin sensitivity. Small, consistent changes are more effective than radical diets.
                * **Key Focus**: Low-impact cardio (swimming/cycling) to protect joints. 
                * **Sugar**: Eliminate liquid sugars (sodas/juices) immediately.
            """,
            "meal_plan": """
                * **Breakfast**: Chia seed pudding made with unsweetened almond milk.
                * **Lunch**: Lentil soup with a side of steamed kale.
                * **Snack**: A few slices of cucumber with a pinch of sea salt.
                * **Dinner**: Grilled tofu or lean turkey patties with a massive serving of green beans.
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
            st.success(f"Welcome, {user}")
            
            # --- MAIN APP LOGIC ---
            col1, col2 = st.columns(2)
            with col1:
                weight = st.number_input("Weight (kg)", min_value=1.0, value=75.0)
            with col2:
                height = st.number_input("Height (m)", min_value=0.5, value=1.75)
            
           if st.button("Calculate & Save to History"):
                bmi = weight / (height**2)
                # Call our new enriched AI engine
                report = get_ai_advice(bmi)
                
                # Save to DB
                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()
                c.execute('INSERT INTO bmi_history(username, weight, bmi) VALUES (?,?,?)', (user, weight, bmi))
                conn.commit()
                conn.close()
                
                # --- DISPLAY RICH UI ---
                st.header(f"Health Analysis for {user}")
                st.subheader(f"BMI Score: {bmi:.2f}")
                st.markdown(f"### Current Standing: :{report['color']}[{report['status']}]")
                
                # Using Tabs for a cleaner look
                tab1, tab2 = st.tabs(["📋 AI Protocol", "🍎 Sample Meal Plan"])
                
                with tab1:
                    st.write(report['advice'])
                
                with tab2:
                    st.write(report['meal_plan'])

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

# --- 5. THE FOOTER (Branding & Credits) ---
st.markdown("---")
foot_col1, foot_col2, foot_col3 = st.columns([1, 2, 1])

with foot_col2:
    st.markdown(
        """
        <div style="text-align: center;">
            <p style="font-family: 'Courier New', Courier, monospace; color: #888; font-size: 0.9em;">
                Powered by <a href="https://dataamnis.netlify.app/?#" target="_blank" 
                style="color: #00d4ff; text-decoration: none; font-weight: bold;">DataAmnis</a>
            </p>
        </div>
        """,
        unsafe_allow_html=True)
