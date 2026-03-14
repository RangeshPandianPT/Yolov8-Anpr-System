import unittest
from fastapi.testclient import TestClient

import server.main as main_module


class StubPipeline:
    def process_image(self, _image_path):
        return {
            "status": "success",
            "predicted_plate": "MH12AB1234",
            "is_authorized": True,
            "best_match_db": "MH12AB1234",
            "distance": 0,
            "detection_confidence": 0.95,
            "detection_bbox": [10, 20, 100, 60],
            "processing_time_sec": 0.01,
        }


class TestANPRApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._original_pipeline = main_module.pipeline
        cls.client = TestClient(main_module.app)

    @classmethod
    def tearDownClass(cls):
        main_module.pipeline = cls._original_pipeline

    def setUp(self):
        main_module.pipeline = StubPipeline()

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "ok")
        self.assertIn("version", body)

    def test_ready(self):
        response = self.client.get("/ready")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["pipeline_initialized"])

    def test_rejects_non_image_upload(self):
        response = self.client.post(
            "/api/verify",
            files={"file": ("note.txt", b"not-an-image", "text/plain")},
        )
        self.assertEqual(response.status_code, 400)

    def test_verify_success(self):
        response = self.client.post(
            "/api/verify",
            files={"file": ("vehicle.jpg", b"mock-bytes", "image/jpeg")},
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "success")
        self.assertEqual(body["predicted_plate"], "MH12AB1234")
        self.assertTrue(body["is_authorized"])


if __name__ == "__main__":
    unittest.main()
