const jwt = require('jsonwebtoken');
const db = require('../database');

// Verify JWT token
const authenticateToken = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN

  if (!token) {
    return res.status(401).json({ 
      success: false, 
      message: 'Access token required' 
    });
  }

  jwt.verify(token, process.env.JWT_SECRET, (err, decoded) => {
    if (err) {
      return res.status(403).json({ 
        success: false, 
        message: 'Invalid or expired token' 
      });
    }

    // Find user in database
    const user = db.findUserById(decoded.userId);
    if (!user) {
      return res.status(404).json({ 
        success: false, 
        message: 'User not found' 
      });
    }

    req.user = {
      userId: decoded.userId,
      username: decoded.username,
      role: decoded.role,
      scopes: decoded.scopes || []
    };
    next();
  });
};

// Check if user is admin
const isAdmin = (req, res, next) => {
  if (req.user.role !== 'admin') {
    return res.status(403).json({ 
      success: false, 
      message: 'Admin access required' 
    });
  }
  next();
};

// Check if user is regular user or admin
const isUser = (req, res, next) => {
  if (req.user.role !== 'user' && req.user.role !== 'admin') {
    return res.status(403).json({ 
      success: false, 
      message: 'User access required' 
    });
  }
  next();
};

// Check if user has required scope(s)
const requireScope = (...requiredScopes) => {
  return (req, res, next) => {
    if (!req.user || !req.user.scopes) {
      return res.status(403).json({ 
        success: false, 
        message: 'No scopes found' 
      });
    }

    // Check if user has ANY of the required scopes
    const hasScope = requiredScopes.some(scope => 
      req.user.scopes.includes(scope)
    );

    if (!hasScope) {
      return res.status(403).json({ 
        success: false, 
        message: `Required scope: ${requiredScopes.join(' or ')}`,
        userScopes: req.user.scopes
      });
    }

    next();
  };
};

// Check if user has ALL required scopes
const requireAllScopes = (...requiredScopes) => {
  return (req, res, next) => {
    if (!req.user || !req.user.scopes) {
      return res.status(403).json({ 
        success: false, 
        message: 'No scopes found' 
      });
    }

    // Check if user has ALL of the required scopes
    const hasAllScopes = requiredScopes.every(scope => 
      req.user.scopes.includes(scope)
    );

    if (!hasAllScopes) {
      const missingScopes = requiredScopes.filter(scope => 
        !req.user.scopes.includes(scope)
      );
      return res.status(403).json({ 
        success: false, 
        message: `Missing required scopes: ${missingScopes.join(', ')}`,
        userScopes: req.user.scopes
      });
    }

    next();
  };
};

module.exports = {
  authenticateToken,
  isAdmin,
  isUser,
  requireScope,
  requireAllScopes
};
