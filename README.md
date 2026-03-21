# bmi-calculator
A simple Body Mass Index Calculator
****************************************
⚖️ BMI Calculator
BMI Caluculator a full-stack Python web application designed to track user BMI, provide personalized health recommendations using AI logic, and visualize weight trends over time. It features a secure authentication system to keep user data private and persistent.

🚀 Key Features
Secure Authentication: User accounts with salted and hashed passwords (SHA-256).

AI Health Analysis: Dynamic BMI calculation with personalized advice based on health zones.

Persistent Data: Integration with a SQLite database for long-term progress tracking.

Data Visualization: Interactive line charts powered by Pandas and Streamlit to monitor weight trends.

Self-Healing Database: Automatic schema migration logic to ensure the database stays up to date.

🛠️ Tech Stack
Frontend: Streamlit (Python Web Framework)

Backend: Python 3.x

Database: SQLite3

Data Science: Pandas (for data manipulation and graphing)

Security: Hashlib (SHA-256 encryption)

📦 Installation & Setup
Clone the repository:

Bash
git clone https://github.com/Andrew-Phiri21/bmi-app.git
cd ultron-bmi-app
Install dependencies:

Bash
pip install streamlit pandas
Run the application:

Bash
python -m streamlit run app.py
📂 Project Structure
app.py: The main application script containing logic, UI, and database functions.

requirements.txt: List of Python packages required for deployment.

andrew_fitness.db: (Auto-generated) The SQLite database file storing user credentials and history.

🛡️ Security Note
This application uses Salting and Hashing to protect user passwords. Raw passwords are never stored in the database, ensuring that user identities remain secure even if the database file is accessed.

👨‍💻 Author
Andrew Phiri
