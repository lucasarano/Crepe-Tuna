import crepe
from scipy.io import wavfile
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Load the audio file
sr, audio = wavfile.read('voice_recording_reduced.wav')

# Predict the pitch
time, frequency, confidence, activation = crepe.predict(audio, sr, viterbi=True, model_capacity='medium')

# Create an array of tuples and filter by confidence
data = [(t, f, c) for t, f, c in zip(time, frequency, confidence) if c > 0.75]

# Extract the filtered values for plotting
filtered_time = [d[0] for d in data]
filtered_frequency = [d[1] for d in data]
filtered_confidence = [d[2] for d in data]

# Group frequencies into notes
notes = []
current_note = []

for i in range(len(filtered_time)):
    if not current_note:
        current_note.append((filtered_time[i], filtered_frequency[i], filtered_confidence[i]))
    else:
        time_diff = filtered_time[i] - current_note[-1][0]
        if time_diff <= 0.07:
            current_note.append((filtered_time[i], filtered_frequency[i], filtered_confidence[i]))
        else:
            notes.append(current_note)
            current_note = [(filtered_time[i], filtered_frequency[i], filtered_confidence[i])]

# Append the last note if it exists
if current_note:
    notes.append(current_note)

longNotes = []

for noteArray in notes:
    timeLast, freqLast, confLast = noteArray[-1]
    timeFirst, freqFirst, confFirst = noteArray[0]
    if (timeLast - timeFirst) > 0.05:
        longNotes.append(noteArray)

notes = longNotes

# Function to convert frequency to nearest musical note
def frequency_to_note(freq):
    A4 = 440.0
    C0 = A4 * pow(2, -4.75)
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    h = round(12 * np.log2(freq / C0))
    octave = h // 12
    n = h % 12
    return note_names[n] + str(octave)


def distanceToNote(freq):
    A4 = 440.0
    C0 = A4 * pow(2, -4.75)
    h = round(12 * np.log2(freq / C0))
    closest_note_freq = C0 * pow(2, h / 12)
    distance = freq - closest_note_freq
    return distance

distance = None

# Calculate weighted average of frequencies for each note and match with initial and ending time
weighted_averages = []
for note in notes:
    times, freqs, confs = zip(*note)
    weighted_avg_freq = np.average(freqs, weights=confs)
    
    start_time = times[0]
    end_time = times[-1]
    if distance == None:
        distance = distanceToNote(weighted_avg_freq)
        print(distance)
    else:
        weighted_avg_freq += distance
    musical_note = frequency_to_note(weighted_avg_freq)
    weighted_averages.append((musical_note, weighted_avg_freq, start_time, end_time))

# Print the weighted averages with initial and ending time for verification
for i, (note, avg, start, end) in enumerate(weighted_averages):
    print(f"Note {i+1}: {note}, Weighted average frequency = {avg:.2f} Hz, Start time = {start:.2f}, End time = {end:.2f}")

# Plot the results
plt.figure(figsize=(12, 12))

# Plot frequency
plt.subplot(3, 1, 1)
plt.scatter(filtered_time, filtered_frequency, s=1)
plt.title('Pitch Estimation (Filtered)')
plt.ylabel('Frequency (Hz)')

# Plot confidence
plt.subplot(3, 1, 2)
plt.scatter(filtered_time, filtered_confidence, s=1)
plt.title('Confidence (Filtered)')
plt.ylabel('Confidence')
plt.xlabel('Time (s)')

# Plot activation
plt.subplot(3, 1, 3)
plt.imshow(np.flip(activation.T, axis=0), aspect='auto', cmap='inferno', extent=[time[0], time[-1], 0, 360])
plt.title('Activation Matrix')
plt.ylabel('Frequency Bin')
plt.xlabel('Time (s)')

plt.tight_layout()
plt.savefig('pitch_analysis_filtered.png')
plt.show()




