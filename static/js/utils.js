/**
 * Utility Functions
 * 
 * This module provides helper functions used throughout the application:
 * - API request wrapper
 * - Error handling
 * - Form validation
 * - Toast notifications
 * 
 * Key Concepts for Interns:
 * - DRY (Don't Repeat Yourself): Reusable functions
 * - Error Handling: Graceful error messages
 * - User Feedback: Toast notifications
 */

import { getToken } from './auth.js';


/**
 * Make an authenticated API request.
 * 
 * This is a wrapper around fetch() that automatically adds the auth token.
 * 
 * @param {string} url - API endpoint URL
 * @param {Object} options - Fetch options (method, body, headers, etc.)
 * @returns {Promise<Response>} Fetch response
 * 
 * @example
 * const response = await apiRequest('/api/users/me', {
 *     method: 'PATCH',
 *     body: JSON.stringify({ name: 'New Name' })
 * });
 * const data = await response.json();
 */
export async function apiRequest(url, options = {}) {
    // Get auth token
    const token = getToken();

    // Set up headers
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };

    // Add auth token if available
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    // Make request
    return fetch(url, {
        ...options,
        headers,
    });
}


/**
 * Display a toast notification.
 * 
 * Shows a temporary message to the user.
 * 
 * @param {string} message - Message to display
 * @param {string} type - Type of message ('success', 'error', 'info', 'warning')
 * @param {number} duration - How long to show the message (milliseconds)
 * 
 * @example
 * showToast('Profile updated successfully!', 'success');
 * showToast('An error occurred', 'error');
 */
export function showToast(message, type = 'info', duration = 3000) {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;

    // Style the toast
    Object.assign(toast.style, {
        position: 'fixed',
        bottom: '20px',
        right: '20px',
        padding: '16px 24px',
        borderRadius: '8px',
        color: 'white',
        fontSize: '14px',
        fontWeight: '500',
        zIndex: '9999',
        animation: 'slideIn 0.3s ease-out',
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
    });

    // Set background color based on type
    const colors = {
        success: '#658C58',
        error: '#E74C3C',
        warning: '#F0E491',
        info: '#3B82F6',
    };
    toast.style.backgroundColor = colors[type] || colors.info;

    // Add to page
    document.body.appendChild(toast);

    // Remove after duration
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}


/**
 * Handle API errors and show user-friendly messages.
 * 
 * @param {Response} response - Fetch response object
 * @returns {Promise<void>}
 * 
 * @example
 * const response = await apiRequest('/api/users/me', { method: 'PATCH', ... });
 * if (!response.ok) {
 *     await handleApiError(response);
 *     return;
 * }
 */
export async function handleApiError(response) {
    let message = 'An error occurred';

    try {
        const data = await response.json();
        message = data.detail || message;
    } catch (e) {
        // Response doesn't have JSON body
    }

    showToast(message, 'error');
}


/**
 * Validate email format.
 * 
 * @param {string} email - Email to validate
 * @returns {boolean} True if valid, false otherwise
 * 
 * @example
 * if (!validateEmail(email)) {
 *     showToast('Please enter a valid email', 'error');
 *     return;
 * }
 */
export function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}


/**
 * Validate password strength.
 * 
 * @param {string} password - Password to validate
 * @returns {Object} { valid: boolean, message: string }
 * 
 * @example
 * const result = validatePassword(password);
 * if (!result.valid) {
 *     showToast(result.message, 'error');
 *     return;
 * }
 */
export function validatePassword(password) {
    if (password.length < 8) {
        return {
            valid: false,
            message: 'Password must be at least 8 characters long'
        };
    }

    return { valid: true, message: '' };
}


/**
 * Format date to readable string.
 * 
 * @param {string} dateString - ISO date string
 * @returns {string} Formatted date
 * 
 * @example
 * const formatted = formatDate('2024-01-15T10:30:00');
 * // Returns: "January 15, 2024"
 */
export function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}


/**
 * Debounce function calls.
 * 
 * Delays execution until after a specified time has passed since the last call.
 * Useful for search inputs, resize handlers, etc.
 * 
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 * 
 * @example
 * const debouncedSearch = debounce((query) => {
 *     searchUsers(query);
 * }, 300);
 * 
 * input.addEventListener('input', (e) => debouncedSearch(e.target.value));
 */
export function debounce(func, wait) {
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


// Add CSS for toast animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);


// Best Practices for Interns:
//
// 1. Reusable Functions:
//    - Write functions that can be used in multiple places
//    - Keep functions focused on one task
//    - Use descriptive names
//
// 2. Error Handling:
//    - Always handle errors gracefully
//    - Provide user-friendly error messages
//    - Log errors for debugging (but not in production)
//
// 3. User Feedback:
//    - Always provide feedback for user actions
//    - Use appropriate message types (success, error, etc.)
//    - Don't overwhelm users with too many messages
//
// 4. Performance:
//    - Use debounce for expensive operations
//    - Cache results when appropriate
//    - Minimize DOM manipulations
//
// 5. Validation:
//    - Validate on both client and server
//    - Client validation for UX (immediate feedback)
//    - Server validation for security (never trust client)
