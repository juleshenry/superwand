"""Finding an image's prominent color regions."""

from __future__ import annotations

from collections import OrderedDict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from os import PathLike
from typing import Any

import numpy as np
import numpy.typing as npt
from PIL import Image, ImageOps
from sklearn.cluster import KMeans

from .color import RGB, FloatArray, oklab_to_rgb, srgb_to_oklab, to_uint8

ImageInput = str | PathLike[str] | Image.Image
SPACES = ("oklab", "rgb")
_CHUNK = 1 << 20  # pixels per assignment batch; bounds peak memory on huge images

U8Array = npt.NDArray[np.uint8]


def load_image(image: ImageInput) -> tuple[U8Array, U8Array | None]:
    """
    Opens a path or PIL image, applies EXIF rotation, and returns (rgb, alpha):
    an (H, W, 3) uint8 array and an (H, W) uint8 alpha array, or None for
    images without transparency.
    """
    img = image if isinstance(image, Image.Image) else Image.open(image)
    img = ImageOps.exif_transpose(img)
    has_alpha = img.mode in ("RGBA", "RGBa", "LA", "La", "PA") or "transparency" in img.info
    if not has_alpha:
        return np.array(img.convert("RGB")), None
    arr = np.array(img.convert("RGBA"))
    return np.ascontiguousarray(arr[..., :3]), np.ascontiguousarray(arr[..., 3])


def _to_space(rgb: npt.ArrayLike, space: str) -> FloatArray:
    if space == "oklab":
        return srgb_to_oklab(rgb)
    return np.asarray(rgb, dtype=np.float64)


def _sq_distances(pts: FloatArray, centers: FloatArray) -> FloatArray:
    """(n, k) squared distances without materializing an (n, k, 3) array."""
    d = (pts**2).sum(1)[:, None] - 2 * pts @ centers.T + (centers**2).sum(1)[None, :]
    return np.maximum(d, 0)


@dataclass
class Regions:
    """
    The result of `find_regions`: every visible pixel belongs to one region.

    labels: (H, W) int16 region index per pixel, -1 for fully transparent pixels.
    colors: each region's representative sRGB color, largest region first.
    counts: pixels per region.
    centers: cluster centers in `space` ("oklab" or "rgb"), index-aligned with colors.
    """

    labels: npt.NDArray[np.int16]
    colors: list[RGB]
    counts: list[int]
    centers: FloatArray
    space: str = "oklab"
    _soft: tuple[npt.NDArray[np.int16], npt.NDArray[np.float32]] | None = field(
        default=None, repr=False, compare=False
    )

    def __len__(self) -> int:
        return len(self.colors)

    @property
    def shape(self) -> tuple[int, int]:
        return (int(self.labels.shape[0]), int(self.labels.shape[1]))

    @property
    def lightness(self) -> FloatArray:
        """OKLab L of each region color."""
        if not self.colors:
            return np.zeros(0)
        return srgb_to_oklab(np.array(self.colors, dtype=np.float64))[:, 0]

    def mask(self, index: int) -> npt.NDArray[np.bool_]:
        return self.labels == index

    def soft_assignment(
        self, rgb: U8Array
    ) -> tuple[npt.NDArray[np.int16], npt.NDArray[np.float32]]:
        """
        Second-nearest region per pixel and the weight (0.5..1) of the nearest
        one, for blending across region edges. Cached after the first call.
        """
        if self._soft is not None:
            return self._soft
        second = self.labels.copy()
        weight = np.ones(self.shape, dtype=np.float32)
        if len(self) > 1:
            flat = rgb.reshape(-1, 3)
            lab = self.labels.reshape(-1)
            sec, wt = second.reshape(-1), weight.reshape(-1)
            visible = np.flatnonzero(lab >= 0)
            for start in range(0, len(visible), _CHUNK):
                idx = visible[start : start + _CHUNK]
                d = np.sqrt(_sq_distances(_to_space(flat[idx], self.space), self.centers))
                nearest = lab[idx]
                d1 = d[np.arange(len(idx)), nearest]
                d[np.arange(len(idx)), nearest] = np.inf
                runner_up = d.argmin(axis=1)
                d2 = d[np.arange(len(idx)), runner_up]
                total = d1 + d2
                sec[idx] = runner_up
                wt[idx] = np.where(total > 0, d2 / np.where(total > 0, total, 1), 1)
        self._soft = (second, weight)
        return self._soft

    def to_dict(self) -> OrderedDict[RGB, npt.NDArray[np.intp]]:
        """The pre-0.4 format: {region color: array of [row, col]}, largest first."""
        return OrderedDict(
            (color, np.argwhere(self.labels == i)) for i, color in enumerate(self.colors)
        )

    @classmethod
    def from_dict(
        cls, regions: Mapping[Sequence[int], npt.ArrayLike], shape: tuple[int, int]
    ) -> Regions:
        """Builds Regions from the pre-0.4 {color: [[row, col], ...]} format."""
        labels = np.full(shape, -1, dtype=np.int16)
        colors: list[RGB] = []
        counts: list[int] = []
        for i, (color, coords) in enumerate(regions.items()):
            pts = np.asarray(coords, dtype=np.intp).reshape(-1, 2)
            labels[pts[:, 0], pts[:, 1]] = i
            colors.append((int(color[0]), int(color[1]), int(color[2])))
            counts.append(len(pts))
        centers = srgb_to_oklab(np.array(colors, dtype=np.float64).reshape(-1, 3))
        return cls(labels, colors, counts, centers, "oklab")


