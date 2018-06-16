# if there is more than one camera and you have the wrong one, change this.
target_camera = 0
# change this if you don't want it to capture when you press space
capture_key = 32
# change this if you dont want the program to quit when you press esc
exit_key = 27
# the name of the window
window_name = "Camera"
# whether the image the camera is sending back needs to be flipped
should_flip = False
# boundary leniency; increase if you are getting invalid matches, decrease if you are getting
# lots of 'Uncertain match exceptions'
word_distance_horizontal = 27

word_distance_vertical_max = 140
word_distance_vertical_min = 20

# size of response text
result_text_scale = 1


class OutputFormat:
    """
        This class is passed to all i/o functions, it contains a set of variables that defines the formatting of output.
        Some variables in this class are string formats with access to the following variables:
        student_id: The student's id number (usually pulled from a card object)
        name: The students name.
        date: the time of entry
    """
    # File path to the output csv file
    file = "output.csv"
    # The columns to write to the file, length must equal the rows field
    columns = ["user_id", "name", "email", "date added"]
    # How each entry should be formatted
    rows = ["{student_id}", "{name}", "{student_id}@student.rmit.edu.au", "{date}"]
    # Only allow unique rows to be added to the output csv
    enforce_unique = True
    # If enforce_unique is set to true, the primary key field should be set to the value you want to be unique
    primary_key = columns[0]
    # The directory where images captured will be saved to.
    cache_dir = "cache"


class Colors:
    success = (0, 255, 0)
    failure = (0, 0, 255)
    neutral = (255, 255, 255)
    outline = (0, 0, 0)
