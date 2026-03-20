# RAML Demo Code Generators & Mocking

RAML (RESTful API Modeling Language) được thiết kế đặc biệt cho việc tái sử dụng code với hệ sinh thái phong phú.

## Sinh Mocks từ hệ thống Osprey-Mock-Service

1. **Cài đặt Osprey**:
   Một Node.js framework thiết kế API từ RAML, hỗ trợ validation tự động.
   ```bash
   npm install -g osprey-mock-service
   ```

2. **Chạy Mock server**:
   Dựa trên file RAML, server sẽ được render lên ngay lập tức.
   ```bash
   osprey-mock-service -f api.raml -p 3000
   ```

## Sinh Document HTML

1. **Cài đặt công cụ RAML2HTML**:
   Chuyển file YAML -> HTML doc trực quan.
   ```bash
   npm install -g raml2html
   ```

2. **Render doc HTML**:
   ```bash
   raml2html api.raml > index.html
   ```

## Sinh Mã Nguồn (Codegen)
Có nhiều tool hỗ trợ biến RAML thành OpenAPI để tận dụng `openapi-generator`, hoặc dùng **RAML for JAX-RS** (đối với hệ sinh thái Java).
```bash
# Ví dụ cài raml2obj và một generator cụ thể
npm install raml-javascript-generator -g
```
