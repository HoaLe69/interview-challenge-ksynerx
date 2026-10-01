# Report

## What I've done

- [x] Mock service VietFul
- [x] Setup project base
- [x] Implement 3 cơ chế nhận dự liệu (Webhook, excel, VietFul)
- [x] Build core logic (hash & upsert) handle phần trách trùng lặp data
- [x] Basic Error handling, Health Check
- [x] Docker Compose (PostgreSQL có healthcheck, CDMS chờ DB healthy, restart policy)

## What I've been considered

- Unit test tự động.
- Hàng đợi bên webhook.
- Retry với backoff khi poll Vietful và khi khởi động DB.
- Batch webhook rất lớn sẽ làm request chậm vì xử lý đồng bộ.

## Đã dùng AI như thế nào?

- Em chủ yếu tập trung vào phần phần phân tích nghiệp vụ. Vì thời gian hạn chế nên các implementation sẽ chủ yếu sẽ giao cho AI, em verify lại output, đồng thời testing. Quá trình verify thì cũng có update lại code vì AI triển khai quá phức tạp.

## Lessons Learned

1. **"Exactly-once" thực chất là idempotent**: Trong hệ phân tán không thể đảm bảo gửi đúng một lần, nên em làm cho việc ghi lại nhiều lần cho cùng kết quả. Cách này đơn giản và cho phép retry thoải mái.

2. **Đẩy việc so sánh xuống database**: Kiểm tra trùng trong bộ nhớ ứng dụng dễ bị race condition khi có nhiều worker. Một câu lệnh UPSERT có điều kiện thì không.

3. **Chuẩn hóa dữ liệu trước khi băm**: Excel cho ra `NaN`, chuỗi rỗng, `TRUE` trong khi JSON cho `null`, `true`. Nếu không chuẩn hóa thì cùng một sản phẩm đi qua hai kênh sẽ có hai hash khác nhau.

4. **Giữ đơn giản**: Với 1 ngày, em bỏ Alembic, hàng đợi và cơ chế retry phía server (polling tự lấy lại dữ liệu ở lượt kế tiếp) để dành thời gian cho phần cốt lõi.
