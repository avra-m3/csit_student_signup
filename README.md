
What you need:

    OCR_AUTH_KEY =  an environment variable, which is a google API key
    Install all files from requirements.txt using pip


Configuration options:

    # if there is more than one camera and you have the wrong one, change this.
    target_camera = 0
    # change this if you don't want it to capture when you press space
    capture_key = 32
    # change this if you dont want the program to quit when you press esc
    exit_key = 27
    # change this to use another output file, anywhere in PATH will work
    output_file = 'output.csv'
    # this is where temp images are saved, probably don't change this
    temp_image_dir = 'image_cache'
    # the name of the window
    window_name = "Camera"
    # whether the image the camera is sending back needs to be flipped
    should_flip = False
    # boundary leniency; increase if you are getting invalid matches, decrease if you are getting
    # lots of 'Uncertain match exceptions'
    word_distance_horizontal = 27
    # size of response text
    result_text_scale = 1
