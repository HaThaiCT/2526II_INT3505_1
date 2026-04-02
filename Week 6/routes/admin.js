const express = require('express');
const router = express.Router();
const db = require('../database');
const { authenticateToken, isAdmin } = require('../middleware/auth');

// All admin routes require authentication and admin role
router.use(authenticateToken);
router.use(isAdmin);

// ==================== BOOK MANAGEMENT ====================

// Get all books
router.get('/books', (req, res) => {
  try {
    const books = db.getAllBooks();
    res.json({
      success: true,
      data: books
    });
  } catch (error) {
    res.status(500).json({ 
      success: false, 
      message: 'Server error', 
      error: error.message 
    });
  }
});

// Get book by ID
router.get('/books/:id', (req, res) => {
  try {
    const book = db.findBookById(parseInt(req.params.id));
    if (!book) {
      return res.status(404).json({ 
        success: false, 
        message: 'Book not found' 
      });
    }
    res.json({
      success: true,
      data: book
    });
  } catch (error) {
    res.status(500).json({ 
      success: false, 
      message: 'Server error', 
      error: error.message 
    });
  }
});

// Create new book
router.post('/books', (req, res) => {
  try {
    const { title, author, isbn, totalCopies } = req.body;

    // Validation
    if (!title || !author || !isbn || !totalCopies) {
      return res.status(400).json({ 
        success: false, 
        message: 'Title, author, ISBN, and total copies are required' 
      });
    }

    if (totalCopies < 1) {
      return res.status(400).json({ 
        success: false, 
        message: 'Total copies must be at least 1' 
      });
    }

    // Check if ISBN already exists
    if (db.findBookByIsbn(isbn)) {
      return res.status(400).json({ 
        success: false, 
        message: 'Book with this ISBN already exists' 
      });
    }

    const newBook = db.createBook({
      title,
      author,
      isbn,
      totalCopies: parseInt(totalCopies)
    });

    res.status(201).json({
      success: true,
      message: 'Book created successfully',
      data: newBook
    });
  } catch (error) {
    res.status(500).json({ 
      success: false, 
      message: 'Server error', 
      error: error.message 
    });
  }
});

// Update book
router.put('/books/:id', (req, res) => {
  try {
    const bookId = parseInt(req.params.id);
    const { title, author, isbn, totalCopies } = req.body;

    const book = db.findBookById(bookId);
    if (!book) {
      return res.status(404).json({ 
        success: false, 
        message: 'Book not found' 
      });
    }

    // Check if new ISBN conflicts with another book
    if (isbn && isbn !== book.isbn) {
      const existingBook = db.findBookByIsbn(isbn);
      if (existingBook && existingBook.id !== bookId) {
        return res.status(400).json({ 
          success: false, 
          message: 'Another book with this ISBN already exists' 
        });
      }
    }

    // Update only provided fields
    const updateData = {};
    if (title) updateData.title = title;
    if (author) updateData.author = author;
    if (isbn) updateData.isbn = isbn;
    if (totalCopies !== undefined) {
      const newTotal = parseInt(totalCopies);
      if (newTotal < 1) {
        return res.status(400).json({ 
          success: false, 
          message: 'Total copies must be at least 1' 
        });
      }
      // Adjust available copies proportionally
      const borrowedCopies = book.totalCopies - book.availableCopies;
      updateData.totalCopies = newTotal;
      updateData.availableCopies = Math.max(0, newTotal - borrowedCopies);
    }

    const updatedBook = db.updateBook(bookId, updateData);

    res.json({
      success: true,
      message: 'Book updated successfully',
      data: updatedBook
    });
  } catch (error) {
    res.status(500).json({ 
      success: false, 
      message: 'Server error', 
      error: error.message 
    });
  }
});

// Delete book
router.delete('/books/:id', (req, res) => {
  try {
    const bookId = parseInt(req.params.id);
    
    const book = db.findBookById(bookId);
    if (!book) {
      return res.status(404).json({ 
        success: false, 
        message: 'Book not found' 
      });
    }

    // Check if book is currently borrowed
    if (book.availableCopies < book.totalCopies) {
      return res.status(400).json({ 
        success: false, 
        message: 'Cannot delete book with active borrows. Wait for all copies to be returned.' 
      });
    }

    db.deleteBook(bookId);

    res.json({
      success: true,
      message: 'Book deleted successfully'
    });
  } catch (error) {
    res.status(500).json({ 
      success: false, 
      message: 'Server error', 
      error: error.message 
    });
  }
});

