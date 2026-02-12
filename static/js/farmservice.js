/**
 * Farm Service Module
 * 
 * Handles all farm-related operations:
 * - Load and display farms
 * - Create, update, delete farms
 * - Update statistics
 * - Handle modal interactions
 */

import { getCurrentUser } from './auth.js';
import {
    initializeMap,
    drawFarmBoundary,
    getDrawnCoordinates,
    clearMap,
    hasDrawnPolygon,
    createPreviewMap,
    INDIA_CENTER,
    DEFAULT_ZOOM
} from './mapHandler.js';

const API_BASE = '/api/farmservice';
let currentEditId = null;
let farmMaps = {}; // Store preview map instances

/**
 * Check authentication and redirect if not logged in
 */
async function checkAuth() {
    const user = await getCurrentUser();
    if (!user) {
        window.location.href = '/login?next=/farmservice';
        return false;
    }
    return true;
}

/**
 * Get auth token from localStorage
 */
function getAuthToken() {
    return localStorage.getItem('access_token');
}

/**
 * Show loading overlay
 */
function showLoading() {
    document.getElementById('loading-overlay').style.display = 'flex';
}

/**
 * Hide loading overlay
 */
function hideLoading() {
    document.getElementById('loading-overlay').style.display = 'none';
}

/**
 * Show error message
 */
function showError(message) {
    alert(`Error: ${message}`);
}

/**
 * Show success message
 */
function showSuccess(message) {
    alert(`Success: ${message}`);
}

/**
 * Load all farms from API
 */
async function loadFarms() {
    try {
        showLoading();

        const response = await fetch(`${API_BASE}/farms`, {
            headers: {
                'Authorization': `Bearer ${getAuthToken()}`
            }
        });

        if (response.status === 401) {
            window.location.href = '/login?next=/farmservice';
            return;
        }

        if (!response.ok) {
            throw new Error('Failed to load farms');
        }

        const data = await response.json();

        // Update statistics
        updateStatistics(data.summary);

        // Display farms
        displayFarms(data.farms);

    } catch (error) {
        console.error('Error loading farms:', error);
        showError('Failed to load farms. Please try again.');
    } finally {
        hideLoading();
    }
}

/**
 * Update statistics cards
 */
function updateStatistics(summary) {
    document.getElementById('stat-total-farms').textContent = summary.total_farms;
    document.getElementById('stat-total-area').textContent = summary.total_area_hectares.toFixed(2);
    document.getElementById('stat-annual-credits').textContent = summary.total_annual_credits.toFixed(2);
    document.getElementById('stat-annual-value').textContent = `₹${summary.total_annual_value_inr.toLocaleString('en-IN')}`;
}

/**
 * Display farms in grid
 */
function displayFarms(farms) {
    const grid = document.getElementById('farms-grid');
    const emptyState = document.getElementById('empty-state');

    if (farms.length === 0) {
        grid.innerHTML = '';
        emptyState.classList.remove('hidden');
        return;
    }

    emptyState.classList.add('hidden');
    grid.innerHTML = farms.map(farm => createFarmCard(farm)).join('');

    // Create preview maps for each farm
    farms.forEach(farm => {
        const mapId = `preview-map-${farm.id}`;
        setTimeout(() => {
            try {
                farmMaps[farm.id] = createPreviewMap(mapId, farm.polygon_coordinates);
            } catch (e) {
                console.error('Failed to create preview map:', e);
            }
        }, 100);
    });
}

/**
 * Create HTML for a farm card
 */
function createFarmCard(farm) {
    const verifiedBadge = farm.is_verified
        ? '<span class="bg-green-500 text-white px-3 py-1 rounded-full text-xs font-bold">✓ Verified</span>'
        : '<span class="bg-yellow-500 text-white px-3 py-1 rounded-full text-xs font-bold">⏳ Pending</span>';

    const borderColor = farm.is_verified ? 'border-green-500' : 'border-yellow-500';

    return `
        <div class="card-retro p-6 ${borderColor} border-4">
            <div class="flex justify-between items-start mb-4">
                <h3 class="text-2xl font-heading text-retro-dark">${farm.display_name}</h3>
                ${verifiedBadge}
            </div>
            
            <div id="preview-map-${farm.id}" class="h-48 rounded-retro mb-4 bg-gray-200"></div>
            
            <div class="space-y-2 text-sm mb-4">
                <p><span class="font-bold">📍 Location:</span> ${farm.district}, ${farm.state}</p>
                <p><span class="font-bold">📏 Area:</span> ${farm.area_hectares.toFixed(2)} hectares</p>
                <p><span class="font-bold">🌱 Soil Type:</span> ${farm.soil_type}</p>
                <p><span class="font-bold">💰 Annual Credits:</span> ${farm.annual_credits.toFixed(2)}</p>
                <p><span class="font-bold">💵 Annual Value:</span> ₹${farm.annual_value_inr.toLocaleString('en-IN')}</p>
            </div>
            
            <div class="flex gap-2">
                <button onclick="window.farmService.editFarm(${farm.id})" class="btn-retro bg-retro-green text-white px-4 py-2 rounded-retro font-bold text-sm flex-1">
                    Edit
                </button>
                <button onclick="window.farmService.deleteFarm(${farm.id}, '${farm.display_name}')" class="btn-retro bg-retro-accent text-white px-4 py-2 rounded-retro font-bold text-sm flex-1">
                    Delete
                </button>
            </div>
        </div>
    `;
}

