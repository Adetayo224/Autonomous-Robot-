# CourierX 🤖
### Autonomous Document Delivery Robot | LAUTECH Campus

![Python](https://img.shields.io/badge/Python-3.13-blue)
![OpenCV](https://img.shields.io/badge/OpenCV-4.10-green)
![Raspberry Pi](https://img.shields.io/badge/RaspberryPi-4B-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## Overview
CourierX is a low-cost autonomous mobile robot designed for document 
delivery within a university campus environment. Built entirely on a 
Python stack without ROS, it demonstrates that capable autonomous 
navigation is achievable using affordable, locally sourceable hardware.

Developed at LAUTECH (Ladoke Akintola University of Technology), Nigeria
by Adetayo Muhammed (Astro) — Associate Embedded Systems Engineer & 
Director of Competitive Robotics, Aurora Robotics.

---

## Demo
> 🎥 YouTube video coming soon — [@samfred_robotics](https://youtube.com/@samfred_robotics)

---

## Features
- 360° obstacle detection using 4x HC-SR04 ultrasonic sensors
- Real-time 2D occupancy grid visualization with OpenCV
- 3D sensor environment visualization using PyOpenGL and Pygame
- Live GPS tracking on satellite map dashboard (Flask + Leaflet.js)
- IR night vision camera with OpenCV for front obstacle verification
- Autonomous motor control via Arduino UNO + L293D motor shield
- Lightweight Python stack — zero ROS dependency
- Runs on Raspberry Pi 4B with Debian 13 (Trixie)

---

## Hardware
| Component | Specification |
|---|---|
| Main Computer | Raspberry Pi 4 Model B |
| Microcontroller | Arduino UNO |
| Motor Driver | L293D Motor Shield |
| Ultrasonic Sensors | 4x HC-SR04 |
| GPS Module | u-blox NEO-8N |
| Camera | OV5647 IR Night Vision (CSI) |
| Drive System | 4-Wheel Differential Drive |
| Power | 12V Battery |

---

## System Architecture
[4x HC-SR04] ──────────────────────┐
[OV5647 Camera] ───────────────────┤
[NEO-8N GPS] ──────────────────────┤──► Raspberry Pi 4B (Python Brain)
│         │
┌────┘         │ USB Serial
│              ▼
│      Arduino UNO
│      L293D Shield
│      4x DC Motors
│
┌─────────▼──────────┐
│   Web Dashboard    │
│  Flask + Leaflet   │
│  Live Satellite Map│
└────────────────────┘
---

## Software Stack
- **Python 3.13** — main navigation logic
- **OpenCV 4.10** — computer vision + 2D visualization
- **PyOpenGL + Pygame** — 3D sensor environment
- **Flask + Leaflet.js** — live GPS satellite map dashboard
- **pyserial** — Arduino and GPS serial communication
- **NumPy** — occupancy grid processing
- **threading** — concurrent sensor acquisition
- **RPi.GPIO** — GPIO control for ultrasonic sensors

---

## Pin Connections

### Ultrasonic Sensors → Raspberry Pi
| Sensor | TRIG | ECHO |
|---|---|---|
| Front | GPIO 17 | GPIO 27 |
| Back | GPIO 22 | GPIO 23 |
| Left | GPIO 16 | GPIO 20 |
| Right | GPIO 5 | GPIO 6 |

### GPS NEO-8N → Raspberry Pi
| GPS Pin | RPi Pin |
|---|---|
| VCC | 5V (Pin 4) |
| GND | GND (Pin 9) |
| TX | GPIO 15 / RXD (Pin 10) |
| RX | GPIO 14 / TXD (Pin 8) |

### Arduino → Raspberry Pi
| Connection | Detail |
|---|---|
| Communication | USB Serial |
| Baud Rate | 9600 |
| Port | /dev/ttyUSB0 |

---

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/Adetayo224/YOUR-REPO-NAME.git
cd YOUR-REPO-NAME
```

### 2. Create virtual environment
```bash
python3 -m venv venv --system-site-packages
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install pyserial numpy matplotlib flask pygame PyOpenGL PyOpenGL_accelerate
```

### 4. Enable serial port for GPS
```bash
sudo raspi-config
# Interface Options → Serial Port
# Login shell: No | Hardware enabled: Yes

sudo nano /etc/udev/rules.d/99-serial.rules
# Add: KERNEL=="ttyS0", MODE="0666"

sudo udevadm control --reload-rules
sudo udevadm trigger
```

### 5. Upload Arduino firmware
Open `arduino/motor_controller/motor_controller.ino` in Arduino IDE,
install the **AFMotor** library, and upload to Arduino UNO.

---

## Usage

### Test ultrasonic sensors
```bash
python3 ultrasonic_test.py
```

### Run 2D sensor visualization
```bash
python3 sensor_map_2d.py
```

### Run 3D sensor environment
```bash
python3 sensor_map_3d.py
```

### Run live GPS satellite map
```bash
python3 gps_map.py
# Opens browser at http://localhost:5000
```

### Motor keyboard control
```bash
# In terminal (not Thonny):
python3 motor_control.py
# Arrow keys to control, SPACE to stop, Q to quit
```

---

## Project Status
- [x] Hardware assembly
- [x] Ultrasonic sensor testing (all 4 confirmed)
- [x] Camera setup and testing
- [x] 2D sensor visualization
- [x] 3D sensor environment
- [x] GPS live satellite map
- [x] Arduino motor control (4 motors)
- [ ] Full navigation brain (sensor fusion)
- [ ] A* path planning
- [ ] Return home function
- [ ] LAUTECH campus deployment
- [ ] Research paper

---

## Roadmap
- Add 4 more ultrasonic sensors (8 total) for full diagonal coverage
- Implement A* pathfinding for autonomous path planning
- Indoor localization using wheel odometry
- Upgrade to ROS 2 Humble (CourierX v2)
- Campus deployment and real-world testing
- IEEE research paper publication

---

## Author
**Adetayo Muhammed (Astro)**
- Associate Embedded Systems Engineer @ PowerTech Nigeria
- Director of Competitive Robotics @ Aurora Robotics
- Michael Taiwo Scholar 2025
- GitHub: [@Adetayo224](https://github.com/Adetayo224)
- YouTube: [@samfred_robotics](https://youtube.com/@samfred_robotics)

---

## License
MIT License — feel free to use, modify and build on this work.

---

*Built in Nigeria 🇳🇬 with locally sourceable hardware.*
*Proof that capable robotics doesn't require expensive equipment.*
