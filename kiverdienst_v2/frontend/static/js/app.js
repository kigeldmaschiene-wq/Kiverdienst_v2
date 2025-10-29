/**
 * KIVerdienst v2 - Frontend JavaScript
 * Vanilla JavaScript utilities and helpers
 */

// ============================================================================
// Toast Notifications
// ============================================================================

/**
 * Show a toast notification
 * @param {string} message - Message to display
 * @param {string} type - Type of toast (success, error, warning, info)
 * @param {number} duration - Duration in milliseconds (default: 3000)
 */
function showToast(message, type = 'info', duration = 3000) {
    const container = document.getElementById('toast-container');
    if (!container) {
        console.error('Toast container not found');
        return;
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <strong>${type.charAt(0).toUpperCase() + type.slice(1)}</strong>
        <p>${message}</p>
    `;

    container.appendChild(toast);

    // Auto-remove toast after duration
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => {
            container.removeChild(toast);
        }, 300);
    }, duration);
}

// ============================================================================
// API Helper Functions
// ============================================================================

/**
 * Make an API request
 * @param {string} endpoint - API endpoint
 * @param {string} method - HTTP method (GET, POST, PUT, DELETE, PATCH)
 * @param {object} data - Request body data
 * @returns {Promise<object>} API response
 */
async function apiRequest(endpoint, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        }
    };

    if (data && method !== 'GET') {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(`/api/${endpoint}`, options);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.message || errorData.detail || `HTTP ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

// ============================================================================
// Date & Time Utilities
// ============================================================================

/**
 * Format a date string to German locale
 * @param {string} dateString - ISO date string
 * @returns {string} Formatted date
 */
function formatDate(dateString) {
    if (!dateString) return '-';
    
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('de-DE', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        });
    } catch (error) {
        return dateString;
    }
}

/**
 * Format a date-time string to German locale
 * @param {string} dateString - ISO date string
 * @returns {string} Formatted date and time
 */
function formatDateTime(dateString) {
    if (!dateString) return '-';
    
    try {
        const date = new Date(dateString);
        return date.toLocaleString('de-DE', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch (error) {
        return dateString;
    }
}

/**
 * Convert date to relative time (e.g., "vor 5 Minuten")
 * @param {string} dateString - ISO date string
 * @returns {string} Relative time
 */
function timeAgo(dateString) {
    if (!dateString) return '-';
    
    try {
        const date = new Date(dateString);
        const now = new Date();
        const seconds = Math.floor((now - date) / 1000);

        if (seconds < 60) return 'gerade eben';
        if (seconds < 3600) {
            const minutes = Math.floor(seconds / 60);
            return `vor ${minutes} Minute${minutes > 1 ? 'n' : ''}`;
        }
        if (seconds < 86400) {
            const hours = Math.floor(seconds / 3600);
            return `vor ${hours} Stunde${hours > 1 ? 'n' : ''}`;
        }
        const days = Math.floor(seconds / 86400);
        return `vor ${days} Tag${days > 1 ? 'en' : ''}`;
    } catch (error) {
        return dateString;
    }
}

// ============================================================================
// Form Utilities
// ============================================================================

/**
 * Get form data as an object
 * @param {HTMLFormElement} form - Form element
 * @returns {object} Form data as key-value pairs
 */
function getFormData(form) {
    const formData = new FormData(form);
    const data = {};
    
    for (const [key, value] of formData.entries()) {
        data[key] = value;
    }
    
    return data;
}

/**
 * Reset form and clear validation errors
 * @param {HTMLFormElement} form - Form element
 */
function resetForm(form) {
    form.reset();
    
    // Clear any validation error classes
    const inputs = form.querySelectorAll('.error');
    inputs.forEach(input => {
        input.classList.remove('error');
    });
}

/**
 * Validate email address
 * @param {string} email - Email address
 * @returns {boolean} True if valid
 */
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// ============================================================================
// String Utilities
// ============================================================================

/**
 * Escape HTML to prevent XSS
 * @param {string} text - Text to escape
 * @returns {string} Escaped text
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Truncate text to specified length
 * @param {string} text - Text to truncate
 * @param {number} length - Max length
 * @returns {string} Truncated text
 */
function truncate(text, length = 100) {
    if (!text || text.length <= length) return text;
    return text.substring(0, length) + '...';
}

/**
 * Capitalize first letter of a string
 * @param {string} text - Text to capitalize
 * @returns {string} Capitalized text
 */
function capitalize(text) {
    if (!text) return '';
    return text.charAt(0).toUpperCase() + text.slice(1);
}

// ============================================================================
// Number Utilities
// ============================================================================

/**
 * Format number with thousands separator
 * @param {number} num - Number to format
 * @returns {string} Formatted number
 */
function formatNumber(num) {
    if (num === null || num === undefined) return '0';
    return num.toLocaleString('de-DE');
}

/**
 * Format bytes to human-readable size
 * @param {number} bytes - Bytes
 * @returns {string} Formatted size
 */
function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// ============================================================================
// Loading Indicator
// ============================================================================

/**
 * Show loading indicator on an element
 * @param {HTMLElement} element - Element to show loading on
 */
function showLoading(element) {
    element.classList.add('loading');
    element.setAttribute('disabled', 'disabled');
}

/**
 * Hide loading indicator from an element
 * @param {HTMLElement} element - Element to hide loading from
 */
function hideLoading(element) {
    element.classList.remove('loading');
    element.removeAttribute('disabled');
}

// ============================================================================
// Local Storage Helpers
// ============================================================================

/**
 * Save data to localStorage
 * @param {string} key - Storage key
 * @param {any} value - Value to store
 */
function saveToStorage(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
        console.error('Failed to save to localStorage:', error);
    }
}

/**
 * Load data from localStorage
 * @param {string} key - Storage key
 * @param {any} defaultValue - Default value if key doesn't exist
 * @returns {any} Stored value or default
 */
function loadFromStorage(key, defaultValue = null) {
    try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : defaultValue;
    } catch (error) {
        console.error('Failed to load from localStorage:', error);
        return defaultValue;
    }
}

