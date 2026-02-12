"""
Geospatial Utility Module

This module provides functions for geospatial calculations, specifically
for calculating land area from polygon coordinates.

Key Concepts:
- Geodesic calculations: Account for Earth's curvature (more accurate)
- Polygon validation: Ensure coordinates form a valid shape
- Coordinate system: Uses WGS84 (standard GPS coordinates)
"""

from typing import List, Tuple
from shapely.geometry import Polygon
from shapely.ops import transform
from pyproj import Geod


def validate_polygon(coordinates: List[List[float]]) -> Tuple[bool, str]:
    """
    Validate that coordinates form a valid polygon.
    
    Checks:
    - Minimum 3 points required
    - No self-intersection
    - Coordinates within valid lat/lon ranges
    
    Args:
        coordinates: List of [lat, lon] pairs
        
    Returns:
        Tuple of (is_valid: bool, error_message: str)
        
    Example:
        >>> coords = [[18.5204, 73.8567], [18.5214, 73.8567], [18.5214, 73.8577]]
        >>> is_valid, msg = validate_polygon(coords)
        >>> print(is_valid)
        True
    """
    # Check minimum points
    if len(coordinates) < 3:
        return False, "Polygon must have at least 3 points"
    
    # Validate lat/lon ranges
    for coord in coordinates:
        if len(coord) != 2:
            return False, "Each coordinate must have exactly 2 values [lat, lon]"
        
        lat, lon = coord
        if not (-90 <= lat <= 90):
            return False, f"Invalid latitude: {lat}. Must be between -90 and 90"
        if not (-180 <= lon <= 180):
            return False, f"Invalid longitude: {lon}. Must be between -180 and 180"
    
    try:
        # Create polygon (Shapely uses lon, lat order - opposite of our input)
        # So we swap the coordinates
        shapely_coords = [(lon, lat) for lat, lon in coordinates]
        polygon = Polygon(shapely_coords)
        
        # Check if polygon is valid (no self-intersection)
        if not polygon.is_valid:
            return False, "Polygon has self-intersecting boundaries"
        
        # Check if polygon has area
        if polygon.area == 0:
            return False, "Polygon has zero area (points are collinear)"
        
        return True, "Valid polygon"
        
    except Exception as e:
        return False, f"Invalid polygon geometry: {str(e)}"


def calculate_area_from_polygon(coordinates: List[List[float]]) -> float:
    """
    Calculate land area from polygon coordinates using geodesic calculations.
    
    This function accounts for Earth's curvature, making it accurate for
    both small and large land areas. Uses the WGS84 ellipsoid model.
    
    Args:
        coordinates: List of [lat, lon] coordinate pairs defining the polygon boundary
        
    Returns:
        float: Area in hectares (1 hectare = 10,000 square meters)
        
    Raises:
        ValueError: If polygon is invalid
        
    Algorithm:
    1. Validate polygon coordinates
    2. Create Shapely polygon geometry
    3. Use geodesic calculations (pyproj.Geod) for accurate area
    4. Convert square meters to hectares
    
    Example:
        >>> # Square farm approximately 1km x 1km
        >>> coords = [
        ...     [18.5204, 73.8567],
        ...     [18.5304, 73.8567],  # ~1km north
        ...     [18.5304, 73.8667],  # ~1km east
        ...     [18.5204, 73.8667],
        ... ]
        >>> area = calculate_area_from_polygon(coords)
        >>> print(f"Area: {area:.2f} hectares")
        Area: ~100.00 hectares
    """
    # Validate polygon first
    is_valid, error_msg = validate_polygon(coordinates)
    if not is_valid:
        raise ValueError(error_msg)
    
    # Convert coordinates to Shapely format (lon, lat)
    shapely_coords = [(lon, lat) for lat, lon in coordinates]
    
    # Create polygon
    polygon = Polygon(shapely_coords)
    
    # Use geodesic calculation for accurate area
    # WGS84 ellipsoid (standard for GPS)
    geod = Geod(ellps="WGS84")
    
    # Calculate geodesic area
    # Returns area in square meters and perimeter
    area_m2, _ = geod.geometry_area_perimeter(polygon)
    
    # Convert to absolute value (area_m2 can be negative depending on orientation)
    area_m2 = abs(area_m2)
    
    # Convert square meters to hectares
    area_hectares = area_m2 / 10000.0
    
    return round(area_hectares, 4)  # Round to 4 decimal places


def get_polygon_center(coordinates: List[List[float]]) -> Tuple[float, float]:
    """
    Calculate the center point (centroid) of a polygon.
    
    This is useful for displaying farms on a map - the center point can be
    used as the default map center when viewing a farm.
    
    Args:
        coordinates: List of [lat, lon] coordinate pairs
        
    Returns:
        Tuple of (center_lat, center_lon)
        
    Example:
        >>> coords = [[18.52, 73.85], [18.53, 73.85], [18.53, 73.86]]
        >>> center_lat, center_lon = get_polygon_center(coords)
        >>> print(f"Center: {center_lat}, {center_lon}")
        Center: 18.526667, 73.853333
    """
    # Validate polygon
    is_valid, error_msg = validate_polygon(coordinates)
    if not is_valid:
        raise ValueError(error_msg)
    
    # Convert to Shapely format
    shapely_coords = [(lon, lat) for lat, lon in coordinates]
    polygon = Polygon(shapely_coords)
    
    # Get centroid
    centroid = polygon.centroid
    
    # Return as lat, lon (swapped from Shapely's lon, lat)
    return round(centroid.y, 6), round(centroid.x, 6)


# Best Practices for Geospatial Calculations:
#
# 1. Coordinate Order:
#    - GPS/User Input: [latitude, longitude]
#    - GeoJSON/Shapely: [longitude, latitude]
#    - Always be aware of which format you're using!
#
# 2. Geodesic vs Planar:
#    - Geodesic: Accounts for Earth's curvature (use for accuracy)
#    - Planar: Treats Earth as flat (faster but less accurate)
#    - For land areas, always use geodesic
#
# 3. Coordinate Systems:
#    - WGS84: Standard GPS coordinate system (what we use)
#    - UTM: Good for local calculations (not used here)
#    - Web Mercator: Used by web maps (not for area calculations!)
#
# 4. Validation:
#    - Always validate input coordinates
#    - Check for self-intersection, zero area
#    - Ensures data quality and prevents errors
#
# 5. Precision:
#    - GPS typically accurate to ~5-10 meters
#    - Don't round coordinates too much (6 decimal places = ~0.1m precision)
#    - Round final area to reasonable precision (4 decimal places for hectares)
