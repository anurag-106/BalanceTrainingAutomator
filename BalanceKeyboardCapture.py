import keyboard  # Requires 'keyboard' library
import time
import sys

if len(sys.argv) != 2:
    print("Usage: python script.py <output_file_path>")
    sys.exit(1)

output_file_path = sys.argv[1]
input_sequence = []
start_time = time.time()

def on_key_press(event):
    key = event.name
    elapsed_time = time.time() - start_time
    input_sequence.append((key, elapsed_time))

keyboard.on_press(on_key_press)

print("Start typing... Press ESC to stop.")

# Keep the script running until 'esc' is pressed
keyboard.wait('esc')

# Writing the input_sequence to the file
with open(output_file_path, 'w') as file:
    for key, timing in input_sequence:
        file.write(f"('{key}', {timing:.2f}),  # Pressed '{key}' after {timing:.2f} seconds\n")

print(f"Input sequence logged to {output_file_path}")
