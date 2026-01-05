from setuptools import setup

APP = ['posture_app.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'icon.icns',
    'packages': ['rumps', 'cv2', 'mediapipe', 'numpy'], 
    'plist': {
        'NSCameraUsageDescription': 'PostureCV needs your camera to monitor posture.',
        'LSUIElement': True, 
        'CFBundleName': 'PostureCV',
        'CFBundleDisplayName': 'PostureCV',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
    }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)