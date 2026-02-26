// Authentication and Session Management
// File: auth.js

console.log('🔐 Auth.js loaded successfully!');

// Check user session and update UI
function checkUserSession() {
    console.log('🔍 Checking user session...');
    const sessionString = localStorage.getItem('userSession');
    
    if (!sessionString) {
        console.log('ℹ️ No active session found');
        return false;
    }
    
    try {
        const userData = JSON.parse(sessionString);
        
        // Validate session data
        if (!userData || !userData.name || !userData.email) {
            console.error('❌ Invalid session data - missing required fields');
            console.log('Session data:', userData);
            localStorage.removeItem('userSession');
            return false;
        }
        
        console.log('✅ User logged in:', userData.name);
        updateNavbarForLoggedInUser(userData);
        return true;
    } catch (error) {
        console.error('❌ Error parsing session:', error);
        console.log('Corrupted session string:', sessionString);
        localStorage.removeItem('userSession');
        alert('Session corrupted! Silakan login kembali.');
        return false;
    }
}

// Update navbar to show user info and logout button
function updateNavbarForLoggedInUser(userData) {
    console.log('🔄 Updating navbar for user:', userData.name);
    
    // Find register, login, user, and logout items by ID
    const registerItem = document.getElementById('registerItem');
    const loginItem = document.getElementById('loginItem');
    const userItem = document.getElementById('userItem');
    const logoutItem = document.getElementById('logoutItem');
    const usernameSpan = document.getElementById('username');
    
    if (registerItem && loginItem && userItem && logoutItem && usernameSpan) {
        // Hide Register and Login buttons
        registerItem.style.display = 'none';
        loginItem.style.display = 'none';
        console.log('✅ Register and Login buttons hidden');
        
        // Show User Info and Logout
        userItem.style.display = '';
        userItem.classList.remove('d-none');
        logoutItem.style.display = '';
        logoutItem.classList.remove('d-none');
        
        // Set username
        usernameSpan.textContent = userData.name;
        console.log('✅ User info displayed:', userData.name);
        console.log('✅ Logout button shown');
    } else {
        console.error('❌ Could not find navbar elements!');
        if (!registerItem) console.error('  - Missing #registerItem');
        if (!loginItem) console.error('  - Missing #loginItem');
        if (!userItem) console.error('  - Missing #userItem');
        if (!logoutItem) console.error('  - Missing #logoutItem');
        if (!usernameSpan) console.error('  - Missing #username');
    }
}

// Confirm logout
function confirmLogout(event) {
    event.preventDefault();
    console.log('🚪 Logout button clicked');
    
    const confirmDialog = confirm('Apakah Anda yakin ingin keluar dari akun Anda?');
    
    if (confirmDialog) {
        handleLogout();
    } else {
        console.log('❌ Logout cancelled');
    }
}

// Handle logout
function handleLogout() {
    console.log('🚪 Logging out...');
    
    // Remove session
    localStorage.removeItem('userSession');
    console.log('✅ Session removed');
    
    // Show success message
    alert('Anda telah berhasil logout. Halaman akan dimuat ulang...');
    
    // Reload page
    window.location.reload();
}

// Initialize on DOM ready
function initAuth() {
    console.log('🚀 Initializing authentication...');
    
    // Wait a bit to ensure DOM is fully loaded
    setTimeout(() => {
        checkUserSession();
    }, 100);
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAuth);
} else {
    initAuth();
}

// Debug: Log current localStorage
// Minimal auth logging (avoid printing session content in production)
console.log('Auth.js initialized');

// Provide backward-compatible global logout function for existing inline handlers
function logout() {
    try {
        handleLogout();
    } catch (e) {
        console.error('Logout failed:', e);
    }
}

// Also expose on window in case other scripts reference it
window.logout = logout;