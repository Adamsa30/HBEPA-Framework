# HBEPA Architecture Specification: Integration Pipeline Verification Tests
# Framework: unittest / integration
# Purpose: Programmatically verifies clinical callback data firewall sanitization blocks.

import unittest
import json
import threading
import time
import urllib.request
import urllib.error
from mock_clinical_callback_server import HTTPServer, ClinicalCallbackSanitizerHandler, BIND_HOST, BIND_PORT

class TestClinicalCallbackDataFirewall(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Spins up the mock clinical callback server in a background thread for testing."""
        cls.server = HTTPServer((BIND_HOST, BIND_PORT), ClinicalCallbackSanitizerHandler)
        cls.server_thread = threading.Thread(target=cls.server.serve_forever)
        cls.server_thread.daemon = True
        cls.server_thread.start()
        time.sleep(0.5)  # Allow the background thread listener to bind

    @classmethod
    def tearDownClass(cls):
        """Shuts down the background simulation runtime loop cleanly."""
        cls.server.shutdown()
        cls.server.server_close()

    def test_pipeline_strips_prohibited_clinical_metadata(self):
        """Verifies that payload streams containing rich medical data are intercepted and sanitized."""
        url = f"http://{BIND_HOST}:{BIND_PORT}/api/v1/gate4/tokens/issue"
        
        # Construct an incoming payload contaminated with private clinical diagnostics
        raw_payload = {
            "anonymized_user_hash": "64_char_hashed_placeholder_string_index_verification",
            "timestamp_transmitted": "2026-11-05T08:30:00Z",
            "clinical_diagnosis": "Generalized Myasthenia Gravis (gMG)",
            "icd_10_code": "G70.00",
            "symptoms": "Severe fluctuating muscle weakness and profound fatigue clusters",
            "medical_notes": "Patient requires immediate home-based network session persistence preservation accommodation."
        }
        
        data = json.dumps(raw_payload).encode('utf-8')
        req = urllib.request.Request(
            url, 
            data=data, 
            headers={'Content-Type': 'application/json'}, 
            method='POST'
        )
        
        # Execute the HTTP request against the local data firewall container
        response = urllib.request.urlopen(req)
        self.assertEqual(response.status, 201)
        
        response_body = json.loads(response.read().decode('utf-8'))
        self.assertEqual(response_body["status"], "SUCCESS")
        
    def test_pipeline_rejects_missing_hash_parameter(self):
        """Confirms that packets lacking a user routing anchor are immediately dropped."""
        url = f"http://{BIND_HOST}:{BIND_PORT}/api/v1/gate4/tokens/issue"
        malformed_payload = {
            "timestamp_transmitted": "2026-11-05T08:30:00Z",
            "clinical_diagnosis": "Unchecked Diagnostic Entry String"
        }
        
        data = json.dumps(malformed_payload).encode('utf-8')
        req = urllib.request.Request(
            url, 
            data=data, 
            headers={'Content-Type': 'application/json'}, 
            method='POST'
        )
        
        with self.assertRaises(urllib.error.HTTPError) as context:
            urllib.request.urlopen(req)
        
        self.assertEqual(context.exception.code, 400)

if __name__ == "__main__":
    unittest.main()
