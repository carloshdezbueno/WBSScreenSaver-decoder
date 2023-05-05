import argparse
import cv2 as cv
import numpy as np

import colors


def main():
    argument_parser = argparse.ArgumentParser(description='Tool for decoding message in captured footage of screensaver')

    argument_parser.add_argument('-i', '--video-file', type=str, required=True, help='Video file to process')

    argument_parser.add_argument('-X', '--rect-horizontal', type=int, required=True, help='Position of capture rectangle (horizontal, top-left corner)')
    argument_parser.add_argument('-Y', '--rect-vertical', type=int, required=True, help='Position of capture rectangle (vertical, top-left corner)')
    argument_parser.add_argument('-W', '--rect-width', type=int, required=True, help='Width of capture rectangle')
    argument_parser.add_argument('-H', '--rect-height', type=int, required=True, help='Height of capture rectangle')

    argument_parser.add_argument('-s', '--min-saturation', type=int, required=False, help='Minimum HSV saturation of analyzed pixels (0-255)', default=40)
    argument_parser.add_argument('-v', '--min-brightness', type=int, required=False, help='Minimum HSV brightness of analyzed pixels (0-255)', default=150)

    argument_parser.add_argument('-r', '--red-coeff', type=float, required=False, help='Coefficient applied to red component (0-1)', default=1.0)
    argument_parser.add_argument('-g', '--green-coeff', type=float, required=False, help='Coefficient applied to green component (0-1)', default=1.0)
    argument_parser.add_argument('-b', '--blue-coeff', type=float, required=False, help='Coefficient applied to blue component (0-1)', default=1.0)

    argument_parser.add_argument('-c', '--min-coverage', type=float, required=False, help='Minimum percentage of pixels in mask relative to capture area (0-100)', default=0.5)
    argument_parser.add_argument('-f', '--min-frames', type=int, required=False, help='Minimum number of frames with same color to register a change', default=5)
    
    argument_parser.add_argument('-F', '--display-feedback', required=False, help='Display video feedback', action='store_true')
    argument_parser.add_argument('-d', '--debug', required=False, help='Enable debugging', action='store_true')

    args = argument_parser.parse_args()

    color_coeffs = [args.red_coeff, args.green_coeff, args.blue_coeff]


    # Color in previous frame (frame -1 is considered to be red)
    previous_frame_color = np.array([180, 0, 0])

    previous_color = []
    frames_with_same_color = 0

    decoded_bits = ""

    capture = cv.VideoCapture(args.video_file)
    if not capture.isOpened():
        print('Could not open file:', args.video_file)
        exit(1)

    while True:
        retval, frame = capture.read()
        if not retval:
            if args.debug:
                print('Next frame not found, exiting')
            capture.release()
            cv.destroyAllWindows()
            break

        # Slide the video to the region selected by the user
        interval_h = slice(args.rect_horizontal, args.rect_horizontal + args.rect_width)
        interval_v = slice(args.rect_vertical, args.rect_vertical + args.rect_height)

        color = colors.get_object_color(frame[interval_v, interval_h], args.min_saturation, args.min_brightness, args.min_coverage, color_coeffs, args.debug)
        if color is None:
            closest = previous_frame_color
        else:
            closest = colors.get_closest_color(color[0], color[1], color[2])

        # Display the color in the frame
        if args.display_feedback or args.debug:
            font = cv.FONT_HERSHEY_SIMPLEX
            cv.putText(frame, str(closest), (50, 50), font, 1, (int(closest[2]), int(closest[1]), int(closest[0])), 2, cv.LINE_AA)
            cv.rectangle(frame, (interval_h.start, interval_v.start), (interval_h.stop, interval_v.stop), (255,0,0), 2)

            # Show the frame Press Q to quit.
            cv.imshow('Feedback', frame)
            if cv.waitKey(1) & 0xFF == ord('q'):
                break

        # In case a fake change occurs, this prevents it
        if not np.array_equal(closest, previous_frame_color):
            frames_with_same_color = 0
            previous_color = previous_frame_color
            previous_frame_color = closest
        else:
            frames_with_same_color += 1

        if frames_with_same_color == args.min_frames:
            if args.debug:
                print("Color change at TS: {:.6f}".format(capture.get(cv.CAP_PROP_POS_MSEC)/1000), "\t-\tChanged from ", previous_color, " to ", closest)

            if len(previous_color) > 0:
                current_index = colors.get_color_index(closest)
                prev_index = colors.get_color_index(previous_color)
                if ((current_index - prev_index) % 3) == 1:
                    # Shift to the right = '1'
                    decoded_bits += '1'
                    if args.debug:
                        print('Decoded: 1')
                else:
                    # Shift to the left = '0'
                    decoded_bits += '0'
                    if args.debug:
                        print('Decoded: 0')
                    

    print('\nDecoded', len(decoded_bits), 'bits:', decoded_bits)

    decoded_bytes = [int(decoded_bits[i*8:i*8+8],2) for i in range(len(decoded_bits)//8)]
    try:
        terminator = decoded_bytes.index(0)
        print('Discarding additional', len(decoded_bits) - 8 * (terminator + 1), 'bits after terminator')
        decoded_bytes = decoded_bytes[:terminator]
    except ValueError:
        print('No terminator found in byte sequence')

    decoded_string = ''.join(chr(c) for c in decoded_bytes)
    print('\nDecoded string:', decoded_string)


if __name__ == '__main__':
    main()