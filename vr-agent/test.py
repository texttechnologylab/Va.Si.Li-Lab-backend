import requests

# Dein Code auf dem Uni-Server
url = "http://vragent.lehre.texttechnologylab.org/chat"
data = {"id": "test", "message": "Hallo"}

response = requests.post(url, json=data)

print(f"Status: {response.status_code}")
# Hier steht der Grund für den Absturz (z.B. der 404-Link von vorhin)
print(f"Fehlermeldung vom Server: {response.text}")