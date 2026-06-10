__#SafeRoute AI: Intelligent Road Hazard Detection and Navigation System__

A production-grade, full-stack AI web application that detects road hazards in CCTV videos and calculates safe routing paths dynamically. The frontend is built on **React.js (Vite)** with **Tailwind CSS** and **Leaflet.js**, while the backend is powered by **Flask** running a frame-by-frame **OpenCV Computer Vision** pipeline with a dual-database connectivity layer (**MongoDB** with automatic offline local **SQLite** fallback).

---

## Key Features

1. **AI Video Hazard Detection**: Frame-by-frame analysis of uploaded CCTV videos. Detects traffic congestion, potholes, flooding, and road blockages. Draws neon coral bounding boxes and scans a scanning laser HUD directly onto the output file.
2. **Dynamic Smart Routing**: Integrates real-world OpenStreetMap (OSM) APIs. Converts search queries to coordinates via Nominatim and plots street-accurate routes using the Open Source Routing Machine (OSRM) proxy.
3. **Hazard Avoidance Recalculation**: If hazards are active on the shortest route, the planner recalculates and recommends the **Safest Highway Express** path in Green, completely avoiding dangerous segments marked in Red.
4. **Dual-Database Resiliency**: Saves uploaded video metadata, hazard timestamps, and route history logs to MongoDB. If MongoDB is offline, it seamlessly falls back to a local SQLite database (`road_hazard.db`) without crashing.
5. **CORS Proxy Security**: Built-in Python proxy endpoints for Nominatim and OSRM bypass potential browser cross-origin constraints.

---

## Technical Stack

*   **Frontend**: React.js, Vite, Tailwind CSS, Leaflet.js, Lucide React, FontAwesome
*   **Backend**: Python, Flask, OpenCV (Image Processing, Color/Contour Segmentation, Canny Edges, Haar Cascades), Numpy
*   **Database**: MongoDB (PyMongo) with offline local SQLite fallback

---

## Setup and Installation

### Prerequisites
*   [Node.js](https://nodejs.org/) (v16.0 or higher)
*   [Python](https://www.python.org/) (v3.8 or higher)
*   *Optional*: [MongoDB Community Server](https://www.mongodb.com/try/download/community) (runs offline fallback on SQLite automatically if MongoDB is not active)

---

### Step 1: Backend Setup
1. Open a terminal and navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Install the required Python dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```
3. Run the Flask application:
   ```bash
   python app.py
   ```
   *The server will start on `http://127.0.0.1:5000`. It will scan for MongoDB and output `>>> Successfully connected to MongoDB` or fallback to SQLite.*

---

### Step 2: Frontend Setup
1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install the dependencies (React, Vite, Tailwind, Leaflet):
   ```bash
   npm install
   ```
3. Start the React development server:
   ```bash
   npm run dev
   ```
   *The Vite dashboard will open at `http://localhost:5173` (or the port specified in terminal).*

---

## Running and Verifying the System

### 1. Route Planner Verification
*   Type your start location (e.g. `KK Nagar, Madurai`) and destination (e.g. `Mattuthavani, Madurai`) in the inputs.
*   Click **Calculate Optimal Path**.
*   The Leaflet map will draw two lines:
    *   **Green Solid Line**: The Safest Route (bypassing any active lane hazards).
    *   **Red Dashed Line**: The Shortest Route (flagged with caution due to active potholes/obstructions).
*   Pins will be placed dynamically on the actual road grids representing potholes and fallen trees.

### 2. Video Analysis Verification
*   Under the **Video Hazard Detection** panel, click **Select Video File** and upload a CCTV road clip (e.g. `cctv_dummy.mp4` or a personal driving recording).
*   Click **Analyze Road Hazards**.
*   The Flask backend will process the video frame-by-frame:
    *   It isolates the bottom road coordinates.
    *   It counts vehicles to evaluate congestion.
    *   It extracts circular contours and calculates solidity to mark potholes in Neon Red.
    *   It segments sky reflections on asphalt to detect flooding in Yellow.
*   Once processing completes, a processed video showing bounding boxes and a laser scanner HUD will play, accompanied by a checklist of detected hazards and occurrence timestamps.
*   The Leaflet map will dynamically update to avoid the newly discovered hazard coordinates!

---

## Troubleshooting

#### Script Execution Blocked on Windows
If `npm` or `npx` fails due to PowerShell Execution Policies, run your terminals with the bypass flag:
```powershell
powershell -ExecutionPolicy Bypass
```
Or run the dev server explicitly using `.cmd` extensions:
```bash
npm.cmd run dev
```

#### MongoDB Offline
If MongoDB is not installed, no actions are required. The server logs `>>> MongoDB service unreachable. Falling back to local offline SQLite database` and initializes all route logging and metadata storage inside `backend/road_hazard.db` automatically.
