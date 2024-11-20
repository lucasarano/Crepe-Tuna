import os
from flask import Flask, request, jsonify
import crepe
from scipy.io import wavfile
import numpy as np
import warnings

app = Flask(__name__)

# To test if server active
@app.route('/', methods=['GET'])
def home():
    return "Server Active", 200

# Filter out the WavFileWarning

def frequency_to_note(freq):
    A4 = 440.0
    C0 = A4 * pow(2, -4.75)
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    h = round(12 * np.log2(freq / C0))
    octave = h // 12
    n = h % 12
    return note_names[n] + str(octave)

def analyze_audio(file_path):
    # Load the file file
    sr, file = wavfile.read(file_path)

    # Predict the pitch
    time, frequency, confidence, activation = crepe.predict(file, sr, viterbi=True, model_capacity='medium')

    # Create an array of tuples and filter by confidence
    data = [(t, f, c) for t, f, c in zip(time, frequency, confidence) if c > 0.82]

    # Extract the filtered values
    filtered_time = [d[0] for d in data]
    filtered_frequency = [d[1] for d in data]
    filtered_confidence = [d[2] for d in data]

    # Group frequencies into notes
    notes = []
    current_note = []
    prev_f = None
    prev_t = None
    note_diff = None

    for i in range(len(filtered_time)):
        if i != 0:
            note_diff = abs((filtered_frequency[i] - prev_f) / (filtered_time[i] - prev_t))
        if not current_note:
            current_note.append((filtered_time[i], filtered_frequency[i], filtered_confidence[i]))
        else:
            time_diff = filtered_time[i] - current_note[-1][0]
            if time_diff <= 0.1 and note_diff is not None and note_diff < 180:
                current_note.append((filtered_time[i], filtered_frequency[i], filtered_confidence[i]))
            else:
                notes.append(current_note)
                current_note = [(filtered_time[i], filtered_frequency[i], filtered_confidence[i])]
        prev_t = filtered_time[i]
        prev_f = filtered_frequency[i]

    if current_note:
        notes.append(current_note)

    long_notes = []
    for note_array in notes:
        time_last, freq_last, conf_last = note_array[-1]
        time_first, freq_first, conf_first = note_array[0]
        if (time_last - time_first) > 0.05:
            long_notes.append(note_array)

    notes = long_notes

    # Calculate weighted average of frequencies for each note and match with initial and ending time
    weighted_averages = []
    for note in notes:
        times, freqs, confs = zip(*note)
        weighted_avg_freq = np.average(freqs, weights=confs)
        start_time = times[0]
        end_time = times[-1]
        duration = end_time - start_time
        musical_note = frequency_to_note(weighted_avg_freq)
        weighted_averages.append({
            "name": musical_note,
            "duration": duration,
            "frequency": weighted_avg_freq,
            "startTime": start_time
        })

    return weighted_averages

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
            result = analyze_audio(file_path)
            
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'Invalid file format'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=True)
