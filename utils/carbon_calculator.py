"""
Carbon Credit Calculator Module

This module calculates carbon credits and their monetary value based on
farm characteristics (area, soil type, verification status).

Key Concepts:
- Carbon Sequestration: How soil captures and stores carbon
- Soil-based Multipliers: Different soils have different carbon retention
- Verification System: Verified farms get full credits, unverified get half
- Market Pricing: Convert credits to monetary value (INR)
"""

from typing import Dict


# Soil type multipliers for carbon sequestration
# Different soil types have varying capacity to store carbon
SOIL_TYPE_MULTIPLIERS: Dict[str, float] = {
    "Loamy": 1.2,    # Best for carbon retention - rich organic matter
    "Clay": 1.0,     # Standard retention - dense structure
    "Sandy": 0.8,    # Lower retention - loose structure
    "Mixed": 1.0,    # Average of different soil types
}

# Crop type multipliers for carbon sequestration
# Different crops have varying carbon sequestration potential
CROP_TYPE_MULTIPLIERS: Dict[str, float] = {
    "Rice": 1.1,          # Paddy fields have high carbon sequestration
    "Wheat": 1.0,         # Standard crop baseline
    "Vegetables": 0.9,    # Shorter growth cycles, less biomass
    "Pulses": 1.2,        # Nitrogen-fixing crops, improve soil carbon
    "Sugarcane": 1.3,     # High biomass production, excellent carbon storage
    "Cotton": 0.8,        # Lower carbon retention
    "Fruits": 1.1,        # Perennial crops with long-term carbon storage
    "Mixed Crops": 1.0,   # Average of different crops
}

# Base credit rate per hectare per year
# This represents the baseline carbon sequestration potential
BASE_CREDIT_RATE = 12.5  # credits/hectare/year

# Market rate per carbon credit in INR
# Current rate: ₹500 per credit
MARKET_RATE_PER_CREDIT = 500.0  # ₹500 per credit

# Verification multiplier
# Unverified farms get 50% credits until they are verified by authorities
VERIFICATION_MULTIPLIER_UNVERIFIED = 0.5
VERIFICATION_MULTIPLIER_VERIFIED = 1.0


# Calculation Formula:
# -------------------
# Annual Credits = Area (ha) × Soil Multiplier × Crop Multiplier × Base Rate × Verification Multiplier
#
# Where:
# - Area: Farm area in hectares
# - Soil Multiplier: 1.2 (Loamy), 1.0 (Clay/Mixed), 0.8 (Sandy)
# - Crop Multiplier: 1.3 (Sugarcane), 1.2 (Pulses), 1.1 (Rice/Fruits), 1.0 (Wheat/Mixed), 0.9 (Vegetables), 0.8 (Cotton)
# - Base Rate: 12.5 credits/hectare/year
# - Verification: 0.5 (unverified) or 1.0 (verified)


def calculate_annual_credits(
    area_hectares: float,
    soil_type: str,
    crop_type: str,
    is_verified: bool = False
) -> float:
    """
    Calculate annual carbon credits for a farm.
    
    Args:
        area_hectares: Farm area in hectares
        soil_type: Type of soil (Loamy, Clay, Sandy, Mixed)
        crop_type: Type of crop (Rice, Wheat, Vegetables, Pulses, Sugarcane, Cotton, Fruits, Mixed Crops)
        is_verified: Whether the farm is verified by authorities
    
    Returns:
        float: Annual carbon credits
    
    Raises:
        ValueError: If inputs are invalid
    
    Example:
        >>> calculate_annual_credits(5.0, "Loamy", "Sugarcane", True)
        97.5  # 5 × 1.2 × 1.3 × 12.5 × 1.0 = 97.5 credits
        
        >>> calculate_annual_credits(5.0, "Loamy", "Rice", False)
        41.25  # 5 × 1.2 × 1.1 × 12.5 × 0.5 = 41.25 credits (unverified)
    """
    # Validate inputs
    if area_hectares <= 0:
        raise ValueError("Area must be positive")
    
    if soil_type not in SOIL_TYPE_MULTIPLIERS:
        raise ValueError(
            f"Invalid soil type: {soil_type}. "
            f"Must be one of: {', '.join(SOIL_TYPE_MULTIPLIERS.keys())}"
        )
    
    if crop_type not in CROP_TYPE_MULTIPLIERS:
        raise ValueError(
            f"Invalid crop type: {crop_type}. "
            f"Must be one of: {', '.join(CROP_TYPE_MULTIPLIERS.keys())}"
        )
    
    # Get multipliers
    soil_multiplier = SOIL_TYPE_MULTIPLIERS[soil_type]
    crop_multiplier = CROP_TYPE_MULTIPLIERS[crop_type]
    verification_multiplier = (
        VERIFICATION_MULTIPLIER_VERIFIED if is_verified 
        else VERIFICATION_MULTIPLIER_UNVERIFIED
    )
    
    # Calculate annual credits
    annual_credits = (
        area_hectares *
        soil_multiplier *
        crop_multiplier *
        BASE_CREDIT_RATE *
        verification_multiplier
    )
    
    # Round to 2 decimal places
    return round(annual_credits, 2)

