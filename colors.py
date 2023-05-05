import numpy as np
import cv2

colors = [
    [180, 0, 0], # red
    [0, 180, 0], # green
    [0, 0, 180], # blue
]

backSub = cv2.createBackgroundSubtractorMOG2()


def get_color_index(color):
    color = list(color)
    return colors.index(color)


def get_frame_from_rgb_components(r, g, b):
    frame = np.array([b, g, r])
    return np.moveaxis(frame, 0, 2).astype(np.uint8)


def distance(color1, color2):
    return np.sqrt(np.sum(np.square(color1 - color2)))


def get_closest_color(r, g, b):
    colors_arr = np.array(colors)
    input_color = np.array([r, g, b])

    return min(colors_arr, key=lambda x: distance(np.array(x), np.array(input_color)))


def get_object_color(frame, min_s, min_v, min_pixels, color_coefficients, display_mask):
    preview_size = (300, int(300 * frame.shape[0] / frame.shape[1]))

    # Color correction
    frame_corrected_b = frame[:, :, 0] * color_coefficients[2]
    frame_corrected_g = frame[:, :, 1] * color_coefficients[1]
    frame_corrected_r = frame[:, :, 2] * color_coefficients[0]
    frame_corrected = get_frame_from_rgb_components(frame_corrected_r, frame_corrected_g, frame_corrected_b)

    if display_mask:
        cv2.imshow('Color correction', cv2.resize(frame_corrected, preview_size))

    
    # Motion-based foreground mask, should contain only the screensaver
    motion_mask = backSub.apply(frame)

    if display_mask:
        cv2.imshow('Motion mask', cv2.resize(motion_mask, preview_size))

    
    # Color-based foreground mask
    hsv = cv2.cvtColor(frame_corrected, cv2.COLOR_BGR2HSV) # Convert the frame to the HSV color space

    color_lower = np.array([0, min_s, min_v]) # Lower bounds of color range
    color_upper = np.array([255, 255, 255]) # Upper bounds of color range
    
    color_mask = cv2.inRange(hsv, color_lower, color_upper)

    if display_mask:
        cv2.imshow('Color mask', cv2.resize(color_mask, preview_size))

    
    # Combine both masks
    mask = motion_mask & color_mask
    object_pixels = frame_corrected[np.where(mask != 0)]

    if display_mask:
        mask_frame = get_frame_from_rgb_components(mask, mask, mask)
        capture_frame = np.where(mask_frame != 0, frame_corrected, np.zeros_like(frame_corrected))
        cv2.imshow('Captured area', cv2.resize(capture_frame, preview_size))

    
    # Ensure that at least 0.5% of the pixels in the frame are in the mask
    if np.count_nonzero(mask) < (frame.size/3 * min_pixels/100):
        return None

    
    # Get the mean color of the object pixels
    color = np.mean(object_pixels, axis=0)

    return color[::-1]
