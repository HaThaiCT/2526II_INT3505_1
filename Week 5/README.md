# Hệ Thống Quản Lý Thư Viện (Library Management System)

## 1. Thiết Kế Data Model (Mô hình dữ liệu)

Hệ thống quản lý thư viện cơ bản bao gồm 3 thực thể chính: **User** (Người dùng), **Book** (Sách), và **Loan** (Phiếu mượn sách).

- **User**:
  - `id` (Primary Key)
  - `name` (String, Required)
  - `email` (String, Unique, Required)
  - `joined_date` (DateTime)

- **Book**:
  - `id` (Primary Key)
  - `title` (String, Required)
  - `author` (String, Required)
  - `published_year` (Integer)
  - `total_copies` (Integer, Default 1)
  - `available_copies` (Integer, Default 1)

- **Loan** (Quan hệ N-N giữa User và Book, được cụ thể hóa thành 1 bảng riêng):
  - `id` (Primary Key)
  - `user_id` (Foreign Key -> User.id)
  - `book_id` (Foreign Key -> Book.id)
  - `borrow_date` (DateTime)
  - `return_date` (DateTime, Nullable - Nếu null tức là chưa trả)
  - `status` (Enum: 'borrowed', 'returned')

## 2. Thiết Kế Resource Tree (Cây tài nguyên RESTful)

Áp dụng tiêu chuẩn RESTful API, thiết kế resource tree phù hợp với Domain:

- `/books` - Quản lý tổng quan kho sách
- `/books/{isbn_hoặc_id}` - Chi tiết 1 cuốn sách cụ thể
- `/users` - Quản lý người dùng thư viện
- `/users/{id}` - Chi tiết 1 người dùng
- `/users/{id}/loans` - **Sub-resource (Nested)**: Xem danh sách các cuốn sách / lịch sử mượn sách của CỤ THỂ 1 người dùng.
- `/users/{id}/loans/active` - Sub-resource: Các sách ĐANG mượn của 1 người dùng.

## 3. Thiết Kế Endpoint Tìm Kiếm và Phân Trang

Endpoint: `GET /books`

Sử dụng **Query Parameters** (tham số truy vấn) để thực hiện tìm kiếm và phân trang, giúp tách biệt resource identifier và resource state/behavior.

**Tham số:**
- `q` hoặc `search`: Từ khóa tìm kiếm (theo tên sách, tác giả).
- `page`: Trang hiện tại (Mặc định: 1).
- `limit` hoặc `per_page`: Số lượng items trên 1 trang (Mặc định: 10, Tối đa: 100).
- `sort_by`: Sắp xếp theo trường (vd: `published_year`, `title`).
- `order`: Hướng sắp xếp (`asc`, `desc`).

**Ví dụ:**
`GET /books?q=python&page=2&limit=5&sort_by=published_year&order=desc`

**Response Payload (Phân trang chuẩn):**
```json
{
  "data": [
    { "id": 1, "title": "Fluent Python", "author": "Luciano Ramalho" },
    ...5 items...
  ],
  "pagination": {
    "total_items": 42,
    "total_pages": 9,
    "current_page": 2,
    "limit": 5,
    "has_next": true,
    "has_prev": true
  }
}
```

---

Dưới đây là Demo Code sử dụng **Flask** và **Flask-SQLAlchemy** để minh họa các khái niệm trên.
