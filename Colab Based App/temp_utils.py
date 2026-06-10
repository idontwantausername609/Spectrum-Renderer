import random
import string

lambda_tokens = ["nm", "wavelength", "wavelength_nm", "lambda", "lambda_nm", "wl", "wl_nm", "Observed", "Observed Wavelength", "obs", "wave"]

int_tokens =["Grey Val", "grey val", "gray val", "grayscale", "gray value", "intensity", "signal", "counts", "value", "int", "rel. int.", "grey", "Rel. Int.", "Relative Intensity", "Rel Int", "Intensity", "A", "Aki", "gA", "gf", "weighted f", "f", "Intensity/Counts", 'rel', 'count', 'flux', 'grey value',]

def clean_title(text):
    text = str(text).strip() if text is not None else ''
    if not text:
        return None
    return text.split()[0]


def normalize_header(value):
    return str(value).strip().lower() if value is not None else ''


def looks_like_number(value):
    try:
        float(value)
        return True
    except (TypeError, ValueError):
        return False


def generate_random_title():
    random_code = ''.join(random.choices(string.digits, k=4))
    return f'Spectrum-{random_code}'
