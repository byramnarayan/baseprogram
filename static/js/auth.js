/**
 * Authentication Utilities
 * 
 * This module handles client-side authentication:
 * - Storing and retrieving JWT tokens
 * - Fetching current user information
 * - Logout functionality
 * 
 * Key Concepts for Interns:
 * - localStorage: Browser storage for persisting data
 * - JWT Tokens: Stateless authentication
 * - Async/Await: Modern JavaScript for handling promises
 * - Caching: Store user data to avoid repeated API calls
 */

// Cache for current user data
// This avoids making multiple API calls for the same data
let currentUser = null;

// Promise to track ongoing fetch request
// Prevents multiple simultaneous requests for user data
let fetchPromise = null;


/**
 * Get the current authenticated user.
 * 
 * This function:
 * 1. Returns cached user if available
 * 2. Returns ongoing fetch promise if one exists
 * 3. Fetches user from API and caches the result
 * 
 * @returns {Promise<Object|null>} User object or null if not authenticated
 * 
 * @example
 * const user = await getCurrentUser();
 * if (user) {
 *     console.log(`Welcome, ${user.name}!`);
 * } else {
 *     window.location.href = '/login';
 * }
 */
export async function getCurrentUser() {
    // Return cached user if available
    if (currentUser) {
        return currentUser;
    }

    // Return ongoing fetch if one exists (prevents duplicate requests)
    if (fetchPromise) {
        return fetchPromise;
    }

    // Get token from localStorage
    const token = localStorage.getItem("access_token");

    // No token = not logged in
    if (!token) {
        return null;
    }

    // Fetch user data from API
    fetchPromise = (async () => {
        try {
            const response = await fetch("/api/users/me", {
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            });

            if (response.ok) {
                // Success - cache and return user data
                currentUser = await response.json();
                return currentUser;
            } else {
                // Token is invalid or expired - clear it
                localStorage.removeItem("access_token");
                return null;
            }
        } catch (error) {
            console.error("Error fetching user:", error);
            return null;
        } finally {
            // Clear fetch promise when done
            fetchPromise = null;
        }
    })();

    return fetchPromise;
}


/**
 * Logout the current user.
 * 
 * This function:
 * 1. Removes the JWT token from localStorage
 * 2. Clears the cached user data
 * 3. Redirects to the login page
 * 
 * @example
 * document.getElementById('logout-btn').addEventListener('click', logout);
 */
export function logout() {
    // Remove token from storage
    localStorage.removeItem("access_token");

    // Clear cached user data
    currentUser = null;

    // Redirect to login page
    window.location.href = "/login";
}


/**
 * Get the stored JWT token.
 * 
 * @returns {string|null} JWT token or null if not logged in
 * 
 * @example
 * const token = getToken();
 * if (token) {
 *     // Make authenticated API request
 *     fetch('/api/some-endpoint', {
 *         headers: { 'Authorization': `Bearer ${token}` }
 *     });
 * }
 */
export function getToken() {
    return localStorage.getItem("access_token");
}


/**
 * Store a JWT token.
 * 
 * @param {string} token - JWT token to store
 * 
 * @example
 * // After successful login
 * const response = await fetch('/api/auth/token', { ... });
 * const data = await response.json();
 * setToken(data.access_token);
 */
export function setToken(token) {
    localStorage.setItem("access_token", token);
}


/**
 * Clear the cached user data.
 * 
 * Use this when user data might have changed (e.g., after profile update).
 * The next call to getCurrentUser() will fetch fresh data from the API.
 * 
 * @example
 * // After updating profile
 * await fetch('/api/users/me', { method: 'PATCH', ... });
 * clearUserCache(); // Force refresh on next getCurrentUser() call
 */
export function clearUserCache() {
    currentUser = null;
}


/**
 * Check if user is authenticated and redirect if not.
 * 
 * Use this on protected pages to ensure only logged-in users can access them.
 * 
 * @returns {Promise<Object|null>} User object if authenticated
 * 
 * @example
 * // At the top of a protected page
 * const user = await requireAuth();
 * // If we get here, user is authenticated
 * displayUserData(user);
 */
export async function requireAuth() {
    const user = await getCurrentUser();
    if (!user) {
        // Not authenticated - redirect to login
        window.location.href = '/login';
        return null;
    }
    return user;
}


// Best Practices for Interns:
//
// 1. Token Storage:
//    - localStorage persists across browser sessions
//    - sessionStorage only lasts for the current session
//    - For sensitive apps, consider using httpOnly cookies instead
//
// 2. Security:
//    - Never log tokens to console in production
//    - Always use HTTPS in production (tokens sent in headers)
//    - Set appropriate token expiration times
//    - Clear tokens on logout
//
// 3. Caching:
//    - Cache user data to reduce API calls
//    - Clear cache when data might have changed
//    - Use promises to prevent duplicate requests
//
// 4. Error Handling:
//    - Always handle fetch errors gracefully
//    - Clear invalid tokens
//    - Provide user feedback for errors
//
// 5. Module Pattern:
//    - Export functions for use in other files
//    - Keep related functionality together
//    - Use descriptive function names
