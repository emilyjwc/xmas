import streamlit as st
import random
import sqlite3

# Establish connection and create table if it doesn't exist
conn = sqlite3.connect("gift_exchange.db")
c = conn.cursor()

c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        name TEXT PRIMARY KEY,
        password TEXT,
        gift TEXT
    )
''')
conn.commit()

# Updated participants list
participants = ["Emily", "Rebecca", "Kelly", "Joanne", "Cecile", "Sammy", "Cathy", "Woody", "Jensen", "Ali", "Joseph",
                "Charlie", "Test", "Test2", "t3"]


# Function to assign gifts and ensure no one draws themselves
def assign_gifts(participants):
    receivers = participants.copy()
    random.shuffle(receivers)
    while any(p == r for p, r in zip(participants, receivers)):
        random.shuffle(receivers)
    return dict(zip(participants, receivers))


# Initialize session state for gift assignments and page
if "gift_assignments" not in st.session_state:
    st.session_state["gift_assignments"] = assign_gifts(participants)

if "page" not in st.session_state:
    st.session_state["page"] = "login_or_setup"


# Admin view to see all gift assignments
def admin_view():
    st.title("管理員模式 - 查看所有抽籤結果")
    admin_password = st.text_input("請輸入管理員密碼", type="password")

    if st.button("登入管理員模式"):
        if admin_password == "admin123":
            st.write("管理員登入成功！")
            c.execute("SELECT name, gift FROM users")
            results = c.fetchall()
            if results:
                st.write("交換禮物名單：")
                for row in results:
                    st.write(f"{row[0]} 抽到的對象是：{row[1]}")
            else:
                st.write("目前尚未有抽籤結果。")
        else:
            st.write("管理員密碼錯誤！")


# Login or set password page
if st.session_state["page"] == "login_or_setup":
    st.title("交換禮物系統 - 登入或設定密碼")

    name = st.text_input("請輸入你的名字")
    password = st.text_input("請輸入密碼", type="password")

    if st.button("設定密碼"):
        if name in participants:
            c.execute("SELECT * FROM users WHERE name = ?", (name,))
            user = c.fetchone()
            if user is None:
                c.execute("INSERT INTO users (name, password) VALUES (?, ?)", (name, password))
                conn.commit()
                st.write("密碼設定成功！")
                st.session_state["page"] = "draw"
                st.session_state["current_user"] = name
            else:
                st.write("此使用者已設定過密碼，請直接登入。")
        else:
            st.write("這個名字不在參與者名單中，請確認後再試。")

    if st.button("登入"):
        c.execute("SELECT * FROM users WHERE name = ? AND password = ?", (name, password))
        user = c.fetchone()
        if user:
            st.write("登入成功！")
            st.session_state["current_user"] = name
            if user[2]:
                st.session_state["page"] = "view"
            else:
                st.session_state["page"] = "draw"
        else:
            st.write("名字或密碼錯誤，請重新輸入。")

    if st.button("管理員登入"):
        st.session_state["page"] = "admin"

# Draw page
elif st.session_state["page"] == "draw":
    st.title("交換禮物系統 - 抽籤")
    name = st.session_state["current_user"]

    # Check if user already has a gift
    c.execute("SELECT gift FROM users WHERE name = ?", (name,))
    result = c.fetchone()
    if result and result[0]:
        st.write(f"🎉 {name}，你的禮物對象是：{result[0]} 🎉")
        if st.button("返回主頁"):
            st.session_state["page"] = "login_or_setup"
    else:
        if st.button("抽籤"):
            gift = st.session_state["gift_assignments"][name]
            c.execute("UPDATE users SET gift = ? WHERE name = ?", (gift, name))
            conn.commit()
            st.write(f"🎉 {name}，你的禮物對象是：{gift} 🎉")
            st.session_state["page"] = "view"

# View result page with only "Return to Main Page" button
elif st.session_state["page"] == "view":
    st.title("交換禮物系統 - 查看結果")
    name = st.session_state["current_user"]

    c.execute("SELECT gift FROM users WHERE name = ?", (name,))
    result = c.fetchone()
    if result and result[0]:
        st.write(f"{name}，你的禮物對象是：{result[0]}")
    else:
        st.write("你尚未抽籤。")

    if st.button("返回主頁"):
        st.session_state["page"] = "login_or_setup"

# Admin page view
elif st.session_state["page"] == "admin":
    admin_view()
    if st.button("返回主頁"):
        st.session_state["page"] = "login_or_setup"
