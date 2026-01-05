import cv2
import mediapipe as mp
import numpy as np
import rumps
import json
import os
import math
import time
import subprocess

# --- CONFIGURATION ---
CONFIG_PATH = os.path.expanduser("~/.posture_config.json")
DEFAULT_THRESHOLD = 30 
BLOCKLIST_APPS = ["zoom.us", "FaceTime", "Photo Booth", "Microsoft Teams", "Webex", "Skype"]

class PostureApp(rumps.App):
    def __init__(self):
        super(PostureApp, self).__init__("🧘")
        
        # --- MENU STRUCTURE ---
        self.menu = [
            "Start Monitoring", 
            "Stop Monitoring", 
            None, 
            "Open Debug View", 
            "Calibrate", 
            None,
            {"Preferences": [
                rumps.MenuItem("Auto-Pause for Zoom/Teams", callback=self.toggle_setting),
                None,
                rumps.MenuItem("Play Sound", callback=self.toggle_setting),
                rumps.MenuItem("Flash Menu", callback=self.toggle_setting),
                rumps.MenuItem("Send Notification", callback=self.toggle_setting),
                None,
                "Change Interval...",
                "Change Threshold (Manual)..."
            ]},
            None,
            "About"
        ]
        
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils 
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.pose = self.mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.7)
        
        self.config = self.load_settings()
        
        # Sync Menu Checkboxes
        self.menu["Preferences"]["Play Sound"].state = self.config.get("alert_sound", False)
        self.menu["Preferences"]["Flash Menu"].state = self.config.get("alert_flash", True)
        self.menu["Preferences"]["Send Notification"].state = self.config.get("alert_notify", True)
        self.menu["Preferences"]["Auto-Pause for Zoom/Teams"].state = self.config.get("auto_pause", True)

        # Timers
        self.monitor_timer = rumps.Timer(self.check_posture, self.config.get("interval", 60))
        self.flash_timer = rumps.Timer(self.flash_alert_animation, 0.6)
        
        # State
        self.is_monitoring = False
        self.current_angle = 0
        self.flash_state = False 

    def load_settings(self):
        default = {
            "interval": 60, 
            "neck_threshold": DEFAULT_THRESHOLD,
            "alert_sound": False,
            "alert_flash": True,
            "alert_notify": True,
            "auto_pause": True
        }
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as f:
                saved = json.load(f)
                default.update(saved)
                return default
        return default

    def save_settings(self):
        with open(CONFIG_PATH, 'w') as f:
            json.dump(self.config, f)

    # --- BLOCKLIST CHECK ---
    def is_blocking_app_running(self):
        try:
            for app_name in BLOCKLIST_APPS:
                result = subprocess.run(["pgrep", "-f", app_name], capture_output=True)
                if result.returncode == 0: 
                    return app_name
        except Exception:
            pass
        return None

    # --- NOTIFICATIONS ---
    def send_notification(self, title, message):
        try:
            rumps.notification(title, "", message)
        except:
            pass
        script = f'display notification "{message}" with title "{title}"'
        try:
            subprocess.run(["osascript", "-e", script], check=False)
        except Exception:
            pass

    # --- MATH & CV ---
    def calculate_neck_angle(self, landmarks_object):
        landmarks = landmarks_object.landmark 
        ear = landmarks[self.mp_pose.PoseLandmark.LEFT_EAR]
        shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
        dx = abs(ear.x - shoulder.x)
        dy = abs(ear.y - shoulder.y)
        return math.degrees(math.atan2(dx, dy))

    def draw_text_with_outline(self, img, text, pos, font_scale, color, thickness=2):
        font = cv2.FONT_HERSHEY_TRIPLEX
        cv2.putText(img, text, pos, font, font_scale, (0, 0, 0), thickness + 3)
        cv2.putText(img, text, pos, font, font_scale, color, thickness)

    def get_landmarks(self, cap, warmup=False):
        if not cap.isOpened(): return None, None
        
        valid_frame = None

        if warmup:
            attempts = 0
            while attempts < 10:
                ret, frame = cap.read()
                if ret and frame is not None:
                    valid_frame = frame
                    if attempts > 3: break 
                attempts += 1
                time.sleep(0.05)
        else:
            ret, frame = cap.read()
            if ret: valid_frame = frame

        if valid_frame is None:
            return None, None

        rgb = cv2.cvtColor(valid_frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb)
        return results.pose_landmarks if results.pose_landmarks else None, valid_frame

    # --- ACTIONS ---
    def toggle_setting(self, sender):
        sender.state = not sender.state 
        key_map = {
            "Play Sound": "alert_sound",
            "Flash Menu": "alert_flash",
            "Send Notification": "alert_notify",
            "Auto-Pause for Zoom/Teams": "auto_pause"
        }
        if sender.title in key_map:
            self.config[key_map[sender.title]] = sender.state
            self.save_settings()

    def flash_alert_animation(self, _):
        self.flash_state = not self.flash_state
        if self.flash_state:
            self.title = "⚠️ SLOUCHING"
        else:
            self.title = f"🔴 {self.current_angle:.0f}°"

    @rumps.clicked("Preferences", "Change Interval...")
    def change_interval(self, _):
        curr = self.config.get("interval", 60)
        resp = rumps.Window("Check interval (seconds):", default_text=str(curr)).run()
        if resp.clicked:
            try:
                val = int(resp.text)
                if val < 2: val = 2
                self.config["interval"] = val
                self.monitor_timer.interval = val
                self.save_settings()
            except ValueError: pass

    @rumps.clicked("Preferences", "Change Threshold (Manual)...")
    def change_threshold_manual(self, _):
        curr = self.config.get("neck_threshold", DEFAULT_THRESHOLD)
        resp = rumps.Window("Angle Threshold (degrees):", default_text=str(int(curr))).run()
        if resp.clicked:
            try:
                val = float(resp.text)
                self.config["neck_threshold"] = val
                self.save_settings()
            except ValueError: pass

    @rumps.clicked("About")
    def about_page(self, _):
        rumps.alert("PostureCV v1.0", "Created by Richard.\n\nKeep your spine healthy.")

    @rumps.clicked("Open Debug View")
    def open_debug_view(self, _):
        window_name = 'PostureCV Debug (Press q to quit)'
        rumps.alert("Debug Mode", "Press 'q' to close window.")
        cap = cv2.VideoCapture(0 + cv2.CAP_AVFOUNDATION)
        
        while True:
            landmarks_obj, frame = self.get_landmarks(cap, warmup=False)
            
            if landmarks_obj and frame is not None:
                h, w, c = frame.shape
                landmarks = landmarks_obj.landmark
                
                self.mp_drawing.draw_landmarks(
                    frame, landmarks_obj, self.mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
                )
                ear = landmarks[self.mp_pose.PoseLandmark.LEFT_EAR]
                shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
                ear_px = (int(ear.x * w), int(ear.y * h))
                shoulder_px = (int(shoulder.x * w), int(shoulder.y * h))

                cv2.line(frame, ear_px, (ear_px[0], ear_px[1] + 120), (0, 255, 255), 2)
                cv2.line(frame, ear_px, shoulder_px, (255, 200, 0), 2)
                
                angle = self.calculate_neck_angle(landmarks_obj)
                end_angle = 90 - angle if ear.x < shoulder.x else 90 + angle
                cv2.ellipse(frame, ear_px, (40, 40), 0, 90, end_angle, (0, 255, 255), 1)

                thresh = self.config.get("neck_threshold", DEFAULT_THRESHOLD)
                color = (0, 255, 0) if angle < thresh else (0, 0, 255)
                
                self.draw_text_with_outline(frame, f"{angle:.0f} deg", (ear_px[0]+20, ear_px[1]), 0.8, color)
                self.draw_text_with_outline(frame, f"Limit: {thresh:.0f} deg", (20, 40), 0.6, (255, 255, 255))
            
            elif frame is None:
                blank = np.zeros((480, 640, 3), np.uint8)
                cv2.putText(blank, "Camera Busy...", (200, 240), cv2.FONT_HERSHEY_TRIPLEX, 1, (255, 255, 255), 2)
                cv2.imshow(window_name, blank)
                if cv2.waitKey(1) & 0xFF == ord('q'): break
                continue

            cv2.imshow(window_name, frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): break
        
        cap.release()
        cv2.destroyAllWindows()

    @rumps.clicked("Calibrate")
    def calibrate(self, _):
        rumps.notification("Calibration", "Sit Up Straight", "Capturing in 3s...")
        time.sleep(3)
        cap = cv2.VideoCapture(0 + cv2.CAP_AVFOUNDATION)
        landmarks_obj, _ = self.get_landmarks(cap, warmup=True)
        cap.release()

        if landmarks_obj:
            baseline = self.calculate_neck_angle(landmarks_obj)
            self.config["neck_threshold"] = baseline + 8
            self.save_settings()
            rumps.alert("Calibrated!", f"Baseline: {baseline:.1f}°\nThreshold: {self.config['neck_threshold']:.1f}°")
        else:
            rumps.alert("Error", "Camera could not see you.")

    def check_posture(self, _):
        if not self.is_monitoring: return

        # 1. SOFT CHECK (Apps)
        if self.config.get("auto_pause", True):
            blocking_app = self.is_blocking_app_running()
            if blocking_app:
                self.title = "🧘 🚫 App Busy"
                return 

        # 2. HARD CHECK (Camera)
        cap = cv2.VideoCapture(0 + cv2.CAP_AVFOUNDATION)
        if not cap.isOpened():
            if self.config.get("auto_pause", True):
                self.title = "🧘 🚫 Cam Busy"
                return
        
        landmarks_obj, _ = self.get_landmarks(cap, warmup=True)
        cap.release()
        
        if landmarks_obj:
            self.current_angle = self.calculate_neck_angle(landmarks_obj)
            thresh = self.config.get("neck_threshold", DEFAULT_THRESHOLD)
            
            if self.current_angle > thresh:
                # --- BAD POSTURE ---
                
                # A. Handle Flashing
                if self.config.get("alert_flash", True):
                    # If flash enabled, timer handles the title
                    if not self.flash_timer.is_alive(): self.flash_timer.start()
                else:
                    # If flash disabled, WE must update title manually here
                    if self.flash_timer.is_alive(): self.flash_timer.stop()
                    self.title = f"🔴 {self.current_angle:.0f}°"

                # B. Notifications & Sound
                if self.config.get("alert_notify", True):
                    self.send_notification("Posture Alert", f"Slouching! ({self.current_angle:.0f}°)")
                if self.config.get("alert_sound", False):
                    os.system("afplay /System/Library/Sounds/Purr.aiff &")
            else:
                # --- GOOD POSTURE ---
                if self.flash_timer.is_alive(): self.flash_timer.stop()
                self.title = f"🧘 {self.current_angle:.0f}°"
        else:
            if self.config.get("auto_pause", True):
                 self.title = "🧘 🚫 Busy"

    @rumps.clicked("Start Monitoring")
    def start_app(self, _):
        self.is_monitoring = True
        self.title = "🧘✅"
        if self.flash_timer.is_alive(): self.flash_timer.stop()
        self.monitor_timer.start()

    @rumps.clicked("Stop Monitoring")
    def stop_app(self, _):
        self.is_monitoring = False
        if self.flash_timer.is_alive(): self.flash_timer.stop()
        self.title = "🧘"
        self.monitor_timer.stop()

if __name__ == "__main__":
    PostureApp().run()