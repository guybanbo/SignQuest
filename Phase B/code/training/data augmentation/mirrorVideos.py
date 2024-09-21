import os
import cv2

# Function to mirror a video
def mirror_video(input_path, output_path):
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print("Error: Could not open video.")
        return
    
    # Get video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Define codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # You can change codec as needed
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    # Read and write frames
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # Mirror the frame
        mirrored_frame = cv2.flip(frame, 1)
        out.write(mirrored_frame)
    
    # Release video capture and writer objects
    cap.release()
    out.release()
    cv2.destroyAllWindows()

# Function to mirror all videos in a directory
def mirror_videos_in_directory(input_dir):
    # Iterate through each folder in input directory
    for root, dirs, files in os.walk(input_dir):
        for filename in files:
            if filename.endswith(('.mp4', '.avi', '.mkv')):  # Add more video formats if needed
                input_path = os.path.join(root, filename)
                output_path = os.path.join(root, f"mirrored_{filename}")
                print(f"Mirroring {input_path}...")
                mirror_video(input_path, output_path)

# Example usage
input_directory = "new_videos"
mirror_videos_in_directory(input_directory)