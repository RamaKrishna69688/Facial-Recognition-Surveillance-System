import cv2
import face_recognition
import os
import numpy as np
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import time
def load_authorized_images():
    authorized_images = []
    authorized_names = []
    authorized_images_dir = 
    for person_name in os.listdir(authorized_images_dir):
        person_folder = os.path.join(authorized_images_dir, person_name)
        if os.path.isdir(person_folder):
            for image_name in os.listdir(person_folder):
                if image_name.endswith(('.jpg', '.png')): 
                    image_path = os.path.join(person_folder, image_name)
                    image = cv2.imread(image_path)
                    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    encoding = face_recognition.face_encodings(image_rgb)[0]
                    authorized_images.append(encoding)
                    authorized_names.append(person_name)   
    return authorized_images, authorized_names
def send_alert_email(sender_email, sender_password, recipient_email, subject, body, image_path):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    try:
        with open(image_path, 'rb') as f:
            img_data = MIMEImage(f.read())
            msg.attach(img_data)
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)
        server.quit()
        print(f"Alert email sent to {recipient_email}!")
    except Exception as e:
        print(f"Failed to send email. Error: {e}")
cap = cv2.VideoCapture(0)
authorized_images, authorized_names = load_authorized_images()
threshold = 0.4  
unknown_detected = {}
sender_email = 'sender_email@gmail.com'
sender_password = 'gmailpassword/app password'
recipient_email = 'recipient_email@gmail.com'
subject = 'Alert: Unauthorized Person Detected'
while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    faces = face_recognition.face_locations(rgb_frame)
    encodings = face_recognition.face_encodings(rgb_frame, faces)
    print(f"Detected faces: {len(faces)}")
    for (top, right, bottom, left), face_encoding in zip(faces, encodings):
        face_distances = face_recognition.face_distance(authorized_images, face_encoding)
        print(f"Face Distances: {face_distances}")
        print(f"Threshold: {threshold}")
        if min(face_distances) < threshold:
            match_index = np.argmin(face_distances)
            name = authorized_names[match_index]
            color = (0, 255, 0)  
        else:
            name = "Unknown"
            color = (0, 0, 255)  
            if name == "Unknown" and (tuple(face_encoding) not in unknown_detected):
                unknown_detected[tuple(face_encoding)] = time.time()  
                unknown_image = frame[top:bottom, left:right]
                unknown_image_path = "unknown_person.jpg"
                cv2.imwrite(unknown_image_path, unknown_image)
                body = f"An unknown person has been detected. Please check the surveillance feed."
                send_alert_email(sender_email, sender_password, recipient_email, subject, body, unknown_image_path)
                time.sleep(5) 
                del unknown_detected[tuple(face_encoding)]
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, color, 1)
    cv2.imshow("Surveillance Camera", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
