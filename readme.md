## 1.Introduction & Architecture

The face recognition system adopts regional feature analysis algorithm, integrates computer image processing technology and bio-statistics principle, uses computer image processing technology to extract portrait feature points from video, uses bio-statistics principle to analyze and establish a mathematical model, and realizes Face retrieval in face image database. With the advancement of machine learning and computer vision techniques, facial recognition has become more accurate and efficient, enabling its widespread adoption in many industries.
In my first step, I focus on setting up a basic web application using Flask and related libraries to run on the web. Our primary goal is to enable the webcam and add buttons to start and stop recording video. This step lays the foundation for the second part of the project, which involves real-time facial recognition.
In my second step, I use OpenCV and face_recognition libraries to perform real-time facial recognition on the captured video stream. This involves detecting and recognizing faces in the video feed, comparing them with known faces in a database, and displaying the results in real-time.

## 2.Technologies

### 2.1.OpenCV

OpenCV is an computer vision library that is open-source and widely used for real-time image and video processing. OpenCV offers a range of functions and tools for image processing, (object recognition, facial recognition, motion tracking .etc.) OpenCV is critical to the project since it enables the application to detect faces in real-time video feeds.

### 2.2.Flask

Flask is a Python-based micro web framework that is used for developing web applications. Flask offers a range of features, including easy-to-use routing, templates, and support for web sockets. Flask makes it easy to develop and deploy web applications.

### 2.3.Flask-SocketIO

Flask-SocketIO is an extension for Flask that enables real-time, bi-directional communication between the server and the client. Flask-SocketIO is built on top of the popular Socket.IO library and offers support for web sockets, long-polling, and other real-time communication technologies. Flask-SocketIO is essential to the project since it enables the application to capture real-time video from the user's webcam and send it to the server for processing.

### 2.4.Face_recognition

face_recognition is a Python-based library that is built on top of OpenCV and offers facial recognition functionality. The library uses machine learning algorithms to detect and recognize faces in images and videos. face_recognition is used in the project to compare the detected faces in the real-time video feed to a database of known faces. Before downloading the library of face_recognition, it is needed to download CMake and dlib first. Since my python version is 3.9. the usable version of CMake is 3.26.3(windows-x86-64); the version of dlib is 19.22.99(the latest one I suppose).
With Flask and Flask-SocketIO, developers can easily create web applications that can capture video from a device's camera and send it to the server for processing. With OpenCV and face_recognition, developers can perform real-time facial recognition on the captured video feed, making it possible to identify individuals in real-time. These technologies work together to provide a powerful set of tools for building web-based facial recognition systems that can run in real-time on a range of devices.

## 3.Functional & Non-Functional Requirements

### 3.1.Functional Requirements

| requirements              | explanation                                                                                                                                                                                                                           |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Webcam Access Permissions | ‘cv2.VideoCapture(0)’ will return video from the first webcam on the computer. Normally only have one default camera.                                                                                                                 |
| Face Detection            | Use the face detection algorithm in the OpenCV library to detect faces in the frames read.                                                                                                                                            |
| Face Feature Extraction   | Use the face feature extraction algorithm in the face_recognition library to extract the feature vector of the face in the frame.                                                                                                     |
| Face Recognition          | Compare the face feature vector extracted from the frame with the face feature vector in the existing database, and identify the user corresponding to the face in the picture                                                        |
| Show results              | Show the results of recognition, including: display the face read by the current camera and which person in the database has the highest similarity, draw a box around the face, display the name and similarity (ie 1-face distance) |

### 3.2.Non-functional Requirements

| requirements | explanation                                                                                                                                                                                  |
| ------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Usability    | The application should have a good user interface, easy to operate and understand. The function of the button should be clearly marked, and a hover prompt should be added when appropriate. |
| Performance  | The application needs to complete tasks such as face detection, feature extraction, and recognition within a reasonable time to ensure user experience.                                      |
| scalability  | Applications need to be scalable to accommodate growing user and data volumes.                                                                                                               |

## 4.Implementation

By analyzing the needs of course design, I decided to divide my back-end code into two parts to write. The first part involves displaying the video on the web, and the second part involves face recognition.

### 4.1.Display video on web

This is a simple webcam live streaming application based on HTML and JavaScript. Based on some conventional principles, I first compiled the front-end HTML page.
It uses Socket.IO for two-way communication between server and client to display live video stream on client.
What this code does is create two buttons on the HTML page, one to start the camera live stream and the other to stop the live stream. Additionally, there is an image tag on the page for displaying a live video stream on the client side.
`<script src="//cdnjs.cloudflare.com/ajax/libs/socket.io/4.1.2/socket.io.min.js" />`
This line of code imports the Socket.IO library, a JavaScript library for real-time two-way communication between client and server. The function of this library is to establish communication between the client and the server through WebSocket or polling technology, so that the server can push data to the client in real time. The library provides a set of APIs that developers can use to implement functions such as receiving data from the server, sending data, and event processing. Here, we implement real-time communication between client and server by introducing Socket.IO library.
In the next JavaScript section, the code initializes the Socket.IO client (const socket = io();) and connects to the server (socket.connect();). When the user clicks the start button, an event is fired to connect to the server. When the user clicks the stop button, the connection is closed and the image tag is reset to stop the display of the video stream. Both event listeners are very basic and common javascript methods.
Finally, since the camera permission is enabled by the server, the client is only responsible for displaying. Therefore, for the convenience of frame reading, when the client receives the image data transmitted from the server, the code converts the data into base64 encoding format and displays it in the image A live video stream is shown on the tab.

```python
socket.on('image', (imageData) => {
  let data = imageData.image
  video.src = 'data:image/jpeg;base64,' + data;
});
```

