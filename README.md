# 👕 ASSA Fashion Store (Flask Version)

Website bán hàng thời trang nam - nữ - unisex, có phân quyền người dùng, hệ thống đăng ký / đăng nhập, giỏ hàng, thanh toán và gợi ý sản phẩm từ mô hình ASSA.

---

## 🚀 Cấu trúc dự án

fashion_store/
│
├── app/
│ ├── routes.py # Xử lý trang chính (home, category, product,...)
│ ├── account_module.py # Đăng ký, đăng nhập, lưu lịch sử mua hàng
│ ├── templates/ # Giao diện HTML (index, login, register, ...)
│ ├── static/ # CSS, JS, hình ảnh
│ └── init.py
│
├── data/
│ ├── products.csv # Danh sách sản phẩm
│ ├── users.csv # Thông tin người dùng
│ ├── history.csv # Lịch sử mua hàng
│ └── fetch_images_from_pexels.py # Tự động lấy ảnh sản phẩm
│
├── app.py # File Flask chính
├── requirements.txt # Danh sách thư viện cần cài
└── README.md # File hướng dẫn


---

## 🧰 Yêu cầu hệ thống

- Python 3.8+
- Pip (trình quản lý gói Python)
- (Tuỳ chọn) Git để clone project nhanh hơn

---

## ⚙️ Cách chạy dự án (từng bước chi tiết)

### 🧩 1️⃣ Kích hoạt môi trường ảo (venv)

**Windows:**
python -m venv venv

venv\Scripts\activate

💡 Khi kích hoạt thành công, terminal sẽ có (venv) ở đầu dòng lệnh.

🧩 2️⃣ Cài đặt thư viện cần thiết

pip install -r requirements.txt

🧩 3️⃣ Kiểm tra dữ liệu

Đảm bảo thư mục data/ có các file:

products.csv

users.csv

history.csv

🧩 4️⃣ Chạy ứng dụng Flask
python app.py

🧩 5️⃣ Truy cập website

Mở trình duyệt và vào link:

http://127.0.0.1:5000/

🌐 Các trang chính
Trang	URL	Mô tả
🏠 Trang chủ	/	Danh mục, banner, sản phẩm nổi bật
👕 Danh mục	/category/<category>	Hiển thị sản phẩm theo loại (male / female / unisex)
📦 Chi tiết sản phẩm	/product/<id>	Thông tin sản phẩm, gợi ý tương tự
🛒 Giỏ hàng	/cart	Sản phẩm người dùng đã thêm
💳 Thanh toán	/checkout	Thanh toán và lưu đơn hàng
👤 Đăng ký	/register	Tạo tài khoản người dùng
🔐 Đăng nhập	/login	Đăng nhập bằng username hoặc email
📜 Lịch sử mua hàng	/account/history	Xem đơn hàng đã mua


❤️ Tác giả
KLTN - Gợi ý sản phẩm ASSA
Sinh viên: Trà Quốc Nam – Phạm Đức Bảo Ngọc – Lê Đình Vũ
Khoa Công nghệ thông tin – HUIT
© 2025 All Rights Reserved