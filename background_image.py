import random
import math
import numpy as np
from PIL import Image

IMAGE_SIZE = 1028
TWO_PI = 2 * math.pi
GRID_SIZE = 256

GOLDEN_ANGLE = math.pi * (3 - math.sqrt(5))  # ~2.4 rad; avoids octave periodicity

# Permutation table (shuffled) and gradient vectors
VECTOR_INDICES = list(range(GRID_SIZE))
random.shuffle(VECTOR_INDICES)
VI = np.array(VECTOR_INDICES, dtype=np.int64)

GRADIENTS = np.array([
    (math.cos(TWO_PI * a / GRID_SIZE), math.sin(TWO_PI * a / GRID_SIZE))
    for a in range(GRID_SIZE)
])

RANDOM_SHIFTS = [random.uniform(1, 10) for _ in range(100)]

# Colors in 0–255 RGB; shape (4, 3) for broadcasting in color interpolation
COLOR_PALETTE = np.array([
    [0x70, 0xab, 0xbd],  # light blue
    [0x36, 0x48, 0x4e],  # charcoal
    [0xa7, 0x74, 0x2f],  # copper
    [0xe2, 0xd4, 0xc1],  # bone
], dtype=float)


def interpolate(a, b, w):
    """Smooth-step cubic interpolation; w clipped to [0, 1]."""
    w = np.clip(w, 0, 1)
    return (b - a) * (3.0 - w * 2.0) * w * w + a


def coordinate_hash(x, y, period):
    """Map integer coordinate arrays to gradient indices via permutation table."""
    inner = VI[(x % period) % GRID_SIZE]
    return VI[((inner + y) % period) % GRID_SIZE]


def noise(x, y, period=GRID_SIZE):
    """Perlin noise on float arrays; returns values in [-1, 1]."""
    ix = np.floor(x).astype(np.int64)
    iy = np.floor(y).astype(np.int64)
    fx, fy = x - ix, y - iy

    dots = []
    for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
        cx, cy = ix + dx, iy + dy
        idx = coordinate_hash(cx, cy, period)
        dots.append((x - cx) * GRADIENTS[idx, 0] + (y - cy) * GRADIENTS[idx, 1])

    return interpolate(
        interpolate(dots[0], dots[1], fx),
        interpolate(dots[2], dots[3], fx),
        fy,
    )


def fractal_noise(x, y, period, octaves, octave_rotation=0.0):
    """Fractional Brownian motion; returns values in [0, 1].

    octave_rotation: rotate coordinates by this angle at each successive octave.
        Breaks the alignment between octaves for more organic patterns.
        GOLDEN_ANGLE (~2.4) avoids all periodicity; math.pi/4 gives a cleaner look.
    """
    result = np.zeros_like(x, dtype=float)
    for o in range(octaves):
        scale = 2 ** o
        if octave_rotation:
            angle = octave_rotation * o
            cos_a, sin_a = math.cos(angle), math.sin(angle)
            xo = (x * cos_a - y * sin_a) * scale
            yo = (x * sin_a + y * cos_a) * scale
        else:
            xo, yo = x * scale, y * scale
        result += (0.5 ** o) * noise(xo, yo, period=int(period * scale))
    return result * 0.5 + 0.5


def colored_warping(x, y, period, octaves, warp_strength=4.0, octave_rotation=0.0):
    """Domain-warped color field; returns (H, W, 3) array in [0, 255].

    warp_strength: uniform multiplier on domain warp offset (W in the Iq formulation).
        0 = plain fractal noise colors, no warping.
        4 = default; 8+ = heavily distorted and turbulent.
    """
    def fn(x, y):
        return fractal_noise(x, y, period, octaves, octave_rotation)

    vx, vy = [x], [y]
    for i in range(3):
        k = 8 * i
        s = float(i > 0)
        vx.append(fn(
            x + warp_strength * vx[-1] * s + RANDOM_SHIFTS[k + 1],
            y + warp_strength * vy[-1] * s + RANDOM_SHIFTS[k + 3],
        ))
        vy.append(fn(
            x + warp_strength * vx[-2] * s + RANDOM_SHIFTS[k + 5],
            y + warp_strength * vy[-1] * s + RANDOM_SHIFTS[k + 7],
        ))

    # Interpolate through palette; weights (H, W) → (H, W, 1) for broadcasting
    rgb = interpolate(COLOR_PALETTE[0], COLOR_PALETTE[1], vx[-2][:, :, np.newaxis])
    rgb = interpolate(rgb,              COLOR_PALETTE[2], vy[-1][:, :, np.newaxis])
    rgb = interpolate(rgb,              COLOR_PALETTE[3], vx[-1][:, :, np.newaxis])
    return rgb


def make_image(size, period, octaves=7, stretch=1.0, rotation=0.0,
               warp_strength=4.0, octave_rotation=0.0):
    """Render one background image.

    stretch: scale x relative to y before all noise.
        1.0 = square/isotropic; 2.0 = horizontal streaks; 0.5 = vertical streaks.
    rotation: rotate the input coordinate grid (radians).
        Breaks x/y axis alignment; math.pi/4 is a good starting point.
    warp_strength: see colored_warping.
    octave_rotation: see fractal_noise.
    """
    scale = period / size
    xs = np.arange(size, dtype=float) * scale
    x_grid, y_grid = np.meshgrid(xs, xs)

    if stretch != 1.0:
        x_grid = x_grid * stretch
    if rotation != 0.0:
        cos_r, sin_r = math.cos(rotation), math.sin(rotation)
        x_grid, y_grid = (x_grid * cos_r - y_grid * sin_r,
                          x_grid * sin_r + y_grid * cos_r)

    rgb = colored_warping(x_grid, y_grid, period, octaves, warp_strength, octave_rotation)
    return Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8), "RGB")


# --- Example outputs --------------------------------------------------------

# Plain: isotropic baseline
make_image(IMAGE_SIZE, period=4).save("bg_plain.png")

# Directional: horizontal stretch + slight global rotation
make_image(IMAGE_SIZE, period=4, stretch=2.5, rotation=math.pi / 8).save("bg_directional.png")

# Organic: golden-angle octave rotation breaks all alignment
make_image(IMAGE_SIZE, period=4, octave_rotation=GOLDEN_ANGLE).save("bg_organic.png")

# Turbulent: heavy warp + octave rotation
make_image(IMAGE_SIZE, period=4, warp_strength=8.0,
           octave_rotation=math.pi / 4).save("bg_turbulent.png")

print("saved bg_plain.png, bg_directional.png, bg_organic.png, bg_turbulent.png")
