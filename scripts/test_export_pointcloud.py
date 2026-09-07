"""Validate lossless conversion and rejection of invalid source runs."""
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from export_pointcloud import export


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "run"
        self.source.mkdir()
        self.output = self.root / "web" / "points.ply"
        self.points = np.array([[1.25, -2, 3], [-0.0, 0, 1e-20], [9, 8, 7]], dtype=np.float32)
        self.colors = np.array([[0, 255, 128], [1, 2, 3], [230, 120, 10]], dtype=np.uint8)
        self.cameras = np.eye(4)[None]
        self.summary = {"status": "complete", "point_counts": {"exported": 3}}
        self.transforms = {"world_from_vggt": "identity"}
        self.save()

    def save(self):
        np.savez(self.source / "pointcloud.npz", points_world_cv=self.points,
                 colors_rgb=self.colors, camera_to_world_cv=self.cameras)
        (self.source / "run_summary.json").write_text(json.dumps(self.summary))
        (self.source / "transforms.json").write_text(json.dumps(self.transforms))

    def rejected(self):
        self.save()
        with self.assertRaises(ValueError):
            export(self.source, self.output)
        self.assertFalse(self.output.exists())

    def test_exact_bytes_and_order(self):
        original = (self.source / "pointcloud.npz").read_bytes()
        metadata = export(self.source, self.output)
        header, payload = self.output.read_bytes().split(b"end_header\n", 1)
        self.assertIn(b"format binary_little_endian 1.0", header)
        self.assertIn(b"element vertex 3", header)
        rows = np.frombuffer(payload, dtype=[("xyz", "<f4", (3,)), ("rgb", "u1", (3,))])
        self.assertEqual(rows["xyz"].tobytes(), self.points.tobytes())
        self.assertEqual(rows["rgb"].tobytes(), self.colors.tobytes())
        self.assertEqual(len(payload), 3 * 15)
        self.assertEqual((self.source / "pointcloud.npz").read_bytes(), original)
        self.assertEqual(metadata["initial_camera"]["up"], [0, -1, 0])

    def test_incomplete_run(self):
        self.summary["status"] = "running"
        self.rejected()

    def test_wrong_count(self):
        self.summary["point_counts"]["exported"] = 4
        self.rejected()

    def test_nonfinite(self):
        self.points[1, 1] = np.nan
        self.rejected()

    def test_wrong_xyz_dtype(self):
        self.points = self.points.astype(np.float64)
        self.rejected()

    def test_wrong_rgb_dtype(self):
        self.colors = self.colors.astype(np.float32)
        self.rejected()

    def test_mismatched_rgb(self):
        self.colors = self.colors[:2]
        self.rejected()

    def test_empty_cloud(self):
        self.points = self.points[:0]
        self.colors = self.colors[:0]
        self.rejected()

    def test_nonidentity_world(self):
        self.transforms["world_from_vggt"] = "other"
        self.rejected()

    def test_bad_camera(self):
        self.cameras[0, 0, 0] = 2
        self.rejected()

    def test_source_cannot_be_overwritten(self):
        with self.assertRaises(ValueError):
            export(self.source, self.source / "pointcloud.ply")

    def test_js_metadata_without_json_sidecar(self):
        metadata_output = self.root / "web/reconstruction-data.js"
        manifest = export(self.source, self.output, metadata_output)
        encoded = metadata_output.read_text().split(" = ", 1)[1].rstrip(";\n")
        self.assertEqual(json.loads(encoded), manifest)
        self.assertFalse(self.output.with_suffix(".json").exists())

    def test_metadata_cannot_overwrite_source(self):
        with self.assertRaises(ValueError):
            export(self.source, self.output, self.source / "run_summary.json")
        self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()
