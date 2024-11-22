from music21 import converter, key

# Load the MIDI file
midi_file = converter.parse('../midi/do_mi_sol_do.mid')

# Analyze the key
key_of_music = midi_file.analyze('key')

print(f"The key of the music is: {key_of_music}")