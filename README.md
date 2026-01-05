# PostureCV
A free and open source tool to fix your posture for macOS  <div align="center">
  <img src="assets/Logo.png" alt = "Logo" width="100"> <br>
      <em>PostureCV Logo</em>
</div>


## Created By
[Richard Li](https://github.com/richardli52)

## What it is
PostureCV is a minimalist menu bar utility that passively monitors your sitting posture using computer vision. 

<div align="center">
  <img src="assets/menu-bar.png" alt = "Menu Bar"> <br>
      <em>Menu Bar</em> 
</div>
<br>

Most posture correction software relies on continuous video feeds which can drain laptop batteries and consume significant CPU resources. Existing web apps can lead to privacy concerns. PostureCV operates differently by capturing one single frame at a specific custom interval, such as every 60 seconds. 

### The Mechanics
Some posture software tracks the absolute pixel position of the face. This breaks down because it leads to false positives when you adjust your laptop screen or move your chair. One other approach, taken by [Posture Pal](https://apps.apple.com/us/app/posture-pal-improve-alert/id1590316152), is tracking where the head is facing based on AirPods. However, this also leads to false positives when you look down, say to grab something, but are not necessarily having bad posture. 

PostureCV uses angles instead of absolute pixel coordinates to determine slouching. It calculates the vector angle between your ear and your shoulder relative to a vertical axis. This makes the detection resilient to camera movement. You can adjust your webcam height or sit further back, and the angle of your neck remains consistent.

<div align="center">
  <img src="assets/debug1.jpeg" alt = "Debug View 1"> <br>
      <em>Demo of Mechanics</em>
</div>
<br>
Learn more about Debug View in the Debugging and Calibration section below. 
<br>
<br>

PostureCV calculates the angle $\theta$, which is shown above, using the arctangent function
$$\theta = \arctan\left(\frac{|x_{ear} - x_{shoulder}|}{|y_{ear} - y_{shoulder}|}\right) \times \frac{180}{\pi}$$

If the calculated angle exceeds your threshold, the system triggers an alert. See the Notifications and Alerts section below for the choice of how you would like to be alerted. 

The main limitation to this approach is a false positive when the head leans to the side. Sensitivity-related errors can be minimized via automatic and manual calibration, as seen in the Debugging and Calibration section below. 

Credit for these mechanics (and other aspects of the setup, including choice of libraries) goes to [Tiff In Tech](https://github.com/TiffinTech/posture-corrector). 

## Usage
1. Download the zipped application file from the Releases section on the right side of this page
2. Unzip the file and drag the app into your Applications folder
3. Open the app and grant camera permissions when macOS prompts you
4. Look for the praying emoji in your macOS menu bar near the clock
<div align="middle">
  <img src="assets/dropdown.png" alt="Dropdown Menu" width="100"> <br>
      <em>Dropdown</em>
</div>
<br>
5. Sit up straight in your ideal posture and click Calibrate in the menu bar dropdown to automatically set your baseline. This can be manually adjusted in the next step as well
<div align="middle">
  <img src="assets/calibration.png" alt="Calibration" width="100"> <br><em> Calibration Confirmation</em><br>
</div>
<br>
6. Use the Preferences menu to adjust how often the app checks your posture and how sensitive the angle detection should be. Also select how you'd like to be notified when you're slouching (see the Notifications and Alerts section below)
<table align="center">
  <tr>
    <td align="center">
      <img src="assets/preferences.png" alt="Preferences" width="150">
      <br>
      <em>Preferences</em>
    </td>
    <td align="center">
      <img src="assets/interval.png" alt="Interval Customization" width="100">
      <br>
      <em>Interval</em>
    </td>
    <td align="center">
      <img src="assets/threshold.png" alt="Threshold Customization" width="100">
      <br>
      <em>Threshold</em>
    </td>
  </tr>
</table>
7. Click Start Monitoring to begin checking for slouching. 
<table align="center">
  <tr>
    <td align="center">
      <img src="assets/noslouch.png" alt="No Slouch" width="150">
      <br>
      <em>Good Posture</em>
    </td>
    <td align="center">
      <img src="assets/slouch2.png" alt="Slouching" width="150">
      <br>
      <em>Slouching</em>
    </td>
  </tr>
</table>

## Debugging and Calibration
If you are unsure why you are receiving alerts, you can click Open Debug View in the menu. This opens a temporary window showing your live camera feed with an overlay of ear and shoulder joint locations detected by computer vision. This allows you to visualize exactly what the computer sees and determine the best angle threshold that constitutes slouching.
<div align="center">
  <img src="assets/debug2.jpeg" alt = "Debug View 2, Slouching"> <br>
      <em>Debug View, Slouching</em>
</div>
<br>

## Auto Pause
To prevent camera conflicts, the application automatically pauses monitoring when it detects that specific video conferencing apps are running. This feature can be turned on or off in Preferences. 
* zoom.us
* FaceTime
* Photo Booth
* Microsoft Teams
* Webex
* Skype

If you use Google Meet or Zoom inside a web browser like Chrome or Safari, the app cannot detect this automatically. You must pause monitoring manually using the menu bar if you'd like.

## Notifications and Alerts
You can customize how the application alerts you when slouching is detected.
* Sound plays a system alert sound
* Flash Menu Bar changes the menu bar icon color to red
* Notification sends a native macOS notification banner
<table align="center">
  <tr>
    <td align="center">
      <img src="assets/slouch1.png" alt="Slouching Alert" width="200">
      <br>
      <em>Slouching Alert Menu Bar Flashing</em>
    </td>
    <td align="center">
      <img src="assets/notification.png" alt="Notification" width="200">
      <br>
      <em>Notification</em>
    </td>
  </tr>
</table>


Note that native notifications will not appear if you have any Focus Mode (such as Do Not Disturb or Personal) active.

## Privacy and Memory
The application is designed privacy-first. It processes all camera data in RAM and discards the data immediately after the angle calculation is complete. The software never saves image files to your hard drive and never transmits video data to any external server or cloud service. It stands out from other offerings, including paid apps, for this reason. Privacy is why I built this project in the first place. 

## Compatibility
The vision model uses MediaPipe, which detects locations of facial features even if you are wearing glasses, headphones, or hats. The only features that matter here are the ears and shoulders. 

## Run from Source
If you prefer to run the Python script directly or modify the code:
1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the app: `python3 posture_app.py`

## Credits
Mechanics and choice of libraries adapted from [Tiff In Tech](https://github.com/TiffinTech/posture-corrector). 