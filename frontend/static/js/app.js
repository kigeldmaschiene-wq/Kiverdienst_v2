/**
 * KIVerdienst v2 - Frontend JavaScript
 * Global utilities and API helpers
 */

// API helper function
async function apiCall(endpoint, method = 'GET', data = null) {
    try {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            }
        };
        
        if (data && (method === 'POST' || method === 'PUT')) {
            options.body = JSON.stringify(data);
        }
        
        // Use proxy endpoint
        const url = `/api/proxy${endpoint}`;
        
        const response = await fetch(url, options);
        const result = await response.json();
        
        return result;
    } catch (error) {
        console.error('API call failed:', error);
        return {
            success: false,
            error: error.message || 'Network error'
        };
    }
}

// Format number with commas
function formatNumber(num) {
    if (!num) return '0';
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

// Format date
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Format datetime
function formatDateTime(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Show notification
function showNotification(message, type = 'info') {
    // Simple alert for now, can be replaced with toast library
    if (type === 'error') {
        alert('Error: ' + message);
    } else if (type === 'success') {
        alert('Success: ' + message);
    } else {
        alert(message);
    }
}

// Confirm action
function confirmAction(message) {
    return confirm(message);
}

// Copy to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied to clipboard', 'success');
    }).catch(err => {
        console.error('Failed to copy:', err);
    });
}

// Debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Initialize tooltips (if needed)
document.addEventListener('DOMContentLoaded', function() {
    console.log('KIVerdienst v2 Frontend Ready');
    
    // Add any global event listeners here
    
    // Check for pre-filled form data from sessionStorage
    if (sessionStorage.getItem('videoTitle')) {
        const titleInput = document.getElementById('title');
        if (titleInput) {
            titleInput.value = sessionStorage.getItem('videoTitle');
            sessionStorage.removeItem('videoTitle');
        }
    }
    
    if (sessionStorage.getItem('videoHook')) {
        const hookInput = document.getElementById('hook');
        if (hookInput) {
            hookInput.value = sessionStorage.getItem('videoHook');
            sessionStorage.removeItem('videoHook');
        }
    }
});

// Export functions for use in templates
window.apiCall = apiCall;
window.formatNumber = formatNumber;
window.formatDate = formatDate;
window.formatDateTime = formatDateTime;
window.showNotification = showNotification;
window.confirmAction = confirmAction;
window.copyToClipboard = copyToClipboard;
