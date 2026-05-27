from PIL import Image, ImageChops
import sys

paths = ['outputs/debug_web_render.png', 'outputs/webapp_response.png']
imgs = [Image.open(p).convert('RGBA') for p in paths]
# Resize to smallest common size
min_size = (min(img.size[0] for img in imgs), min(img.size[1] for img in imgs))
imgs = [img.resize(min_size) for img in imgs]

diff = ImageChops.difference(imgs[0], imgs[1])
# compute bbox of non-zero regions
bbox = diff.getbbox()
if bbox is None:
    print('IDENTICAL')
else:
    # compute mean squared error
    import numpy as np
    a = np.array(imgs[0], dtype=np.float32)
    b = np.array(imgs[1], dtype=np.float32)
    mse = ((a - b) ** 2).mean()
    print('DIFFER', 'mse={:.4f}'.format(mse), 'bbox=', bbox)
    diff.save('outputs/image_diff.png')
    print('Wrote outputs/image_diff.png')