// ==================== USER MANAGEMENT ====================

// Get all users
router.get('/users', (req, res) => {
  try {
    const users = db.getAllUsers();
    res.json({
      success: true,
      data: users
    });
  } catch (error) {
    res.status(500).json({ 
      success: false, 
      message: 'Server error', 
      error: error.message 
    });
  }
});

// Get user by ID
router.get('/users/:id', (req, res) => {
  try {
    const user = db.findUserById(parseInt(req.params.id));
    if (!user) {
      return res.status(404).json({ 
        success: false, 
        message: 'User not found' 
      });
    }

    const { password, ...userWithoutPassword } = user;
    res.json({
      success: true,
      data: userWithoutPassword
    });
  } catch (error) {
    res.status(500).json({ 
      success: false, 
      message: 'Server error', 
      error: error.message 
    });
  }
});

// Delete user (admin cannot delete themselves)
router.delete('/users/:id', (req, res) => {
  try {
    const userId = parseInt(req.params.id);

    if (userId === req.user.userId) {
      return res.status(400).json({ 
        success: false, 
        message: 'Cannot delete your own account' 
      });
    }

    const user = db.findUserById(userId);
    if (!user) {
      return res.status(404).json({ 
        success: false, 
        message: 'User not found' 
      });
    }

    // Check if user has active borrows
    const activeRecords = db.getUserBorrowRecords(userId)
      .filter(record => record.status === 'borrowed');
    
    if (activeRecords.length > 0) {
      return res.status(400).json({ 
        success: false, 
        message: 'Cannot delete user with active book borrows' 
      });
    }

    db.deleteUser(userId);

    res.json({
      success: true,
      message: 'User deleted successfully'
    });
  } catch (error) {
    res.status(500).json({ 
      success: false, 
      message: 'Server error', 
      error: error.message 
    });
  }
});

// ==================== LENDING MANAGEMENT ====================

// Lend book to user (admin assigns book to user)
router.post('/lend', (req, res) => {
  try {
    const { userId, bookId } = req.body;

    if (!userId || !bookId) {
      return res.status(400).json({ 
        success: false, 
        message: 'User ID and Book ID are required' 
      });
    }

    // Check if user exists
    const user = db.findUserById(parseInt(userId));
    if (!user) {
      return res.status(404).json({ 
        success: false, 
        message: 'User not found' 
      });
    }

    // Check if book exists
    const book = db.findBookById(parseInt(bookId));
    if (!book) {
      return res.status(404).json({ 
        success: false, 
        message: 'Book not found' 
      });
    }

    // Check if book is available
    if (book.availableCopies < 1) {
      return res.status(400).json({ 
        success: false, 
        message: 'No copies available for this book' 
      });
    }

    // Check if user already borrowed this book
    const existingRecord = db.getActiveBorrowRecord(parseInt(userId), parseInt(bookId));
    if (existingRecord) {
      return res.status(400).json({ 
        success: false, 
        message: 'User already has an active borrow for this book' 
      });
    }

    // Create borrow record
    const record = db.createBorrowRecord(parseInt(userId), parseInt(bookId));

    // Decrease available copies
    book.availableCopies--;

    res.status(201).json({
      success: true,
      message: 'Book lent successfully',
      data: {
        record,
        user: { id: user.id, username: user.username },
        book: { id: book.id, title: book.title }
      }
    });
  } catch (error) {
    res.status(500).json({ 
      success: false, 
      message: 'Server error', 
      error: error.message 
    });
  }
});

// Get all borrow records
router.get('/borrow-records', (req, res) => {
  try {
    const records = db.getAllBorrowRecords();
    
    // Enrich records with user and book information
    const enrichedRecords = records.map(record => {
      const user = db.findUserById(record.userId);
      const book = db.findBookById(record.bookId);
      return {
        ...record,
        user: user ? { id: user.id, username: user.username, email: user.email } : null,
        book: book ? { id: book.id, title: book.title, author: book.author } : null
      };
    });

    res.json({
      success: true,
      data: enrichedRecords
    });
  } catch (error) {
    res.status(500).json({ 
      success: false, 
      message: 'Server error', 
      error: error.message 
    });
  }
});

module.exports = router;
