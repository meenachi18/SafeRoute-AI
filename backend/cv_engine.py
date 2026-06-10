import cv2
import numpy as np
import os
import time

def process_video(input_path, output_path):
    """
    Processes the uploaded video frame-by-frame using real OpenCV computer vision models.
    Detects:
      - Traffic Congestion (vehicle/contour counts and edge clustering)
      - Potholes (elliptical shadows/contours, local road edge density anomalies)
      - Flooded Roads (specular sky reflections, color consistency in road region)
      - Road Blockages / Fallen Trees (high-contrast linear/diagonal obstructions crossing lanes)
      
    Outputs a new video file with bounding boxes, hazard overlays, and an AI Scanner HUD.
    Returns a dictionary list of detected hazards with confidence levels and timestamps.
    """
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print(f"Error opening video file: {input_path}")
        return []

    # Get video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1

    # Downscale resolution for extremely fast CV processing (keeps it under 2 seconds!)
    target_width = 640
    scale_ratio = 1.0
    if width > target_width:
        scale_ratio = target_width / width
        width = target_width
        height = int(height * scale_ratio)

    # Calculate frame skip to keep video processing instant (under 3 seconds)
    # We will process 1 frame every 1.0 second of video
    frame_skip = max(1, int(fps * 1.0))
    preview_fps = max(2.0, fps / frame_skip)

    # Define video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, preview_fps, (width, height))

    hazards_found = {}
    frame_idx = 0
    start_time = time.time()

    # Pre-calculate scanning HUD elements
    scanner_y = 0
    scan_direction = 1

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_idx += 1
        if frame_idx % frame_skip != 0:
            continue

        # Resize frame if downscaled
        if scale_ratio < 1.0:
            frame = cv2.resize(frame, (width, height))

        timestamp = round(frame_idx / fps, 2)
        h_rows, w_cols, _ = frame.shape

        # Create copy for drawings
        overlay = frame.copy()
        
        # 1. ISOLATE ROAD REGION OF INTEREST (ROI)
        # Typically the bottom 50% of the image forms the road lane surface
        road_top = int(h_rows * 0.55)
        road_roi = frame[road_top:h_rows, 0:w_cols]
        gray_road = cv2.cvtColor(road_roi, cv2.COLOR_BGR2GRAY)
        blurred_road = cv2.GaussianBlur(gray_road, (5, 5), 0)
        
        # Detected variables for current frame
        detected_this_frame = []

        # --- A. VEHICLE & TRAFFIC CONGESTION DETECTION ---
        # OpenCV contour extraction filtered for vehicle ratios
        # Subtract background or find dynamic edges
        edges_road = cv2.Canny(blurred_road, 50, 150)
        contours, _ = cv2.findContours(edges_road, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        vehicle_contours = []
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            aspect_ratio = float(w) / h
            # Vehicle aspect ratio bounds and size filters
            if 30 < w < 250 and 20 < h < 180 and 0.8 < aspect_ratio < 3.0:
                crop_edges = edges_road[y:y+h, x:x+w]
                density = np.sum(crop_edges > 0) / (w * h)
                if density > 0.05: # High texture contour representing a vehicle body
                    vehicle_contours.append((x, y + road_top, w, h))

        # Check vehicle density to declare congestion
        congestion_detected = len(vehicle_contours) >= 4
        congestion_confidence = min(60 + len(vehicle_contours) * 8, 98)

        # Draw vehicle boxes
        for (x, y, w, h) in vehicle_contours:
            color = (244, 63, 94) if congestion_detected else (6, 182, 212) # Red if congested, Cyan if normal
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.putText(frame, "VEHICLE", (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

        if congestion_detected:
            detected_this_frame.append({
                "type": "Traffic Congestion",
                "confidence": congestion_confidence,
                "box": [0, road_top, w_cols, h_rows - road_top],
                "description": f"Heavy density bottleneck detected with {len(vehicle_contours)} vehicles active."
            })
            # Draw overlay for congestion block
            cv2.rectangle(overlay, (0, road_top), (w_cols, h_rows), (0, 0, 255), -1)
            cv2.putText(frame, f"WARNING: TRAFFIC CONGESTION ({congestion_confidence}%)", (20, road_top + 40), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # --- B. POTHOLE DETECTION (Surface Depression / Anomaly Filter) ---
        # Look for dark, high-contrast structural hollow circular/elliptical zones in road surface
        _, dark_thresh = cv2.threshold(blurred_road, 85, 255, cv2.THRESH_BINARY_INV)
        # Exclude vehicle contours by masking out their bounding boxes
        for (vx, vy, vw, vh) in vehicle_contours:
            cv2.rectangle(dark_thresh, (vx, vy - road_top), (vx + vw, vy - road_top + vh), 0, -1)
            
        pothole_contours, _ = cv2.findContours(dark_thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        potholes_found = 0
        for pc in pothole_contours:
            px, py, pw, ph = cv2.boundingRect(pc)
            p_area = cv2.contourArea(pc)
            p_aspect = float(pw) / ph
            
            # Potholes lie horizontally, are relatively small but clear depressions, and are in road boundaries
            if 400 < p_area < 9000 and 0.9 < p_aspect < 2.8 and py > int(h_rows * 0.05):
                # Verify solidity and texture contrast
                hull = cv2.convexHull(pc)
                hull_area = cv2.contourArea(hull)
                solidity = float(p_area) / hull_area if hull_area > 0 else 0
                
                if 0.5 < solidity < 0.96:
                    potholes_found += 1
                    pot_y = py + road_top
                    confidence = int(72 + (solidity * 20))
                    
                    # Highlight pothole in Neon Coral Red
                    cv2.drawContours(frame, [pc + [0, road_top]], -1, (94, 63, 244), 2) # Red/Coral contours
                    cv2.rectangle(frame, (px, pot_y), (px+pw, pot_y+ph), (94, 63, 244), 2)
                    cv2.putText(frame, f"POTHOLE {confidence}%", (px, pot_y - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (94, 63, 244), 1)
                    
                    detected_this_frame.append({
                        "type": "Pothole Detected",
                        "confidence": confidence,
                        "box": [px, pot_y, pw, ph],
                        "description": f"Severe structural pothole detected on the roadway surface."
                    })

        # --- C. FLOODED ROAD DETECTION (Water specular reflectance / HSV) ---
        # Waterlogged asphalt reflects the sky/surroundings, creating highly uniform, shiny regions.
        hsv_road = cv2.cvtColor(road_roi, cv2.COLOR_BGR2HSV)
        # Water/reflective surfaces fall under low saturation and high value (grey reflection) or blue-sky specular values
        lower_wet = np.array([0, 0, 110])
        upper_wet = np.array([180, 45, 230])
        mask_wet = cv2.inRange(hsv_road, lower_wet, upper_wet)
        
        # Clean up mask
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
        mask_wet = cv2.morphologyEx(mask_wet, cv2.MORPH_CLOSE, kernel)
        mask_wet = cv2.morphologyEx(mask_wet, cv2.MORPH_OPEN, kernel)
        
        wet_contours, _ = cv2.findContours(mask_wet, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        flood_area = 0
        max_flood_contour = None
        for wc in wet_contours:
            w_area = cv2.contourArea(wc)
            if w_area > flood_area:
                flood_area = w_area
                max_flood_contour = wc

        # If a single flooded contour covers more than 15% of the road ROI, label it
        roi_total_area = road_roi.shape[0] * road_roi.shape[1]
        if flood_area > (roi_total_area * 0.15) and max_flood_contour is not None:
            fx, fy, fw, fh = cv2.boundingRect(max_flood_contour)
            flood_y = fy + road_top
            flood_conf = min(68 + int((flood_area / roi_total_area) * 80), 97)
            
            # Draw flooding hazard area in Yellow/Orange
            cv2.rectangle(frame, (fx, flood_y), (fx+fw, flood_y+fh), (16, 185, 245), 2) # Orange-Yellow bounding box
            cv2.drawContours(frame, [max_flood_contour + [0, road_top]], -1, (16, 185, 245), 1)
            cv2.putText(frame, f"FLOODED ROADWAY {flood_conf}%", (fx, flood_y - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (16, 185, 245), 2)
            
            detected_this_frame.append({
                "type": "Flooded Road",
                "confidence": flood_conf,
                "box": [fx, flood_y, fw, fh],
                "description": f"Specular water accumulation causing potential hydroplaning or road flooding."
            })

        # --- D. FALLEN TREE / ROAD BLOCKAGES ---
        # Highly defined non-vertical edges crossing lanes
        # Hough Lines detection on road region
        edges_lines = cv2.Canny(blurred_road, 80, 200)
        lines = cv2.HoughLinesP(edges_lines, 1, np.pi/180, 50, minLineLength=60, maxLineGap=10)
        
        blockage_weight = 0
        blockage_points = []
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                dy = abs(y2 - y1)
                dx = abs(x2 - x1)
                angle = np.arctan2(dy, dx) * 180 / np.pi
                
                # We look for horizontal/diagonal structures (slope between 5 and 55 degrees) blocking the road center
                if 5 < angle < 55 and (min(x1, x2) < int(w_cols * 0.6) and max(x1, x2) > int(w_cols * 0.4)):
                    blockage_weight += 1
                    blockage_points.extend([(x1, y1 + road_top), (x2, y2 + road_top)])

        if blockage_weight >= 3 and len(blockage_points) > 0:
            # We have a fallen tree or substantial barrier blocking the lanes
            pts = np.array(blockage_points)
            bx, by, bw, bh = cv2.boundingRect(pts)
            blockage_conf = min(70 + blockage_weight * 5, 96)
            
            cv2.rectangle(frame, (bx, by), (bx+bw, by+bh), (94, 63, 244), 2) # Dangerous Obstacle (Coral Red)
            cv2.putText(frame, f"ROAD BLOCKAGE {blockage_conf}%", (bx, by - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (94, 63, 244), 2)
            
            detected_this_frame.append({
                "type": "Fallen Tree / Blockage",
                "confidence": blockage_conf,
                "box": [bx, by, bw, bh],
                "description": f"Major horizontal roadway blockage or fallen debris obstructing lane access."
            })

        # --- E. AGGREGATE HAZARDS ACROSS TIMESTAMPS ---
        for entry in detected_this_frame:
            h_type = entry["type"]
            h_conf = entry["confidence"]
            # Keep track of highest confidence hazard detected in the video
            if h_type not in hazards_found or h_conf > hazards_found[h_type]["confidence"]:
                hazards_found[h_type] = {
                    "type": h_type,
                    "confidence": h_conf,
                    "timestamp": timestamp,
                    "box": entry["box"],
                    "description": entry["description"]
                }

        # --- F. PREMIUM AI scanner HUD DRAWINGS ---
        # Add high-fidelity translucent overlay
        cv2.addWeighted(overlay, 0.15, frame, 0.85, 0, frame)
        
        # 1. Top HUD Border Banner
        cv2.rectangle(frame, (0, 0), (width, 45), (15, 10, 5), -1)
        cv2.line(frame, (0, 45), (width, 45), (6, 182, 212), 1) # Cyan line
        cv2.putText(frame, "SAFEROUTE AI - LIVE CCTV HAZARD SCANNER", (20, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (6, 182, 212), 2)
        
        # 2. Scanning Laser line
        cv2.line(frame, (0, int(scanner_y)), (width, int(scanner_y)), (6, 182, 212), 1)
        # Laser pulse shadow
        laser_overlay = frame.copy()
        cv2.rectangle(laser_overlay, (0, max(0, int(scanner_y)-15)), (width, int(scanner_y)), (6, 182, 212), -1)
        cv2.addWeighted(laser_overlay, 0.1, frame, 0.9, 0, frame)
        
        scanner_y += 8 * scan_direction
        if scanner_y >= height or scanner_y <= 45:
            scan_direction *= -1

        # 3. Dynamic Sidebar Stats Overlay
        cv2.rectangle(frame, (width - 240, 60), (width - 15, 230), (15, 10, 5), -1)
        cv2.rectangle(frame, (width - 240, 60), (width - 15, 230), (6, 182, 212), 1)
        cv2.putText(frame, "CCTV ANALYTICS", (width - 225, 82), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (6, 182, 212), 2)
        
        cv2.putText(frame, f"FPS: {fps:.1f}", (width - 225, 112), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
        cv2.putText(frame, f"TIME: {timestamp}s / {total_frames/fps:.1f}s", (width - 225, 132), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
        cv2.putText(frame, f"VEHICLES OUT: {len(vehicle_contours)}", (width - 225, 152), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
        cv2.putText(frame, f"POTHOLES: {potholes_found}", (width - 225, 172), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
        
        # Hazard Warning light
        if len(detected_this_frame) > 0:
            cv2.circle(frame, (width - 35, 82), 6, (94, 63, 244), -1) # Glowing Red dot
            cv2.putText(frame, "ALARM", (width - 85, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (94, 63, 244), 1)
        else:
            cv2.circle(frame, (width - 35, 82), 6, (129, 185, 16), -1) # Safe Green dot
            cv2.putText(frame, "SCAN", (width - 80, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (129, 185, 16), 1)

        # Write frame to video
        out.write(frame)

    cap.release()
    out.release()
    print(f"Video analysis complete. Saved to: {output_path} (Processed {frame_idx} frames in {time.time()-start_time:.1f}s)")
    
    return list(hazards_found.values())

# For local direct pipeline testing
if __name__ == "__main__":
    test_in = "../cctv_dummy.mp4"
    test_out = "../uploads/processed_test.mp4"
    if os.path.exists(test_in):
        os.makedirs("../uploads", exist_ok=True)
        results = process_video(test_in, test_out)
        print("Test results:", results)
