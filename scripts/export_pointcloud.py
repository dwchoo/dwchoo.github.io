#!/usr/bin/env python3
"""Export a completed VGGT run without filtering or changing point order."""

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


def export(source_run, output, metadata_output=None):
    source_run = source_run.resolve()
    output = output.resolve()
    if output == source_run or source_run in output.parents:
        raise ValueError("Output must be outside the source run")
    if output.suffix != ".ply":
        raise ValueError("Output must have a .ply extension")
    metadata_output = (metadata_output or output.with_suffix(".json")).resolve()
    if source_run == metadata_output or source_run in metadata_output.parents:
        raise ValueError("Metadata output must be outside the source run")
    if metadata_output.suffix not in (".json", ".js"):
        raise ValueError("Metadata output must have a .json or .js extension")
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
        temporary.chmod(0o644)
        temporary.replace(output)
        metadata_output.parent.mkdir(parents=True, exist_ok=True)
        metadata = json.dumps(manifest, indent=2)
        if metadata_output.suffix == ".js":
            metadata = "// Generated by scripts/export_pointcloud.py.\nexport const reconstruction = " + metadata + ";"
        metadata_output.write_text(metadata + "\n")
        return manifest
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--metadata-output", type=Path,
                        help="Optional .json or .js viewer metadata destination")
    args = parser.parse_args()
    try:
        manifest = export(args.source_run, args.output, args.metadata_output)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Export failed: {error}", file=sys.stderr)
        return 1
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
