"""Validate lossless conversion and rejection of invalid source runs."""
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from export_pointcloud import export
from export_pointcloud import sha256


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

    def save_reconstruction(self):
        from PIL import Image

        self.points = np.array([[10.5, -3.5, 3]], dtype=np.float32)
        rgb = np.arange(18, dtype=np.uint8).reshape(2, 3, 3)
        self.colors = rgb.reshape(-1, 3)[[5]]
        self.cameras[0, :3, 3] = [10, -4, 2]
        self.summary["point_counts"]["exported"] = 1
        self.save()
        np.savez(self.source / "pointcloud.npz", points_world_cv=self.points,
                 colors_rgb=self.colors, camera_to_world_cv=self.cameras,
                 source_flat_index=np.array([5], dtype=np.int64))
        self.predictions = {
            "depth": np.ones((1, 2, 3), dtype=np.float32),
            "depth_conf": np.arange(1, 7, dtype=np.float32).reshape(1, 2, 3),
            "valid_image_mask": np.array([[[False, True, True], [True, True, True]]]),
            "intrinsic": np.array([[[2, 0, 1], [0, 2, 0], [0, 0, 1]]], dtype=np.float32),
        }
        np.savez(self.source / "predictions.npz", **self.predictions)
        (self.source / "processed_images").mkdir()
        image = self.source / "processed_images/frame_0000.png"
        Image.fromarray(rgb).save(image)
        (self.source / "input_manifest.json").write_text(json.dumps({
            "frames": [{"processed_sha256": sha256(image)}],
        }))

    def test_recover_more_points_in_pixel_order(self):
        self.save_reconstruction()
        manifest = export(self.source, self.output, confidence_percentile=50)
        data = self.output.read_bytes().split(b"end_header\n", 1)[1]
        rows = np.frombuffer(data, dtype=[("xyz", "<f4", (3,)), ("rgb", "u1", (3,))])
        np.testing.assert_array_equal(rows["xyz"], [[9.5, -3.5, 3], [10, -3.5, 3], [10.5, -3.5, 3]])
        np.testing.assert_array_equal(rows["rgb"], [[9, 10, 11], [12, 13, 14], [15, 16, 17]])
        self.assertEqual(manifest["reconstruction"]["reference_points_retained"], 1)
        self.assertEqual(manifest["reconstruction"]["confidence_threshold"], 4)
        self.assertIsNone(manifest["reconstruction"]["point_cap"])

    def test_recovery_excludes_invalid_depth_and_padding(self):
        self.save_reconstruction()
        self.predictions["depth"][0, 0, 1] = 0
        self.predictions["depth"][0, 0, 2] = np.nan
        np.savez(self.source / "predictions.npz", **self.predictions)
        manifest = export(self.source, self.output, confidence_percentile=0)
        self.assertEqual(manifest["point_count"], 3)
        self.assertEqual(manifest["reconstruction"]["valid_point_count"], 3)

    def test_recovery_rejects_percentile_out_of_range(self):
        self.save_reconstruction()
        for percentile in [-1, 101, float("nan")]:
            with self.subTest(percentile=percentile), self.assertRaises(ValueError):
                export(self.source, self.output, confidence_percentile=percentile)

    def test_recovery_rejects_changed_processed_image(self):
        self.save_reconstruction()
        (self.source / "processed_images/frame_0000.png").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "checksum mismatch"):
            export(self.source, self.output, confidence_percentile=50)

    def test_recovery_rejects_wrong_depth_source(self):
        self.save_reconstruction()
        self.predictions["depth"][0, 1, 2] = 2
        np.savez(self.source / "predictions.npz", **self.predictions)
        with self.assertRaisesRegex(ValueError, "do not reproduce"):
            export(self.source, self.output, confidence_percentile=50)

    def test_recovery_rejects_bad_intrinsics(self):
        self.save_reconstruction()
        self.predictions["intrinsic"][0, 0, 0] = 0
        np.savez(self.source / "predictions.npz", **self.predictions)
        with self.assertRaisesRegex(ValueError, "intrinsics"):
            export(self.source, self.output, confidence_percentile=50)


if __name__ == "__main__":
    unittest.main()
