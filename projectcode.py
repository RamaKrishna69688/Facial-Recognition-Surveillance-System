import cv2  # OpenCV library for image processing and video capturing
import face_recognition  # Library to detect and recognize faces
import os  # To interact with the file system
import numpy as np  # Numpy for numerical operations
import smtplib  # Library for sending emails
from email.mime.multipart import MIMEMultipart  # MIME multipart to structure email
from email.mime.text import MIMEText  # To add the email body text
from email.mime.image import MIMEImage  # To send images as attachments
import time  # For working with time-related operations

# Function to load and encode authorized images
def load_authorized_images():
    authorized_images = []  # List to store the encoded images of authorized people
    authorized_names = []  # List to store the names corresponding to the images
    authorized_images_dir = "path_to_your_image_dataset"  # Replace with the actual path of your images

    # Loop through all folders (each folder represents a person)
    for person_name in os.listdir(authorized_images_dir):
        person_folder = os.path.join(authorized_images_dir, person_name)
        if os.path.isdir(person_folder):  # Ensure it is a directory (person folder)
            for image_name in os.listdir(person_folder):  # Loop through each image in the folder
                if image_name.endswith(('.jpg', '.png')):  # Check if the file is an image
                    image_path = os.path.join(person_folder, image_name)  # Get the full path of the image
                    image = cv2.imread(image_path)  # Read the image using OpenCV
                    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert image from BGR to RGB format
                    encoding = face_recognition.face_encodings(image_rgb)[0]  # Encode the face from the image
                    authorized_images.append(encoding)  # Append the encoding to the authorized images list
                    authorized_names.append(person_name)  # Append the name to the list
    return authorized_images, authorized_names  # Return the list of encoded images and names

# Function to send an email alert with an image attachment
def send_alert_email(sender_email, sender_password, recipient_email, subject, body, image_path):
    msg = MIMEMultipart()  # Create a MIME message
    msg['From'] = sender_email  # Set the sender email
    msg['To'] = recipient_email  # Set the recipient email
    msg['Subject'] = subject  # Set the email subject
    msg.attach(MIMEText(body, 'plain'))  # Attach the body of the email in plain text

    try:
        # Open and read the image to send as an attachment
        with open(image_path, 'rb') as f:
            img_data = MIMEImage(f.read())  # Read the image data
            msg.attach(img_data)  # Attach the image to the email

        # Setup the SMTP server and login with the sender's credentials
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)  # Use Gmail SMTP server with SSL
        server.login(sender_email, sender_password)  # Login to the server
        text = msg.as_string()  # Convert the message to string format
        server.sendmail(sender_email, recipient_email, text)  # Send the email
        server.quit()  # Quit the server after sending the email
        print(f"Alert email sent to {recipient_email}!")  # Confirmation message
    except Exception as e:
        print(f"Failed to send email. Error: {e}")  # Error handling if email fails to send

# Initialize the webcam
cap = cv2.VideoCapture(0)

# Load the authorized images and names
authorized_images, authorized_names = load_authorized_images()

# Set a threshold for facial recognition distance (higher means stricter matching)
threshold = 0.4

# Dictionary to track unknown faces that have already been detected
unknown_detected = {}

# Email credentials (ensure to replace with your actual credentials)
sender_email = 'sender_email@gmail.com'
sender_password = 'your_gmail_password_or_app_password'  # Gmail password or app-specific password
recipient_email = 'recipient_email@gmail.com'
subject = 'Alert: Unauthorized Person Detected'  # Subject for the email

# Main loop to capture video from the webcam
while True:
    ret, frame = cap.read()  # Capture a frame from the webcam
    if not ret:
        print("Failed to grab frame")
        break  # Exit the loop if frame is not captured

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert the frame to RGB format for face recognition
    faces = face_recognition.face_locations(rgb_frame)  # Detect faces in the frame
    encodings = face_recognition.face_encodings(rgb_frame, faces)  # Get face encodings for the detected faces

    print(f"Detected faces: {len(faces)}")  # Print the number of faces detected

    # Loop through each face detected in the frame
    for (top, right, bottom, left), face_encoding in zip(faces, encodings):
        # Calculate the distance between the current face and all authorized faces
        face_distances = face_recognition.face_distance(authorized_images, face_encoding)
        print(f"Face Distances: {face_distances}")  # Print the calculated distances
        print(f"Threshold: {threshold}")  # Print the threshold value

        # Check if the face matches any authorized face
        if min(face_distances) < threshold:  # If the minimum distance is below the threshold, it's a match
            match_index = np.argmin(face_distances)  # Get the index of the best match
            name = authorized_names[match_index]  # Get the name of the matched person
            color = (0, 255, 0)  # Green color for authorized person
        else:
            name = "Unknown"  # Mark the person as "Unknown" if no match is found
            color = (0, 0, 255)  # Red color for unknown person

            # Check if the unknown person is not already detected (to prevent multiple alerts for the same person)
            if name == "Unknown" and (tuple(face_encoding) not in unknown_detected):
                unknown_detected[tuple(face_encoding)] = time.time()  # Add to unknown_detected dictionary
                unknown_image = frame[top:bottom, left:right]  # Crop the face from the frame
                unknown_image_path = "unknown_person.jpg"  # Set the path to save the unknown person image
                cv2.imwrite(unknown_image_path, unknown_image)  # Save the image of the unknown person

                # Send an alert email
                body = f"An unknown person has been detected. Please check the surveillance feed."
                send_alert_email(sender_email, sender_password, recipient_email, subject, body, unknown_image_path)

                time.sleep(5)  # Wait for 5 seconds before checking for other unknown faces to avoid multiple alerts
                del unknown_detected[tuple(face_encoding)]  # Remove the entry from unknown_detected after the alert

        # Draw a rectangle around the face and display the name of the person
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        font = cv2.FONT_HERSHEY_DUPLEX  # Choose the font for the name
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, color, 1)  # Display the name on the frame

    # Show the video feed with the detected faces
    cv2.imshow("Surveillance Camera", frame)

    # Break the loop if 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()

