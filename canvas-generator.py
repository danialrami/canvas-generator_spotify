import os
import random
import numpy as np
import subprocess
from PIL import Image, ImageDraw, ImageChops
from glitch_this import ImageGlitcher
import warnings
warnings.filterwarnings("ignore", category=Image.DecompressionBombWarning)

# Constants
TARGET_WIDTH = 720  # Spotify Canvas minimum width
TARGET_HEIGHT = 1280  # Spotify Canvas minimum height (9:16 ratio)
DEFAULT_BPM = 88
CANVAS_DURATION = 8  # Spotify requires exactly 8 seconds

def check_ffmpeg():
    """Check if FFmpeg is installed"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True)
        return True
    except FileNotFoundError:
        print("Error: FFmpeg is not installed. Please install FFmpeg to convert to MP4.")
        return False

def apply_artifacting(image, intensity=50):
    try:
        image = image.copy()
        draw = ImageDraw.Draw(image)
        width, height = image.size

        for _ in range(intensity):
            # Random line
            start = (random.randint(0, width), random.randint(0, height))
            end = (random.randint(0, width), random.randint(0, height))
            color = (random.randint(0, 255), random.randint(0, 255), 
                    random.randint(0, 255), random.randint(50, 200))
            draw.line([start, end], fill=color, width=random.randint(1, 5))

            # Random rectangle
            x1, y1 = random.randint(0, width), random.randint(0, height)
            x2, y2 = x1 + random.randint(10, 50), y1 + random.randint(10, 50)
            color = (random.randint(0, 255), random.randint(0, 255), 
                    random.randint(0, 255), random.randint(50, 200))
            draw.rectangle([x1, y1, x2, y2], fill=color)

        return image
    except Exception as e:
        print(f"Error applying artifacting: {e}")
        return image

def apply_smearing(image, strength=20):
    """Apply a digital smearing effect to the image"""
    try:
        img_array = np.array(image)
        height, width = img_array.shape[:2]
        
        for x in range(width):
            if random.random() < 0.1:  # 10% chance of smearing each column
                streak_height = random.randint(10, strength)
                y_start = random.randint(0, height - streak_height)
                
                for y in range(y_start, min(y_start + streak_height, height)):
                    if y > 0:
                        alpha = 1.0 - ((y - y_start) / streak_height)
                        img_array[y] = (img_array[y] * alpha + img_array[y-1] * (1-alpha))
        
        return Image.fromarray(img_array)
    except Exception as e:
        print(f"Error applying smearing: {e}")
        return image

def blend_images(img1, img2, alpha):
    """Blend two images with given alpha value"""
    return Image.blend(img1, img2, alpha)

def create_crossfade_frames(glitch_frames, num_transition_frames=5):
    """Create smooth transitions between glitch frames with smearing"""
    print("Applying crossfade and smearing effects...")
    smoothed_frames = []
    
    for i in range(len(glitch_frames)):
        current_frame = glitch_frames[i]
        next_frame = glitch_frames[(i + 1) % len(glitch_frames)]
        
        current_frame = apply_smearing(current_frame, strength=40)
        next_frame = apply_smearing(next_frame, strength=40)
        
        smoothed_frames.append(current_frame)
        
        for j in range(num_transition_frames):
            alpha = (j + 1) / (num_transition_frames + 1)
            transition_frame = blend_images(current_frame, next_frame, alpha)
            transition_frame = apply_smearing(transition_frame, strength=30)
            smoothed_frames.append(transition_frame)
    
    return smoothed_frames

def convert_gif_to_mp4(gif_path, output_path):
    """Convert GIF to MP4 with proper Spotify Canvas settings"""
    print("Converting to MP4 format...")
    try:
        cmd = [
            'ffmpeg', '-i', gif_path,
            '-movflags', '+faststart',
            '-pix_fmt', 'yuv420p',
            '-vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2',
            '-r', '30',
            '-t', str(CANVAS_DURATION),
            '-y',
            output_path
        ]
        subprocess.run(cmd, check=True)
        return True
    except Exception as e:
        print(f"Error converting to MP4: {e}")
        return False

def create_spotify_canvas(input_image_path, bpm):
    try:
        if not os.path.exists(input_image_path):
            print("Error: File does not exist")
            return None

        base_name = os.path.splitext(os.path.basename(input_image_path))[0]
        output_dir = f"{base_name}_canvas"
        os.makedirs(output_dir, exist_ok=True)
        
        glitcher = ImageGlitcher()
        
        # Adjusted parameters for 8-second duration
        FRAMES = 24  # Standard video framerate
        TRANSITION_FRAMES = 3
        TOTAL_DURATION = 8000  # 8 seconds in milliseconds
        DURATION = TOTAL_DURATION // (FRAMES + (FRAMES * TRANSITION_FRAMES))
        
        print("Opening and processing image...")
        image = Image.open(input_image_path).convert('RGBA')
        
        if image.size[0] < TARGET_WIDTH or image.size[1] < TARGET_HEIGHT:
            print("Warning: Input image resolution is lower than target resolution")
        
        original_aspect = image.size[0] / image.size[1]
        canvas_aspect = TARGET_WIDTH / TARGET_HEIGHT
        
        if original_aspect > canvas_aspect:
            new_height = TARGET_HEIGHT
            new_width = int(new_height * original_aspect)
        else:
            new_width = TARGET_WIDTH
            new_height = int(new_width / original_aspect)
        
        print("Resizing image...")
        resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        left = (resized_image.size[0] - TARGET_WIDTH) // 2
        top = (resized_image.size[1] - TARGET_HEIGHT) // 2
        right = left + TARGET_WIDTH
        bottom = top + TARGET_HEIGHT
        
        cropped_image = resized_image.crop((left, top, right, bottom))
        
        print("Applying artifacting effects...")
        artifacted_image = apply_artifacting(cropped_image, intensity=75)
        
        if artifacted_image.mode != 'RGB':
            artifacted_image = artifacted_image.convert('RGB')
        
        print("Generating glitch effects...")
        glitch_imgs = glitcher.glitch_image(
            artifacted_image, 
            3.0,  # Glitch intensity
            color_offset=True,
            scan_lines=True,
            gif=True,
            frames=FRAMES
        )
        
        smoothed_frames = create_crossfade_frames(glitch_imgs, TRANSITION_FRAMES)
        
        print("Saving output files...")
        static_path = os.path.join(output_dir, f'{base_name}_canvas_static.png')
        gif_path = os.path.join(output_dir, f'{base_name}_canvas.gif')
        mp4_path = os.path.join(output_dir, f'{base_name}_canvas.mp4')
        
        artifacted_image.save(static_path)
        smoothed_frames[0].save(
            gif_path,
            format='GIF',
            append_images=smoothed_frames[1:],
            save_all=True,
            duration=DURATION,
            loop=0
        )
        
        if convert_gif_to_mp4(gif_path, mp4_path):
            print(f"Static canvas generated at: {static_path}")
            print(f"GIF canvas generated at: {gif_path}")
            print(f"MP4 canvas generated at: {mp4_path}")
            return static_path, gif_path, mp4_path
        
        return static_path, gif_path

    except Exception as e:
        print(f"Error processing image: {e}")
        return None

def main():
    if not check_ffmpeg():
        exit(1)
        
    input_image_path = input("Enter the path to your album artwork: ").strip("'")
    
    while True:
        try:
            bpm = float(input(f"Enter the BPM of your song (default is {DEFAULT_BPM}): ") or DEFAULT_BPM)
            if bpm > 0:
                break
            print("BPM must be greater than 0")
        except ValueError:
            print("Please enter a valid number")
    
    result = create_spotify_canvas(input_image_path, bpm)
    if result is None:
        print("Failed to create canvas")

if __name__ == "__main__":
    main()
