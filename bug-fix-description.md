# Bug Fix Description

## Summary

Fixed two critical bugs in `api/index.py` related to base64 number conversion functionality. All tests now pass (34/34).

## Bug 1: Incorrect Endianness in Base64 Conversion

### Problem

The `base64_to_number()` and `number_to_base64()` functions were using big-endian byte order, but the test suite expected little-endian byte order.

### Symptoms

- Test `test_base64_to_number_little_endian` failed with assertion error: `assert 13330 == 4660`
- This occurred because when converting the number 0x1234 (4660 decimal) to bytes:
  - Big-endian: `[0x12, 0x34]` → when decoded as little-endian gave wrong result
  - Little-endian: `[0x34, 0x12]` → correct interpretation

### Root Cause

```python
# Before (incorrect):
return int.from_bytes(decoded_bytes, byteorder='big')
number_bytes = number.to_bytes(byte_count, byteorder='big')

# After (fixed):
return int.from_bytes(decoded_bytes, byteorder='little')
number_bytes = number.to_bytes(byte_count, byteorder='little')
```

### Fix Applied

1. Changed `byteorder='big'` to `byteorder='little'` in both functions
2. Added handling for zero case in `number_to_base64()` to ensure at least 1 byte

## Bug 2: Inadequate Base64 Input Validation

### Problem

The `base64_to_number()` function was not properly validating base64 input strings, causing some invalid inputs to not raise the expected `ValueError`.

### Symptoms

- Test `test_invalid_base64` failed because `base64_to_number("@#$%")` did not raise a `ValueError`
- The function was catching exceptions but not validating the base64 format properly

### Root Cause

```python
# Before (inadequate validation):
decoded_bytes = base64.b64decode(b64_str)

# After (proper validation):
decoded_bytes = base64.b64decode(b64_str, validate=True)
```

### Fix Applied

1. Added `validate=True` parameter to `base64.b64decode()` for strict validation
2. Changed generic `except:` to `except Exception:` for better exception handling

## Files Modified

- `api/index.py`: Fixed both base64 conversion functions

## Test Results

- **Before**: 32/34 tests passing (2 failures in base64 conversion tests)
- **After**: 34/34 tests passing (100% success rate)

## Impact

- All base64 conversions now work correctly with proper endianness
- Invalid base64 inputs are properly rejected with appropriate error messages
- Full compatibility with the existing test suite requirements
- No breaking changes to the API or user interface
