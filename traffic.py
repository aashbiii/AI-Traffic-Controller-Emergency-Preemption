import sys
import time
import serial
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QFileDialog, QVBoxLayout, QHBoxLayout, QSpinBox
from PyQt5.QtCore import QTimer
import torch
import cv2
import os
import json
import requests
from traffic_api import traffic_data, start_api_server

# Load YOLO Model
YOLO_PATH = "yolov5"
model = torch.hub.load(YOLO_PATH, 'custom', path=f"{YOLO_PATH}/yolov5s.pt", source='local')

# Vehicle & Emergency Classes
VEHICLE_CLASSES = ['car', 'bus', 'truck', 'motorbike']
EMERGENCY_CLASSES = ['ambulance', 'firetruck', 'police', 'fire truck']

# Serial Connection (Change COM port if needed)
try:
    arduino = serial.Serial('COM6', 9600, timeout=1)
    time.sleep(2)
except Exception as e:
    print("\u26a0\ufe0f Arduino not connected:", e)
    arduino = None

class TrafficLightSimulator(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Traffic Light System")
        self.setGeometry(100, 100, 700, 500)

        self.active_road = 1
        self.timer_seconds = 60
        self.default_timer = 60
        self.one_time_timer_active = False

        self.manual_switch_pending = False

        self.road_data = {
            1: {'vehicles': 0, 'emergency': 0},
            2: {'vehicles': 0, 'emergency': 0}
        }

        self.initUI()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)
        
        self.android_timer = QTimer()
        self.android_timer.timeout.connect(self.apply_android_input)
        self.android_timer.start(2000)  # Every 2 seconds


        self.send_arduino_signal()
        start_api_server()

    def initUI(self):
        layout = QVBoxLayout()

        self.road1_label = QLabel("\ud83d\udd34 Road 1 (Red)", self)
        self.road2_label = QLabel("\ud83d\udfe2 Road 2 (Green)", self)

        self.upload_road1_btn = QPushButton("Upload Road 1 Image", self)
        self.upload_road1_btn.clicked.connect(lambda: self.upload_image(1))
        self.upload_road2_btn = QPushButton("Upload Road 2 Image", self)
        self.upload_road2_btn.clicked.connect(lambda: self.upload_image(2))

        self.switch_btn = QPushButton("\ud83d\udd04 Switch Roads", self)
        self.switch_btn.clicked.connect(self.manual_switch_trigger)

        self.timer_input = QSpinBox(self)
        self.timer_input.setRange(5, 300)
        self.timer_input.setValue(self.timer_seconds)

        self.set_timer_btn = QPushButton("Set Timer", self)
        self.set_timer_btn.clicked.connect(self.set_custom_timer)

        self.one_time_input = QSpinBox(self)
        self.one_time_input.setRange(5, 300)
        self.one_time_input.setValue(15)

        self.set_one_time_btn = QPushButton("Set Current Timer", self)
        self.set_one_time_btn.clicked.connect(self.set_one_time_timer)

        self.road1_count = QLabel("Road 1 - Vehicles: 0 | Emergency: 0", self)
        self.road2_count = QLabel("Road 2 - Vehicles: 0 | Emergency: 0", self)
        self.timer_label = QLabel(f"Time Remaining: {self.timer_seconds}s", self)
        self.status_label = QLabel("Status: Waiting for input...", self)

        road1_layout = QVBoxLayout()
        road1_layout.addWidget(self.road1_label)
        road1_layout.addWidget(self.upload_road1_btn)
        road1_layout.addWidget(self.road1_count)

        road2_layout = QVBoxLayout()
        road2_layout.addWidget(self.road2_label)
        road2_layout.addWidget(self.upload_road2_btn)
        road2_layout.addWidget(self.road2_count)

        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self.switch_btn)
        controls_layout.addWidget(self.timer_input)
        controls_layout.addWidget(self.set_timer_btn)
        controls_layout.addWidget(self.one_time_input)
        controls_layout.addWidget(self.set_one_time_btn)

        roads_layout = QHBoxLayout()
        roads_layout.addLayout(road1_layout)
        roads_layout.addLayout(road2_layout)

        layout.addLayout(roads_layout)
        layout.addLayout(controls_layout)
        layout.addWidget(self.timer_label)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def manual_switch_trigger(self):
        self.manual_switch_pending = True
        self.timer_seconds = 5
        self.status_label.setText("\ud83d\udd52 Manual switch initiated. Yellow signal for 5 seconds.")
        self.update_UI()

    def update_timer(self):
        if self.timer_seconds > 0:
            self.timer_seconds -= 1
        else:
            if self.manual_switch_pending:
                self.manual_switch_pending = False
            self.switch_road()
        self.update_UI()

    def switch_road(self):
        self.active_road = 2 if self.active_road == 1 else 1
        if self.one_time_timer_active:
            self.timer_seconds = self.one_time_input.value()
            self.status_label.setText(f"\u23f1\ufe0f One-time timer set: {self.timer_seconds}s")
            self.one_time_timer_active = False
        else:
            self.timer_seconds = self.default_timer
            self.status_label.setText(f"\u2705 Switched to Road {self.active_road}")
        self.send_arduino_signal()

    def upload_image(self, road):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg)")
        if file_name:
            vehicle_count, emergency_count = self.detect_vehicles(file_name)
            self.road_data[road]['vehicles'] = vehicle_count
            self.road_data[road]['emergency'] = emergency_count
            self.status_label.setText(f"\ud83d\udea6 Road {road}: {vehicle_count} vehicles, {emergency_count} emergency detected.")
            self.check_emergency_conditions()
            self.update_UI()

    def detect_vehicles(self, file_path):
        vehicle_count = 0
        emergency_count = 0
        img = cv2.imread(file_path)
        if img is None:
            return 0, 0

        results = model(img)
        detected_objects = results.pandas().xyxy[0]

        for _, row in detected_objects.iterrows():
            name = row['name']
            confidence = row['confidence']
            if name in VEHICLE_CLASSES:
                vehicle_count += 1
            if name in EMERGENCY_CLASSES or (name == "truck" and 0.50 <= confidence <= 0.75):
                emergency_count += 1

        return vehicle_count, emergency_count

    def check_emergency_conditions(self):
        r1e = self.road_data[1]['emergency']
        r2e = self.road_data[2]['emergency']
        if r1e and r2e:
            self.timer_seconds = 15
        elif r1e and self.active_road == 2:
            self.timer_seconds = 5
        elif r2e and self.active_road == 1:
            self.timer_seconds = 5

    def set_custom_timer(self):
        self.default_timer = self.timer_input.value()
        self.timer_seconds = self.default_timer
        self.status_label.setText(f"\u23f2\ufe0f Timer set to {self.default_timer}s for all future cycles.")
        self.update_UI()

    def set_one_time_timer(self):
        # self.one_time_timer_active = True
        self.timer_seconds = self.one_time_input.value()
        self.status_label.setText(f"\u23f1\ufe0f Timer overridden to {self.timer_seconds}s (One-Time)")
        self.update_UI()

    def update_UI(self):
        self.road1_count.setText(f"Road 1 - Vehicles: {self.road_data[1]['vehicles']} | Emergency: {self.road_data[1]['emergency']}")
        self.road2_count.setText(f"Road 2 - Vehicles: {self.road_data[2]['vehicles']} | Emergency: {self.road_data[2]['emergency']}")
        self.timer_label.setText(f"Time Remaining: {self.timer_seconds}s")

        if self.timer_seconds <= 5:
            self.road1_label.setText("\ud83d\udfe1 Road 1 (Yellow)")
            self.road2_label.setText("\ud83d\udfe1 Road 2 (Yellow)")
        else:
            self.road1_label.setText("\ud83d\udfe2 Road 1 (Green)" if self.active_road == 1 else "\ud83d\udd34 Road 1 (Red)")
            self.road2_label.setText("\ud83d\udfe2 Road 2 (Green)" if self.active_road == 2 else "\ud83d\udd34 Road 2 (Red)")

        traffic_data["active_road"] = self.active_road
        traffic_data["timer"] = self.timer_seconds
        traffic_data["road1"] = self.road_data[1]
        traffic_data["road2"] = self.road_data[2]

        self.send_arduino_signal()

    def send_arduino_signal(self):
        if arduino:
            try:
                if self.timer_seconds <= 5:
                    arduino.write(f"Y1".encode())
                    arduino.write(f"Y2".encode())
                else:
                    arduino.write(f"G{self.active_road}".encode())
                    arduino.write(f"R{2 if self.active_road == 1 else 1}".encode())
            except Exception as e:
                print("\u26a0\ufe0f Error sending to Arduino:", e)
                
    def apply_android_input(self):
        try:
            url = "http://192.168.179.247:5000/api/traffic_status"
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                data = response.json()
                new_active_road = data.get("active_road")
                new_timer = data.get("timer")

                if new_active_road in [1, 2] and new_active_road != self.active_road:
                    print(f"📲 Android requested switch to Road {new_active_road}")
                    self.active_road = new_active_road
                    self.timer_seconds = 5  # 🟡 Force 5 seconds on switch from Android
                    self.status_label.setText(f"🚨 Android override → Road {new_active_road}, 5s timer")
                    self.send_arduino_signal()
                    self.update_UI()
                    
                elif new_timer != self.timer_seconds:
                    print(f"📲 Android requested to change Current Timer to {new_timer}")
                    self.timer_seconds = new_timer
                    self.status_label.setText(f"🚨 Android override → Current Timer to {new_timer}")
                    self.send_arduino_signal()
                    self.update_UI()

            else:
                print(f"⚠️ Error fetching from Android API: Status {response.status_code}")
        except requests.RequestException as e:
            print(f"⚠️ Could not connect to Android API: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TrafficLightSimulator()
    window.show()
    sys.exit(app.exec_())