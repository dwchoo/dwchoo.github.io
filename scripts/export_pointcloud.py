#!/usr/bin/env python3
"""Export a completed VGGT cloud, optionally recovering more points from depth."""

import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile

import numpy as np


VERTEX_DTYPE = np.dtype([
    ("x", "<f4"), ("y", "<f4"), ("z", "<f4"),
    ("red", "u1"), ("green", "u1"), ("blue", "u1"),
])


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reconstruct(source_run, percentile, reference_points, reference_colors, cameras):
    """Repeat depth unprojection in source frame/pixel order, without a point cap."""
    from PIL import Image

    if not np.isfinite(percentile) or not 0 <= percentile <= 100:
        raise ValueError("Confidence percentile must be between 0 and 100")
    paths = [source_run / "predictions.npz", source_run / "input_manifest.json"]
    hashes = {path.name: sha256(path) for path in paths}
    manifest = json.loads(paths[1].read_text())
    with np.load(paths[0], allow_pickle=False) as data:
        depth = data["depth"]
        confidence = data["depth_conf"]
        mask = data["valid_image_mask"]
        intrinsic = data["intrinsic"]
    if depth.ndim != 3 or depth.shape != confidence.shape or depth.shape != mask.shape or mask.dtype != bool:
        raise ValueError("Depth, confidence and valid mask must have matching SxHxW shapes")
    frames, height, width = depth.shape
    if len(cameras) != frames or intrinsic.shape != (frames, 3, 3) or len(manifest["frames"]) != frames:
        raise ValueError("Camera/image counts do not match the predictions")
    u, v = np.meshgrid(np.arange(width), np.arange(height))
    points = np.empty((*depth.shape, 3), dtype=np.float32)
    colors = np.empty((*depth.shape, 3), dtype=np.uint8)
    for i in range(frames):
        k = intrinsic[i].astype(np.float64)
        transform = cameras[i]
        if (not np.isfinite(k).all() or k[0, 0] <= 0 or k[1, 1] <= 0
                or k[0, 1] != 0 or k[1, 0] != 0 or not np.array_equal(k[2], [0, 0, 1])):
            raise ValueError("Invalid pinhole camera intrinsics")
        rotation = transform[:3, :3]
        if (not np.isfinite(transform).all() or not np.allclose(transform[3], [0, 0, 0, 1])
                or not np.allclose(rotation.T @ rotation, np.eye(3), atol=1e-5)
                or not np.isclose(np.linalg.det(rotation), 1)):
            raise ValueError("Invalid camera transform")
        d = depth[i].astype(np.float64)
        with np.errstate(invalid="ignore", over="ignore"):
            camera_points = np.stack(((u - k[0, 2]) * d / k[0, 0],
                                      (v - k[1, 2]) * d / k[1, 1], d), axis=-1)
            points[i] = (camera_points @ rotation.T + transform[:3, 3]).astype(np.float32)
        relative = f"processed_images/frame_{i:04d}.png"
        image_path = source_run / relative
        image_hash = sha256(image_path)
        if manifest["frames"][i].get("processed_sha256") != image_hash:
            raise ValueError(f"Processed image checksum mismatch: {relative}")
        hashes[relative] = image_hash
        with Image.open(image_path) as image:
            rgb = np.asarray(image.convert("RGB"))
        if rgb.shape != (height, width, 3):
            raise ValueError("Processed image dimensions do not match depth")
        colors[i] = rgb
    valid = (mask & np.isfinite(depth) & (depth > 0) & np.isfinite(confidence)
             & np.isfinite(points).all(axis=-1))
    if not valid.any():
        raise ValueError("No finite positive depth in valid image regions")
    # Verify the original published rows against the recovered depth/image data.
    with np.load(source_run / "pointcloud.npz", allow_pickle=False) as cloud:
        reference_indices = cloud["source_flat_index"]
    if (reference_indices.shape != (len(reference_points),) or reference_indices.dtype.kind not in "iu"
            or (reference_indices < 0).any() or (reference_indices >= depth.size).any()):
        raise ValueError("Invalid source pixel indices")
    flat_points, flat_colors = points.reshape(-1, 3), colors.reshape(-1, 3)
    if (flat_points[reference_indices].tobytes() != reference_points.tobytes()
            or flat_colors[reference_indices].tobytes() != reference_colors.tobytes()):
        raise ValueError("Recovered XYZ/RGB do not reproduce the reference point cloud")
    threshold = float(np.percentile(confidence[valid], percentile))
    selected = np.flatnonzero(valid & (confidence >= threshold))
    if not len(selected):
        raise ValueError("No points passed the confidence threshold")
    return flat_points[selected], flat_colors[selected], {
        "geometry_source": "depth_unprojection",
        "confidence_percentile": percentile,
        "confidence_threshold": threshold,
        "valid_point_count": int(valid.sum()),
        "point_cap": None,
        "reference_point_count": len(reference_points),
        "reference_points_retained": int(np.isin(reference_indices, selected, assume_unique=True).sum()),
        "source_files_sha256": hashes,
    }


