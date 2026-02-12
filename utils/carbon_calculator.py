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


# Soil type multipliers based on carbon sequestration capacity
# These values reflect how well different soil types capture and retain carbon
SOIL_TYPE_MULTIPLIERS: Dict[str, float] = {
    "Loamy": 1.2,   # Best for carbon sequestration (well-balanced soil)
    "Clay": 1.0,    # Standard retention (dense, holds nutrients)
    "Sandy": 0.8,   # Lower retention (loose, drains quickly)
    "Mixed": 1.0,   # Average of various soil types
}

# Base rate: Credits per hectare per year
# This is the baseline for a standard farm
BASE_CREDIT_RATE = 12.5  # credits/hectare/year

# Default market rate per credit (in INR)
# This can be made dynamic in the future by fetching from a market_rates table
DEFAULT_MARKET_RATE_INR = 500.0  # ₹500 per credit


def calculate_annual_credits(
    area_hectares: float,
    soil_type: str,
    is_verified: bool = False
) -> float:
    """
    Calculate annual carbon credits for a farm.
    
    Formula:
        credits = area × soil_multiplier × base_rate × verification_multiplier
    
    Args:
        area_hectares: Farm area in hectares
        soil_type: Type of soil ("Loamy", "Clay", "Sandy", "Mixed")
        is_verified: Whether farm is verified by a validator (default: False)
        
    Returns:
        float: Annual carbon credits
        
    Raises:
        ValueError: If soil_type is not recognized or area is invalid
        
    Example:
        >>> # 2.5 hectare farm with loamy soil (verified)
        >>> credits = calculate_annual_credits(2.5, "Loamy", True)
        >>> print(f"Annual credits: {credits}")
        Annual credits: 37.5
        
        >>> # Same farm but unverified (gets 50% credits)
        >>> credits = calculate_annual_credits(2.5, "Loamy", False)
        >>> print(f"Annual credits: {credits}")
        Annual credits: 18.75
    """
    # Validate inputs
    if area_hectares <= 0:
        raise ValueError(f"Invalid area: {area_hectares}. Area must be positive.")
    
    if soil_type not in SOIL_TYPE_MULTIPLIERS:
        raise ValueError(
            f"Invalid soil type: {soil_type}. "
            f"Must be one of: {list(SOIL_TYPE_MULTIPLIERS.keys())}"
        )
    
    # Get soil multiplier
    soil_multiplier = SOIL_TYPE_MULTIPLIERS[soil_type]
    
    # Verification multiplier
    # Unverified farms get 50% credits (pending validation)
    # Verified farms get 100% credits (fully validated)
    verification_multiplier = 1.0 if is_verified else 0.5
    
    # Calculate credits
    annual_credits = (
        area_hectares *
        soil_multiplier *
        BASE_CREDIT_RATE *
        verification_multiplier
    )
    
    # Round to 2 decimal places
    return round(annual_credits, 2)


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
