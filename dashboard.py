import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, auth
import matplotlib.pyplot as plt
import pandas as pd


cred = credentials.Certificate("service_account.json")
firebase_admin.initialize_app(cred)


db = firestore.client()


def fetch_user_data(user_id):
    doc_ref = db.collection("users").document(user_id)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    else:
        return None


def fetch_all_users_data():
    users_ref = db.collection("users")
    docs = users_ref.stream()
    users_data = [doc.to_dict() for doc in docs]
    return users_data


def login():
    st.sidebar.subheader("logins")
    email = st.sidebar.text_input("email")
    password = st.sidebar.text_input("password", type="password")
    if st.sidebar.button("Login"):
        try:
            user = auth.get_user_by_email(email)
            # Normally, we should verify the password here, but for simplicity, we're skipping it
            st.session_state["user_id"] = user.uid
            st.session_state["email"] = email
            st.sidebar.success(f"Logged in as {email}")
        except:
            st.sidebar.error("Invalid email or password")


def logout():
    st.sidebar.subheader("Logout")
    if st.sidebar.button("Logout"):
        st.session_state["user_id"] = None
        st.sidebar.success("Logged out")


def general_dashboard():
    st.subheader("General Dashboard")
    users_data = fetch_all_users_data()

    if users_data:
        df = pd.DataFrame(users_data)

        # Number of users by location
        if "location" in df.columns:
            st.write("Number of Users by Location")
            location_count = df["location"].value_counts()
            st.bar_chart(location_count)
        else:
            st.error("Location data not available.")

        # Number of users by age
        if "age" in df.columns:
            st.write("Number of Users by Age")
            age_count = df["age"].value_counts()
            st.bar_chart(age_count)
        else:
            st.error("Age data not available.")
    else:
        st.error("No user data available.")


def personalized_dashboard():
    user_data = fetch_user_data(st.session_state["user_id"])
    if user_data:
        st.write(f"Welcome, {user_data.get('name', 'User')}!")

        # Sidebar options
        st.sidebar.subheader("Options")
        option = st.sidebar.selectbox("Choose an option", ["Location", "Query"])

        if option == "Location":
            st.write("Your Location Data:")
            st.write(user_data.get("location", "Location data not available."))

        if option == "Query":
            st.write("Your Queries:")
            st.write(user_data.get("queries", "No queries available."))
    else:
        st.error("User data not found.")


def main():
    st.title("User Dashboard")

    if "user_id" not in st.session_state:
        st.session_state["user_id"] = None

    if st.session_state["user_id"]:
        logout()
        personalized_dashboard()
    else:
        login()
        general_dashboard()


if __name__ == "__main__":
    main()
