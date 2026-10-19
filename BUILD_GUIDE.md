# Build Guide — Smart Attendance Professional UI

This is the project source, not a prebuilt APK. It has not been compiled/tested on a physical Android device. Camera QR scanning depends on packaging compatibility and must be tested on your phone.

## Windows 10 + WSL2 Ubuntu
If Ubuntu is not installed, open PowerShell as Administrator and run `wsl --install -d Ubuntu`.

In Ubuntu run:
```bash
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip python3-venv autoconf libtool pkg-config zlib1g-dev libncurses-dev cmake libffi-dev libssl-dev build-essential
python3 -m venv ~/buildenv
source ~/buildenv/bin/activate
pip install --upgrade pip setuptools wheel
pip install buildozer cython
```
Copy `main.py`, `buildozer.spec`, and `generate_qr.py` to `~/SmartAttendance` (build inside Linux home, not `/mnt/c`). Then:
```bash
source ~/buildenv/bin/activate
cd ~/SmartAttendance
buildozer android debug
```
If successful, APK should be in `~/SmartAttendance/bin/`. First build downloads SDK/NDK and may take a while; keep internet on and have 10–15 GB free.

## Demo QR
On Windows with Python installed:
```powershell
py -m pip install qrcode[pil]
py generate_qr.py 101 "Student Name"
```
The QR content is `STUDENT:101`. Register roll number 101 in the app, then scan it. Manual QR text field can test attendance without camera.

## Screens
- Professional dashboard with registered-student and present-today cards
- Student registration form
- QR scanner and manual QR text field
- Attendance history
- SQLite local storage and duplicate attendance blocking per student per date

Official docs:
- https://kivy.org/doc/stable/guide/packaging-android.html
- https://buildozer.readthedocs.io/en/latest/installation/
- https://learn.microsoft.com/en-us/windows/wsl/install

Static student QR codes can be shared; this is a college demo, not a secure production attendance system.\n