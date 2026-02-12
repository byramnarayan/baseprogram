/**
 * Map Handler Module
 * 
 * Handles all map-related functionality using Leaflet.js with MapTiler SDK:
 * - Initialize maps with satellite view
 * - Enable drawing tools with area measurement
 * - Calculate areas from polygons using geodesic methods
 * - Display existing farm boundaries
 * - Auto-center to user location
 */

let currentMap = null;
let drawnItems = null;
let drawControl = null;

// India center coordinates for initial map view (fallback)
export const INDIA_CENTER = [20.5937, 78.9629];
export const DEFAULT_ZOOM = 5;

// MapTiler API key - Replace with your own key from https://cloud.maptiler.com/
const MAPTILER_API_KEY = 'EtqU4387OjSDZvoVP09H';

/**
 * Initialize a Leaflet map in the specified container with MapTiler satellite view
 */
export function initializeMap(containerId, center = null, zoom = DEFAULT_ZOOM) {
    // Remove existing map if any
    if (currentMap) {
        currentMap.remove();
        currentMap = null;
    }

    // Create map (no editable option to avoid Leaflet.Editable conflicts)
    currentMap = L.map(containerId);

    // Add MapTiler layer with satellite view and auto-centering
    const mtLayer = L.maptiler.maptilerLayer({
        apiKey: MAPTILER_API_KEY,
        style: L.maptiler.MapStyle.SATELLITE, // Satellite view
        geolocate: center === null // Auto-center to user location if no center provided
    }).addTo(currentMap);

    // If center is provided, set it manually
    if (center) {
        currentMap.setView(center, zoom);
    } else {
        // Fallback to India center if geolocation fails
        currentMap.setView(INDIA_CENTER, DEFAULT_ZOOM);
    }

    // Initialize FeatureGroup for drawn items
    drawnItems = new L.FeatureGroup();
    currentMap.addLayer(drawnItems);

    // Add draw control with area measurement enabled
    drawControl = new L.Control.Draw({
        position: 'topright',
        draw: {
            polygon: {
                allowIntersection: false,
                showArea: true,
                metric: ['ha', 'm'],
                feet: false,
                nautic: false,
                shapeOptions: {
                    color: '#31694E',
                    fillColor: '#BBC863',
                    fillOpacity: 0.5,
                    weight: 3
                }
            },
            polyline: false,
            rectangle: false,
            circle: false,
            marker: false,
            circlemarker: false
        },
        edit: {
            featureGroup: drawnItems,
            remove: true
        }
    });
    currentMap.addControl(drawControl);

    // Handle drawn shapes
    currentMap.on(L.Draw.Event.CREATED, function (event) {
        const layer = event.layer;
        drawnItems.clearLayers(); // Only allow one polygon at a time
        drawnItems.addLayer(layer);

        // Calculate and display area
        const coordinates = getCoordinatesFromLayer(layer);
        const area = calculateAreaFromCoordinates(coordinates);
        const calcAreaEl = document.getElementById('calculated-area');
        if (calcAreaEl) {
            calcAreaEl.textContent = `${area.toFixed(4)} hectares`;
        }

        // Store coordinates in hidden field
        const coordsEl = document.getElementById('farm-coordinates');
        if (coordsEl) {
            coordsEl.value = JSON.stringify(coordinates);
        }
    });

    currentMap.on(L.Draw.Event.EDITED, function (event) {
        const layers = event.layers;
        layers.eachLayer(function (layer) {
            const coordinates = getCoordinatesFromLayer(layer);
            const area = calculateAreaFromCoordinates(coordinates);
            const calcAreaEl = document.getElementById('calculated-area');
            if (calcAreaEl) {
                calcAreaEl.textContent = `${area.toFixed(4)} hectares`;
            }
            const coordsEl = document.getElementById('farm-coordinates');
            if (coordsEl) {
                coordsEl.value = JSON.stringify(coordinates);
            }
        });
    });

    currentMap.on(L.Draw.Event.DELETED, function () {
        const calcAreaEl = document.getElementById('calculated-area');
        if (calcAreaEl) {
            calcAreaEl.textContent = '-- hectares';
        }
        const coordsEl = document.getElementById('farm-coordinates');
        if (coordsEl) {
            coordsEl.value = '';
        }
    });

    return currentMap;
}

/**
 * Draw an existing farm boundary on the map
 */
