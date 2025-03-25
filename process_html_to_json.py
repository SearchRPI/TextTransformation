import socket
import json
import threading
import re
from bs4 import BeautifulSoup
from collections import defaultdict

HOST = 'localhost'
LISTEN_PORT = 9001       # Receives HTML from crawler
FORWARD_HOST = 'localhost'
FORWARD_PORT = 9002      # Sends word data to C++ indexer

TAG_PRIORITY = {
    "title": 5,
    "h1": 4,
    "h2": 3,
    "h3": 2,
    "p": 1,
    "div": 0.5,
    "span": 0.3
}

def extract_tagged_words(html):
    soup = BeautifulSoup(html, "html.parser")
    word_info = {}

    for tag in soup.find_all(True):  # all tags
        tag_name = tag.name.lower()
        if tag_name not in TAG_PRIORITY:
            continue

        text = tag.get_text(separator=" ")
        words = re.findall(r'\b[a-zA-Z0-9]{2,}\b', text.lower())

        for word in words:
            if word not in word_info:
                word_info[word] = {"count": 0, "tag": tag_name}
            word_info[word]["count"] += 1

            # Update tag if this tag is more important
            current_priority = TAG_PRIORITY.get(word_info[word]["tag"], 0)
            new_priority = TAG_PRIORITY.get(tag_name, 0)
            if new_priority > current_priority:
                word_info[word]["tag"] = tag_name

    return word_info

def forward_to_indexer(message):
    try:
        with socket.create_connection((FORWARD_HOST, FORWARD_PORT)) as s:
            s.sendall((json.dumps(message) + "\n").encode())
    except Exception as e:
        print(f"[!] Failed to forward to indexer: {e}")

def handle_client(conn, addr):
    with conn:
        try:
            data = b""
            while True:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                data += chunk
                if b"\n" in chunk:
                    break

            entry = json.loads(data.decode())
            url = entry["url"]
            html = entry["html"]

            word_data = extract_tagged_words(html)
            if word_data:
                message = {
                    "url": url,
                    "words": word_data
                }
                forward_to_indexer(message)

        except Exception as e:
            print(f"[!] Error processing from {addr}: {e}")

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, LISTEN_PORT))
        server.listen()
        print(f"[✓] Text Transformer listening on {HOST}:{LISTEN_PORT}")

        while True:
            conn, addr = server.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    start_server()
