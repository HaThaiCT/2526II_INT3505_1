# OpenAPI (OAS) Code Generation & Mocks

## Cài đặt và Sinh Code

Để sinh code server/client từ file `openapi.yml`, ta có thể dùng `openapi-generator-cli`.

1. **Cài đặt openapi-generator-cli**:
   Có thể cài dễ dàng qua NPM hoặc dùng Docker:
   ```bash
   npm install @openapitools/openapi-generator-cli -g
   ```

2. **Cách sinh mã nguồn Server (NodeJS / Express)**:
   ```bash
   openapi-generator-cli generate -i openapi.yml -g nodejs-express-server -o ./server
   ```

3. **Cách sinh mã Client (Python)**:
   ```bash
   openapi-generator-cli generate -i openapi.yml -g python -o ./client
   ```

4. **Tạo Mock Server & Test**:
   Dùng tính năng mock của Prism:
   ```bash
   npm install -g @stoplight/prism-cli
   prism mock openapi.yml
   ```
   Server mock sẽ tự động lắng nghe và khi gọi GET `/books` bạn sẽ nhận phản hồi tự động dựa trên schema.
