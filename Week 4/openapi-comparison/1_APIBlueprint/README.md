# API Blueprint Generator & Mocks

API Blueprint dùng cú pháp Markdown nên cực kỳ dễ đọc, tập trung vào Human-readable documentation.

## Render HTML

1. **Cài đặt Aglio**:
   Aglio được dùng để render API Blueprint ra HTML đẹp mắt.
   ```bash
   npm install -g aglio
   ```

2. **Render doc**:
   ```bash
   aglio -i api.apib -o index.html
   ```

## Sinh Mock Server

1. **Cài đặt Drakov**:
   Drakov giả lập server từ file API Blueprint.
   ```bash
   npm install -g drakov
   ```

2. **Chạy Mock server**:
   ```bash
   drakov -f api.apib -p 3000
   ```

## API Testing
Có thể sử dụng **Dredd** để test API. Dredd phân tích file blueprint và gọi tới API ở backend để kiểm chứng việc backend code có giống với blueprint docs không.
```bash
npm install -g dredd
dredd api.apib http://localhost:3000
```