def find_regions(
    image: ImageInput,
    k: int = 4,
    *,
    seed: int = 42,
    max_samples: int = 100_000,
    space: str = "oklab",
) -> Regions:
    """
    Splits an image into its `k` most prominent color regions with k-means.

    Clustering runs in OKLab by default, so regions follow perceived color
    differences; space="rgb" clusters raw sRGB values as superwand < 0.4 did.
    Fully transparent pixels are ignored. Results are reproducible for a
    given `seed`.
    """
    rgb, alpha = load_image(image)
    return regions_from_array(rgb, alpha, k, seed=seed, max_samples=max_samples, space=space)


def regions_from_array(
    rgb: U8Array,
    alpha: U8Array | None,
    k: int = 4,
    *,
    seed: int = 42,
    max_samples: int = 100_000,
    space: str = "oklab",
) -> Regions:
    """`find_regions` for an already-loaded (H, W, 3) uint8 array and optional alpha."""
    if k < 1:
        raise ValueError(f"k must be at least 1, got {k}")
    if space not in SPACES:
        raise ValueError(f"space must be one of {SPACES}, got {space!r}")
    h, w = rgb.shape[:2]
    flat = rgb.reshape(-1, 3)
    labels = np.full(h * w, -1, dtype=np.int16)

    visible: npt.NDArray[Any] | None
    pool: npt.NDArray[Any]
    if alpha is None:
        visible = None
        pool = np.arange(h * w)
    else:
        a = alpha.reshape(-1)
        visible = np.flatnonzero(a > 0)
        pool = np.flatnonzero(a >= 128)  # sample the palette from solid pixels
        if len(pool) == 0:
            pool = visible
    if len(pool) == 0:  # fully transparent image
        return Regions(labels.reshape(h, w), [], [], np.zeros((0, 3)), space)

    rng = np.random.default_rng(seed)
    if len(pool) > max_samples:
        pool = rng.choice(pool, max_samples, replace=False)
    # Cluster unique colors weighted by frequency: same result, much faster on flat art
    uniq, freq = np.unique(flat[pool], axis=0, return_counts=True)
    n_clusters = min(k, len(uniq))
    kmeans = KMeans(n_clusters=n_clusters, random_state=seed, n_init="auto")
    kmeans.fit(_to_space(uniq, space), sample_weight=freq)
    centers = kmeans.cluster_centers_

    targets = np.arange(h * w) if visible is None else visible
    for start in range(0, len(targets), _CHUNK):
        idx = targets[start : start + _CHUNK]
        labels[idx] = _sq_distances(_to_space(flat[idx], space), centers).argmin(axis=1)

    # Renumber by size, largest first, dropping clusters no pixel landed in
    counts = np.bincount(labels[targets], minlength=n_clusters)
    order = [int(i) for i in np.argsort(-counts, kind="stable") if counts[i] > 0]
    remap = np.full(n_clusters + 1, -1, dtype=np.int16)  # last slot maps -1 to -1
    remap[order] = np.arange(len(order))
    labels = remap[labels]  # type: ignore[assignment]

    centers = centers[order]
    if space == "oklab":
        colors = [oklab_to_rgb(c) for c in centers]
    else:
        colors = [(int(v[0]), int(v[1]), int(v[2])) for v in to_uint8(centers)]
    return Regions(
        labels.reshape(h, w),
        colors,
        [int(counts[i]) for i in order],
        np.asarray(centers, dtype=np.float64),
        space,
    )


def extract_palette(image: ImageInput, k: int = 4, **kwargs: object) -> list[RGB]:
    """The image's `k` dominant colors as RGB tuples, most prominent first."""
    return list(find_regions(image, k, **kwargs).colors)  # type: ignore[arg-type]
