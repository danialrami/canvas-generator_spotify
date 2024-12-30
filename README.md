# Spotify Canvas Generator

A Python tool that transforms static album artwork into a dynamic Spotify Canvas - the [short looping visuals](https://artists.spotify.com/canvas) that play alongside tracks in the Spotify app. Create animated artwork with glitch effects and smooth transitions.

## Quick Start

```
git clone [repository-url]
pip install -r requirements.txt
python3 canvas-generator.py
```

## Features

- Converts static images to 8-second Spotify Canvas videos
- Maintains Spotify's required 720x1280 (9:16) resolution
- Generates glitch effects with customizable intensity
- Creates smooth transitions between frames
- Supports BPM-synchronized animations
- Outputs in multiple formats (static PNG, GIF, and MP4)

## Requirements

- Python 3.8+
- FFmpeg
- PIL (Python Imaging Library)
- NumPy
- glitch_this

## Installation

1. Clone the repository
2. Install required dependencies:
```
pip install -r requirements.txt
```
3. Install FFmpeg (required for MP4 conversion)

## Usage

Run the script and follow the prompts:
```
python canvas-generator.py
```

You'll need to provide:
- Path to your album artwork
- BPM of your song (optional, defaults to 88)

## Output

The script generates three files in a new directory named after your input file:
- Static canvas (PNG)
- Animated canvas (GIF)
- Spotify-ready canvas (MP4)

## Versions

###  `canvas-generator.py` - Includes additional visual artifacts

#### Original - [Madonna and Child](https://www.nga.gov/collection/art-object-page.41675.html)

![[madonna_child.jpg]]

#### Spotify Canvas

![[madonna_child_canvas.gif]]

### `canvas-generator_no-artifacts.py` - Clean version without random artifacts

#### Original - [The Seine](https://www.nga.gov/collection/art-object-page.52624.html)

![[the_seine.jpg]]

#### Spotify Canvas

![[the_seine_canvas.gif]]

## Customization

The following parameters can be adjusted in the script:

- Frame Rate: 24 fps (FRAMES constant)
- Transition Frames: 3 frames between effects (TRANSITION_FRAMES)
- Glitch Intensity: 3.0 (default in glitch_image())
- Smearing Strength: 20-40 (adjustable in apply_smearing())

## Troubleshooting

- Error "FFmpeg not found": Ensure FFmpeg is installed and in system PATH 
- Low resolution warning: Use source images of at least 720x1280 pixels 
- Glitch artifacts too intense: Lower the glitch_intensity parameter

## Notes

- Input images should ideally be high resolution
- The script will automatically resize and crop images to fit Spotify's requirements
- Generated MP4 files are optimized for [Spotify Canvas specifications](https://support.spotify.com/us/artists/article/canvas-guidelines/)