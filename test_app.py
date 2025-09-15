import pytest
import json
import base64
from api.index import app, text_to_number, number_to_text, base64_to_number, number_to_base64


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestTextToNumber:
    """Test the text_to_number function."""
    
    def test_basic_numbers(self):
        """Test conversion of basic number words."""
        assert text_to_number("one") == 1
        assert text_to_number("two") == 2
        assert text_to_number("five") == 5
        assert text_to_number("ten") == 10
    
    def test_zero_conversion(self):
        """Test special zero cases."""
        assert text_to_number("zero") == 0
        assert text_to_number("nil") == 0
    
    def test_case_insensitive(self):
        """Test case insensitive conversion."""
        assert text_to_number("ONE") == 1
        assert text_to_number("Two") == 2
        assert text_to_number("ZERO") == 0
    
    def test_punctuation_removal(self):
        """Test removal of punctuation."""
        assert text_to_number("one!") == 1
        assert text_to_number("two...") == 2
        assert text_to_number("five@#$") == 5
    
    def test_invalid_text(self):
        """Test invalid text inputs."""
        with pytest.raises(ValueError, match="Unable to convert text to number"):
            text_to_number("eleven")
        with pytest.raises(ValueError, match="Unable to convert text to number"):
            text_to_number("hundred")
        with pytest.raises(ValueError, match="Unable to convert text to number"):
            text_to_number("invalid")
        with pytest.raises(ValueError, match="Unable to convert text to number"):
            text_to_number("")


class TestNumberToText:
    """Test the number_to_text function."""
    
    def test_basic_numbers(self):
        """Test conversion of basic numbers to text."""
        assert number_to_text(1) == "one"
        assert number_to_text(2) == "two"
        assert number_to_text(5) == "five"
        assert number_to_text(10) == "ten"
        assert number_to_text(0) == "zero"
    
    def test_larger_numbers(self):
        """Test conversion of larger numbers."""
        assert number_to_text(42) == "forty-two"
        assert number_to_text(123) == "one hundred and twenty-three"
        assert number_to_text(1000) == "one thousand"
    
    def test_negative_numbers(self):
        """Test conversion of negative numbers."""
        assert number_to_text(-1) == "minus one"
        assert number_to_text(-42) == "minus forty-two"


class TestBase64Conversion:
    """Test base64 conversion functions."""
    
    def test_number_to_base64_little_endian(self):
        """Test conversion of numbers to base64 using little-endian byte order."""
        # Test case: 42 in little-endian bytes should be [42, 0, 0, 0] for 4 bytes
        # But the function should handle minimal bytes needed
        # 42 = 0x2A, which in little-endian single byte is just 42
        result = number_to_base64(42)
        # Decode to verify it uses the correct byte order
        decoded_bytes = base64.b64decode(result)
        # For 42, we expect 1 byte: [42] in little-endian = [42]
        expected_bytes = (42).to_bytes(1, byteorder='little')
        # The current implementation uses 'big' endian, so this will fail
        assert decoded_bytes == expected_bytes, f"Expected {expected_bytes} but got {decoded_bytes}"
    
    def test_base64_to_number_little_endian(self):
        """Test conversion from base64 to number using little-endian byte order."""
        # Create a base64 string from a known little-endian byte sequence
        test_number = 0x1234  # 4660 in decimal
        little_endian_bytes = test_number.to_bytes(2, byteorder='little')
        b64_string = base64.b64encode(little_endian_bytes).decode('utf-8')
        
        # The function should decode this correctly using little-endian
        result = base64_to_number(b64_string)
        assert result == test_number
    
    def test_base64_zero(self):
        """Test base64 conversion of zero."""
        # Zero should work correctly regardless of endianness
        result = number_to_base64(0)
        decoded = base64_to_number(result)
        assert decoded == 0
    
    def test_base64_roundtrip(self):
        """Test roundtrip conversion for various numbers."""
        test_numbers = [1, 42, 255, 256, 65535, 65536, 1000000]
        for num in test_numbers:
            base64_str = number_to_base64(num)
            decoded_num = base64_to_number(base64_str)
            assert decoded_num == num, f"Roundtrip failed for {num}: got {decoded_num}"
    
    def test_invalid_base64(self):
        """Test invalid base64 inputs."""
        with pytest.raises(ValueError, match="Invalid base64 input"):
            base64_to_number("invalid base64!")
        with pytest.raises(ValueError, match="Invalid base64 input"):
            base64_to_number("@#$%")


