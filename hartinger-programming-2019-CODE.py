#! /usr/bin/env python3

# Automatic Crystal Detection

# creator: Corinna Hartinger (corinna.hartinger@univ.ox.ac.uk)
# created October 28, 2019
# Version 3 (last edited: November 1st, 2019)


"""
PROGRAM INFORMATION

This program allows the user to chose a folder containing .jpg images, each of a single well used in protein crystallisation. All images in the folder will be checked for crystals by finding contours in the image and filtering them by size.

REQUIREMENTS:
The program must be placed in the same directory as the folder of images. The images should be of .jpg type.

OUTPUT:
Lists of the names of the images corresponding to whether 
1) a crystal was automatically detected in the image
2) no crystal was automatically detected or
3) the program was unable to decide whether there is a crystal or not.

OPTIONAL:
After the automatic image analysis, the program will ask whether the user would like to manually check the images that could not be classified unambiguously.
This will output two more lists:
4) manually detected crystals
5) manually decided no crystals are present.

"""




"""--- IMPORTS ---"""
import sys
import os
import cv2
import numpy as np


"""--- USER-TWEAKABLE VARIABLES ---"""

# name of the list containing ALL image
name_of_list = 'list_of_names_of_crystal_images.txt'

# threshold. the necessary threshold depends very much on the brightness of the images and has been set to give good results for the example images
threshold = 110

"""--- FUNCTIONS ---"""

# to create a list of all the images within the specified folder
def make_list_of_all_image_names(directory_name, name): # takes in the name of the directory, which 							was specified by the user and the name of the list
	image_name_list = open(name, 'w')
	image_name_list.write("#This is a list of all the images" \
			" that will be analysed by " + sys.argv[0] + ": \n")
	line_counter = 0

	# loops through all the images in the specified folder and attaches their name to a list 		but only if it is of .jpg type
	for entry in os.listdir(directory_name):
		if os.path.isfile(os.path.join(directory_name, entry)) and '.txt' not in entry and '.jpg' in entry:
			line_counter += 1
			image_name_list.write(entry + '\n') #appends all none .txt files in the 							    folder to a list
		elif os.path.isfile(os.path.join(directory_name, entry)) and '.txt' in entry:
			print('\nThere is/are .txt files in the folder.') 
		else: 
			print('\nFiles that are not .jpg images (or .txt) were found in the folder.\nPlease remove them to continue with the program.')
			print('\n---Program exited---')
			exit() #program exits if none .jpg image files (other than .txt 				files) are found in the folder
	
	number_of_images = line_counter
	print('\n' + str(line_counter) + ' image files found in the directory ' + \
		directory_name+ ' have been added to the list '+ name + '.\n')
	image_name_list.close()

	upper_directory_name = os.getcwd()
	
	actual_directory_name = upper_directory_name+'/'+directory_name

	return upper_directory_name, actual_directory_name, number_of_images # gives the full name 						of the specified directory and the number of images that 						were found inside it

# takes an image and makes it smaller and crops the middle part to get rid of the edges of the well 
def resize_and_crop(image_file):	
	img = cv2.imread(image_file)
	img = cv2.resize(img, (512, 384))
	crop_img = img[60:340, 90:420]

	return crop_img #returns the smaller and cropped image

# takes in an image and the threshold to use for conversion to a black and white image
def make_image_binary(image_file, threshold):
	gray = cv2.cvtColor(src = image_file, code = cv2.COLOR_BGR2GRAY)
	blur = cv2.GaussianBlur(src = gray, 
	    ksize = (7, 7), 
	    sigmaX = 5)
	(threshold, binary) = cv2.threshold(src = blur,
	    thresh = threshold, 
	    maxval = 255, 
	    type = cv2.THRESH_BINARY)

	binary_inv = cv2.bitwise_not(binary)
	
	return binary_inv #returns an image that was converted to grayscale, then blurred, then 				converted to binary image, which was then inverted

# takes in the image that was cropped and the same cropped image that was converted to a binary image
#from the binary image it finds the contours and draws them onto the cropped image
def find_and_draw_contours(cropped_image, binary_image):
	(contours, _) = cv2.findContours(image = binary_image, 
    mode = cv2.RETR_EXTERNAL,
    method = cv2.CHAIN_APPROX_SIMPLE)
	list_of_area = [0]
	for contour in contours:
		cv2.drawContours(image = cropped_image, 
		    contours = contours, 
		    contourIdx = -1, 
		    color = (0, 0, 255), 
		    thickness = 3)
		area =abs((cv2.contourArea(contour, True)))
		list_of_area.append(area)
	
	biggest_shape = max(list_of_area)
	whole_area = sum(list_of_area)

	#to classify the image it looks at the biggest shape found in the image
	#if it is within a certain range it is probably not noise or contaminations but a crystal

	result = 'undetermined'
	if biggest_shape > 6000 and biggest_shape < 12000 and whole_area < 12000:
		result = 'Crystal detected!'
	elif biggest_shape > 1900 and biggest_shape <= 6000:
		result = 'There may be a crystal in this image!'
	else:
		result = 'No crystal detected!'
		
	return cropped_image, result #returns the cropped image which now has the contours on it


