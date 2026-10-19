# Build the Smart Attendance APK online with GitHub Actions

1. Sign in to GitHub and create a repository named `SmartAttendance`.
2. Upload the contents of this project folder to the repository root. Make sure `main.py` and `buildozer.spec` are at the root and that the `.github/workflows/build-apk.yml` file is included.
3. Commit the files to the `main` branch.
4. Open the repository's **Actions** tab. If prompted, enable GitHub Actions.
5. Select **Build Smart Attendance APK** from the workflows list. Click **Run workflow** if it is shown; otherwise, the first push to `main` should start it automatically.
6. Open the running workflow and wait for it to finish. The first Android build can take a while.
7. If it succeeds, scroll to **Artifacts** and download `SmartAttendance-debug-apk`. Extract the downloaded artifact ZIP to get the `.apk`.
8. Transfer the APK to your Android phone and install it. Android may ask you to allow installation from that source.

## Important
- This project is a demo and the build has not been tested on your phone.
- If the build fails, open the failed run, copy the last 30–50 lines of the error log, and use those lines to troubleshoot.
- QR scanner dependencies may require compatibility fixes during the first Android build.
- Do not add passwords, signing keys, or other secrets to the repository.
