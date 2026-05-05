import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Workshop Inventory System", layout="wide")

# ===== BRANDING HEADER WITH YOUR LOGO =====
st.markdown("---")
col1, col2 = st.columns([1, 4])

with col1:
    # Check if logo exists
    if os.path.exists("logo.png"):
        st.image("logo.png", width=100)
    else:
        st.warning("⚠️ Logo file not found. Please ensure 'logo.png' is in the folder")
        st.markdown("## 🏫")  # Fallback emoji

with col2:
    st.markdown("""
    ### Diploma in Mechanical Engineering  
    **ME4105: Final Year Project**  
    *Workshop Inventory Management System*
    """)

st.markdown("---")

# Student and supervisor info
col_a, col_b = st.columns(2)
with col_a:
    st.info("👨‍🎓 **Student:** Mohammad Abdul Haliq Hasnal (22FTE2816)")
with col_b:
    st.info("👨‍🏫 **Supervisor:** Sir Nadjuan Narawi")

st.markdown("---")

# Sidebar
st.sidebar.title("🔧 Workshop Inventory")
st.sidebar.markdown("---")

# Add logo to sidebar too
if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", width=150)

st.sidebar.markdown("**ME4105 Final Year Project**")
st.sidebar.markdown("*Mohammad Abdul Haliq Hasnal*")

page = st.sidebar.radio("Navigation", [
    "📊 Dashboard", 
    "➕ Add Item", 
    "✏️ Edit/Delete", 
    "🔄 Check Out/In", 
    "📜 Borrow History", 
    "📄 Reports"
])

# ===== YOUR DATABASE CODE HERE (same as before) =====
CSV_FILE = "inventory.csv"
HISTORY_FILE = "borrow_history.csv"

def init_database():
    if not os.path.exists(CSV_FILE):
        sample_data = pd.DataFrame({
            "id": [1, 2, 3],
            "item_name": ["Hammer", "Drill", "Screwdriver Set"],
            "quantity": [5, 2, 3],
            "min_stock": [2, 1, 2],
            "location": ["Shelf A1", "Shelf B2", "Toolbox C3"]
        })
        sample_data.to_csv(CSV_FILE, index=False)
    
    if not os.path.exists(HISTORY_FILE):
        history_data = pd.DataFrame(columns=["timestamp", "student_name", "item_name", "action", "quantity_after"])
        history_data.to_csv(HISTORY_FILE, index=False)

def load_data():
    return pd.read_csv(CSV_FILE)

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

def load_history():
    return pd.read_csv(HISTORY_FILE)

def save_history(df):
    df.to_csv(HISTORY_FILE, index=False)

def add_to_history(student_name, item_name, action, quantity_after):
    history_df = load_history()
    new_entry = pd.DataFrame([{
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "student_name": student_name,
        "item_name": item_name,
        "action": action,
        "quantity_after": quantity_after
    }])
    history_df = pd.concat([history_df, new_entry], ignore_index=True)
    save_history(history_df)

init_database()

# ==================== DASHBOARD ====================
if page == "📊 Dashboard":
    st.title("📊 Inventory Dashboard")
    
    df = load_data()
    
    # Search bar
    search = st.text_input("🔍 Search tools by name", "")
    if search:
        df = df[df["item_name"].str.contains(search, case=False)]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Items", len(df))
    with col2:
        st.metric("Total Quantity", df["quantity"].sum())
    with col3:
        checked_out = (df["quantity"] == 0).sum()
        st.metric("Out of Stock", checked_out)
    
    st.subheader("⚠️ Low Stock Alerts")
    low_stock = df[df["quantity"] <= df["min_stock"]]
    if not low_stock.empty:
        for _, item in low_stock.iterrows():
            st.warning(f"**{item['item_name']}** - Only {item['quantity']} left (Min: {item['min_stock']})")
    else:
        st.success("All items are well-stocked!")
    
    st.subheader("📋 Full Inventory")
    st.dataframe(df, use_container_width=True)

# ==================== ADD ITEM ====================
elif page == "➕ Add Item":
    st.title("➕ Add New Tool")
    
    df = load_data()
    
    with st.form("add_form"):
        col1, col2 = st.columns(2)
        with col1:
            item_name = st.text_input("Item Name")
            quantity = st.number_input("Quantity", min_value=0, step=1)
            min_stock = st.number_input("Minimum Stock", min_value=0, step=1)
        with col2:
            location = st.text_input("Location")
        
        submitted = st.form_submit_button("Add Item")
        
        if submitted and item_name:
            new_id = df["id"].max() + 1 if not df.empty else 1
            new_row = pd.DataFrame([{
                "id": new_id,
                "item_name": item_name,
                "quantity": quantity,
                "min_stock": min_stock,
                "location": location
            }])
            df = pd.concat([df, new_row], ignore_index=True)
            save_data(df)
            add_to_history("Technician", item_name, "ADDED", quantity)
            st.success(f"✅ {item_name} added!")
            st.balloons()

