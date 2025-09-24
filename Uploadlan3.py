import streamlit as st
import requests
from io import BytesIO
from PIL import Image

st.title("🖼️ Test hiển thị ảnh Google Drive")

# ID file Google Drive
file_id = "144OpPO0kfqMUUuNga8LJIFwqnNlYQMQG"

# Chuyển sang link direct
direct_url = f"https://drive.google.com/uc?export=download&id={file_id}"
st.write("🔗 Link direct:", direct_url)

try:
    response = requests.get(direct_url)
    response.raise_for_status()
    image = Image.open(BytesIO(response.content))
    st.image(image, caption="Ảnh test từ Google Drive", use_container_width=True)
except Exception as e:
    st.error(f"❌ Lỗi khi tải ảnh: {e}")