Then we can turn to server side. First thing to do is initializing a web server. Below is the official code for adding Flask-SocketIO to a Flask application, which I used directly in my code.

```
from flask import Flask, render_template, request
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
if __name__ == '__main__':
    socketio.run(app, port=5001)
```

The socketio.run() function encapsulates the start of the web server and replaces the standard Flask development server start of app.run(). Set the port to 5001.
Before defining my thread function, I define two global variables: the current client id and whether the thread is stopped. Define a thread function for processing video stream data. Authorize the camera through cap = cv2.VideoCapture(0), and call the cap.read() method to return two values: ret and frame, which respectively represent the boolean value of whether the image reading is successful and the read image frame. If ret is False, it means that the image reading failed and the loop can be exited. If the frame is successfully read, the image will be converted to base64 format, and then sent the image data to the current client.

```
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        _, img_encode = cv2.imencode('.jpg', frame)
        img_base64 = base64.b64encode(img_encode).decode('utf-8')
        socketio.emit('image', {'image': img_base64}, room=client_sid)
```

Define a routing function for rendering pages; define a Socket.IO event handler for client connection (connect()); define another Socket.IO event handler for client disconnection (disconnect()).

### 4.2.Face Recognition

Add face recognition into the previous server part code. First step is to read face information from given images. Load the image file from the specified path and store it in the variable yifei_image. Perform face encoding on yifei_image, generate a list containing face feature vectors, take the first feature vector and store it in the variable yifei_face_encoding. Repeat the above work, and then create a list of known face encoding vectors (according to the requirements, it should be necessary to read three different faces, so I stored two faces, namely myself and trump, and I let the other face be used as ‘unknown’) and a list of names of known faces.

```
yifei_image = face_recognition.load_image_file("Facedata/Yifei.JPG")
yifei_face_encoding = face_recognition.face_encodings(yifei_image)[0]
known_face_encodings = [ yifei_face_encoding, trump_face_encoding]
known_face_names = ["Yifei", "Trump"]
Convert the picture from BGR format to RGB format, because OpenCV uses BGR format, and face_recognition uses RGB format.
rgb_small_frame = small_frame[:, :, ::-1]
```

Then use the face_recognition.face_locations function to find all the face locations in the current video frame, returning it as a list of rectangles. Then use the face_recognition.face_encodings function to calculate the encoding of each face. Here, the list comprehension and loop traversal are used to store the codes of all faces in a list.
Next, by traversing the encoding of each face, use the face_recognition.compare_faces function to compare whether the encoding of the current face matches the pre-saved face encoding. If the match is successful, get the corresponding person's name from the known_face_names list. Otherwise, use the face_recognition.face_distance function to find the distance between the current face code and known face codes, and select the known face code with the smallest distance as the matching result. Add matching person names to the face_names list. If process_this_frame is False, skip the current frame and proceed to the next frame.

```
face_names = []
for face_encoding in face_encodings:
# See if the face is a match for the known face(s)
matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
name = "Unknown"
# use the known face with the smallest distance to the new face
face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
best_match_index = np.argmin(face_distances)
if matches[best_match_index]:
  name = known_face_names[best_match_index]
  name = name+ ' ' + str(1-face_distances[0])
face_names.append(name)
```

The last part of the code is to draw the face recognition result on the original video frame, including marking the position of the face with a rectangular frame, and adding the corresponding name tag below the face. Finally output the video with the recognition result.

```
  # Draw a box around the face
  cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
  # Draw a label with a name below the face
  cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
  font = cv2.FONT_HERSHEY_DUPLEX
  cv2.putText(frame, name,  (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
```

### 4.2.1.Compress the frames

Due to the large amount of calculation for face recognition, in order to improve the processing speed, the code reduces the video frame to 1/4 of the original size for processing. Add this part before the process of ‘Convert the image from BGR color to RGB color’.
small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
After finishing analyzing, it is needed to draw the box around face. In this step, the program should scale back up face locations since the frame I detected in was scaled to 1/4 size. Top, button, left, right (four parameters used in previous key code for locate the box) should all multiply 4.

## 5.Conclusion

This paper introduces a real-time camera face recognition web application based on Flask, Flask-SocketIO, OpenCV, and face_recognition. The application has good user interaction and real-time performance, and can be widely used in practical applications in the field of face recognition.
The use of Flask and Flask-SocketIO provides a robust and extensible framework for developing web applications with real-time capabilities. This application uses OpenCV and the face_recognition library to process video frames and recognize faces in real time. OpenCV is a powerful computer vision library that can efficiently process video frames and provides a variety of computer vision algorithms. face_recognition is a popular and accurate face recognition library whose integration makes it possible to recognize known faces and detect unknown faces in real time. The use of these libraries provides strong support for the real-time performance of the application.
The application had several functional requirements that were met, including the ability to capture and process video streams from the camera, the ability to detect and recognize faces in real-time, and the ability to display video streams containing detected faces with associated tags.
In terms of non-functional requirements, applications are designed with performance and usability in mind. The real-time nature of applications requires efficient and optimized code, and using a lightweight web framework like Flask can achieve fast responses and reduce overhead. I think the app's interface design is intuitive and user-friendly, with clear labels and feedback to the user.
Overall, a real-time face recognition web application built on Flask, Flask-SocketIO, OpenCV, and face_recognition is a powerful and versatile tool with a wide range of potential applications. Our application can be extended to more practical application scenarios, such as security systems, attendance systems, face payment systems, etc. In these fields, face recognition technology has been widely used. While there are still challenges to be addressed, such as accuracy and privacy concerns, we believe this application has important practical implications and potential.