/**
 * Remove data from localStorage
 * @param {string} key - Storage key
 */
function removeFromStorage(key) {
    try {
        localStorage.removeItem(key);
    } catch (error) {
        console.error('Failed to remove from localStorage:', error);
    }
}

// ============================================================================
// Debounce & Throttle
// ============================================================================

/**
 * Debounce a function
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 */
function debounce(func, wait = 300) {
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

/**
 * Throttle a function
 * @param {Function} func - Function to throttle
 * @param {number} limit - Time limit in milliseconds
 * @returns {Function} Throttled function
 */
function throttle(func, limit = 300) {
    let inThrottle;
    return function executedFunction(...args) {
        if (!inThrottle) {
            func(...args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// ============================================================================
// Confirmation Dialog
// ============================================================================

/**
 * Show a confirmation dialog
 * @param {string} message - Message to display
 * @returns {Promise<boolean>} True if confirmed
 */
async function confirmAction(message) {
    return new Promise((resolve) => {
        const result = confirm(message);
        resolve(result);
    });
}

// ============================================================================
// Copy to Clipboard
// ============================================================================

/**
 * Copy text to clipboard
 * @param {string} text - Text to copy
 * @returns {Promise<boolean>} True if successful
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showToast('In Zwischenablage kopiert', 'success');
        return true;
    } catch (error) {
        console.error('Failed to copy to clipboard:', error);
        showToast('Fehler beim Kopieren', 'error');
        return false;
    }
}

// ============================================================================
// Element Visibility
// ============================================================================

/**
 * Show an element
 * @param {HTMLElement|string} element - Element or selector
 */
function show(element) {
    const el = typeof element === 'string' ? document.querySelector(element) : element;
    if (el) el.style.display = 'block';
}

/**
 * Hide an element
 * @param {HTMLElement|string} element - Element or selector
 */
function hide(element) {
    const el = typeof element === 'string' ? document.querySelector(element) : element;
    if (el) el.style.display = 'none';
}

/**
 * Toggle element visibility
 * @param {HTMLElement|string} element - Element or selector
 */
function toggle(element) {
    const el = typeof element === 'string' ? document.querySelector(element) : element;
    if (el) {
        el.style.display = el.style.display === 'none' ? 'block' : 'none';
    }
}

// ============================================================================
// Query String Utilities
// ============================================================================

/**
 * Get URL parameter value
 * @param {string} param - Parameter name
 * @returns {string|null} Parameter value
 */
function getUrlParam(param) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(param);
}

/**
 * Set URL parameter without page reload
 * @param {string} param - Parameter name
 * @param {string} value - Parameter value
 */
function setUrlParam(param, value) {
    const url = new URL(window.location);
    url.searchParams.set(param, value);
    window.history.pushState({}, '', url);
}

// ============================================================================
// Initialization
// ============================================================================

// Global error handler
window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
});

// Global unhandled rejection handler
window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled rejection:', event.reason);
});

// Console welcome message
console.log('%cKIVerdienst v2', 'font-size: 24px; font-weight: bold; color: #3B82F6;');
console.log('%cAutonomous TikTok Content Generation System', 'font-size: 14px; color: #6B7280;');
console.log('%cv2.0.0', 'font-size: 12px; color: #9CA3AF;');

// Export functions for global access
window.KV = {
    // Toast
    showToast,
    
    // API
    apiRequest,
    
    // Date & Time
    formatDate,
    formatDateTime,
    timeAgo,
    
    // Forms
    getFormData,
    resetForm,
    isValidEmail,
    
    // Strings
    escapeHtml,
    truncate,
    capitalize,
    
    // Numbers
    formatNumber,
    formatBytes,
    
    // Loading
    showLoading,
    hideLoading,
    
    // Storage
    saveToStorage,
    loadFromStorage,
    removeFromStorage,
    
    // Utilities
    debounce,
    throttle,
    confirmAction,
    copyToClipboard,
    show,
    hide,
    toggle,
    getUrlParam,
    setUrlParam
};
