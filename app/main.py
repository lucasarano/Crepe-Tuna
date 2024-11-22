import io
import os

from flask import Flask, request, jsonify
from flask import send_file

from app.model import analyze_audio_old, export_to_midi

app = Flask(__name__)

# To test if server active
@app.route('/', methods=['GET'])
def home():
    return "Server Active", 200

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({'error': 'No file file provided'}), 400

    audio_file = request.files['file']
    if audio_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if audio_file and audio_file.filename.endswith('.wav'):
        save_directory = './'
        os.makedirs(save_directory, exist_ok=True)
        file_path = os.path.join(save_directory, audio_file.filename)
        audio_file.save(file_path)

        try:
            result = analyze_audio_old(file_path)

            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'Invalid file format'}), 400




@app.route('/midi', methods=['POST'])
def create_midi():
    # Assuming your audio file was uploaded with the request
    if 'file' not in request.files:
        return 'No file uploaded', 400

    file = request.files['file']
    if file.filename == '':
        return 'No file selected', 400

    # Create a temporary path to save the uploaded wav file
    temp_wav_path = "temp_audio.wav"
    file.save(temp_wav_path)
    # Create a temporary path for the MIDI file
    temp_midi_path = "temp_output.mid"
    try:
        # Analyze the audio using your existing function
        notes = analyze_audio_old(temp_wav_path)

        # Convert to MIDI using your existing function
        export_to_midi(notes, temp_midi_path)

        # Read the MIDI file into memory
        with open(temp_midi_path, 'rb') as midi_file:
            midi_data = io.BytesIO(midi_file.read())

        # Clean up temporary files
        os.remove(temp_wav_path)
        os.remove(temp_midi_path)

        # Return the MIDI file
        return send_file(
            midi_data,
            mimetype='audio/midi',
            as_attachment=True,
            download_name='converted.mid'
        )

    except Exception as e:
        # Clean up temporary files in case of error
        if os.path.exists(temp_wav_path):
            os.remove(temp_wav_path)
        if os.path.exists(temp_midi_path):
            os.remove(temp_midi_path)
        return str(e), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=True)

