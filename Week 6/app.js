require('dotenv').config();
const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');

// Import routes
const authRoutes = require('./routes/auth');
const adminRoutes = require('./routes/admin');
const userRoutes = require('./routes/user');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Request logging middleware
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
  next();
});

// Routes
app.use('/api/auth', authRoutes);
app.use('/api/admin', adminRoutes);
app.use('/api/user', userRoutes);

// Root endpoint
app.get('/', (req, res) => {
  res.json({
    success: true,
    message: 'Library Management API',
    version: '1.0.0',
    endpoints: {
      auth: {
        register: 'POST /api/auth/register',
        login: 'POST /api/auth/login'
      },
      admin: {
        books: 'GET/POST /api/admin/books',
        bookById: 'GET/PUT/DELETE /api/admin/books/:id',
        users: 'GET /api/admin/users',
        userById: 'GET/DELETE /api/admin/users/:id',
        lendBook: 'POST /api/admin/lend',
        borrowRecords: 'GET /api/admin/borrow-records'
      },
      user: {
        books: 'GET /api/user/books',
        bookById: 'GET /api/user/books/:id',
        borrowBook: 'POST /api/user/borrow/:bookId',
        returnBook: 'POST /api/user/return/:bookId',
        myBorrows: 'GET /api/user/my-borrows',
        myActiveBorrows: 'GET /api/user/my-active-borrows'
      }
    }
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    success: false,
    message: 'Endpoint not found'
  });
});

// Error handler
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({
    success: false,
    message: 'Internal server error',
    error: err.message
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`=============================================`);
  console.log(`Library Management API Server`);
  console.log(`Server is running on port ${PORT}`);
  console.log(`Environment: ${process.env.NODE_ENV || 'development'}`);
  console.log(`API Base URL: http://localhost:${PORT}`);
  console.log(`=============================================`);
  console.log(`\nDefault Accounts:`);
  console.log(`Admin - username: admin, password: admin123`);
  console.log(`User  - username: user1, password: user123`);
  console.log(`=============================================\n`);
});

module.exports = app;
