const express = require('express');
const router = express.Router();
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const db = require('../database');

// Generate JWT token
const generateToken = (user) => {
  return jwt.sign(
    { 
      userId: user.id, 
      username: user.username, 
      role: user.role,
      scopes: user.scopes || []
    },
    process.env.JWT_SECRET,
    { expiresIn: process.env.JWT_EXPIRES_IN }
  );
};

// Generate Refresh Token
const generateRefreshToken = (user) => {
  return jwt.sign(
    { 
      userId: user.id,
      type: 'refresh'
    },
    process.env.JWT_REFRESH_SECRET || process.env.JWT_SECRET,
    { expiresIn: '7d' } // Refresh token lasts 7 days
  );
};

// Register new user
router.post('/register', async (req, res) => {
  try {
    const { username, password, email, role } = req.body;

    // Validation
    if (!username || !password || !email) {
      return res.status(400).json({ 
        success: false, 
        message: 'Username, password, and email are required' 
      });
    }

    // Check if user already exists
    if (db.findUserByUsername(username)) {
      return res.status(400).json({ 
        success: false, 
        message: 'Username already exists' 
      });
    }

    if (db.findUserByEmail(email)) {
      return res.status(400).json({ 
        success: false, 
        message: 'Email already exists' 
      });
    }

    // Hash password
    const hashedPassword = await bcrypt.hash(password, 10);

    // Create user (default role is 'user')
    const newUser = db.createUser({
      username,
      password: hashedPassword,
      email,
      role: role === 'admin' ? 'admin' : 'user' // Only allow explicit admin role
    });

    // Generate tokens
    const accessToken = generateToken(newUser);
    const refreshToken = generateRefreshToken(newUser);

    // Store refresh token in database
    const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000); // 7 days
    db.createRefreshToken(newUser.id, refreshToken, expiresAt);

    // Remove password from response
    const { password: _, ...userWithoutPassword } = newUser;

    res.status(201).json({
      success: true,
      message: 'User registered successfully',
      data: {
        user: userWithoutPassword,
        accessToken,
        refreshToken,
        expiresIn: process.env.JWT_EXPIRES_IN || '24h'
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

// Login
router.post('/login', async (req, res) => {
  try {
    const { username, password } = req.body;

    // Validation
    if (!username || !password) {
      return res.status(400).json({ 
        success: false, 
        message: 'Username and password are required' 
      });
    }

    // Find user
    const user = db.findUserByUsername(username);
    if (!user) {
      return res.status(401).json({ 
        success: false, 
        message: 'Invalid credentials' 
      });
    }

    // Check password
    const isPasswordValid = await bcrypt.compare(password, user.password);
    if (!isPasswordValid) {
      return res.status(401).json({ 
        success: false, 
        message: 'Invalid credentials' 
      });
    }

    // Generate tokens
    const accessToken = generateToken(user);
    const refreshToken = generateRefreshToken(user);

    // Store refresh token in database
    const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000); // 7 days
    db.createRefreshToken(user.id, refreshToken, expiresAt);

    // Remove password from response
    const { password: _, ...userWithoutPassword } = user;

    res.json({
      success: true,
      message: 'Login successful',
      data: {
        user: userWithoutPassword,
        accessToken,
        refreshToken,
        expiresIn: process.env.JWT_EXPIRES_IN || '24h'
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

// Refresh Access Token
router.post('/refresh', async (req, res) => {
  try {
    const { refreshToken } = req.body;

    if (!refreshToken) {
      return res.status(400).json({
        success: false,
        message: 'Refresh token required'
      });
    }

    // Check if refresh token exists and not revoked
    const storedToken = db.findRefreshToken(refreshToken);
    if (!storedToken) {
      return res.status(403).json({
        success: false,
        message: 'Invalid or revoked refresh token'
      });
    }

    // Verify refresh token
    jwt.verify(refreshToken, process.env.JWT_REFRESH_SECRET || process.env.JWT_SECRET, (err, decoded) => {
      if (err) {
        return res.status(403).json({
          success: false,
          message: 'Invalid or expired refresh token'
        });
      }

      // Check if token has expired
      if (storedToken.expiresAt < new Date()) {
        return res.status(403).json({
          success: false,
          message: 'Refresh token expired'
        });
      }

      // Get user
      const user = db.findUserById(decoded.userId);
      if (!user) {
        return res.status(404).json({
          success: false,
          message: 'User not found'
        });
      }

      // Generate new access token
      const newAccessToken = generateToken(user);

      res.json({
        success: true,
        message: 'Access token refreshed',
        data: {
          accessToken: newAccessToken,
          expiresIn: process.env.JWT_EXPIRES_IN || '24h'
        }
      });
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Server error',
      error: error.message
    });
  }
});

// Logout (revoke refresh token)
router.post('/logout', async (req, res) => {
  try {
    const { refreshToken } = req.body;

    if (!refreshToken) {
      return res.status(400).json({
        success: false,
        message: 'Refresh token required'
      });
    }

    // Revoke the refresh token
    const revoked = db.revokeRefreshToken(refreshToken);

    if (!revoked) {
      return res.status(404).json({
        success: false,
        message: 'Refresh token not found'
      });
    }

    res.json({
      success: true,
      message: 'Logged out successfully'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Server error',
      error: error.message
    });
  }
});

// Revoke all refresh tokens for a user (logout from all devices)
router.post('/logout-all', async (req, res) => {
  try {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];

    if (!token) {
      return res.status(401).json({
        success: false,
        message: 'Access token required'
      });
    }

    // Verify access token
    jwt.verify(token, process.env.JWT_SECRET, (err, decoded) => {
      if (err) {
        return res.status(403).json({
          success: false,
          message: 'Invalid or expired token'
        });
      }

      // Revoke all user's refresh tokens
      const revokedCount = db.revokeAllUserRefreshTokens(decoded.userId);

      res.json({
        success: true,
        message: `Logged out from all devices`,
        revokedTokens: revokedCount
      });
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
