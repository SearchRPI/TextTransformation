import json
import re
import os

CRAWLER_PIPE = "/tmp/crawler_pipe"
STEMMER_PIPE = "/tmp/stemmer_pipe"

def extract_words_from_html(html):
    """Extract words from HTML, ignoring scripts and styles."""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")

    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.extract()

    # Extract visible text and tokenize into words
    text = soup.get_text(separator=" ")
    words = re.findall(r'\b[a-zA-Z0-9]{2,}\b', text.lower())  # Extract words (at least 2 chars)
    return words

def send_to_cpp(words, url):
    """Send words + URL to the C++ program via named pipe."""
    try:
        with open(STEMMER_PIPE, "w") as pipe:
            message = f"{url}\n" + "\n".join(words) + "\nEND_OF_ENTRY\n"
            pipe.write(message)
    except Exception as e:
        print(f"Error writing to C++ pipe: {e}")

def process_continuous_input():
    """Continuously read from the crawler pipe and process data."""
    with open(CRAWLER_PIPE, "r") as pipe:
        while True:
            line = pipe.readline().strip()
            if not line:
                continue  # Skip empty lines

            try:
                entry = json.loads(line)
                url = entry["url"]
                html = entry["html"]

                # Extract words
                words = extract_words_from_html(html)
                if words:
                    send_to_cpp(words, url)

            except Exception as e:
                print(f"Error processing entry: {e}")

if __name__ == "__main__":
    # Ensure named pipes exist
    if not os.path.exists(CRAWLER_PIPE):
        os.mkfifo(CRAWLER_PIPE)
    if not os.path.exists(STEMMER_PIPE):
        os.mkfifo(STEMMER_PIPE)

    print("Listening for incoming web pages...")
    process_continuous_input()
