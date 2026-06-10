# SafeRoute AI: Intelligent Road Hazard Detection and Navigation System

## Project Overview

SafeRoute AI is an intelligent road safety and navigation application designed to help users choose safer travel routes by identifying potential road hazards. Unlike traditional navigation systems that focus only on the shortest or fastest path, SafeRoute AI aims to improve road safety through hazard-aware navigation.

The system integrates route analysis, CCTV video-based hazard detection, interactive maps, and voice alerts to assist users in making safer travel decisions.

---

## Problem Statement

Existing navigation applications primarily optimize travel time and distance without considering road conditions such as potholes, waterlogging, fallen trees, traffic congestion, or road damage. This can lead to vehicle damage, delays, and increased accident risks.

SafeRoute AI addresses this challenge by providing a platform that combines navigation with hazard awareness.

---

## Features

* User authentication interface
* Route selection using source and destination locations
* Interactive map visualization
* Safe route analysis and recommendations
* CCTV video upload and hazard analysis
* Hazard alert notifications
* Detection scenarios for:

  * Potholes
  * Waterlogging
  * Fallen trees / road blockages
  * Traffic congestion
* Voice alert support for improved user interaction
* Mobile-inspired responsive user interface

---

## Technologies Used

### Frontend

* HTML5
* CSS3
* JavaScript (ES6)

### Backend

* Python Flask
* Flask-CORS

### Computer Vision

* OpenCV

### Mapping and Navigation

* Leaflet.js
* OpenStreetMap (OSM)
* OSRM (Open Source Routing Machine)

### Voice Assistance

* Web Speech Synthesis API
* Web Speech Recognition API

---

## System Modules

### Login Module

Provides user authentication and access to the SafeRoute AI dashboard.

### Route Analysis Module

Allows users to enter source and destination locations and receive safer route recommendations.

### CCTV Hazard Analysis Module

Accepts uploaded CCTV or road footage and performs hazard analysis to identify road-related risks.

### Navigation Module

Displays maps and route information using interactive mapping services.

### Alert Module

Provides visual notifications regarding detected hazards.

### Voice Assistance Module

Supports voice-based alerts and hands-free interaction using browser speech APIs.

---

## Project Workflow

1. User signs into the application.
2. User enters source and destination locations.
3. The system performs route analysis.
4. The application displays navigation information.
5. Users can upload CCTV footage for hazard analysis.
6. The backend processes the uploaded footage.
7. Detected hazards are presented through alerts and notifications.
8. Voice assistance provides additional guidance.

---

## Current Implementation

The current version of SafeRoute AI serves as a functional prototype demonstrating the integration of navigation services with road hazard awareness.

The implemented system includes:

* Frontend interface for navigation and hazard reporting.
* Backend support for CCTV footage processing.
* Hazard alert generation.
* Route visualization and analysis.

The CCTV analysis component currently demonstrates prototype-level hazard analysis using uploaded footage suitable for academic evaluation and proof-of-concept purposes.

---

## Future Enhancements

Future versions of SafeRoute AI can be extended with:

* Real-time CCTV camera integration
* YOLO-based deep learning hazard detection
* Live traffic API integration
* Weather data integration
* IoT-based road condition monitoring
* Android mobile application deployment
* Community-based hazard reporting
* Cloud database support for real-time updates

---

## How to Run the Project

### Clone the Repository

```bash
git clone https://github.com/meenachi18/SafeRoute-AI.git
```

### Navigate to the Project Directory

```bash
cd SafeRoute-AI
```

### Install Backend Dependencies

```bash
pip install flask flask-cors opencv-python numpy
```

### Run the Flask Server

```bash
python app.py
```

### Launch the Frontend

Open `index.html` using Live Server in Visual Studio Code.

---

## Repository Information

GitHub Repository:

https://github.com/meenachi18/SafeRoute-AI

---

## Conclusion

SafeRoute AI demonstrates how Artificial Intelligence, Computer Vision, and Smart Navigation technologies can be combined to improve road safety and enhance user travel experiences. The project provides a strong foundation for future development toward real-time intelligent transportation systems.

---

## Author

**Meenachi**

Bachelor of Engineering Project
