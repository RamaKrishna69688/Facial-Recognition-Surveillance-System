# Facial-Recognition-Surveillance-System
A facial recognition-based surveillance system that identifies authorized individuals and sends an alert email with an image when an unknown person is detected.

This project is a real-time facial recognition-based surveillance system built with Python. It uses the **OpenCV** and **face_recognition** libraries to detect and recognize faces from a webcam feed. If an unknown person is detected, the system sends an email alert with the image of the unknown person.

## Features

- **Real-time Face Detection**: Detects faces in live video feed from the webcam.
- **Face Recognition**: Compares detected faces with a preloaded set of authorized images.
- **Email Alerts**: Sends an email notification with the image of the unknown person when detected.
- **Threshold Matching**: Allows setting a confidence threshold to control how strictly faces need to match.

## Installation

1. **Clone the repository**:
   First, clone this repository to your local machine:
   ```bash
   git clone https://github.com/yourusername/yourrepo.git
Install the required dependencies: This project requires Python 3 and several libraries. You can install them using pip:

pip install opencv-python face_recognition numpy smtplib
Prepare the authorized images:

Create a folder named Authorised_images in your project directory.
Inside this folder, create subfolders with the names of the authorized people (e.g., John_Doe).
Add image files (e.g., .jpg or .png) of those people inside their respective subfolders.
Usage
Edit the email settings:

Open the surveillance_system.py file.
Replace sender_email, sender_password, and recipient_email with your email details.
Run the script: To start the facial recognition system, simply run:

bash
python surveillance_system.py
The system will start the webcam, detect faces, and check if they match the authorized faces. If an unknown face is detected, an email alert will be sent.

Stop the system: Press 'q' to quit the system at any time.
