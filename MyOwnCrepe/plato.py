import argparse
import os
import sys
from tabulate import tabulate
from pprint import pprint
from model import analyze_audio

"""
CLI tool to analyze audio, simplifies testing without a server.
To run this tool, run the following command:
    python plato.py wavfilename.wav
Use recorder.py to record a wav audio file.
"""

def pretty_print_result(result):
    print("\nAnalysis Results:")
    if isinstance(result, dict):
        # If result is a dictionary, use pprint
        pprint(result, width=100, sort_dicts=False)
    elif isinstance(result, list):
        # If result is a list, try to use tabulate
        if result and isinstance(result[0], dict):
            # If it's a list of dictionaries, extract keys for headers
            headers = result[0].keys()
            table = [[row.get(col, '') for col in headers] for row in result]
            print(tabulate(table, headers=headers, tablefmt="grid"))
        else:
            # If it's a simple list, just use pprint
            pprint(result, width=100)
    else:
        # For any other type, use str() and print
        print(str(result))

def main():
    parser = argparse.ArgumentParser(description="Analyze an audio file.")
    parser.add_argument("audio_file", nargs="?", help="The audio file to analyze (should be a .wav file)")
    args = parser.parse_args()

    audio_file = args.audio_file

    if not audio_file:
        audio_file = input("Please enter the name of the audio file to analyze: ")

    # Check if the file exists
    if not os.path.exists(audio_file):
        print(f"Error: The file '{audio_file}' does not exist.")
        sys.exit(1)

    # Check if the file has a .wav extension, add it if necessary
    if not audio_file.lower().endswith('.wav'):
        audio_file += '.wav'
        if not os.path.exists(audio_file):
            print(f"Error: The file '{audio_file}' does not exist.")
            sys.exit(1)

    try:
        print("Analyzing audio...")
        file_path = os.path.join('./', audio_file)
        result = analyze_audio(file_path)
        pretty_print_result(result)

        return result
    except Exception as e:
        print(f"An error occurred while analyzing the file: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
