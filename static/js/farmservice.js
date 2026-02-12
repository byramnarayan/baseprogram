/**
 * Farm Service Module
 * 
 * Handles all farm-related operations:
 * - Multi-step form navigation
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
let currentStep = 1;
const totalSteps = 3;

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

// ============================================================================
// Multi-Step Navigation
// ============================================================================

/**
 * Update progress bar
 */
function updateProgressBar() {
    const progressFill = document.getElementById('progress-fill');
    const percentage = ((currentStep - 1) / (totalSteps - 1)) * 100;
    progressFill.style.width = `${percentage}%`;

    // Update step indicators
    document.querySelectorAll('.step').forEach((step, index) => {
        const stepNumber = index + 1;
        step.classList.remove('active', 'completed');

        if (stepNumber < currentStep) {
            step.classList.add('completed');
        } else if (stepNumber === currentStep) {
            step.classList.add('active');
        }
    });
}

/**
 * Show specific step
 */
function showStep(stepNumber) {
    // Hide all steps
    document.querySelectorAll('.step-content').forEach(content => {
        content.classList.remove('active');
    });

    // Show current step
    const stepContent = document.querySelector(`.step-content[data-step="${stepNumber}"]`);
    if (stepContent) {
        stepContent.classList.add('active');
    }

    // Update button visibility
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const submitBtn = document.getElementById('submit-btn');

    prevBtn.disabled = stepNumber === 1;

    if (stepNumber === totalSteps) {
        nextBtn.style.display = 'none';
        submitBtn.style.display = 'block';
    } else {
        nextBtn.style.display = 'block';
        submitBtn.style.display = 'none';
    }

    // Initialize map when step 2 is shown
    if (stepNumber === 2) {
        setTimeout(() => {
            initializeMap('farm-map', null, DEFAULT_ZOOM);
        }, 100);
    }

    // Update estimated credits when step 3 is shown
    if (stepNumber === 3) {
        updateEstimatedCredits();
    }

    updateProgressBar();
}

/**
 * Validate current step
 */
function validateCurrentStep() {
    if (currentStep === 1) {
        // Validate basic info
        const phone = document.getElementById('farm-phone').value;
        const district = document.getElementById('farm-district').value;
        const state = document.getElementById('farm-state').value;

        if (!phone || !district || !state) {
            showError('Please fill in all required fields (Phone, District, State)');
            return false;
        }

        if (phone.length < 10) {
            showError('Phone number must be at least 10 digits');
            return false;
        }

        return true;
    }

    if (currentStep === 2) {
        // Validate map drawing
        if (!hasDrawnPolygon()) {
            showError('Please draw your farm boundary on the map');
            return false;
        }

        const coordinates = getDrawnCoordinates();
        if (!coordinates || coordinates.length < 3) {
            showError('Farm boundary must have at least 3 points');
            return false;
        }

        return true;
    }

    if (currentStep === 3) {
        // Validate crop and soil selection
        const cropType = document.getElementById('farm-crop-type').value;
        const soilType = document.getElementById('farm-soil-type').value;

        if (!cropType || !soilType) {
            showError('Please select both crop type and soil type');
            return false;
        }

        return true;
    }

    return true;
}

/**
 * Go to next step
 */
function nextStep() {
    if (!validateCurrentStep()) {
        return;
    }

    if (currentStep < totalSteps) {
        currentStep++;
        showStep(currentStep);
    }
}

/**
 * Go to previous step
 */
function previousStep() {
    if (currentStep > 1) {
        currentStep--;
        showStep(currentStep);
    }
}

/**
 * Calculate estimated credits based on current selections
 */
function updateEstimatedCredits() {
    const coordinates = getDrawnCoordinates();
    if (!coordinates || coordinates.length < 3) {
        document.getElementById('estimated-credits').textContent = '--';
        document.getElementById('estimated-value').textContent = '--';
        return;
    }

    // Get area from displayed value
    const areaText = document.getElementById('calculated-area').textContent;
    const area = parseFloat(areaText);

    if (isNaN(area) || area <= 0) {
        document.getElementById('estimated-credits').textContent = '--';
        document.getElementById('estimated-value').textContent = '--';
        return;
    }

    // Get multipliers
    const cropType = document.getElementById('farm-crop-type').value;
    const soilType = document.getElementById('farm-soil-type').value;

    const cropMultipliers = {
        "Rice": 1.1,
        "Wheat": 1.0,
        "Vegetables": 0.9,
        "Pulses": 1.2,
        "Sugarcane": 1.3,
        "Cotton": 0.8,
        "Fruits": 1.1,
        "Mixed Crops": 1.0
    };

    const soilMultipliers = {
        "Loamy": 1.2,
        "Clay": 1.0,
        "Sandy": 0.8,
        "Mixed": 1.0
    };

    const cropMultiplier = cropType ? (cropMultipliers[cropType] || 1.0) : 1.0;
    const soilMultiplier = soilType ? (soilMultipliers[soilType] || 1.0) : 1.0;

    // Calculate credits (unverified = 50%)
    const baseRate = 12.5;
    const verificationMultiplier = 0.5; // New farms are unverified

    const credits = area * soilMultiplier * cropMultiplier * baseRate * verificationMultiplier;
    const value = credits * 500; // ₹500 per credit

    document.getElementById('estimated-credits').textContent = credits.toFixed(2);
    document.getElementById('estimated-value').textContent = value.toLocaleString('en-IN');
}

// ============================================================================
// Farm CRUD Operations
// ============================================================================

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
                <p><span class="font-bold">🌾 Crop Type:</span> ${farm.crop_type}</p>
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
    currentStep = 1;

    document.getElementById('modal-title').textContent = 'Add New Farm';
    document.getElementById('farm-form').reset();
    document.getElementById('edit-farm-id').value = '';
    clearMap();

    // Reset estimated credits
    document.getElementById('estimated-credits').textContent = '--';
    document.getElementById('estimated-value').textContent = '--';

    // Show modal and first step
    document.getElementById('farm-modal').style.display = 'flex';
    showStep(1);
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
        currentStep = 1;

        document.getElementById('modal-title').textContent = 'Edit Farm';
        document.getElementById('edit-farm-id').value = farmId;

        // Populate form
        document.getElementById('farm-name').value = farm.farm_name || '';
        document.getElementById('farm-phone').value = farm.phone;
        document.getElementById('farm-district').value = farm.district;
        document.getElementById('farm-state').value = farm.state;
        document.getElementById('farm-soil-type').value = farm.soil_type;
        document.getElementById('farm-crop-type').value = farm.crop_type;

        // Show modal
        document.getElementById('farm-modal').style.display = 'flex';
        showStep(1);

        // Store coordinates for step 2
        setTimeout(() => {
            if (farm.polygon_coordinates) {
                initializeMap('farm-map', [farm.latitude, farm.longitude], 13);
                drawFarmBoundary(farm.polygon_coordinates, true);
            }
        }, 500);

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

    // Final validation
    if (!validateCurrentStep()) {
        return;
    }

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
        crop_type: document.getElementById('farm-crop-type').value,
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
    currentStep = 1;
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

    // Multi-step navigation
    document.getElementById('prev-btn').addEventListener('click', previousStep);
    document.getElementById('next-btn').addEventListener('click', nextStep);

    // Update estimated credits when selections change
    document.getElementById('farm-crop-type').addEventListener('change', updateEstimatedCredits);
    document.getElementById('farm-soil-type').addEventListener('change', updateEstimatedCredits);

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
