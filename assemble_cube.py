from pickle import load
from RubiksDetection.rpd.metafeatures import Face
import cv2 as cv
import matplotlib.pyplot as plt
from RubiksDetection.rpd.rubik_state import RubikStateEngine
import os

#read each color file in the test_data folder
# Get the path to the test_data folder
test_data_folder = './test_data'

face_arrays = []
# Iterate over each file in the test_data folder
for filename in os.listdir(test_data_folder):
    # Construct the full path to the file
    file_path = os.path.join(test_data_folder, filename)

    # Check if the file is a pickle file
    if filename.endswith('.pickle'):
        # Open the file in binary mode
        with open(file_path, 'rb') as file:
            # Unpickle the face array
            face_array = load(file)
            face_array = list(filter(lambda x: x is not None, face_array))

            # Process the face array as needed
            # ...
            face_arrays.append(face_array)

if len(face_arrays) == 6:
    print("All faces were loaded correctly")
else:
    print("Some faces were not loaded correctly")
    raise ValueError("Some faces were not loaded correctly")

# Create a RubikStateEngine object
rubik_state = RubikStateEngine()
# Iterate over each face array
for face_array in face_arrays:
    rubik_state.consume_face(face_array[0])

# Check if the cube is complete
if rubik_state.is_complete():
    print("The cube is complete")

# Fit the cube
rubik_state.fit()

#Debug the image
img = rubik_state.debug_image()
cv.imshow('Rubik State', img)
plt.show()
cv.waitKey(0)