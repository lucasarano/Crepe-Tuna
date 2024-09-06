# USE THIS FILE FOR RAPID PROTOTYPING. THIS FILE IS MEANT TO SERVE AS A TESTING GROUND FOR A FUTURE IMPLEMENTATION OF model.py.
import numpy as np
from scipy import signal
from scipy.io import wavfile
import crepe
import matplotlib.pyplot as plt
from ruptures import Pelt


def freq_to_note(freq):
    return 69 + 12 * np.log2(freq / 440)


def note_to_freq(note):
    return 440 * (2 ** ((note - 69) / 12))


def note_name(midi_note):
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    return notes[int(midi_note) % 12] + str(int((midi_note - 12) / 12))


def quantize_to_musical_notes(frequency):
    notes = freq_to_note(frequency)
    quantized_notes = np.round(notes)
    return note_to_freq(quantized_notes)


def analyze_and_plot_audio(file_path, median_window=15, penalty=15, min_duration=0.1, merge_threshold=0.5):
    # Load the file
    sr, audio = wavfile.read(file_path)

    # Predict the pitch
    time, frequency, confidence, _ = crepe.predict(audio, sr, viterbi=True, model_capacity='full')

    # Filter out low confidence predictions
    high_confidence = confidence > 0.80
    time = time[high_confidence]
    frequency = frequency[high_confidence]

    # Apply median filter
    frequency_median = signal.medfilt(frequency, kernel_size=median_window)

    # Quantize to musical notes
    quantized_freq = quantize_to_musical_notes(frequency_median)

    # Detect change points
    algo = Pelt(model="l2").fit(quantized_freq.reshape(-1, 1))
    change_points = algo.predict(pen=penalty)

    # Segment the pitch data
    segmented_frequency = np.zeros_like(quantized_freq)
    segments = []
    for start, end in zip([0] + change_points, change_points + [len(quantized_freq)]):
        if end > len(time):  # Ensure we don't go out of bounds
            end = len(time)
        if start < len(time) and (time[end - 1] - time[start]) >= min_duration:
            segment_freq = np.median(quantized_freq[start:end])
            segments.append((start, end, segment_freq))

    # Merge similar adjacent segments
    merged_segments = []
    for segment in segments:
        if not merged_segments or abs(
                freq_to_note(segment[2]) - freq_to_note(merged_segments[-1][2])) > merge_threshold:
            merged_segments.append(segment)
        else:
            last_start, _, last_freq = merged_segments[-1]
            merged_segments[-1] = (last_start, segment[1],
                                   np.median(quantized_freq[last_start:segment[1]]))

    # Create segmented frequency array
    for start, end, freq in merged_segments:
        segmented_frequency[start:end] = freq

    # Plot the results
    plt.figure(figsize=(12, 6))
    plt.scatter(time, frequency, s=1, alpha=0.5, label='Original', color='blue')
    plt.scatter(time, segmented_frequency, s=2, label='Segmented', color='red')

    # Add note labels
    for start, end, freq in merged_segments:
        midi_note = freq_to_note(freq)
        note = note_name(midi_note)
        plt.text(time[start], freq, note, fontsize=8, verticalalignment='bottom')

    plt.xlabel('Time (s)')
    plt.ylabel('Frequency (Hz)')
    plt.title(f'Pitch Detection Results with Note Quantization (Median Window: {median_window}, Penalty: {penalty})')
    plt.legend()
    plt.grid(True)
    plt.show()

    return time, segmented_frequency, quantized_freq

if __name__ == '__main__':
    analyze_and_plot_audio("../audio/dakitiInCulc.wav", median_window=31, penalty=20, min_duration=0.2, merge_threshold=0.25)