export function drawFarmBoundary(coordinates, fitBounds = true) {
    if (!currentMap || !coordinates || coordinates.length < 3) {
        return;
    }

    // Clear existing polygons
    drawnItems.clearLayers();

    // Convert [lat, lon] to Leaflet format
    const leafletCoords = coordinates.map(coord => [coord[0], coord[1]]);

    // Create polygon
    const polygon = L.polygon(leafletCoords, {
        color: '#31694E',
        fillColor: '#BBC863',
        fillOpacity: 0.5,
        weight: 3
    });

    drawnItems.addLayer(polygon);

    // Fit map to polygon bounds if requested
    if (fitBounds) {
        const bounds = polygon.getBounds();
        currentMap.fitBounds(bounds);
    }

    // Update area display
    const area = calculateAreaFromCoordinates(coordinates);
    const calcAreaEl = document.getElementById('calculated-area');
    if (calcAreaEl) {
        calcAreaEl.textContent = `${area.toFixed(4)} hectares`;
    }
    const coordsEl = document.getElementById('farm-coordinates');
    if (coordsEl) {
        coordsEl.value = JSON.stringify(coordinates);
    }
}

/**
 * Extract coordinates from a Leaflet layer
 */
function getCoordinatesFromLayer(layer) {
    const latlngs = layer.getLatLngs()[0]; // Get outer ring for polygon
    return latlngs.map(latlng => [latlng.lat, latlng.lng]);
}

/**
 * Calculate area from polygon coordinates using Shoelace formula
 * Returns area in hectares
 * Note: This is an approximation. Server uses more accurate geodesic calculation.
 */
function calculateAreaFromCoordinates(coordinates) {
    if (!coordinates || coordinates.length < 3) {
        return 0;
    }

    // Convert lat/lon to approximate meters using simple projection
    const R = 6371000; // Earth radius in meters

    // Calculate area using spherical excess formula
    let area = 0;
    const numPoints = coordinates.length;

    for (let i = 0; i < numPoints; i++) {
        const j = (i + 1) % numPoints;

        const lat1 = coordinates[i][0] * Math.PI / 180;
        const lat2 = coordinates[j][0] * Math.PI / 180;
        const lon1 = coordinates[i][1] * Math.PI / 180;
        const lon2 = coordinates[j][1] * Math.PI / 180;

        area += (lon2 - lon1) * (2 + Math.sin(lat1) + Math.sin(lat2));
    }

    area = Math.abs(area * R * R / 2.0);

    // Convert square meters to hectares
    return area / 10000;
}

/**
 * Get drawn coordinates
 */
export function getDrawnCoordinates() {
    const coordsStr = document.getElementById('farm-coordinates')?.value;
    if (!coordsStr) return null;

    try {
        return JSON.parse(coordsStr);
    } catch (e) {
        console.error('Failed to parse coordinates:', e);
        return null;
    }
}

/**
 * Clear the map and reset drawing state
 */
export function clearMap() {
    if (drawnItems) {
        drawnItems.clearLayers();
    }
    const calcAreaEl = document.getElementById('calculated-area');
    if (calcAreaEl) {
        calcAreaEl.textContent = '-- hectares';
    }
    const coordsEl = document.getElementById('farm-coordinates');
    if (coordsEl) {
        coordsEl.value = '';
    }
}

/**
 * Check if map has a drawn polygon
 */
export function hasDrawnPolygon() {
    return drawnItems && drawnItems.getLayers().length > 0;
}

/**
 * Create a small preview map for farm cards
 */
export function createPreviewMap(containerId, coordinates) {
    // Create a small map
    const map = L.map(containerId, {
        dragging: false,
        zoomControl: false,
        scrollWheelZoom: false,
        doubleClickZoom: false,
        touchZoom: false
    });

    // Add MapTiler satellite layer
    L.maptiler.maptilerLayer({
        apiKey: MAPTILER_API_KEY,
        style: L.maptiler.MapStyle.SATELLITE
    }).addTo(map);

    // Draw polygon
    const leafletCoords = coordinates.map(coord => [coord[0], coord[1]]);
    const polygon = L.polygon(leafletCoords, {
        color: '#31694E',
        fillColor: '#BBC863',
        fillOpacity: 0.5,
        weight: 3
    }).addTo(map);

    // Fit to bounds
    map.fitBounds(polygon.getBounds());

    return map;
}
