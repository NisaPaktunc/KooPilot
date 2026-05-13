from pyngrok import ngrok
import time
import sys

print("Starting ngrok...")
try:
    public_url = ngrok.connect(8000).public_url
    print("NGROK_URL: " + public_url)
    with open("ngrok_url.txt", "w") as f:
        f.write(public_url)
    while True:
        time.sleep(1)
except Exception as e:
    print("Error:", e)
    sys.exit(1)
