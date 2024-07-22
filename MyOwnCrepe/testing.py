import requests

def send_audio_file(file_path, server_url):
    with open(file_path, 'rb') as audio_file:
        files = {'audio': audio_file}
        response = requests.post(server_url, files=files)
        
        if response.status_code == 200:
            print("Response received successfully:")
            print(response.json())
        else:
            print(f"Failed to get a successful response: {response.status_code}")
            print(response.json())

if __name__ == "__main__":
    # Replace with the path to your audio file
    file_path = 'audio.wav'
    
    # Replace with your server's URL
    server_url = 'http://0.0.0.0:4000/analyze'
    
    send_audio_file(file_path, server_url)
