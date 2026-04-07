import cv2
import os
import csv
from datetime import datetime
from django.http import StreamingHttpResponse, JsonResponse
from django.shortcuts import render

# camera global
camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# face model
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

# dataset folder
DATASET_PATH = "dataset"
if not os.path.exists(DATASET_PATH):
    os.makedirs(DATASET_PATH)


# 🔥 live stream
def gen_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


def camera_feed(request):
    return StreamingHttpResponse(
        gen_frames(),
        content_type='multipart/x-mixed-replace; boundary=frame'
    )


def capture(request):
    name = request.GET.get('name')

    success, frame = camera.read()
    if not success:
        return JsonResponse({'status': 'error'})

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    if len(faces) == 0:
        return JsonResponse({'status': 'no_face'})

    # save face
    for (x, y, w, h) in faces:
        face_img = frame[y:y+h, x:x+w]
        filepath = os.path.join(DATASET_PATH, f"{name}.jpg")
        cv2.imwrite(filepath, face_img)

    # 🔥 current date
    today = datetime.now().strftime("%Y-%m-%d")

    file_exists = os.path.isfile("attendance.csv")
    already_registered = False

    if file_exists:
        with open("attendance.csv", "r") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 3:
                    saved_name, saved_time, saved_date = row

                    # ✅ same name + same date
                    if saved_name == name and saved_date == today:
                        already_registered = True
                        break

    if already_registered:
        return JsonResponse({'status': 'already_registered'})

    # ✅ save attendance
    with open("attendance.csv", "a", newline="") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(["Name", "Time", "Date"])

        time_now = datetime.now().strftime("%H:%M:%S")
        writer.writerow([name, time_now, today])

    return JsonResponse({'status': 'success'})
def home(request):
    return render(request, 'app/index.html')