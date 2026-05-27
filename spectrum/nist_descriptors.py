"""
NIST descriptor constants and parsing functions.
Descriptor format: (include, intensity_multiplier, width_multiplier, confidence, visual_action)
"""

NIST_DESCRIPTORS = {
    # (descriptor_string): (include, intensity_multiplier, width_multiplier, confidence_label, visual_action)
    '*': (True, 1.0, 1.0, 'medium', 'line'),          # Shared intensity
    ':': (True, 1.0, 1.0, 'high', 'line'),            # Rounded Ritz value
    '-': (True, 0.8, 1.0, 'medium', 'line'),          # Somewhat lower intensity
    'a': (True, 0.5, 1.0, 'low', 'line'),             # Absorption
    'b': (True, 1.0, 1.2, 'high', 'band-edge'),       # Band head
    'bl': (True, 1.0, 1.25, 'medium', 'blend'),       # Blended
    'B': (True, 1.0, 1.8, 'high', 'broad'),           # Autoionization broadening
    'c': (True, 1.0, 1.1, 'high', 'line'),            # Complex
    'd': (True, 1.0, 1.1, 'high', 'line'),            # Diffuse
    'D': (True, 1.0, 1.0, 'high', 'doublet'),         # Double line; two nearby components, not a broader single line
    'E': (True, 0.9, 1.3, 'medium', 'broad'),         # Overexposed
    'f': (True, 1.0, 1.0, 'high', 'line'),            # Forbidden
    'g': (True, 1.0, 1.0, 'high', 'line'),            # Ground term
    'G': (True, 1.0, 1.0, 'low', 'line'),             # Roughly estimated wavelength
    'H': (True, 0.7, 1.5, 'low', 'broad'),            # Very hazy
    'h': (True, 1.0, 1.1, 'high', 'line'),            # Hazy (diffuse)
    'hfs': (True, 1.0, 1.35, 'high', 'cluster'),      # Hyperfine structure
    'i': (True, 0.6, 1.0, 'low', 'line'),             # Uncertain identification
    'j': (True, 1.0, 1.0, 'high', 'line'),            # Wavelength smoothed
    'l': (True, 1.0, 1.0, 'high', 'line'),            # Shaded to longer wavelengths
    'm': (False, 0.0, 0.0, 'excluded', 'skip'),       # Masked — skip
    'p': (True, 0.8, 1.2, 'medium', 'line'),          # Perturbed
    'q': (True, 1.0, 1.0, 'high', 'line'),            # Asymmetric
    'r': (True, 1.0, 1.0, 'high', 'line'),            # Easily reversed
    's': (True, 1.0, 1.0, 'high', 'line'),            # Shaded to shorter wavelengths
    't': (True, 0.7, 1.0, 'low', 'line'),             # Tentative
    'u': (True, 0.75, 1.2, 'medium', 'cluster'),      # Unresolved
    'w': (True, 1.0, 1.8, 'high', 'broad'),           # Wide
    'x': (True, 1.0, 1.0, 'low', 'line'),             # Extrapolated wavelength
}

DESCRIPTOR_KEYS = sorted(NIST_DESCRIPTORS.keys(), key=len, reverse=True)
CONFIDENCE_ORDER = {'high': 0, 'medium': 1, 'low': 2, 'excluded': 3}


def split_descriptor_tokens(descriptor_text):
    """
    Split composite descriptor strings like 'bl*' or 'w*' into known tokens.
    
    Args:
        descriptor_text (str): Raw descriptor suffix from intensity column
    
    Returns:
        list[str]: List of recognized descriptor tokens
    """
    remaining = descriptor_text.strip()
    tokens = []
    while remaining:
        matched = None
        for key in DESCRIPTOR_KEYS:
            if remaining.startswith(key):
                matched = key
                break
        if matched is None:
            # Consume one unknown character to avoid infinite loop
            tokens.append(remaining[0])
            remaining = remaining[1:]
            continue
        tokens.append(matched)
        remaining = remaining[len(matched):]
    return tokens


def combine_descriptor_rules(tokens):
    """
    Combine multiple descriptor tokens into aggregate rules.
    
    Args:
        tokens (list[str]): Parsed descriptor tokens
    
    Returns:
        tuple: (include, intensity_multiplier, width_multiplier, confidence, actions, unknown_tokens)
    """
    include = True
    intensity_multiplier = 1.0
    width_multiplier = 1.0
    confidence = 'high'
    actions = []
    unknown_tokens = []

    for token in tokens:
        rule = NIST_DESCRIPTORS.get(token)
        if rule is None:
            unknown_tokens.append(token)
            continue
        token_include, token_intensity, token_width, token_confidence, token_action = rule
        include = include and token_include
        intensity_multiplier *= token_intensity
        width_multiplier = max(width_multiplier, token_width)
        if CONFIDENCE_ORDER[token_confidence] > CONFIDENCE_ORDER[confidence]:
            confidence = token_confidence
        if token_action not in actions:
            actions.append(token_action)

    return include, intensity_multiplier, width_multiplier, confidence, actions, unknown_tokens


def parse_nist_intensity(intensity_value):
    """
    Parse numeric intensity with optional descriptor suffix. Example: '100bl*'
    
    Args:
        intensity_value: Cell value from intensity column
    
    Returns:
        tuple: (numeric_intensity, raw_descriptor, tokens, intensity_multiplier, 
                width_multiplier, confidence, actions, unknown_tokens)
    """
    if intensity_value is None:
        return None, '', [], 1.0, 1.0, 'high', [], []

    value_str = str(intensity_value).strip()
    i = 0
    while i < len(value_str) and (value_str[i].isdigit() or value_str[i] in '.+-'):
        i += 1

    numeric_part = value_str[:i].strip()
    descriptor_text = value_str[i:].strip()

    if not numeric_part:
        return None, descriptor_text, [], 1.0, 1.0, 'high', [], []

    try:
        numeric_intensity = float(numeric_part)
    except ValueError:
        return None, descriptor_text, [], 1.0, 1.0, 'high', [], []

    tokens = split_descriptor_tokens(descriptor_text) if descriptor_text else []
    include, intensity_multiplier, width_multiplier, confidence, actions, unknown_tokens = combine_descriptor_rules(tokens)

    return numeric_intensity, descriptor_text, tokens, intensity_multiplier, width_multiplier, confidence, actions, unknown_tokens
