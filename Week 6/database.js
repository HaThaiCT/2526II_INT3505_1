// In-memory database simulation
// In production, you would use MongoDB, PostgreSQL, etc.

class Database {
  constructor() {
    this.users = [
      {
        id: 1,
        username: 'admin',
        password: '$2a$10$S11pSAobjR4LRqOP8yoH6eUSrzfrssPFPfYXxxahPPRMV0XRaR//G', // 'admin123'
        role: 'admin',
        email: 'admin@library.com',
        scopes: ['books:read', 'books:write', 'books:delete', 'users:read', 'users:write', 'users:delete', 'borrow:all']
      },
      {
        id: 2,
        username: 'user1',
        password: '$2a$10$nJoKGdMLjAJvJxPmVrtayeWay4uuiY0eBfaITUjEKwNLAWc./1rTK', // 'user123'
        role: 'user',
        email: 'user1@library.com',
        scopes: ['books:read', 'borrow:own']
      }
    ];

    this.books = [
      {
        id: 1,
        title: 'The Great Gatsby',
        author: 'F. Scott Fitzgerald',
        isbn: '978-0743273565',
        totalCopies: 5,
        availableCopies: 5,
        createdAt: new Date()
      },
      {
        id: 2,
        title: 'To Kill a Mockingbird',
        author: 'Harper Lee',
        isbn: '978-0061120084',
        totalCopies: 3,
        availableCopies: 3,
        createdAt: new Date()
      },
      {
        id: 3,
        title: '1984',
        author: 'George Orwell',
        isbn: '978-0451524935',
        totalCopies: 4,
        availableCopies: 4,
        createdAt: new Date()
      }
    ];

    this.borrowRecords = [];
    
    // Refresh tokens storage
    this.refreshTokens = [];
    
    this.userIdCounter = this.users.length + 1;
    this.bookIdCounter = this.books.length + 1;
    this.borrowIdCounter = 1;
    this.refreshTokenIdCounter = 1;
  }

  // User methods
  findUserById(id) {
    return this.users.find(user => user.id === id);
  }

  findUserByUsername(username) {
    return this.users.find(user => user.username === username);
  }

  findUserByEmail(email) {
    return this.users.find(user => user.email === email);
  }

  createUser(userData) {
    const newUser = {
      id: this.userIdCounter++,
      ...userData,
      createdAt: new Date()
    };
    this.users.push(newUser);
    return newUser;
  }

  getAllUsers() {
    return this.users.map(user => {
      const { password, ...userWithoutPassword } = user;
      return userWithoutPassword;
    });
  }

  deleteUser(id) {
    const index = this.users.findIndex(user => user.id === id);
    if (index !== -1) {
      this.users.splice(index, 1);
      return true;
    }
    return false;
  }

  // Book methods
  findBookById(id) {
    return this.books.find(book => book.id === id);
  }

  findBookByIsbn(isbn) {
    return this.books.find(book => book.isbn === isbn);
  }

  getAllBooks() {
    return this.books;
  }

  createBook(bookData) {
    const newBook = {
      id: this.bookIdCounter++,
      ...bookData,
      availableCopies: bookData.totalCopies,
      createdAt: new Date()
    };
    this.books.push(newBook);
    return newBook;
  }

  updateBook(id, bookData) {
    const book = this.findBookById(id);
    if (book) {
      Object.assign(book, bookData);
      book.updatedAt = new Date();
      return book;
    }
    return null;
  }

  deleteBook(id) {
    const index = this.books.findIndex(book => book.id === id);
    if (index !== -1) {
      this.books.splice(index, 1);
      return true;
    }
    return false;
  }

  // Borrow record methods
  createBorrowRecord(userId, bookId) {
    const record = {
      id: this.borrowIdCounter++,
      userId,
      bookId,
      borrowDate: new Date(),
      dueDate: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000), // 14 days
      returnDate: null,
      status: 'borrowed'
    };
    this.borrowRecords.push(record);
    return record;
  }

  getUserBorrowRecords(userId) {
    return this.borrowRecords.filter(record => record.userId === userId);
  }

  getActiveBorrowRecord(userId, bookId) {
    return this.borrowRecords.find(
      record => record.userId === userId && 
                record.bookId === bookId && 
                record.status === 'borrowed'
    );
  }

  returnBook(recordId) {
    const record = this.borrowRecords.find(r => r.id === recordId);
    if (record) {
      record.returnDate = new Date();
      record.status = 'returned';
      return record;
    }
    return null;
  }

  getAllBorrowRecords() {
    return this.borrowRecords;
  }

  // Refresh token methods
  createRefreshToken(userId, token, expiresAt) {
    const refreshToken = {
      id: this.refreshTokenIdCounter++,
      userId,
      token,
      createdAt: new Date(),
      expiresAt,
      revoked: false
    };
    this.refreshTokens.push(refreshToken);
    return refreshToken;
  }

  findRefreshToken(token) {
    return this.refreshTokens.find(rt => rt.token === token && !rt.revoked);
  }

  revokeRefreshToken(token) {
    const refreshToken = this.refreshTokens.find(rt => rt.token === token);
    if (refreshToken) {
      refreshToken.revoked = true;
      refreshToken.revokedAt = new Date();
      return true;
    }
    return false;
  }

  revokeAllUserRefreshTokens(userId) {
    const userTokens = this.refreshTokens.filter(rt => rt.userId === userId && !rt.revoked);
    userTokens.forEach(rt => {
      rt.revoked = true;
      rt.revokedAt = new Date();
    });
    return userTokens.length;
  }

  cleanExpiredRefreshTokens() {
    const now = new Date();
    this.refreshTokens = this.refreshTokens.filter(rt => 
      rt.expiresAt > now || !rt.revoked
    );
  }
}

// Create singleton instance
const db = new Database();

module.exports = db;
