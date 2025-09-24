import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# --- 1. Kết nối Google Sheets ---
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope,
)
client = gspread.authorize(credentials)

# --- 2. Mở file Google Sheets ---
sheet_url = "https://docs.google.com/spreadsheets/d/1my6VbCaAlDjVm5ITvjSV94tVU8AfR8zrHuEtKhjCAhY/edit?usp=sharing"
spreadsheet = client.open_by_url(sheet_url)

# --- 3. Lấy danh sách sheet ---
worksheets = spreadsheet.worksheets()
sheet_names = [ws.title for ws in worksheets]

# --- 4. Sidebar chọn sheet ---
selected_sheet = st.sidebar.selectbox("Chọn sheet để xem:", sheet_names)
worksheet = spreadsheet.worksheet(selected_sheet)

# --- 5. Đọc dữ liệu ---
records = worksheet.get_all_records(head=1)  # dòng 1 là header
df = pd.DataFrame(records)

# --- 6. Hiển thị dữ liệu ---
st.title("🔍 Quản lý dữ liệu Google Sheets")
st.subheader(f"Sheet đang xem: **{selected_sheet}**")
st.dataframe(df)

# --- 7. Hiển thị ảnh ---
possible_img_cols = [c for c in df.columns if "img" in c.lower() or "image" in c.lower() or "ảnh" in c.lower()]

if possible_img_cols:
    img_col = possible_img_cols[0]
    st.subheader("🖼️ Hình ảnh minh hoạ")
    for idx, row in df.iterrows():
        img_url = str(row.get(img_col, "")).strip()
        name = row.get("name", f"Row {idx+2}")

        if not img_url or not img_url.startswith("http"):
            continue

        # Chuyển link Google Drive về direct link
        if "drive.google.com/file/d/" in img_url:
            try:
                file_id = img_url.split("/d/")[1].split("/")[0]
                img_url = f"https://drive.google.com/uc?export=view&id={file_id}"
            except Exception:
                pass

        try:
            st.image(img_url, caption=name, use_container_width=True)
        except Exception:
            st.warning(f"⚠️ Không hiển thị được ảnh tại dòng {idx+2}: {img_url}")
else:
    st.info("📌 Không tìm thấy cột hình ảnh trong sheet.")

# --- 8. Tìm kiếm nhanh ---
st.subheader("🔎 Tìm kiếm")
search_term = st.text_input("Nhập id hoặc name để lọc:")

if search_term:
    if {"id", "name"}.issubset(df.columns):
        filtered = df[df.apply(
            lambda row: search_term.lower() in str(row.get("id", "")).lower()
            or search_term.lower() in str(row.get("name", "")).lower(), axis=1)]
        st.write(f"### Kết quả lọc cho '{search_term}':")
        st.dataframe(filtered)
    else:
        st.warning("❌ Sheet này không có cột 'id' hoặc 'name', không thể tìm kiếm.")

# --- 9. Nhập dữ liệu mới ---
st.subheader("✍️ Thêm dữ liệu mới vào sheet")

with st.form("add_row_form"):
    new_id = st.text_input("ID sản phẩm")
    new_name = st.text_input("Tên sản phẩm")
    new_quantity = st.text_input("Số lượng")
    submitted = st.form_submit_button("Thêm")

    if submitted:
        if len(df.columns) > 0:
            # Chuẩn bị dòng dữ liệu mới, căn theo số cột header
            new_row_dict = {
                "id": new_id,
                "name": new_name,
                "quantity": new_quantity
            }
            new_row = [new_row_dict.get(col, "") for col in df.columns]
            worksheet.append_row(new_row)
            st.success("✅ Đã thêm dữ liệu thành công! Vui lòng reload để xem kết quả.")
        else:
            st.error("❌ Không tìm thấy header trong sheet. Vui lòng kiểm tra file Google Sheets.")

# --- 10. Cập nhật dữ liệu ---
st.subheader("📝 Chỉnh sửa dữ liệu theo ID")

with st.form("update_form"):
    update_id = st.text_input("Nhập ID sản phẩm cần chỉnh sửa")
    new_name_update = st.text_input("Tên sản phẩm mới (bỏ trống nếu giữ nguyên)")
    new_quantity_update = st.text_input("Số lượng mới (bỏ trống nếu giữ nguyên)")
    update_btn = st.form_submit_button("Cập nhật")

    if update_btn:
        if "id" in df.columns and update_id in df["id"].astype(str).values:
            row_index = df[df["id"].astype(str) == update_id].index[0] + 2  # +2 vì dòng 1 là header
            if new_name_update:
                worksheet.update_cell(row_index, df.columns.get_loc("name") + 1, new_name_update)
            if new_quantity_update:
                worksheet.update_cell(row_index, df.columns.get_loc("quantity") + 1, new_quantity_update)
            st.success(f"✅ Đã cập nhật sản phẩm có ID = {update_id}")
        else:
            st.error("❌ Không tìm thấy sản phẩm với ID này.")
