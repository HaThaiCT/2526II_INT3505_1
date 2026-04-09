const express = require('express');
const router = express.Router();
const { authenticateToken, requireScope, requireAllScopes } = require('../middleware/auth');

// Demo: Public endpoint (no authentication required)
router.get('/public', (req, res) => {
  res.json({
    success: true,
    message: 'This is a public endpoint - No authentication required',
    data: {
      timestamp: new Date(),
      description: 'Anyone can access this endpoint'
    }
  });
});

// Demo: Authenticated endpoint (requires valid token)
router.get('/authenticated', authenticateToken, (req, res) => {
  res.json({
    success: true,
    message: 'This endpoint requires authentication',
    data: {
      user: {
        userId: req.user.userId,
        username: req.user.username,
        role: req.user.role,
        scopes: req.user.scopes
      },
      description: 'You are authenticated!'
    }
  });
});

// Demo: Requires 'books:read' scope
router.get('/books-read', 
  authenticateToken, 
  requireScope('books:read'),
  (req, res) => {
    res.json({
      success: true,
      message: 'You have books:read permission',
      data: {
        requiredScope: 'books:read',
        userScopes: req.user.scopes,
        demoBooks: [
          { id: 1, title: 'Book 1' },
          { id: 2, title: 'Book 2' }
        ]
      }
    });
  }
);

// Demo: Requires 'books:write' scope
router.post('/books-write', 
  authenticateToken, 
  requireScope('books:write'),
  (req, res) => {
    res.json({
      success: true,
      message: 'You have books:write permission',
      data: {
        requiredScope: 'books:write',
        userScopes: req.user.scopes,
        action: 'Book created (demo)',
        book: { id: 999, title: req.body.title || 'New Book' }
      }
    });
  }
);

// Demo: Requires 'books:delete' scope
router.delete('/books-delete/:id', 
  authenticateToken, 
  requireScope('books:delete'),
  (req, res) => {
    res.json({
      success: true,
      message: 'You have books:delete permission',
      data: {
        requiredScope: 'books:delete',
        userScopes: req.user.scopes,
        action: 'Book deleted (demo)',
        bookId: req.params.id
      }
    });
  }
);

// Demo: Requires EITHER 'users:read' OR 'users:write' scope
router.get('/users-any', 
  authenticateToken, 
  requireScope('users:read', 'users:write'),
  (req, res) => {
    res.json({
      success: true,
      message: 'You have users:read OR users:write permission',
      data: {
        requiredScopes: 'users:read OR users:write',
        userScopes: req.user.scopes,
        note: 'This endpoint accepts users who have ANY of the required scopes'
      }
    });
  }
);

// Demo: Requires ALL: 'books:write' AND 'books:delete' scopes
router.post('/books-full-access', 
  authenticateToken, 
  requireAllScopes('books:write', 'books:delete'),
  (req, res) => {
    res.json({
      success: true,
      message: 'You have BOTH books:write AND books:delete permissions',
      data: {
        requiredScopes: ['books:write', 'books:delete'],
        userScopes: req.user.scopes,
        note: 'This endpoint requires ALL specified scopes'
      }
    });
  }
);

// Demo: Admin-only endpoint (requires 'users:delete' scope - only admin has this)
router.delete('/admin-only', 
  authenticateToken, 
  requireScope('users:delete'),
  (req, res) => {
    res.json({
      success: true,
      message: 'Admin-only endpoint',
      data: {
        requiredScope: 'users:delete',
        userScopes: req.user.scopes,
        note: 'Only admin users have this scope'
      }
    });
  }
);

// Demo: Get user's current scopes
router.get('/my-scopes', authenticateToken, (req, res) => {
  res.json({
    success: true,
    message: 'Your current scopes',
    data: {
      user: req.user.username,
      role: req.user.role,
      scopes: req.user.scopes,
      description: 'These are the permissions you have access to'
    }
  });
});

// Demo: Scope hierarchy explanation
router.get('/scope-info', (req, res) => {
  res.json({
    success: true,
    message: 'Scope Information',
    data: {
      availableScopes: {
        'books:read': 'View books',
        'books:write': 'Create/Update books',
        'books:delete': 'Delete books',
        'users:read': 'View users',
        'users:write': 'Create/Update users',
        'users:delete': 'Delete users (Admin only)',
        'borrow:own': 'Borrow/Return own books',
        'borrow:all': 'Manage all borrow records (Admin only)'
      },
      roleScopes: {
        admin: [
          'books:read', 'books:write', 'books:delete',
          'users:read', 'users:write', 'users:delete',
          'borrow:all'
        ],
        user: [
          'books:read',
          'borrow:own'
        ]
      },
      middleware: {
        'requireScope(scope1, scope2, ...)': 'Requires ANY of the listed scopes',
        'requireAllScopes(scope1, scope2, ...)': 'Requires ALL of the listed scopes'
      }
    }
  });
});

module.exports = router;