# ==================== EDIT/DELETE ====================
elif page == "✏️ Edit/Delete":
    st.title("✏️ Edit or Delete Tools")
    
    df = load_data()
    
    if df.empty:
        st.warning("No items found")
    else:
        item_to_edit = st.selectbox("Select tool to edit/delete", df["item_name"].tolist())
        item_data = df[df["item_name"] == item_to_edit].iloc[0]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Edit Item")
            new_name = st.text_input("New Name", item_data["item_name"])
            new_qty = st.number_input("New Quantity", value=int(item_data["quantity"]), min_value=0)
            new_min = st.number_input("New Min Stock", value=int(item_data["min_stock"]), min_value=0)
            new_loc = st.text_input("New Location", item_data["location"])
            
            if st.button("💾 Save Changes"):
                df.loc[df["item_name"] == item_to_edit, "item_name"] = new_name
                df.loc[df["item_name"] == new_name, "quantity"] = new_qty
                df.loc[df["item_name"] == new_name, "min_stock"] = new_min
                df.loc[df["item_name"] == new_name, "location"] = new_loc
                save_data(df)
                st.success("✅ Changes saved!")
                st.rerun()
        
        with col2:
            st.subheader("Delete Item")
            st.warning(f"Are you sure you want to delete **{item_to_edit}**?")
            if st.button("🗑️ Permanently Delete", type="primary"):
                df = df[df["item_name"] != item_to_edit]
                save_data(df)
                add_to_history("Technician", item_to_edit, "DELETED", 0)
                st.success(f"❌ {item_to_edit} deleted!")
                st.rerun()

# ==================== CHECK OUT/IN ====================
elif page == "🔄 Check Out/In":
    st.title("🔄 Borrow or Return Tools")
    
    df = load_data()
    
    if df.empty:
        st.warning("No items available")
    else:
        student_name = st.text_input("📝 Student Name (Required)")
        selected_item = st.selectbox("Select Tool", df["item_name"].tolist())
        item_data = df[df["item_name"] == selected_item].iloc[0]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Available", item_data["quantity"])
        with col2:
            st.metric("Min Stock", item_data["min_stock"])
        with col3:
            st.metric("Location", item_data["location"])
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📤 BORROW", use_container_width=True, type="primary"):
                if not student_name:
                    st.error("Please enter student name")
                elif item_data["quantity"] > 0:
                    new_qty = item_data["quantity"] - 1
                    df.loc[df["item_name"] == selected_item, "quantity"] = new_qty
                    save_data(df)
                    add_to_history(student_name, selected_item, "BORROWED", new_qty)
                    st.success(f"✅ {selected_item} borrowed by {student_name}!")
                    st.rerun()
                else:
                    st.error("Out of stock!")
        
        with col2:
            if st.button("📥 RETURN", use_container_width=True):
                if not student_name:
                    st.error("Please enter student name")
                else:
                    new_qty = item_data["quantity"] + 1
                    df.loc[df["item_name"] == selected_item, "quantity"] = new_qty
                    save_data(df)
                    add_to_history(student_name, selected_item, "RETURNED", new_qty)
                    st.success(f"✅ {selected_item} returned by {student_name}!")
                    st.rerun()
        
        if item_data["quantity"] <= item_data["min_stock"]:
            st.warning(f"⚠️ Low stock! Only {item_data['quantity']} left")

# ==================== BORROW HISTORY ====================
elif page == "📜 Borrow History":
    st.title("📜 Borrow & Return History")
    
    history_df = load_history()
    
    if history_df.empty:
        st.info("No transactions yet")
    else:
        students = ["All"] + history_df["student_name"].unique().tolist()
        filter_student = st.selectbox("Filter by student", students)
        
        filtered = history_df.copy()
        if filter_student != "All":
            filtered = filtered[filtered["student_name"] == filter_student]
        
        st.dataframe(filtered, use_container_width=True)
        
        csv = filtered.to_csv(index=False)
        st.download_button("📥 Download History CSV", csv, "borrow_history.csv", mime="text/csv")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Transactions", len(filtered))
        with col2:
            st.metric("Unique Students", filtered["student_name"].nunique())

# ==================== REPORTS ====================
elif page == "📄 Reports":
    st.title("📄 Inventory Reports")
    
    df = load_data()
    
    low_stock_only = st.checkbox("Show only low stock items")
    
    filtered_df = df.copy()
    if low_stock_only:
        filtered_df = filtered_df[filtered_df["quantity"] <= filtered_df["min_stock"]]
    
    st.dataframe(filtered_df, use_container_width=True)
    
    if not filtered_df.empty:
        csv = filtered_df.to_csv(index=False)
        st.download_button("📥 Download Report", csv, "inventory_report.csv", mime="text/csv")

# ==================== FOOTER ====================
st.sidebar.markdown("---")
st.sidebar.caption(f"📅 ME4105 Final Year Project 2026")
st.sidebar.caption("🔧 Diploma in Mechanical Engineering")

st.markdown("---")
st.caption("© 2026 Mohammad Abdul Haliq Hasnal | ME4105 Final Year Project | Supervised by Sir Nadjuan Narawi")