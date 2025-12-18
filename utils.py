"""
═══════════════════════════════════════════════════════════════════════════════
TKM Patient Generator - Utility Functions
Common helper functions used across modules
═══════════════════════════════════════════════════════════════════════════════
"""

import random


def calculate_bmi(height_cm, weight_kg):
    """
    Calculate BMI from height and weight.
    
    Args:
        height_cm: Height in centimeters
        weight_kg: Weight in kilograms
    
    Returns:
        BMI value (float)
    """
    height_m = height_cm / 100
    return weight_kg / (height_m * height_m)


def get_bmi_category(bmi):
    """
    Get BMI category based on WHO standards.
    
    Args:
        bmi: BMI value
    
    Returns:
        Category string (Korean/English)
    """
    if bmi < 18.5:
        return "저체중 (Underweight)"
    elif bmi < 25:
        return "정상 (Normal)"
    elif bmi < 30:
        return "과체중 (Overweight)"
    else:
        return "비만 (Obese)"


def safe_get(session, key, default=None):
    """
    Safely get a value from session state with a default.
    
    Args:
        session: Streamlit session_state object
        key: Key to retrieve
        default: Default value if key doesn't exist
    
    Returns:
        Value from session or default
    """
    return getattr(session, key, default) if hasattr(session, key) else default


def safe_append(session, list_key, value):
    """
    Safely append a value to a list in session state.
    
    Args:
        session: Streamlit session_state object
        list_key: Key of the list attribute
        value: Value to append
    """
    if hasattr(session, list_key):
        target_list = getattr(session, list_key)
        if isinstance(target_list, list) and value not in target_list:
            target_list.append(value)


def random_in_range(min_val, max_val, is_float=False, decimals=1):
    """
    Generate a random value in the given range.
    
    Args:
        min_val: Minimum value
        max_val: Maximum value
        is_float: Whether to return a float
        decimals: Number of decimal places for float
    
    Returns:
        Random value in range
    """
    if is_float:
        return round(random.uniform(min_val, max_val), decimals)
    return random.randint(min_val, max_val)


def clamp(value, min_val, max_val):
    """
    Clamp a value between min and max.
    
    Args:
        value: Value to clamp
        min_val: Minimum bound
        max_val: Maximum bound
    
    Returns:
        Clamped value
    """
    return max(min_val, min(value, max_val))


def weighted_choice(options, weights):
    """
    Make a weighted random choice from options.
    
    Args:
        options: List of options
        weights: List of weights (same length as options)
    
    Returns:
        Randomly selected option based on weights
    """
    return random.choices(options, weights=weights, k=1)[0]


def severity_to_text(severity, scale=5, korean=True):
    """
    Convert numeric severity to descriptive text.
    
    Args:
        severity: Numeric severity (0-5 or 0-10)
        scale: Maximum scale value (5 or 10)
        korean: Whether to include Korean text
    
    Returns:
        Descriptive text for severity
    """
    if scale == 5:
        if severity == 0:
            return "없음 (None)" if korean else "None"
        elif severity <= 1:
            return "경미 (Mild)" if korean else "Mild"
        elif severity <= 2:
            return "약간 (Slight)" if korean else "Slight"
        elif severity <= 3:
            return "중등도 (Moderate)" if korean else "Moderate"
        elif severity <= 4:
            return "심함 (Severe)" if korean else "Severe"
        else:
            return "매우 심함 (Very Severe)" if korean else "Very Severe"
    elif scale == 10:
        if severity == 0:
            return "없음 (None)" if korean else "None"
        elif severity <= 2:
            return "경미 (Mild)" if korean else "Mild"
        elif severity <= 4:
            return "약간 (Slight)" if korean else "Slight"
        elif severity <= 6:
            return "중등도 (Moderate)" if korean else "Moderate"
        elif severity <= 8:
            return "심함 (Severe)" if korean else "Severe"
        else:
            return "극심 (Extreme)" if korean else "Extreme"
    return str(severity)


def format_vital_signs(session):
    """
    Format vital signs into a display string.
    
    Args:
        session: Streamlit session_state object
    
    Returns:
        Formatted vital signs string
    """
    return (
        f"BP: {session.sbp}/{session.dbp} mmHg, "
        f"HR: {session.pulse_rate}/min, "
        f"RR: {session.resp}/min, "
        f"BT: {session.temp}°C"
    )


def is_valid_blood_pressure(sbp, dbp):
    """
    Check if blood pressure values are valid and safe.
    
    Args:
        sbp: Systolic blood pressure
        dbp: Diastolic blood pressure
    
    Returns:
        True if valid, False otherwise
    """
    # Check ranges
    if sbp < 90 or sbp > 180:
        return False
    if dbp < 60 or dbp > 110:
        return False
    # Check pulse pressure (SBP - DBP should be at least 20)
    if sbp - dbp < 20:
        return False
    return True


def validate_session_state(session, required_keys):
    """
    Validate that required keys exist in session state.
    
    Args:
        session: Streamlit session_state object
        required_keys: List of required key names
    
    Returns:
        List of missing keys (empty if all present)
    """
    missing = []
    for key in required_keys:
        if not hasattr(session, key):
            missing.append(key)
    return missing