/**
 * Show add farm modal
 */
function showAddFarmModal() {
    currentEditId = null;
    document.getElementById('modal-title').textContent = 'Add New Farm';
    document.getElementById('farm-form').reset();
    document.getElementById('edit-farm-id').value = '';
    clearMap();

    // Show modal
    document.getElementById('farm-modal').style.display = 'flex';

    // Initialize map with slight delay - use null for auto-centering to user location
    setTimeout(() => {
        initializeMap('farm-map', null, DEFAULT_ZOOM);
    }, 100);
}

/**
 * Show edit farm modal
 */
async function editFarm(farmId) {
    try {
        showLoading();

        const response = await fetch(`${API_BASE}/farms/${farmId}`, {
            headers: {
                'Authorization': `Bearer ${getAuthToken()}`
            }
        });

        if (!response.ok) {
            throw new Error('Failed to load farm details');
        }

        const farm = await response.json();

        currentEditId = farmId;
        document.getElementById('modal-title').textContent = 'Edit Farm';
        document.getElementById('edit-farm-id').value = farmId;

        // Populate form
        document.getElementById('farm-name').value = farm.farm_name || '';
        document.getElementById('farm-phone').value = farm.phone;
        document.getElementById('farm-district').value = farm.district;
        document.getElementById('farm-state').value = farm.state;
        document.getElementById('farm-soil-type').value = farm.soil_type;

        // Show modal
        document.getElementById('farm-modal').style.display = 'flex';

        // Initialize map and draw existing boundary
        setTimeout(() => {
            initializeMap('farm-map', [farm.latitude, farm.longitude], 13);
            drawFarmBoundary(farm.polygon_coordinates, true);
        }, 100);

    } catch (error) {
        console.error('Error loading farm:', error);
        showError('Failed to load farm details');
    } finally {
        hideLoading();
    }
}

/**
 * Delete farm
 */
async function deleteFarm(farmId, farmName) {
    if (!confirm(`Are you sure you want to delete "${farmName}"? This action cannot be undone.`)) {
        return;
    }

    try {
        showLoading();

        const response = await fetch(`${API_BASE}/farms/${farmId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${getAuthToken()}`
            }
        });

        if (!response.ok) {
            throw new Error('Failed to delete farm');
        }

        showSuccess(`Farm "${farmName}" deleted successfully`);
        await loadFarms();

    } catch (error) {
        console.error('Error deleting farm:', error);
        showError('Failed to delete farm');
    } finally {
        hideLoading();
    }
}

/**
 * Submit farm form (create or update)
 */
async function submitFarmForm(event) {
    event.preventDefault();

    // Validate polygon is drawn
    if (!hasDrawnPolygon()) {
        showError('Please draw the farm boundary on the map');
        return;
    }

    const coordinates = getDrawnCoordinates();
    if (!coordinates || coordinates.length < 3) {
        showError('Invalid farm boundary. Please draw at least 3 points');
        return;
    }

    // Get form data
    const formData = {
        farm_name: document.getElementById('farm-name').value || null,
        phone: document.getElementById('farm-phone').value,
        district: document.getElementById('farm-district').value,
        state: document.getElementById('farm-state').value,
        soil_type: document.getElementById('farm-soil-type').value,
        polygon_coordinates: coordinates
    };

    const editId = document.getElementById('edit-farm-id').value;
    const isEdit = !!editId;

    try {
        showLoading();

        const url = isEdit ? `${API_BASE}/farms/${editId}` : `${API_BASE}/farms`;
        const method = isEdit ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method: method,
            headers: {
                'Authorization': `Bearer ${getAuthToken()}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            const errorData = await response.json();
            console.error('Backend error:', errorData);

            // Extract detailed error message
            let errorMessage = 'Failed to save farm';
            if (errorData.detail) {
                if (typeof errorData.detail === 'string') {
                    errorMessage = errorData.detail;
                } else if (Array.isArray(errorData.detail)) {
                    // Pydantic validation errors
                    errorMessage = errorData.detail.map(err =>
                        `${err.loc.join('.')}: ${err.msg}`
                    ).join('\n');
                } else if (errorData.detail.message) {
                    errorMessage = errorData.detail.message;
                }
            }
            throw new Error(errorMessage);
        }

        const result = await response.json();

        showSuccess(`Farm ${isEdit ? 'updated' : 'created'} successfully!`);

        // Close modal and reload farms
        document.getElementById('farm-modal').style.display = 'none';
        await loadFarms();

    } catch (error) {
        console.error('Error saving farm:', error);
        showError(error.message);
    } finally {
        hideLoading();
    }
}

/**
 * Close modal
 */
function closeModal() {
    document.getElementById('farm-modal').style.display = 'none';
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    // Check authentication
    if (!await checkAuth()) {
        return;
    }

    // Load farms
    await loadFarms();

    // Set up event listeners
    document.getElementById('add-farm-btn').addEventListener('click', showAddFarmModal);
    document.getElementById('refresh-btn').addEventListener('click', loadFarms);
    document.getElementById('cancel-modal-btn').addEventListener('click', closeModal);
    document.getElementById('farm-form').addEventListener('submit', submitFarmForm);

    // Close modal when clicking outside
    document.getElementById('farm-modal').addEventListener('click', (e) => {
        if (e.target.id === 'farm-modal') {
            closeModal();
        }
    });
});

// Export functions for global access
window.farmService = {
    editFarm,
    deleteFarm
};
