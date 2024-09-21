import os
import cv2
import numpy as np

# Function to apply translation to a video
def translate_video(input_path, output_path, translate_params):
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print("Error: Could not open video.")
        return
    
    # Get video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    # Calculate translation in pixels
    tx_percent, ty_percent = translate_params
    tx = int(width * tx_percent)
    ty = int(height * ty_percent)
    
    # Define codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # You can change codec as needed
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    # Read and write frames
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Apply translation to the frame
        translated_frame = np.zeros_like(frame)
        translated_frame[max(0, ty):min(height, height+ty), max(0, tx):min(width, width+tx)] = frame[max(0, -ty):min(height, height-ty), max(0, -tx):min(width, width-tx)]
        out.write(translated_frame)
    
    # Release video capture and writer objects
    cap.release()
    out.release()
    cv2.destroyAllWindows()

# Function to apply translation to all videos in a directory with multiple translation parameters
def translate_videos_in_directory(input_dir):
    # List of translation parameters to apply
    translation_parameters_list = [
        (-0.1, 0),   # Shift horizontally by -10% of width, vertically by 0% of height
        (-0.05, 0),  # Shift horizontally by -5% of width, vertically by 0% of height
        (0.05, 0),   # Shift horizontally by 5% of width, vertically by 0% of height
        (0.1, 0)     # Shift horizontally by 10% of width, vertically by 0% of height
    ]

    # Iterate through each folder in input directory
    for root, dirs, files in os.walk(input_dir):
        for filename in files:
            if filename.endswith(('.mp4', '.avi', '.mkv')):  # Add more video formats if needed
                input_path = os.path.join(root, filename)
                
                # Check if the filename indicates that it has been previously shifted
                if "translated_tx_" in filename or "translated_ty_" in filename:
                    print(f"Skipping {input_path} (already translated).")
                    continue

                for translation_params in translation_parameters_list:
                    # Modify the output filename to include translation parameters
                    output_filename = f"translated_tx_{int(translation_params[0] * 100)}_ty_{int(translation_params[1] * 100)}_{filename}"
                    output_path = os.path.join(root, output_filename)
                    
                    # Check if the translated file already exists
                    if not os.path.exists(output_path):
                        print(f"Translating {input_path} with params {translation_params}...")
                        translate_video(input_path, output_path, translation_params)
                    else:
                        print(f"Skipping {input_path} with params {translation_params} (already translated).")

# Example usage
input_directory = "videos"
translate_videos_in_directory(input_directory)
