const express = require('express');
const router = express.Router();
const db = require('../database');
const { authenticateToken } = require('../middleware/auth');

// All user routes require authentication
router.use(authenticateToken);

// ==================== BOOK BROWSING ====================

// Get all available books
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

// ==================== BORROW MANAGEMENT ====================

// Borrow a book
router.post('/borrow/:bookId', (req, res) => {
  try {
    const bookId = parseInt(req.params.bookId);
    const userId = req.user.userId;

    // Check if book exists
    const book = db.findBookById(bookId);
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
    const existingRecord = db.getActiveBorrowRecord(userId, bookId);
    if (existingRecord) {
      return res.status(400).json({ 
        success: false, 
        message: 'You have already borrowed this book' 
      });
    }

    // Create borrow record
    const record = db.createBorrowRecord(userId, bookId);

    // Decrease available copies
    book.availableCopies--;

    res.status(201).json({
      success: true,
      message: 'Book borrowed successfully',
      data: {
        record,
        book: {
          id: book.id,
          title: book.title,
          author: book.author
        },
        dueDate: record.dueDate
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

// Return a book
router.post('/return/:bookId', (req, res) => {
  try {
    const bookId = parseInt(req.params.bookId);
    const userId = req.user.userId;

    // Check if book exists
    const book = db.findBookById(bookId);
    if (!book) {
      return res.status(404).json({ 
        success: false, 
        message: 'Book not found' 
      });
    }

    // Find active borrow record
    const record = db.getActiveBorrowRecord(userId, bookId);
    if (!record) {
      return res.status(400).json({ 
        success: false, 
        message: 'You have not borrowed this book or already returned it' 
      });
    }

    // Return the book
    db.returnBook(record.id);

    // Increase available copies
    book.availableCopies++;

    // Check if returned late
    const isLate = new Date() > new Date(record.dueDate);

    res.json({
      success: true,
      message: 'Book returned successfully',
      data: {
        record: {
          id: record.id,
          borrowDate: record.borrowDate,
          dueDate: record.dueDate,
          returnDate: record.returnDate,
          isLate
        },
        book: {
          id: book.id,
          title: book.title,
          author: book.author
        }
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

// ==================== USER'S BORROW HISTORY ====================

// Get current user's borrow records
router.get('/my-borrows', (req, res) => {
  try {
    const userId = req.user.userId;
    const records = db.getUserBorrowRecords(userId);

    // Enrich records with book information
    const enrichedRecords = records.map(record => {
      const book = db.findBookById(record.bookId);
      const isLate = record.status === 'borrowed' && new Date() > new Date(record.dueDate);
      
      return {
        id: record.id,
        borrowDate: record.borrowDate,
        dueDate: record.dueDate,
        returnDate: record.returnDate,
        status: record.status,
        isLate,
        book: book ? {
          id: book.id,
          title: book.title,
          author: book.author,
          isbn: book.isbn
        } : null
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

// Get current user's active borrows
router.get('/my-active-borrows', (req, res) => {
  try {
    const userId = req.user.userId;
    const records = db.getUserBorrowRecords(userId)
      .filter(record => record.status === 'borrowed');

    // Enrich records with book information
    const enrichedRecords = records.map(record => {
      const book = db.findBookById(record.bookId);
      const isLate = new Date() > new Date(record.dueDate);
      const daysUntilDue = Math.ceil((new Date(record.dueDate) - new Date()) / (1000 * 60 * 60 * 24));
      
      return {
        id: record.id,
        borrowDate: record.borrowDate,
        dueDate: record.dueDate,
        isLate,
        daysUntilDue,
        book: book ? {
          id: book.id,
          title: book.title,
          author: book.author,
          isbn: book.isbn
        } : null
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
