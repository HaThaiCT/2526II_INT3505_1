# TypeSpec (Trực quan, Code-first API Design)

TypeSpec (của Microsoft) là một ngôn ngữ giúp định nghĩa API giống hệt TypeScript, loại bỏ nhược điểm verbose của YAML như ở OpenAPI.

## Sinh OpenAPI 3 / Mocks

TypeSpec có nhiệm vụ lớn nhất là "compile" ra được ra các file YAML OpenAPI, Protobuf, v.v tùy vào `emitters`. File `.tsp` rất dễ maintain và kế thừa.

1. **Cài đặt compiler (`tsp`)**:
   Bạn cần có Node.js:
   ```bash
   npm install -g @typespec/compiler @typespec/http @typespec/openapi3
   ```

2. **Khởi tạo và cấu hình project**:
   ```bash
   tsp init # Làm theo các bước
   npm install
   ```

3. **Biên dịch sinh ra OpenAPI.yaml**:
   Khi bạn biên dịch file TypeSpec, framework sẽ tạo ra file `openapi.yaml`.
   ```bash
   tsp compile main.tsp --emit @typespec/openapi3
   ```
   Kết quả trả về sẽ có thư mục `tsp-output` chứa OpenAPI json/yaml (mặc định yaml). Bạn hoàn toàn có thể tiếp tục mang file config yaml đó vào swagger hoặc `openapi-generator-cli` để sinh code, tạo mock server như OpenAPI.

## Generation Automation (CI/CD)
Trong bước pipeline, TypeSpec được gọi để compile sinh artifact `.yaml` -> Artifact này đẩy vào bộ engine tạo SDKs, sinh docs cho Server APIs. Sự kết hợp này mang lại hiệu suất code tuyệt vời mà không phải maintain cục YAML lớn. 
