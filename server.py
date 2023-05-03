import threading
import cv2
import base64
import numpy as np
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import face_recognition

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# 存储当前客户端的sid
client_sid = None

# 停止线程标志
stop_thread = False


def video_thread():
    global stop_thread
    cap = cv2.VideoCapture(0)

    # Load a sample picture and learn how to recognize it.
    krish_image = face_recognition.load_image_file("Facedata/Yifei.JPG")
    krish_face_encoding = face_recognition.face_encodings(krish_image)[0]

    # Load a second sample picture and learn how to recognize it.
    bradley_image = face_recognition.load_image_file("Facedata/Trump.jpg")
    bradley_face_encoding = face_recognition.face_encodings(bradley_image)[0]

    # Create arrays of known face encodings and their names
    known_face_encodings = [
        krish_face_encoding,
        bradley_face_encoding
    ]
    known_face_names = [
        "Yifei",
        "Trump"
    ]
    # Initialize some variables
    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]

        # Only process every other frame of video to save time
        if process_this_frame:
            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_names = []
            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"

                # # If a match was found in known_face_encodings, just use the first one.
                # if True in matches:
                #     first_match_index = matches.index(True)
                #     name = known_face_names[first_match_index]

                # Or instead, use the known face with the smallest distance to the new face
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]
                    name = name+ ' ' + str(1-face_distances[0])

                face_names.append(name)

        process_this_frame = not process_this_frame

        # Display the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name,  (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        # Display the resulting image
        # cv2.imshow('Video', frame)
        # 将图片转换为base64格式
        _, img_encode = cv2.imencode('.jpg', frame)
        img_base64 = base64.b64encode(img_encode).decode('utf-8')
        # 向当前客户端发送图片数据
        socketio.emit('image', {'image': img_base64}, room=client_sid)
        if stop_thread:
            break
    cap.release()
    cv2.destroyAllWindows()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def connect():
    global client_sid, video_t, stop_thread

    # 清理上一个线程
    stop_thread = True
    if 'video_t' in globals() and video_t.is_alive():
        video_t.join()

    # 将当前客户端的sid保存下来，用于向特定的客户端发送消息
    client_sid = request.sid

    print(client_sid)
    # 开启一个新的线程传输视频数据
    stop_thread = False
    video_t = threading.Thread(target=video_thread)
    video_t.start()

@socketio.on('disconnect')
def disconnect():
    global stop_thread

    # 停止当前线程
    stop_thread = True
    if 'video_t' in globals() and video_t.is_alive():
        video_t.join()

if __name__ == '__main__':

    socketio.run(app, port=5001)
