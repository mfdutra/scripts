#!/bin/bash

# Photo Slideshow Creator with Zoom Effect
# Usage: ./photo_slideshow.sh photo1.jpg photo2.jpg photo3.jpg ...

# Check if any arguments were provided
if [ $# -eq 0 ]; then
    echo "Error: No photos provided"
    echo "Usage: $0 photo1.jpg photo2.jpg photo3.jpg ..."
    exit 1
fi

# Check if ffmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "Error: ffmpeg is not installed"
    echo "Please install ffmpeg first"
    exit 1
fi

# Configuration
DURATION=5  # Duration per photo in seconds
FADE_DURATION=0.5  # Cross-fade duration in seconds
OUTPUT="slideshow_$(date +%Y%m%d_%H%M%S).mp4"
TEMP_DIR="slideshow_temp_$$"
RESOLUTION="1920:1080"  # Output resolution

# Create temporary directory
mkdir -p "$TEMP_DIR"

echo "Creating slideshow with ${#@} photos..."
echo "Duration per photo: ${DURATION} seconds"
echo "Output file: $OUTPUT"

# Process each photo
counter=0
for photo in "$@"; do
    if [ ! -f "$photo" ]; then
        echo "Warning: File not found: $photo (skipping)"
        continue
    fi
    
    echo "Processing: $photo"

    # ==============================================================================
    # FFMPEG COMMAND 1: Create individual video clip from photo with zoom effect
    # ==============================================================================
    # This creates a 5-second video clip from a still photo with a smooth zoom-in
    # effect. Works with both landscape and portrait orientations by using a
    # blurred background to fill the frame.
    #
    # Input options:
    #   -loop 1          : Loop the input image (required for still images)
    #   -i "$photo"      : Input photo file
    #
    # Video filter (-vf) breakdown:
    #   The filter chain processes the image through multiple stages:
    #
    #   1. split[original][copy]
    #      - Splits input into two identical streams for separate processing
    #      - [original] = will become the centered foreground image
    #      - [copy] = will become the blurred background
    #
    #   2. [copy]scale=${RESOLUTION}:force_original_aspect_ratio=increase
    #      - Scales the copy to fill the entire 1920x1080 frame
    #      - force_original_aspect_ratio=increase: ensures image completely covers
    #        the frame (may extend beyond borders before cropping)
    #
    #   3. crop=${RESOLUTION}
    #      - Crops the scaled image to exactly 1920x1080
    #      - Combined with previous scale, this ensures full frame coverage
    #
    #   4. gblur=sigma=20
    #      - Applies Gaussian blur with sigma=20 (heavy blur)
    #      - Creates an artistic blurred background effect
    #
    #   5. eq=brightness=-0.3[blurred]
    #      - Darkens the blurred image by 30% using equalizer filter
    #      - Prevents background from competing with foreground
    #      - Saves result as [blurred] stream
    #
    #   6. [original]scale=${RESOLUTION}:force_original_aspect_ratio=decrease
    #      - Scales original to fit WITHIN the 1920x1080 frame
    #      - force_original_aspect_ratio=decrease: ensures entire image is visible
    #      - Landscape photos will have space above/below
    #      - Portrait photos will have space left/right
    #      - Saves result as [scaled] stream
    #
    #   7. [blurred][scaled]overlay=(W-w)/2:(H-h)/2
    #      - Overlays the [scaled] image centered on the [blurred] background
    #      - (W-w)/2 : horizontal centering (Width-width)/2
    #      - (H-h)/2 : vertical centering (Height-height)/2
    #      - W,H = background dimensions (1920x1080)
    #      - w,h = foreground dimensions (varies by photo)
    #
    #   8. zoompan=z='min(zoom+0.0015,1.5)':d=${DURATION}*25:s=${RESOLUTION/:/x}:fps=25
    #      - Applies smooth zoom-in effect to the composed image
    #      - z='min(zoom+0.0015,1.5)' : zoom formula
    #        * Starts at zoom=1.0 (100%)
    #        * Increases by 0.0015 per frame
    #        * Caps at 1.5 (150% zoom)
    #        * Over 125 frames (5 sec * 25fps), zooms from 100% to ~118.75%
    #      - d=${DURATION}*25 : duration in frames (5 seconds * 25 fps = 125 frames)
    #      - s=${RESOLUTION/:/x} : output size 1920x1080 (converts : to x)
    #      - fps=25 : output frame rate (25 frames per second)
    #
    # Output options:
    #   -t $DURATION         : Duration of output video (5 seconds)
    #   -c:v libx264         : Use H.264 video codec (widely compatible)
    #   -pix_fmt yuv420p     : Pixel format for maximum compatibility
    #   -y                   : Overwrite output file if it exists
    #   -loglevel error      : Only show errors (suppress informational output)
    #
    ffmpeg -loop 1 -i "$photo" \
        -vf "split[original][copy];[copy]scale=${RESOLUTION}:force_original_aspect_ratio=increase,crop=${RESOLUTION},gblur=sigma=20,eq=brightness=-0.3[blurred];[original]scale=${RESOLUTION}:force_original_aspect_ratio=decrease[scaled];[blurred][scaled]overlay=(W-w)/2:(H-h)/2,zoompan=z='min(zoom+0.0015,1.5)':d=${DURATION}*25:s=${RESOLUTION/:/x}:fps=25" \
        -t $DURATION \
        -c:v libx264 -pix_fmt yuv420p \
        "${TEMP_DIR}/clip_$(printf "%03d" $counter).mp4" \
        -y -loglevel error
    
    if [ $? -ne 0 ]; then
        echo "Error processing $photo"
        rm -rf "$TEMP_DIR"
        exit 1
    fi
    
    counter=$((counter + 1))
done

# Check if we processed any photos
if [ $counter -eq 0 ]; then
    echo "Error: No valid photos were processed"
    rm -rf "$TEMP_DIR"
    exit 1
fi

echo "Processed $counter photos"

# Combine clips with cross-fade transitions
echo "Combining clips with cross-fade transitions..."

if [ $counter -eq 1 ]; then
    # ==============================================================================
    # FFMPEG COMMAND 2a: Single clip (no transitions needed)
    # ==============================================================================
    # When there's only one photo, just copy the clip without re-encoding
    #
    # Input options:
    #   -i "${TEMP_DIR}/clip_000.mp4"  : Input video file
    #
    # Output options:
    #   -c copy       : Copy streams without re-encoding (fast, no quality loss)
    #   -y            : Overwrite output file if it exists
    #   -loglevel error : Only show errors
    #
    ffmpeg -i "${TEMP_DIR}/clip_000.mp4" -c copy "$OUTPUT" -y -loglevel error
else
    # ==============================================================================
    # FFMPEG COMMAND 2b: Multiple clips with cross-fade transitions
    # ==============================================================================
    # Combines multiple video clips with smooth cross-fade transitions between them.
    # Uses the xfade filter to create professional-looking transitions.
    #
    # Build input arguments for all clips
    inputs=""
    for i in $(seq 0 $((counter - 1))); do
        inputs="$inputs -i ${TEMP_DIR}/clip_$(printf "%03d" $i).mp4"
    done

    # Build xfade filter chain
    # -------------------------
    # The xfade filter creates smooth transitions between video clips.
    # For multiple clips, we chain xfade filters together:
    #
    # Example with 3 clips:
    #   [0:v][1:v]xfade=transition=fade:duration=0.5:offset=4.5[v01];
    #   [v01][2:v]xfade=transition=fade:duration=0.5:offset=9.0[out]
    #
    # Explanation:
    #   - First xfade: Fades from clip 0 to clip 1
    #     * Starts at 4.5s (just before clip 1 would normally start)
    #     * Lasts 0.5s, so clips overlap during this time
    #     * Output labeled [v01]
    #   - Second xfade: Fades from [v01] (combined 0+1) to clip 2
    #     * Starts at 9.0s (5s + 5s - 0.5s - 0.5s)
    #     * Final output labeled [out]
    #
    # Offset calculation:
    #   offset = (clip_number * DURATION) - (clip_number * FADE_DURATION)
    #   This ensures each fade starts FADE_DURATION before the next clip
    #
    filter=""
    for i in $(seq 1 $((counter - 1))); do
        # Calculate offset: each transition starts FADE_DURATION before the next clip
        # Example: For clip 1: 1*5 - 1*0.5 = 4.5s
        #          For clip 2: 2*5 - 2*0.5 = 9.0s
        offset=$(echo "$i * $DURATION - $i * $FADE_DURATION" | bc)

        # Determine input labels
        # First transition uses raw input [0:v], rest use previous output [vXX]
        if [ $i -eq 1 ]; then
            in1="0:v"
        else
            in1="v$(printf "%02d" $((i-1)))"
        fi
        in2="${i}:v"

        # Determine output label
        # Last transition outputs to [out], others to intermediate labels [vXX]
        if [ $i -eq $((counter - 1)) ]; then
            out="out"
        else
            out="v$(printf "%02d" $i)"
        fi

        # Add to filter chain
        # xfade parameters:
        #   transition=fade : Type of transition (fade/dissolve effect)
        #   duration=0.5    : Length of transition in seconds
        #   offset=X.X      : When transition starts in the timeline
        if [ -z "$filter" ]; then
            filter="[${in1}][${in2}]xfade=transition=fade:duration=${FADE_DURATION}:offset=${offset}[${out}]"
        else
            filter="${filter};[${in1}][${in2}]xfade=transition=fade:duration=${FADE_DURATION}:offset=${offset}[${out}]"
        fi
    done

    # Execute ffmpeg with the constructed filter chain
    #
    # Input options:
    #   $inputs : All input video clips (-i clip_000.mp4 -i clip_001.mp4 ...)
    #
    # Filter options:
    #   -filter_complex "$filter" : Complex filter graph with xfade chain
    #   -map "[out]"              : Use the final output from filter chain
    #
    # Output options:
    #   -y            : Overwrite output file if it exists
    #   -loglevel error : Only show errors
    #
    ffmpeg $inputs -filter_complex "$filter" -map "[out]" "$OUTPUT" -y -loglevel error
fi

if [ $? -eq 0 ]; then
    echo "Success! Video created: $OUTPUT"
    # Calculate actual duration: clips overlap by FADE_DURATION
    total_duration=$(echo "$counter * $DURATION - ($counter - 1) * $FADE_DURATION" | bc)
    echo "Total duration: ${total_duration} seconds"
else
    echo "Error creating final video"
    rm -rf "$TEMP_DIR"
    exit 1
fi

# Clean up temporary files
rm -rf "$TEMP_DIR"
echo "Cleanup complete"
