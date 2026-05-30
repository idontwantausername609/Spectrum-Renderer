import re
import importlib
import numpy as np
import pandas as pd
from scipy.signal import find_peaks
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import utils
import nist_codes
import generic_render

try:
    import nist_helper
    descriptor_tokens = [t.lower() for t in getattr(nist_helper, "NIST_DESCRIPTORS", [])]
except Exception:
    nist_helper = None
    descriptor_tokens = []

def is_nist_descriptor(descriptor, descriptor_tokens=descriptor_tokens):
    if not descriptor:
        return False
    desc_text = str(descriptor).lower()
    return any(token in desc_text for token in descriptor_tokens)