# Hướng Dẫn Deploy Bot qua GitHub Actions

Để bot tự động chạy mỗi 15 phút trên GitHub, bạn cần thực hiện các bước sau:

## Bước 1: Đưa Code lên GitHub
Nếu bạn chưa đưa project này lên GitHub, hãy tạo một Repository mới và push code lên đó.

## Bước 2: Cấu hình WEBHOOK_URL trên GitHub
Vì lý do bảo mật, chúng ta không lưu `WEBHOOK_URL` trực tiếp trong code mà sẽ dùng **GitHub Secrets**.

1. Vào Repository của bạn trên GitHub.
2. Chọn tab **Settings** (Cài đặt).
3. Ở menu bên trái, tìm mục **Secrets and variables** -> **Actions**.
4. Bấm nút **New repository secret**.
5. Nhập các thông tin sau:
   - **Name**: `WEBHOOK_URL`
   - **Secret**: (Dánリンク Webhook Discord của bạn vào đây)
6. Bấm **Add secret**.

## Bước 3: Kiểm tra và Kích hoạt
1. Chọn tab **Actions** trên GitHub.
2. Bạn sẽ thấy workflow tên là **WWM Bot Check**.
3. Nếu nó chưa tự chạy, bạn có thể bấm vào workflow đó và chọn **Run workflow** để test thử ngay lập tức.

## Lưu ý về History
Workflow này đã được cấu hình để tự động ghi lại lịch sử các tin đã gửi vào file `data/history.json` và push ngược lại lên repository. Điều này giúp bot không gửi lặp lại các tin cũ.

---
*Bot sẽ tự động quét tin mới mỗi 15 phút kể từ khi bạn hoàn thành các bước trên.*