def export(source_run, output, confidence_percentile=None):
    source_run = source_run.resolve()
    output = output.resolve()
    if output == source_run or source_run in output.parents:
        raise ValueError("Output must be outside the source run")
    if output.suffix != ".ply":
        raise ValueError("Output must have a .ply extension")
    source = source_run / "pointcloud.npz"
    source_hash = sha256(source)
    summary = json.loads((source_run / "run_summary.json").read_text())
    transforms = json.loads((source_run / "transforms.json").read_text())
    if summary.get("status") != "complete":
        raise ValueError("Source run is not complete")
    if transforms.get("world_from_vggt") != "identity":
        raise ValueError("Expected world_from_vggt=identity")
    with np.load(source, allow_pickle=False) as data:
        points = data["points_world_cv"]
        colors = data["colors_rgb"]
        cameras = data["camera_to_world_cv"]
    if points.dtype.kind != "f" or points.dtype.itemsize != 4:
        raise ValueError("points_world_cv must be float32")
    if points.ndim != 2 or points.shape[1] != 3 or not len(points):
        raise ValueError("points_world_cv must be nonempty Nx3")
    if not np.isfinite(points).all():
        raise ValueError("Point coordinates must be finite")
    if colors.dtype != np.uint8 or colors.shape != points.shape:
        raise ValueError("colors_rgb must be uint8 Nx3 matching the points")
    count = len(points)
    recorded_count = summary.get("point_counts", {}).get("exported")
    if type(recorded_count) is not int or recorded_count != count:
        raise ValueError("Recorded exported point count does not match")
    if cameras.ndim != 3 or cameras.shape[1:] != (4, 4) or not len(cameras):
        raise ValueError("camera_to_world_cv must contain 4x4 matrices")
    camera = cameras[0]
    if not np.isfinite(camera).all() or not np.allclose(camera[3], [0, 0, 0, 1]):
        raise ValueError("Invalid first camera transform")
    rotation = camera[:3, :3]
    if not np.allclose(rotation.T @ rotation, np.eye(3), atol=1e-5) or not np.isclose(np.linalg.det(rotation), 1):
        raise ValueError("First camera must contain a proper rotation")

    recovery = None
    if confidence_percentile is not None:
        points, colors, recovery = reconstruct(source_run, confidence_percentile, points, colors, cameras)
        count = len(points)

    vertices = np.empty(count, dtype=VERTEX_DTYPE)
    for i, field in enumerate(("x", "y", "z")):
        vertices[field] = points[:, i]
    for i, field in enumerate(("red", "green", "blue")):
        vertices[field] = colors[:, i]
    header = ("ply\nformat binary_little_endian 1.0\n"
              f"element vertex {count}\n"
              "property float x\nproperty float y\nproperty float z\n"
              "property uchar red\nproperty uchar green\nproperty uchar blue\nend_header\n").encode("ascii")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=output.parent, delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(header)
            vertices.tofile(handle)
        # Read the actual exported bytes back, including order, before publishing.
        exported = np.fromfile(temporary, dtype=VERTEX_DTYPE, offset=len(header))
        for i, field in enumerate(("x", "y", "z")):
            if exported[field].tobytes() != points[:, i].astype("<f4").tobytes():
                raise ValueError("XYZ round-trip verification failed")
        for i, field in enumerate(("red", "green", "blue")):
            if not np.array_equal(exported[field], colors[:, i]):
                raise ValueError("RGB round-trip verification failed")
        if sha256(source) != source_hash:
            raise ValueError("Source changed during export")
        if recovery:
            for relative, expected in recovery["source_files_sha256"].items():
                if sha256(source_run / relative) != expected:
                    raise ValueError(f"Source changed during export: {relative}")
        manifest = {
            "source_run": source_run.name,
            "source_sha256": source_hash,
            "ply_sha256": sha256(temporary),
            "point_count": count,
            "byte_length": temporary.stat().st_size,
            "world_from_vggt": "identity",
            "initial_camera": {
                "position": camera[:3, 3].tolist(),
                "forward": rotation[:, 2].tolist(),
                "up": (-rotation[:, 1]).tolist(),
            },
        }
        if recovery:
            manifest["reconstruction"] = recovery
        temporary.chmod(0o644)
        temporary.replace(output)
        output.with_suffix(".json").write_text(json.dumps(manifest, indent=2) + "\n")
        return manifest
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--confidence-percentile", type=float,
                        help="Rebuild from saved depth at this percentile, with no point cap")
    args = parser.parse_args()
    try:
        manifest = export(args.source_run, args.output, args.confidence_percentile)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Export failed: {error}", file=sys.stderr)
        return 1
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
