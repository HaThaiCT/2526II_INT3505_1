from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__)

# Simple in-memory data instead of a database class
books = [
    {
        "id": "1",
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "publishedYear": 2008,
        "genre": "Software Engineering"
    },
    {
        "id": "2",
        "title": "The Pragmatic Programmer",
        "author": "Andrew Hunt, David Thomas",
        "publishedYear": 1999,
        "genre": "Software Engineering"
    }
]

@app.get("/books")
def list_books():
    return jsonify(books)

@app.post("/books")
def create_book():
    data = request.json or {}
    new_book = {
        "id": str(len(books) + 1),
        "title": data.get("title"),
        "author": data.get("author"),
        "publishedYear": data.get("publishedYear"),
        "genre": data.get("genre")
    }
    books.append(new_book)
    return jsonify(new_book), 201

@app.get("/books/<id>")
def get_book(id):
    book = next((b for b in books if b["id"] == id), None)
    if book:
        return jsonify(book)
    return jsonify({"error": "Book not found"}), 404

@app.put("/books/<id>")
def update_book(id):
    data = request.json or {}
    book = next((b for b in books if b["id"] == id), None)
    if not book:
        return jsonify({"error": "Book not found"}), 404
        
    book.update({
        "title": data.get("title", book["title"]),
        "author": data.get("author", book["author"]),
        "publishedYear": data.get("publishedYear", book["publishedYear"]),
        "genre": data.get("genre", book["genre"])
    })
    return jsonify(book)

@app.delete("/books/<id>")
def delete_book(id):
    global books
    books = [b for b in books if b["id"] != id]
    return "", 204

@app.get("/openapi.yaml")
def openapi_spec():
    return send_from_directory(".", "openapi.yaml")

@app.get("/docs")
def swagger_ui():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Simple Books API Docs</title>
        <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
        <script>
            window.onload = () => {
                SwaggerUIBundle({
                    url: "/openapi.yaml",
                    dom_id: "#swagger-ui"
                });
            };
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(debug=True)


# Truy cập http://localhost:5000/docs để xem tài liệu API.