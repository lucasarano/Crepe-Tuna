import os
from flask import Flask, request, jsonify
from model import analyze_audio

app = Flask(__name__)

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    audio_file = request.files['file']
    if audio_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if audio_file and audio_file.filename.endswith('.wav'):
        save_directory = './'
        os.makedirs(save_directory, exist_ok=True)
        file_path = os.path.join(save_directory, audio_file.filename)
        audio_file.save(file_path)

        try:
            result = analyze_audio(file_path)
            
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'Invalid file format'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=True)
