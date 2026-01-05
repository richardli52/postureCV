# PostureCV
A free and open source tool to fix your posture for macOS

## Created By
Richard Li - https://github.com/richardli52

## What it is
This is a minimalist menu bar utility that passively monitors your sitting posture using computer vision. 

![PostureCV (the praying emoji) in the menu bar](assets/menu-bar.png)

Most posture correction software relies on continuous video feeds which can drain laptop batteries and consume significant CPU resources. This application operates differently by capturing one single frame at a specific interval such as every 60 seconds. It analyzes this frame to calculate the vertical vector angle between your ear and your shoulder. If this angle exceeds your custom threshold it indicates you are slouching forward or leaning heavily to one side.

## Privacy and Memory
The application is designed with a privacy-first architecture. It processes all camera data in Random Access Memory (RAM) and discards the data immediately after the angle calculation is complete. The software never saves image files to your hard drive and never transmits video data to any external server or cloud service.

## Compatibility
The vision model utilizes the MediaPipe framework which is robust enough to detect skeletal landmarks even if you are wearing glasses, over-ear headphones, or hats.

## Usage Guide
1. Download the zipped application file from the Releases section on the right side of this page
2. Unzip the file and drag the app into your Applications folder
3. Open the app and grant camera permissions when macOS prompts you
4. Look for the small posture icon in your macOS menu bar near the clock
5. Sit up straight in your ideal posture and click Calibrate in the menu to set your baseline
6. Use the Preferences menu to adjust how often the app checks your posture and how sensitive the angle detection should be

## Debugging and Calibration
If you are unsure why you are receiving alerts you can click Open Debug View in the menu. This opens a temporary window showing your live camera feed with a skeletal wireframe overlay. This allows you to visualize exactly what the computer sees and determine the best angle threshold for your specific setup.

## Auto Pause
To prevent camera conflicts the application automatically pauses monitoring when it detects that specific video conferencing apps are running.
* zoom.us
* FaceTime
* Photo Booth
* Microsoft Teams
* Webex
* Skype

If you use Google Meet or Zoom inside a web browser like Chrome or Safari the app cannot detect this automatically so you must pause monitoring manually using the menu bar option.

## Notifications and Alerts
You can customize how the application alerts you when poor posture is detected.
* Sound plays a system alert sound
* Flash Menu Bar changes the menu bar icon color to red
* Notification sends a native macOS notification banner

Note that native notifications will not appear if you have Do Not Disturb or a Focus Mode active.

## Credits
Logic adapted from TiffinTech - https://github.com/TiffinTech/posture-corrector