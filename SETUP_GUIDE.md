# Hướng Dẫn Cấu Hình Bot "Where Winds Meet" (Stable & Localized)
 
 Bot này sẽ tự động kiểm tra tin mới từ Trang chủ chính thức của "Where Winds Meet" và Google News, sau đó dịch sang tiếng Việt và gửi về Telegram của bạn.
 
 ## Yêu Cầu
 1. Một `TELEGRAM_BOT_TOKEN` và `TELEGRAM_CHAT_ID`.
 2. Python đã được cài đặt (phiên bản 3.9+).
 
 ## Bước 1: Lấy thông tin Telegram Bot
 
 1. Vào ứng dụng Telegram và tìm **@BotFather**.
 2. Gõ lệnh `/newbot` và làm theo hướng dẫn để tạo bot mới.
 3. Copy mã Token được cung cấp (ví dụ: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`). Đây là `TELEGRAM_BOT_TOKEN`.
 4. Gửi một tin nhắn bất kỳ cho bot bạn vừa tạo.
 5. Lấy `TELEGRAM_CHAT_ID` bằng cách truy cập: `https://api.telegram.org/bot<TOKEN_CỦA_BẠN>/getUpdates` và tìm `"chat":{"id":...}`.
 
 ## Bước 2: Cài Đặt & Chạy Bot
 
 1. Tạo file `.env` (copy từ `.env.example` nếu có) và dán thông tin vào:
    ```ini
    TELEGRAM_BOT_TOKEN=điền_token_vào_đây
    TELEGRAM_CHAT_ID=điền_chat_id_vào_đây
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
 1. `TELEGRAM_BOT_TOKEN` và `TELEGRAM_CHAT_ID` trong file `.env` đã chính xác chưa.
 2. File `data/history.json` đang lưu thời gian kiểm tra cuối cùng. Bạn có thể xóa file này để bot quét lại các tin cũ (trong vòng 24h qua).
