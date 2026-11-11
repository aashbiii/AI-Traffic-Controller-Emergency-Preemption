# AI Traffic Controller & Emergency Vehicle Preemption

![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![YOLOv5](https://img.shields.io/badge/YOLOv5-Vision%20Detection-orange.svg)
![PyQt5](https://img.shields.io/badge/GUI-PyQt5-green.svg)
![Arduino](https://img.shields.io/badge/Hardware-Arduino%20C%2B%2B-teal.svg)
![Android](https://img.shields.io/badge/Mobile-Android%20Kotlin-brightgreen.svg)
![Flask](https://img.shields.io/badge/API-Flask%20REST-red.svg)

An intelligent multi-modal traffic signal control system combining deep learning object detection, hardware microcontroller interfacing, a desktop monitoring GUI, and mobile connectivity. The system optimizes green signal durations dynamically based on vehicle density and provides instant preemption overrides for emergency vehicles (ambulances, fire engines, police).

---

## 📌 Multi-Tier System Architecture

1. **Computer Vision Inference (Ultralytics YOLOv5):**
   - Utilizes `yolov5s.pt` to detect standard vehicles (`car`, `bus`, `truck`, `motorbike`) and emergency vehicles.
   - Calculates dynamic road priority based on real-time vehicle counts per lane.
2. **Hardware Actuation Layer (Arduino `traffic.ino`):**
   - Connects to an Arduino Uno/Mega over USB Serial (`COM6`, 9600 baud via `pyserial`).
   - Actuates physical traffic signal LEDs (Red, Yellow, Green) on Road 1 and Road 2 via 2-character serial commands (e.g. `1G` for Road 1 Green, `2R` for Road 2 Red).
3. **Supervisory Desktop GUI (`traffic.py` / PyQt5):**
   - Visual dashboard displaying active road states, countdown timers, vehicle tallies, image test loaders, manual road override triggers, and emergency override indicators.
4. **Distributed API Server (`traffic_api.py`):**
   - Integrated multithreaded Flask REST API exposing `/api/traffic_status` and `/api/update_traffic` with CORS enabled.
5. **Mobile Companion Application (`TrafficApp`):**
   - Native Android application built in Kotlin (`build.gradle.kts`) enabling remote traffic monitoring and administrative signal status inspection.

---

## 📁 Repository Structure

```
├── traffic.py                                 # Main PyQt5 desktop GUI & YOLOv5 vision controller
├── traffic2.py & traffic3.py                  # Alternate iterations & test harnesses
├── traffic_api.py                             # Multithreaded Flask REST API
├── yolov5s.pt                                 # Pretrained YOLOv5 small weights
├── traffic/traffic.ino                        # Arduino C++ traffic light firmware
├── TrafficApp/                                # Android Kotlin companion application
├── PHOTOS/                                    # Test images for vehicles and emergency vehicles
└── yolov5/                                    # Ultralytics YOLOv5 inference framework
```

---

## 🚀 How to Run

### 1. Arduino Hardware Setup
1. Upload `traffic/traffic.ino` to your Arduino Uno / Mega board via Arduino IDE.
2. Connect LEDs for Road 1 (Pins 2, 3, 4) and Road 2 (Pins 5, 6, 7).

### 2. Desktop Application & Vision Engine
```bash
# Install dependencies
pip install -r yolov5/requirements.txt PyQt5 pyserial flask flask-cors

# Launch desktop GUI
python traffic.py
```

### 3. REST API & Mobile Companion
- The Flask REST API can be started via:
  ```bash
  python traffic_api.py
  ```
- The Android app located in `TrafficApp/` can be built and deployed via Android Studio.

---

## 👤 Author
**Ashbi Saju**  
GitHub: [@aashbiii](https://github.com/aashbiii)
