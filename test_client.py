import base64
import os
import unittest
import logging
import threading
from urllib import request
from urllib.error import URLError

from private_captcha import Client, SolutionError
from private_captcha.models import VerifyCode
from private_captcha.client import DEFAULT_FORM_FIELD


class TestPrivateCaptchaClient(unittest.TestCase):
    """Test suite for Private Captcha client."""

    SOLUTIONS_COUNT = 16
    SOLUTION_LENGTH = 8
    _cached_puzzle = None
    _puzzle_lock = threading.Lock()

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures that can be reused across tests."""
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

        cls.api_key = os.getenv("PC_API_KEY")
        if not cls.api_key:
            raise ValueError("PC_API_KEY environment variable not set")

    @classmethod
    def fetch_test_puzzle(cls) -> bytes:
        """Fetch a test puzzle from the API (cached after first call)."""
        if cls._cached_puzzle is not None:
            return cls._cached_puzzle

        with cls._puzzle_lock:
            if cls._cached_puzzle is not None:
                return cls._cached_puzzle

            puzzle_url = "https://api.privatecaptcha.com/puzzle?sitekey=aaaaaaaabbbbccccddddeeeeeeeeeeee"
            headers = {"Origin": "not.empty"}

            req = request.Request(puzzle_url, headers=headers)

            try:
                with request.urlopen(req) as response:
                    cls._cached_puzzle = response.read()
                    return cls._cached_puzzle
            except URLError as e:
                raise AssertionError(f"Failed to fetch test puzzle: {e}")

    def test_stub_puzzle(self):
        """Test verification with empty solutions (should fail with test property error)."""
        puzzle = self.fetch_test_puzzle()

        client = Client(api_key=self.api_key)

        # Create empty solutions
        empty_solutions_bytes = bytes(self.SOLUTIONS_COUNT * self.SOLUTION_LENGTH)
        solutions_str = base64.b64encode(empty_solutions_bytes).decode("ascii")
        payload = f"{solutions_str}.{puzzle.decode('ascii')}"

        output = client.verify(payload)

        # Should succeed but indicate test property error
        self.assertTrue(output.success)
        self.assertEqual(output.code, VerifyCode.TEST_PROPERTY_ERROR)

    def test_verify_error(self):
        """Test verification with malformed puzzle data."""
        puzzle = self.fetch_test_puzzle()

        client = Client(api_key=self.api_key)

        # Create malformed solutions (half the expected length)
        malformed_solutions_bytes = bytes(
            self.SOLUTIONS_COUNT * self.SOLUTION_LENGTH // 2
        )
        solutions_str = base64.b64encode(malformed_solutions_bytes).decode("ascii")
        payload = f"{solutions_str}.{puzzle.decode('ascii')}"

        output = client.verify(payload)

        # Should fail with parse response error
        self.assertFalse(output.success)
        self.assertEqual(output.code, VerifyCode.PARSE_RESPONSE_ERROR)

    def test_verify_empty_solution(self):
        """Test that empty solution raises SolutionError."""
        client = Client(api_key=self.api_key)

        with self.assertRaises(SolutionError):
            client.verify("")

    def test_retry_backoff(self):
        """Test retry logic with non-existent domain."""
        from private_captcha.exceptions import VerificationFailedError

        # Use a non-existent domain to trigger retries
        client = Client(
            api_key=self.api_key,
            domain="192.0.2.1:9999",  # Test IP that should be unreachable
            timeout=1.0,
        )

        # This should fail after multiple attempts
        with self.assertRaises(VerificationFailedError) as context:
            client.verify(solution="asdf", max_backoff_seconds=1, attempts=4)

        # Should have failed after 4 attempts
        self.assertEqual(context.exception.attempts, 4)

    def test_api_key_validation(self):
        """Test that empty API key raises APIKeyError."""
        from private_captcha.exceptions import APIKeyError

        with self.assertRaises(APIKeyError):
            Client(api_key="")

    def test_verify_request_success(self):
        """Test verify_request method with valid form data."""
        puzzle = self.fetch_test_puzzle()
        client = Client(api_key=self.api_key)

        # Create form data with empty solutions (will trigger test property error)
        empty_solutions_bytes = bytes(self.SOLUTIONS_COUNT * self.SOLUTION_LENGTH)
        solutions_str = base64.b64encode(empty_solutions_bytes).decode("ascii")
        payload = f"{solutions_str}.{puzzle.decode('ascii')}"

        form_data = {DEFAULT_FORM_FIELD: payload}

        # This should not raise an exception for test property (it's considered "success")
        try:
            client.verify_request(form_data)
        except SolutionError:
            self.fail("verify_request should not fail for test property error")

    def test_verify_request_failure(self):
        """Test verify_request method with invalid form data."""
        client = Client(api_key=self.api_key)

        # Test with malformed data
        form_data = {DEFAULT_FORM_FIELD: "invalid-solution"}

        with self.assertRaises(SolutionError):
            client.verify_request(form_data)

    def test_custom_form_field(self):
        """Test client with custom form field name."""
        CUSTOM_FORM_FIELD = "custom-field"
        puzzle = self.fetch_test_puzzle()
        client = Client(api_key=self.api_key, form_field=CUSTOM_FORM_FIELD)

        empty_solutions_bytes = bytes(self.SOLUTIONS_COUNT * self.SOLUTION_LENGTH)
        solutions_str = base64.b64encode(empty_solutions_bytes).decode("ascii")
        payload = f"{solutions_str}.{puzzle.decode('ascii')}"

        # Should look for the custom field name
        form_data = {CUSTOM_FORM_FIELD: payload}

        try:
            client.verify_request(form_data)
        except SolutionError:
            self.fail("verify_request should work with custom form field")

        default_client = Client(api_key=self.api_key)
        with self.assertRaises(SolutionError):
            default_client.verify_request(form_data)

    def test_eu_domain(self):
        """Test client with EU domain."""
        client = Client(api_key=self.api_key, domain="api.eu.privatecaptcha.com")

        self.assertIn("api.eu.privatecaptcha.com", client.endpoint)


if __name__ == "__main__":
    unittest.main()
