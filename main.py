import streamlit as st
import json
import hashlib
import os
from datetime import datetime

# App Name and Config
APP_NAME = "GreenWallet"
APP_LOGO = "💳"  # Green circle + credit card emoji

# User class
class User:
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = hashlib.sha256(password.encode()).hexdigest()

    def to_dict(self):
        return {
            "username": self.username,
            "email": self.email,
            "password": self.password
        }

# Payment class
class Payment:
    def __init__(self, user_id, amount, description):
        self.user_id = user_id
        self.amount = amount
        self.description = description
        self.date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "amount": self.amount,
            "description": self.description,
            "date": self.date
        }

# Database class
class Database:
    def __init__(self):
        self.data_file = "greenwallet_data.json"
        self.data = self._load_data()

    def _load_data(self):
        if not os.path.exists(self.data_file):
            return {"users": [], "payments": []}
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except:
            return {"users": [], "payments": []}

    def save_data(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=4)

    def add_user(self, user):
        for existing_user in self.data["users"]:
            if existing_user["username"] == user.username:
                return False
        self.data["users"].append(user.to_dict())
        self.save_data()
        return True

    def get_user(self, username, password):
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        for user in self.data["users"]:
            if user["username"] == username and user["password"] == hashed_password:
                return user
        return None

    def add_payment(self, payment):
        self.data["payments"].append(payment.to_dict())
        self.save_data()

    def get_user_payments(self, user_id):
        return [p for p in self.data["payments"] if p["user_id"] == user_id]

# Initialize database
db = Database()

# Streamlit app configuration
st.set_page_config(
    page_title=APP_NAME,
    layout="wide",
    page_icon="🟢"
)

# Enhanced CSS for green theme
st.markdown(f"""
    <style>
    .stApp {{
        background-color: #071907;
        color: white;
    }}
    .stSidebar {{
        background-color: #0f452a !important;
    }}
    .stButton>button {{
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: bold;
    }}
    .stButton>button:hover {{
        background-color: #45a049;
    }}
    .stTextInput>div>div>input {{
        background-color: #002200;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 8px;
    }}
    .metric-card {{
        background-color: #004d26;
        padding: 20px;
        border-radius: 8px;
        margin: 10px 0;
    }}
    .payment-card {{
        background-color: #004d26;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 12px;
        border-left: 4px solid #4CAF50;
    }}
    </style>
""", unsafe_allow_html=True)

# Session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.user_id = None

# Main Function
def main():
    # Header with Logo and App Name
    st.markdown(f"""
        <div style='text-align: center; padding: 30px 0 20px 0;'>
            <div style="font-size: 60px;">{APP_LOGO}</div>
            <div style='font-size: 42px; font-weight: bold; color: #4CAF50;'>{APP_NAME}</div>
        </div>
    """, unsafe_allow_html=True)

    # Sidebar Menu
    if st.session_state.logged_in:
        menu_option = st.sidebar.radio(
            "Menu",
            ["Dashboard", "Make Payment", "Payment History", "Logout"]
        )
    else:
        menu_option = st.sidebar.radio(
            "Menu",
            ["Login", "Register"]
        )

    # LOGIN
    if menu_option == "Login" and not st.session_state.logged_in:
        st.markdown("<h3 style='text-align: center;'>Login</h3>", unsafe_allow_html=True)
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("Login")

        if login_button:
            user = db.get_user(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.username = user["username"]
                st.session_state.user_id = user["username"]
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid username or password")

    # REGISTER
    elif menu_option == "Register" and not st.session_state.logged_in:
        st.markdown("<h3 style='text-align: center;'>Register</h3>", unsafe_allow_html=True)
        with st.form("register_form", clear_on_submit=False):
            new_username = st.text_input("New Username")
            new_email = st.text_input("Email")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            register_button = st.form_submit_button("Register")

        if register_button:
            if new_password == confirm_password:
                new_user = User(new_username, new_email, new_password)
                if db.add_user(new_user):
                    st.success("Registration successful! Please log in.")
                else:
                    st.error("Username already exists")
            else:
                st.error("Passwords do not match")

    # DASHBOARD
    elif menu_option == "Dashboard" and st.session_state.logged_in:
        st.title(f"Welcome to {APP_NAME}, {st.session_state.username}!")
        st.write("Your personal finance dashboard")
        payments = db.get_user_payments(st.session_state.user_id)
        total = sum(float(p["amount"]) for p in payments)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
                <div class="metric-card">
                    <h3>Total Payments</h3>
                    <h1>${total:,.2f}</h1>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            if payments:
                latest = max(payments, key=lambda x: x["date"])
                st.markdown(f"""
                    <div class="metric-card">
                        <h3>Latest Payment</h3>
                        <h1>${float(latest['amount']):,.2f}</h1>
                        <p>{latest['description']}</p>
                    </div>
                """, unsafe_allow_html=True)

    # MAKE PAYMENT
    elif menu_option == "Make Payment" and st.session_state.logged_in:
        st.title("Make a Payment")
        with st.form("payment_form"):
            amount = st.number_input("Amount ($)", min_value=0.01, step=0.01, format="%.2f")
            description = st.text_input("Description")
            submit = st.form_submit_button("Submit Payment")
            if submit:
                payment = Payment(st.session_state.user_id, amount, description)
                db.add_payment(payment)
                st.success("Payment submitted successfully!")
                st.rerun()

    # PAYMENT HISTORY
    elif menu_option == "Payment History" and st.session_state.logged_in:
        st.title("Payment History")
        payments = db.get_user_payments(st.session_state.user_id)
        if not payments:
            st.info("No payment history found.")
        else:
            for p in sorted(payments, key=lambda x: x["date"], reverse=True):
                st.markdown(f"""
                    <div class="payment-card">
                        <div style="display: flex; justify-content: space-between;">
                            <strong>{p['description']}</strong>
                            <strong>${float(p['amount']):,.2f}</strong>
                        </div>
                        <p><small>{p['date']}</small></p>
                    </div>
                """, unsafe_allow_html=True)

    # LOGOUT
    elif menu_option == "Logout":
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.user_id = None
        st.success("Logged out successfully.")
        st.rerun()

if __name__ == "__main__":
    main()
