import json
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import re

# Process the HTML file and write the information to a JSON
# TODO: Write the information to a database
# TODO: Store any additional information needed for the ranking algorithm
def process_html_to_json(html_file, output_file):
    with open(html_file, 'r') as f:
        contents = f.read()

    # Parse HTML
    soup = BeautifulSoup(contents, "html.parser")
    text = soup.get_text(separator=' ')

    # Normalize whitespace
    cleaned_text = re.sub(r'\s+', ' ', text)
    # Remove special characters
    cleaned_text = re.sub(r'[^a-zA-Z0-9\s]', '', cleaned_text)
    # Convert everything to lowercase
    cleaned_text = cleaned_text.lower()

    # Tokenize
    tokens = word_tokenize(cleaned_text)

    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token not in stop_words]

    # Stem the tokens
    stemmer = PorterStemmer()
    stemmed_tokens = [stemmer.stem(token) for token in tokens]

    # Create JSON of data
    output_data = {
        "stemmed_tokens": stemmed_tokens
    }

    # Write JSON to file
    with open(output_file, 'w') as json_file:
        json.dump(output_data, json_file, indent=4)
    print(f"Processed data written to {output_file}")