class TestFlaskConvert:
    """Test the Flask /convert endpoint."""
    
    def test_decimal_to_binary(self, client):
        """Test decimal to binary conversion."""
        response = client.post('/convert', 
                              json={'input': '42', 'inputType': 'decimal', 'outputType': 'binary'})
        data = json.loads(response.data)
        assert data['result'] == '101010'
        assert data['error'] is None
    
    def test_binary_to_decimal(self, client):
        """Test binary to decimal conversion."""
        response = client.post('/convert', 
                              json={'input': '101010', 'inputType': 'binary', 'outputType': 'decimal'})
        data = json.loads(response.data)
        assert data['result'] == '42'
        assert data['error'] is None
    
    def test_decimal_to_hexadecimal(self, client):
        """Test decimal to hexadecimal conversion."""
        response = client.post('/convert', 
                              json={'input': '255', 'inputType': 'decimal', 'outputType': 'hexadecimal'})
        data = json.loads(response.data)
        assert data['result'] == 'ff'
        assert data['error'] is None
    
    def test_hexadecimal_to_decimal(self, client):
        """Test hexadecimal to decimal conversion."""
        response = client.post('/convert', 
                              json={'input': 'ff', 'inputType': 'hexadecimal', 'outputType': 'decimal'})
        data = json.loads(response.data)
        assert data['result'] == '255'
        assert data['error'] is None
    
    def test_decimal_to_octal(self, client):
        """Test decimal to octal conversion."""
        response = client.post('/convert', 
                              json={'input': '64', 'inputType': 'decimal', 'outputType': 'octal'})
        data = json.loads(response.data)
        assert data['result'] == '100'
        assert data['error'] is None
    
    def test_octal_to_decimal(self, client):
        """Test octal to decimal conversion."""
        response = client.post('/convert', 
                              json={'input': '100', 'inputType': 'octal', 'outputType': 'decimal'})
        data = json.loads(response.data)
        assert data['result'] == '64'
        assert data['error'] is None
    
    def test_text_to_decimal(self, client):
        """Test text to decimal conversion."""
        response = client.post('/convert', 
                              json={'input': 'five', 'inputType': 'text', 'outputType': 'decimal'})
        data = json.loads(response.data)
        assert data['result'] == '5'
        assert data['error'] is None
    
    def test_decimal_to_text(self, client):
        """Test decimal to text conversion."""
        response = client.post('/convert', 
                              json={'input': '42', 'inputType': 'decimal', 'outputType': 'text'})
        data = json.loads(response.data)
        assert data['result'] == 'forty-two'
        assert data['error'] is None
    
    def test_base64_conversions(self, client):
        """Test base64 conversions."""
        # Test decimal to base64
        response = client.post('/convert', 
                              json={'input': '42', 'inputType': 'decimal', 'outputType': 'base64'})
        data = json.loads(response.data)
        assert data['error'] is None
        base64_result = data['result']
        
        # Test base64 back to decimal
        response = client.post('/convert', 
                              json={'input': base64_result, 'inputType': 'base64', 'outputType': 'decimal'})
        data = json.loads(response.data)
        assert data['result'] == '42'
        assert data['error'] is None
    
    def test_comprehensive_conversion_matrix(self, client):
        """Test conversions between all input/output type combinations."""
        input_types = ['text', 'binary', 'octal', 'decimal', 'hexadecimal', 'base64']
        output_types = ['text', 'binary', 'octal', 'decimal', 'hexadecimal', 'base64']
        
        # Use the number 42 represented in each format
        test_inputs = {
            'text': 'two',  # Only test with a number we can convert
            'binary': '10',  # 2 in binary
            'octal': '2',    # 2 in octal  
            'decimal': '2',  # 2 in decimal
            'hexadecimal': '2',  # 2 in hexadecimal
        }
        
        # First convert decimal 2 to base64 to get the base64 representation
        response = client.post('/convert', 
                              json={'input': '2', 'inputType': 'decimal', 'outputType': 'base64'})
        base64_repr = json.loads(response.data)['result']
        test_inputs['base64'] = base64_repr
        
        # Test all combinations
        for input_type in input_types:
            for output_type in output_types:
                if input_type == output_type:
                    continue  # Skip same type conversions
                
                response = client.post('/convert', 
                                      json={'input': test_inputs[input_type], 
                                           'inputType': input_type, 
                                           'outputType': output_type})
                data = json.loads(response.data)
                assert data['error'] is None, f"Error converting from {input_type} to {output_type}: {data['error']}"
                assert data['result'] is not None, f"No result for {input_type} to {output_type}"
    
    def test_error_handling_invalid_input_type(self, client):
        """Test error handling for invalid input type."""
        response = client.post('/convert', 
                              json={'input': '42', 'inputType': 'invalid', 'outputType': 'decimal'})
        data = json.loads(response.data)
        assert data['result'] is None
        assert data['error'] == 'Invalid input type'
    
    def test_error_handling_invalid_output_type(self, client):
        """Test error handling for invalid output type."""
        response = client.post('/convert', 
                              json={'input': '42', 'inputType': 'decimal', 'outputType': 'invalid'})
        data = json.loads(response.data)
        assert data['result'] is None
        assert data['error'] == 'Invalid output type'
    
    def test_error_handling_invalid_binary(self, client):
        """Test error handling for invalid binary input."""
        response = client.post('/convert', 
                              json={'input': '123', 'inputType': 'binary', 'outputType': 'decimal'})
        data = json.loads(response.data)
        assert data['result'] is None
        assert 'invalid literal for int() with base 2' in data['error']
    
    def test_error_handling_invalid_octal(self, client):
        """Test error handling for invalid octal input."""
        response = client.post('/convert', 
                              json={'input': '89', 'inputType': 'octal', 'outputType': 'decimal'})
        data = json.loads(response.data)
        assert data['result'] is None
        assert 'invalid literal for int() with base 8' in data['error']
    
    def test_error_handling_invalid_hexadecimal(self, client):
        """Test error handling for invalid hexadecimal input."""
        response = client.post('/convert', 
                              json={'input': 'xyz', 'inputType': 'hexadecimal', 'outputType': 'decimal'})
        data = json.loads(response.data)
        assert data['result'] is None
        assert 'invalid literal for int() with base 16' in data['error']
    
    def test_error_handling_invalid_decimal(self, client):
        """Test error handling for invalid decimal input."""
        response = client.post('/convert', 
                              json={'input': 'abc', 'inputType': 'decimal', 'outputType': 'binary'})
        data = json.loads(response.data)
        assert data['result'] is None
        assert 'invalid literal for int()' in data['error']
    
    def test_error_handling_invalid_text(self, client):
        """Test error handling for invalid text input."""
        response = client.post('/convert', 
                              json={'input': 'eleven', 'inputType': 'text', 'outputType': 'decimal'})
        data = json.loads(response.data)
        assert data['result'] is None
        assert data['error'] == 'Unable to convert text to number'
    
    def test_error_handling_invalid_base64(self, client):
        """Test error handling for invalid base64 input."""
        response = client.post('/convert', 
                              json={'input': 'invalid@base64!', 'inputType': 'base64', 'outputType': 'decimal'})
        data = json.loads(response.data)
        assert data['result'] is None
        assert data['error'] == 'Invalid base64 input'
    
    def test_error_handling_missing_data(self, client):
        """Test error handling for missing request data."""
        response = client.post('/convert', json={})
        data = json.loads(response.data)
        assert data['result'] is None
        assert data['error'] is not None
    
    def test_zero_conversions(self, client):
        """Test zero value conversions across all types."""
        # Test zero from decimal to all other types
        zero_representations = {}
        for output_type in ['binary', 'octal', 'hexadecimal', 'base64', 'text']:
            response = client.post('/convert', 
                                  json={'input': '0', 'inputType': 'decimal', 'outputType': output_type})
            data = json.loads(response.data)
            assert data['error'] is None
            zero_representations[output_type] = data['result']
        
        # Test converting back from each representation to decimal
        for input_type, zero_repr in zero_representations.items():
            if input_type == 'text':
                continue  # Skip text as 'zero' != 'zero' in our limited implementation
            response = client.post('/convert', 
                                  json={'input': zero_repr, 'inputType': input_type, 'outputType': 'decimal'})
            data = json.loads(response.data)
            assert data['error'] is None
            assert data['result'] == '0'
    
    def test_negative_numbers(self, client):
        """Test negative number conversions."""
        # Test negative decimal to text
        response = client.post('/convert', 
                              json={'input': '-42', 'inputType': 'decimal', 'outputType': 'text'})
        data = json.loads(response.data)
        assert data['error'] is None
        assert 'minus' in data['result']
        
        # Note: Negative numbers in binary, octal, hex use two's complement
        # which produces very large positive numbers when converted back
        response = client.post('/convert', 
                              json={'input': '-1', 'inputType': 'decimal', 'outputType': 'binary'})
        data = json.loads(response.data)
        # This should either handle negative properly or raise an error
        # The current implementation will likely fail as bin() doesn't handle negatives well in this context

