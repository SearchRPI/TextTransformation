import os
import json
import pytest
from process_html_to_json import process_html_to_json

# Collect test cases based on available files in test_data
test_data_dir = os.path.join(os.path.dirname(__file__), "test_data")
test_cases = [
    (os.path.join(test_data_dir, f"{name}.html"), os.path.join(test_data_dir, f"{name}.json"))
    for name in {
        os.path.splitext(file)[0]
        for file in os.listdir(test_data_dir)
        if file.endswith(".html")
    }
]

@pytest.mark.parametrize("input_file, expected_file", test_cases, ids=[os.path.basename(tc[0]).replace('.html', '') for tc in test_cases])
def test_process_html(input_file, expected_file):
    """
    Test process_html_to_json with multiple test cases defined in test_data.
    Each test case consists of an input HTML file and an expected JSON output file.
    """
    output_file = input_file.replace(".html", "_output.json")  # Temporary output file
    
    # Run the function
    process_html_to_json(input_file, output_file)
    
    # Read the actual output
    with open(output_file, "r") as f:
        actual_output = json.load(f)
    
    # Read the expected output
    with open(expected_file, "r") as f:
        expected_output = json.load(f)
    
    # Assert that the actual output matches the expected output
    assert actual_output == expected_output, f"Test case failed for {os.path.basename(input_file)}"
    
    # Clean up the output file
    os.remove(output_file)
