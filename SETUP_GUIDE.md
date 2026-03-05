# Hướng Dẫn Cấu Hình Bot "Where Winds Meet" (Stable & Localized)
 
 Bot này sẽ tự động kiểm tra tin mới từ Trang chủ chính thức của "Where Winds Meet" và Google News, sau đó dịch sang tiếng Việt và gửi về Discord của bạn.
 
 ## Yêu Cầu
 1. Một đường dẫn (URL) Discord Webhook.
 2. Python đã được cài đặt (phiên bản 3.9+).
 
 ## Bước 1: Lấy Discord Webhook URL
 
 1. Vào server Discord của bạn.
 2. Chọn kênh bạn muốn bot gửi tin nhắn vào (ví dụ: `#news`).
 3. Bấm vào biểu tượng bánh răng **"Edit Channel"** (Chỉnh sửa kênh) bên cạnh tên kênh.
 4. Chọn menu **"Integrations"**.
 5. Chọn **"Webhooks"** -> **"New Webhook"**.
 6. Đặt tên bot (ví dụ: `WWM Update`) và chọn kênh.
 7. Bấm nút **"Copy Webhook URL"**.
 8. Dán URL này vào file `.env` ở dòng `WEBHOOK_URL=...`
 
 ## Bước 2: Cài Đặt & Chạy Bot
 
 1. Tạo file `.env` (copy từ `.env.example` nếu có) và dán Webhook URL vào:
    ```ini
    WEBHOOK_URL=https://discord.com/api/webhooks/......
    ```
 2. Mở Terminal và cài đặt thư viện:
    ```bash
    pip install -r requirements.txt
    ```
 3. Chạy bot để kiểm tra ngay lập tức:
    ```bash
    python src/monitor.py
    ```
 
 ## Tính Năng Đặc Biệt
 - **Nguồn tin ổn định**: Sử dụng Google News và Trang chủ chính thức để tránh bị chặn.
 - **Tự động dịch**: Mọi thông tin tiếng Trung (CN) sẽ được tự động dịch sang tiếng Việt (VN) trước khi gửi.
 - **Tự động hóa**: Bot đã được cấu hình sẵn để chạy hàng ngày qua GitHub Actions.
 
 ## Khắc phục lỗi (Troubleshooting)
 Nếu bot không gửi tin nhắn, hãy kiểm tra:
 1. `WEBHOOK_URL` trong file `.env` đã chính xác chưa.
 2. File `data/history.json` đang lưu thời gian kiểm tra cuối cùng. Bạn có thể xóa file này để bot quét lại các tin cũ (trong vòng 24h qua).
