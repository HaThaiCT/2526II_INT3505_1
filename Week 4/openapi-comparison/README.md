# So sánh OpenAPI, API Blueprint, RAML và TypeSpec

| Tiêu chí | OpenAPI (Swagger) | API Blueprint | RAML | TypeSpec |
| :--- | :--- | :--- | :--- | :--- |
| **Định dạng** | YAML / JSON | Markdown (với mở rộng MSON) | YAML | Ngôn ngữ chuyên dụng (giống TypeScript) |
| **Độ phổ biến** | Rất cao, chuẩn công nghiệp do cộng đồng lớn. | Trung bình, phổ biến với những ai thích Markdown. | Khá giảm dần so với OpenAPI. Của MuleSoft. | Mới, đang nổi lên bởi Microsoft. |
| **Mục đích chính**| Tài liệu hoá, sinh code, thiết kế API. | Thiết kế API hướng tài liệu (Documentation-driven). | Thiết kế API dựa trên tái sử dụng (phân cấp). | Thiết kế API abstract, biên dịch sang OpenAPI, Protobuf, v.v. |
| **Đường cong học tập** | Trung bình, YAML có thể dài và phức tạp. | Thấp, dễ đọc vì là Markdown. | Trung bình, cú pháp kế thừa mạnh. | Khá, đặc biệt nếu đã quen TypeScript. |
| **Sinh Code / Sinh Mocks** | Cực kỳ mạnh mẽ với hệ sinh thái lớn (openapi-generator, prism, stoplight). | Có hỗ trợ (Aglio, Drakov, Dredd test), nhưng không phong phú bằng. | Có hỗ trợ mạnh thông qua hệ sinh thái RAML2HTML, Osprey. | Biên dịch thành OpenAPI, từ đó tận dụng hệ sinh thái OpenAPI. |

---

Dưới đây là một hệ thống thư viện quản lý có các APIs cơ bản (GET, POST sách) được thiết kế qua mỗi ngôn ngữ.