# function to open the images that could not be classified unambiguously and show them to the user so they can decide whether it contains a crystal or not and append it to the appropriate list
# takes the list with the 'maybe' images and the exact name of the directory that was specified
def looping_through_maybes(maybe_list_file, actual_directory_name):
	
	maybe_list = open(maybe_list_file, 'r')
	list_of_checked_positive = open('Manually_crystals_detected.txt', 'w')
	list_of_checked_negative = open('Manually_no_crystals_detected.txt', 'w')

	os.chdir(actual_directory_name)
	
	image_counter = 0
	print('Press \'y\' to classify as crystal.\nPress \'n\' to classify as not a crystal.\nPress \'Esc\' to exit.\n')
	for line in maybe_list:
		image_name = line.strip()
		
		image_counter += 1
		img = cv2.imread(image_name)
		img = cv2.resize(img, (512, 384))
		

		cv2.imshow(('Image '+str(image_counter)), img)
		
		
		if cv2.waitKey(0) == ord('y'):
			print('Image '+str(image_counter)+' will be added to the Manually_crystals_detected.txt file.')
			cv2.destroyAllWindows()
			list_of_checked_positive.write(image_name + '\n')
		elif cv2.waitKey(0) == ord('n'):
			print('Image '+str(image_counter)+' will be added to the Manually_no_crystals_detected.txt file.')
			cv2.destroyAllWindows()
			list_of_checked_negative.write(image_name + '\n')
		elif cv2.waitKey(0) == 27:
			print('You decided to stop.\n')
			cv2.destroyAllWindows()
			break
		else:
			cv2.destroyAllWindows()			
			print('Invalid key. Press \'y\', \'n\' or \'Esc\'.')
			
	else:
		print('\nAll files have been analysed.\n')
		print('\n---Program finished---')
		
	maybe_list.close()
	list_of_checked_positive.close()
	list_of_checked_negative.close()

"""--- END OF FUNCTIONS ---"""







"""--- PROGRAM PROCEDURE ---"""

#chose the directory containing the images, either via 2nd command line argument or via input
if len(sys.argv) > 1:
	directory_name = sys.argv[1]
else:
	directory_name = input('\nPlease write the name of the directory with images to be analysed: \n')
	if directory_name == '':
		print('\nPlease input the name of the directory with the images to be analysed,'\
			 ' either as second argument in the command line or when prompted.')
		print('\n---Programm exited---')
		exit()





#here the program makes a list of all the images in the specified folder
#will exit and send an error message if the directory was not found
try:
	current_directory_name, actual_directory_name, number_of_images = make_list_of_all_image_names(directory_name, name_of_list)

except FileNotFoundError:
	print('\nYou called the directory: ' + directory_name)
	print('This directory was not found.\nPlease check the spelling and that the directory is in the same folder as the program ' + sys.argv[0] + '.')
	print('\n---Program exited---')
	exit()


#next it opens the list with the file names
#the program changes to the directory with the images
#the images from the list are then opened, one after the other, and processed
#based on the results from the analysis the file name is added to the lists 'Crystal detected', 'Check for crystal manually' or 'No crystal detected'

list_of_file_names = open(name_of_list, 'r')
yes = open('Crystal_detected.txt', 'w')
no = open('No_crystal_detected.txt', 'w')
maybe = open('Check_for_crystals.txt', 'w')

os.chdir(actual_directory_name)

image_counter = 0
yes_counter = 0
no_counter = 0
maybe_counter = 0
for line in list_of_file_names:
	image_name = line.strip()
	if '#' not in line: #to not get the description above the list
		image_counter += 1
		cropped_image = resize_and_crop(image_name) #take the image and crops it
		binary_image = make_image_binary(cropped_image, threshold) #takes the cropped image 										and makes it binary
		
		cropped_with_contours, result = find_and_draw_contours(cropped_image, binary_image)
		#find the contours of any shapes and decides based on the size of the biggest shape 			whether there is a crystal
		
		if result == 'Crystal detected!':
			yes_counter +=1
			yes.write(image_name + '\n')
		elif result == 'No crystal detected!':
			no.write(image_name + '\n')
			no_counter += 1
		elif result == 'There may be a crystal in this image!':
			maybe.write(image_name + '\n')
			maybe_counter += 1
		else:
			print('Image was not classified!')
		print('\nImage number ' + str(image_counter) +' in list was processed.\nThe result was: '+ result)

print('\n----------------------\nAnalyses of images has finished:')
print(str(yes_counter) + ' images were found to have crystals.\n'+ str(no_counter) +' images were found to not contain crystals and\n' +str(maybe_counter) + ' images could not be classified unambiguously.')

list_of_file_names.close()
yes.close()
no.close()
maybe.close()
os.chdir(current_directory_name)


#if there are images that could not be classified clearly it will ask the user whether they want to check them manually
if maybe_counter > 0:
	user_looping_decision = input('\nWould you like to manually go through the images in the Check_for_crystals.txt list file?\nEnter: y for Yes, enter anything else to stop.\n')

	if user_looping_decision == 'y' or user_looping_decision == 'Y':
		print('\nYou decided to manually classify the images that could not be classified unambiguously.\n')
		looping_through_maybes('Check_for_crystals.txt', actual_directory_name)
	else:
		print('\nYou decided not to check the images manually.')
		print('\n---Program finished---')
		exit()

"""--- END OF PROGRAM PROCEDURE ---"""




