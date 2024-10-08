import crepe
from scipy.io import wavfile
from scipy import signal
import numpy as np
import matplotlib.pyplot as plt


def frequency_to_note(freq):
    A4 = 440.0
    C0 = A4 * pow(2, -4.75)
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    h = round(12 * np.log2(freq / C0))
    octave = h // 12
    n = h % 12
    return note_names[n] + str(octave)


from ruptures import Pelt


def analyze_and_plot_audio(file_path, median_window=99, min_size=10, penalty=10):
    # Load the file
    sr, audio = wavfile.read(file_path)

    # Predict the pitch
    time, frequency, confidence, _ = crepe.predict(audio, sr, viterbi=True, model_capacity='full')

    # Filter out low confidence predictions
    high_confidence = confidence > 0.85
    time = time[high_confidence]
    frequency = frequency[high_confidence]

    # Apply median filter
    frequency_median = signal.medfilt(frequency, kernel_size=median_window)

    # Detect change points
    algo = Pelt(model="l2").fit(frequency_median.reshape(-1, 1))
    change_points = algo.predict(pen=penalty)

    # Segment the pitch data
    segmented_frequency = np.zeros_like(frequency_median)
    for start, end in zip([0] + change_points, change_points + [len(frequency_median)]):
        if end - start >= min_size:  # Only keep segments of a minimum size
            segmented_frequency[start:end] = np.median(frequency_median[start:end])

    # Plot the results
    plt.figure(figsize=(12, 6))
    plt.scatter(time, frequency, s=1, alpha=0.5, label='Original', color='blue')
    plt.scatter(time, segmented_frequency, s=2, label='Segmented', color='red')
    plt.xlabel('Time (s)')
    plt.ylabel('Frequency (Hz)')
    plt.title(f'Pitch Detection Results (Median Window: {median_window}, Penalty: {penalty})')
    plt.legend()
    plt.grid(True)
    plt.show()

    return time, segmented_frequency



if __name__ == '__main__':
    file_path = '../audio/voice_recording.wav'
    analyze_and_plot_audio(file_path, median_window=21, min_size=10, penalty=5)

def analyze_audio(file_path):
    # Load the file
    sr, file = wavfile.read(file_path)

    # Predict the pitch
    time, frequency, confidence, activation = crepe.predict(file, sr, viterbi=True, model_capacity='full')

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
