# USE THIS FILE FOR RAPID PROTOTYPING. THIS FILE IS MEANT TO SERVE AS A TESTING GROUND FOR A FUTURE IMPLEMENTATION OF model.py.
import logging
import numpy as np
from scipy import signal
from scipy.io import wavfile
import crepe
import matplotlib.pyplot as plt
from ruptures import Pelt
from statistics import mode, StatisticsError

logging.basicConfig(level=logging.WARNING)



def note_to_freq(note):
    return 440 * (2 ** ((note - 69) / 12))


def note_name(midi_note):
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    return notes[int(midi_note) % 12] + str(int((midi_note - 12) / 12))



def adaptive_median_filter(data, max_window):
    result = np.zeros_like(data)
    for i in range(len(data)):
        window = min(max_window, 2 * (i % (max_window // 2)) + 1)
        start = max(0, i - window // 2)
        end = min(len(data), i + window // 2 + 1)
        result[i] = np.median(data[start:end])
    return result




def robust_change_point_detection(data, penalty):
    # Use a combination of methods for more robust detection
    algo = Pelt(model="rbf").fit(data.reshape(-1, 1))
    change_points_pelt = algo.predict(pen=penalty)

    # You might want to combine this with other methods like
    # Dynamic programming or Bayesian online changepoint detection
    return change_points_pelt



def enhanced_segment_merging(segments, merge_threshold):
    merged = []
    for segment in segments:
        if not merged or abs(segment[2] - merged[-1][2]) > merge_threshold:
            merged.append(segment)
        else:
            last = merged[-1]
            merged[-1] = (last[0], segment[1], weighted_average(last, segment))
    return merged


def weighted_average(seg1, seg2):
    w1, w2 = seg1[1] - seg1[0], seg2[1] - seg2[0]
    return (seg1[2] * w1 + seg2[2] * w2) / (w1 + w2)


def create_segmented_frequency(merged_segments, length):
    segmented_frequency = np.zeros(length)
    for start, end, freq in merged_segments:
        segmented_frequency[start:end] = freq
    return segmented_frequency


def improved_quantize_to_musical_notes(frequency):
    A4 = 440
    notes = 12 * (np.log2(frequency / A4) + 4)
    return np.round(notes)


def freq_to_note(freq):
    A4 = 440
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    note_number = 12 * (np.log2(freq / A4) + 4)
    note_index = int(round(note_number)) % 12
    octave = int(note_number // 12) - 1
    return f"{notes[note_index]}{octave}"


def improved_segmentation(time, freq, change_points, min_duration, min_samples=3):
    segments = []
    for start, end in zip([0] + list(change_points), list(change_points) + [len(freq)]):
        if end > len(time):
            end = len(time)
        segment_duration = time[end - 1] - time[start] if start < len(time) else 0
        segment_freqs = freq[start:end]

        if segment_duration >= min_duration and len(segment_freqs) >= min_samples:
            try:
                segment_freq = np.median(segment_freqs)  # Using median instead of mode
                segments.append((start, end, segment_freq))
            except StatisticsError:
                logging.warning(f"Could not determine median for segment: start={start}, end={end}")

    return segments


def analyze_and_plot_audio(file_path, median_window=31, penalty=20, min_duration=0.1, merge_threshold=0.5):
    # ... (keep the existing code for loading and initial processing)
    # Load the file
    sr, audio = wavfile.read(file_path)

    # Convert stereo to mono if necessary
    if len(audio.shape) > 1:
        audio = np.mean(audio, axis=1)

    # Predict the pitch using CREPE
    time, frequency, confidence, _ = crepe.predict(audio, sr, viterbi=True, model_capacity='full')

    # Apply more sophisticated filtering
    high_confidence = confidence > 0.80
    time = time[high_confidence]
    frequency = frequency[high_confidence]

    # Apply median filter with dynamic window size
    frequency_median = adaptive_median_filter(frequency, max_window=median_window)

    # Use more robust change point detection
    change_points = robust_change_point_detection(frequency_median, penalty)

    # Improved segmentation with overlapping windows
    segments = improved_segmentation(time, frequency_median, change_points, min_duration)

    # Create final segmented frequency array
    segmented_frequency = create_segmented_frequency(segments, len(frequency_median))

    # Plot the results
    plt.figure(figsize=(12, 6))
    plt.scatter(time, frequency, s=1, alpha=0.5, label='Original', color='blue')
    plt.scatter(time, segmented_frequency, s=2, label='Segmented', color='red')

    # Add note labels
    for start, end, freq in segments:
        note = freq_to_note(freq)
        plt.text(time[start], freq, note, fontsize=8, verticalalignment='bottom')

    plt.xlabel('Time (s)')
    plt.ylabel('Frequency (Hz)')
    plt.title(f'Pitch Detection Results with Note Quantization (Median Window: {median_window}, Penalty: {penalty})')
    plt.legend()
    plt.grid(True)
    plt.ylim(0, max(frequency.max(), segmented_frequency.max()) * 1.1)  # Adjust y-axis limit
    plt.show()

    return time, segmented_frequency, frequency_median

if __name__ == '__main__':
    analyze_and_plot_audio("../audio/dakitiInCulc.wav", median_window=15, penalty=5, min_duration=0.2,
                           merge_threshold=0.25)
