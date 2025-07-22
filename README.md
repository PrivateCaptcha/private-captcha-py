# private-captcha-py

Python client for server-side verification of Private Captcha solutions.

## Installation

```bash
pip install private-captcha-py
```

## Quick Start

```python
from private_captcha import Client

# Initialize the client with your API key
client = Client(api_key="your-api-key-here")

# Verify a captcha solution
try:
    result = client.verify(solution="user-solution-from-frontend")
    if result.success:
        print("Captcha verified successfully!")
    else:
        print(f"Verification failed: {result}")
except Exception as e:
    print(f"Error: {e}")
```

## Usage

### Basic Verification

```python
from private_captcha import Client, SolutionError

client = Client(api_key="your-api-key")

try:
    result = client.verify("captcha-solution-string")
    
    if result.success:
        # Captcha is valid, proceed with your logic
        print("Human verified!")
    else:
        # Captcha failed verification
        print(f"Verification failed with code: {result.code}")
        
except SolutionError as e:
    # Handle captcha-specific errors
    print(f"Solution error: {e}")
except Exception as e:
    # Handle other errors (network, API, etc.)
    print(f"Unexpected error: {e}")
```

### Web Framework Integration

#### Flask Example

```python
from flask import Flask, request
from private_captcha import Client, SolutionError

app = Flask(__name__)
client = Client(api_key="your-api-key")

@app.route('/submit', methods=['POST'])
def submit_form():
    try:
        # Verify captcha from form data
        client.verify_request(request.form)
        
        # Process your form data here
        return "Form submitted successfully!"
        
    except SolutionError:
        return "Captcha verification failed", 400
```

#### Django Example

```python
from django.http import HttpResponse
from private_captcha import Client, SolutionError

client = Client(api_key="your-api-key")

def submit_view(request):
    if request.method == 'POST':
        try:
            client.verify_request(request.POST)
            # Process form data
            return HttpResponse("Success!")
        except SolutionError:
            return HttpResponse("Captcha failed", status=400)
```

## Configuration

### Client Options

```python
from private_captcha import Client

client = Client(
    api_key="your-api-key",
    domain="api.privatecaptcha.com",  # or "api.eu.privatecaptcha.com" for EU
    form_field="private-captcha-solution",  # custom form field name
    timeout=10.0,  # request timeout in seconds
    failed_status_code=403  # HTTP status for middleware failures
)
```

### Regional Domains

```python
# Use EU domain
eu_client = Client(
    api_key="your-api-key",
    domain="api.eu.privatecaptcha.com"
)

# Or specify custom domain
custom_client = Client(
    api_key="your-api-key", 
    domain="your-custom-domain.com"
)
```

### Retry Configuration

```python
result = client.verify(
    solution="captcha-solution",
    max_backoff_seconds=15,  # maximum wait between retries
    attempts=3  # number of retry attempts
)
```

## Error Handling

The library provides specific exception types for different error scenarios:

```python
from private_captcha import (
    Client, 
    APIKeyError, 
    SolutionError, 
    VerificationFailedError
)

try:
    client = Client(api_key="")  # Empty API key
except APIKeyError:
    print("Invalid API key provided")

try:
    result = client.verify("")  # Empty solution
except SolutionError:
    print("Invalid or empty captcha solution")

try:
    result = client.verify("solution", attempts=3)
except VerificationFailedError as e:
    print(f"Failed after {e.attempts} attempts")
```

## Response Objects

The `verify()` method returns a `VerifyOutput` object with the following properties:

```python
result = client.verify("solution")

print(result.success)      # bool: True if verification succeeded
print(result.code)         # VerifyCode: Specific result code
print(result.origin)       # str: Origin domain (if available)
print(result.timestamp)    # str: Verification timestamp
print(result.request_id)   # str: Request ID for debugging
```

### Verification Codes

- `NO_ERROR` (0): Success
- `ERROR_OTHER` (1): General error
- `DUPLICATE_SOLUTIONS_ERROR` (2): Solution already used
- `INVALID_SOLUTION_ERROR` (3): Invalid solution format
- `PARSE_RESPONSE_ERROR` (4): Malformed response
- `PUZZLE_EXPIRED_ERROR` (5): Puzzle has expired
- `INVALID_PROPERTY_ERROR` (6): Invalid puzzle property
- `WRONG_OWNER_ERROR` (7): Site key mismatch
- `VERIFIED_BEFORE_ERROR` (8): Already verified
- `MAINTENANCE_MODE_ERROR` (9): Service maintenance
- `TEST_PROPERTY_ERROR` (10): Test environment
- `INTEGRITY_ERROR` (11): Data integrity issue

## Requirements

- Python 3.7+
- No external dependencies (uses only standard library)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues with this Python client, please open an issue on GitHub.
For Private Captcha service questions, visit [privatecaptcha.com](https://privatecaptcha.com).