DEFAULT_MARKET_RATE_INR = 500.0
def calculate_annual_value(
    credits: float,
    market_rate: float = DEFAULT_MARKET_RATE_INR
) -> float:
    """
    Calculate the monetary value of carbon credits.
    
    Simple multiplication: credits × market_rate
    
    Args:
        credits: Number of carbon credits
        market_rate: Price per credit in INR (default: ₹500)
        
    Returns:
        float: Annual value in INR
        
    Example:
        >>> # 37.5 credits at ₹500 each
        >>> value = calculate_annual_value(37.5)
        >>> print(f"Annual value: ₹{value:,.2f}")
        Annual value: ₹18,750.00
        
        >>> # Custom market rate (e.g., premium market)
        >>> value = calculate_annual_value(37.5, market_rate=600)
        >>> print(f"Annual value: ₹{value:,.2f}")
        Annual value: ₹22,500.00
    """
    if credits < 0:
        raise ValueError(f"Invalid credits: {credits}. Credits cannot be negative.")
    
    if market_rate <= 0:
        raise ValueError(f"Invalid market rate: {market_rate}. Must be positive.")
    
    annual_value = credits * market_rate
    
    # Round to 2 decimal places
    return round(annual_value, 2)


def get_soil_types() -> list[str]:
    """
    Get list of valid soil types.
    
    Useful for frontend dropdowns and validation.
    
    Returns:
        List of soil type names
        
    Example:
        >>> soil_types = get_soil_types()
        >>> print(soil_types)
        ['Loamy', 'Clay', 'Sandy', 'Mixed']
    """
    return list(SOIL_TYPE_MULTIPLIERS.keys())


def estimate_earnings(
    area_hectares: float,
    soil_type: str,
    is_verified: bool = False,
    market_rate: float = DEFAULT_MARKET_RATE_INR
) -> Dict[str, float]:
    """
    Calculate complete earnings breakdown for a farm.
    
    Convenience function that combines both credit and value calculations.
    Returns a dictionary with all relevant financial information.
    
    Args:
        area_hectares: Farm area in hectares
        soil_type: Type of soil
        is_verified: Verification status
        market_rate: Market rate per credit (default: ₹500)
        
    Returns:
        Dictionary with:
            - area: Farm area
            - soil_type: Soil type
            - annual_credits: Credits per year
            - annual_value_inr: Value in INR
            - market_rate: Rate used
            - is_verified: Verification status
            
    Example:
        >>> earnings = estimate_earnings(3.2, "Loamy", True)
        >>> print(earnings)
        {
            'area': 3.2,
            'soil_type': 'Loamy',
            'annual_credits': 48.0,
            'annual_value_inr': 24000.0,
            'market_rate': 500.0,
            'is_verified': True
        }
    """
    credits = calculate_annual_credits(area_hectares, soil_type, is_verified)
    value = calculate_annual_value(credits, market_rate)
    
    return {
        "area": area_hectares,
        "soil_type": soil_type,
        "annual_credits": credits,
        "annual_value_inr": value,
        "market_rate": market_rate,
        "is_verified": is_verified,
    }


# Carbon Credit Background for Interns:
#
# 1. What are Carbon Credits?
#    - 1 credit = 1 ton of CO2 removed/prevented from atmosphere
#    - Farming practices can sequester carbon in soil
#    - Credits can be sold to companies to offset their emissions
#
# 2. Why Different Soil Types?
#    - Loamy soil: Best structure for carbon retention
#    - Clay soil: Dense, holds carbon well but harder to work
#    - Sandy soil: Loose structure, carbon escapes more easily
#    - Mixed soil: Combination of types, average performance
#
# 3. Verification System:
#    - Unverified farms: New registrations, not yet validated
#    - Verified farms: Validated by expert/satellite/field visit
#    - Half credits for unverified: Conservative estimate until proven
#
# 4. Market Rate:
#    - Currently fixed at ₹500/credit for simplicity
#    - Real markets: Prices fluctuate based on supply/demand
#    - Future enhancement: Dynamic pricing from market_rates table
#
# 5. Calculation Example:
#    Farm: 5 hectares, Loamy soil, Verified
#    Credits: 5 × 1.2 × 12.5 × 1.0 = 75 credits/year
#    Value: 75 × ₹500 = ₹37,500/year
#    
#    Same farm unverified:
#    Credits: 5 × 1.2 × 12.5 × 0.5 = 37.5 credits/year
#    Value: 37.5 × ₹500 = ₹18,750/year
