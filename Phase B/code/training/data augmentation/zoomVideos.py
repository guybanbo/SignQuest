import os
import cv2

# Function to zoom a video
def zoom_video(input_path, output_path, zoom_factor=1.2):
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
    
    # Calculate the cropping coordinates
    new_width = int(width / zoom_factor)
    new_height = int(height / zoom_factor)
    x1 = (width - new_width) // 2
    y1 = (height - new_height) // 2
    x2 = x1 + new_width
    y2 = y1 + new_height
    
    # Read and write frames
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # Crop the frame to the center
        cropped_frame = frame[y1:y2, x1:x2]
        # Resize the frame back to original size
        zoomed_frame = cv2.resize(cropped_frame, (width, height))
        out.write(zoomed_frame)
    
    # Release video capture and writer objects
    cap.release()
    out.release()
    cv2.destroyAllWindows()

# Function to zoom all videos in a directory
def zoom_videos_in_directory(input_dir, zoom_factor=1.1):
    # Iterate through each folder in input directory
    for root, dirs, files in os.walk(input_dir):
        for filename in files:
            if filename.endswith(('.mp4', '.avi', '.mkv')):  # Add more video formats if needed
                input_path = os.path.join(root, filename)
                file_base, file_ext = os.path.splitext(filename)
                output_filename = f"{file_base}_zoom_{zoom_factor}x{file_ext}"
                output_path = os.path.join(root, output_filename)
                print(f"Zooming {input_path} with zoom factor {zoom_factor}...")
                zoom_video(input_path, output_path, zoom_factor)

# Example usage
input_directory = "new_videos"
zoom_videos_in_directory(input_directory, zoom_factor=1.1)