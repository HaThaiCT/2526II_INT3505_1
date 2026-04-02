// Utility script to generate bcrypt password hashes
// Run this once to get the correct hashes for default users

const bcrypt = require('bcryptjs');

async function generateHashes() {
  const adminPassword = await bcrypt.hash('admin123', 10);
  const userPassword = await bcrypt.hash('user123', 10);
  
  console.log('Admin password hash (admin123):', adminPassword);
  console.log('User password hash (user123):', userPassword);
  console.log('\nCopy these hashes to database.js');
}

generateHashes();
