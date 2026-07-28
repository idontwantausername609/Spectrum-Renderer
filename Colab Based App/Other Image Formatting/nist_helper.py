# NIST Descriptors and Descriptor Effects

NIST_DESCRIPTORS = ['*'	,
':'	,
'-' ,
'a'	,
'b'	,
'bl'	,
'B'	,
'c'	,
'd'	,
'D'	,
'E'	,
'f'	,
'g'	,
'G'	,
'H'	,
'h'	,
'hfs'	,
'i'	,
'j'	,
'l'	,
'm'	,
'p'	,
'q'	,
'r'	,
's'	,
't'	,
'u'	,
'w'	,
'x'	,]

# Recommended base rule set (intensity_multiplier, width_multiplier, confidence, action)

DESCRIPTOR_EFFECTS = {
    '*': (1.0, 1.0, 'medium', 'shared'),      # shared intensity (handled specially)
    ':': (1.0, 1.0, 'high', 'rounded'),       # rounded Ritz — no change
    '-': (0.80, 1.0, 'medium', 'dim'),        # somewhat lower
    'a': (0.50, 1.0, 'low', 'absorption'),    # observed in absorption
    'b': (1.00, 1.20, 'high', 'band-edge'),   # band head -> slightly broader
    'bl':(1.00, 1.25, 'medium', 'blend'),     # blended -> broader
    'B': (1.00, 1.80, 'high', 'broad'),       # autoionization broadening -> much broader
    'c': (1.00, 1.10, 'high', 'complex'),     # complex -> mild broadening
    'd': (1.00, 1.10, 'high', 'diffuse'),
    'D': (1.00, 1.00, 'high', 'doublet'),     # double -> treat as double later if implemented
    'E': (0.90, 1.30, 'medium', 'overexposed'), # overexposed -> slightly dimmer & broader
    'f': (1.00, 1.00, 'high', 'forbidden'),
    'g': (1.00, 1.00, 'high', 'ground-term'),
    'G': (1.00, 1.00, 'low', 'uncertain-pos'),
    'H': (0.70, 1.50, 'low', 'very-hazy'),
    'h': (1.00, 1.10, 'high', 'hazy'),
    'hfs':(1.00, 1.35, 'high', 'hfs'),
    'i': (0.60, 1.00, 'low', 'uncertain-id'),
    'j': (1.00, 1.00, 'high', 'smoothed'),
    'l': (1.00, 1.00, 'high', 'shaded-longer'),
    'm': (0.00, 0.00, 'excluded', 'masked'),  # skip these lines
    'p': (0.80, 1.20, 'medium', 'perturbed'),
    'q': (1.00, 1.00, 'high', 'asymmetric'),
    'r': (1.00, 1.00, 'high', 'reversed'),
    's': (1.00, 1.00, 'high', 'shaded-shorter'),
    't': (0.70, 1.00, 'low', 'tentative'),
    'u': (0.75, 1.20, 'medium', 'unresolved'),
    'w': (1.00, 1.80, 'high', 'wide'),
    'x': (1.00, 1.00, 'low', 'extrapolated'),
}

# Precompute keys sorted longest-first (so 'hfs' and 'bl' match before 'h' / 'b')
_DESCRIPTOR_KEYS_SORTED = sorted(DESCRIPTOR_EFFECTS.keys(), key=len, reverse=True)

def compute_descriptor_effects(tokens, group_size=None):
    include = True
    intensity_mult = 1.0
    width_mult = 1.0
    actions = []
    # pick worst (max numeric) confidence index
    conf_order = {'high':0, 'medium':1, 'low':2, 'excluded':3}
    worst_conf = 'high'

    # handle tokens list (assumed normalized, e.g. ['bl','*'])
    for tok in tokens:
        rule = DESCRIPTOR_EFFECTS.get(tok)
        if rule is None:
            continue
        rule_int, rule_width, rule_conf, rule_action = rule[0], rule[1], rule[2], rule[3]
        # combine include: if any token excludes, whole line excluded
        if rule_conf == 'excluded' or rule_int == 0.0:
            include = False
        intensity_mult *= rule_int
        width_mult = max(width_mult, rule_width)
        if rule_action not in actions:
            actions.append(rule_action)
        # update worst confidence
        if conf_order.get(rule_conf, 0) > conf_order.get(worst_conf, 0):
            worst_conf = rule_conf

    shared_hint = False
    if '*' in tokens:
        if group_size and group_size > 1:
            intensity_mult = intensity_mult / float(group_size)
        else:
            shared_hint = True  # caller may decide how to handle

    return {
        "include": bool(include),
        "intensity_multiplier": float(intensity_mult),
        "width_multiplier": float(width_mult),
        "actions": actions,
        "confidence": worst_conf,
        "shared_hint": shared_hint,
    }
