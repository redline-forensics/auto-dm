<h1 align="center">
  <br>
    <img src="https://cdn.rawgit.com/redline-forensics/auto-dm/master/resources/icons/icons8-Traffic-Jam-80.svg" alt="AutoDM" width="200">
  <br>
    AutoDM
  <br>
</h1>

<h4 align="center">A job processing automation suite for Delta [v] and RedLine.</h4>
<br>

![screenshot](https://raw.githubusercontent.com/redline-forensics/auto-dm/master/resources/usage.gif)

## Key Features

* Automated SCENE site and vehicle processing
* Hotkeys for opening job folder or Basecamp page

## Installation

1. Download the <a href="https://github.com/redline-forensics/auto-dm/releases">latest release</a>
2. Unzip to your install location
3. Run ```main_app.exe```
4. Input your settings using the gear button in the top right:
   * <b>Basecamp Email/Password</b>: used to open a job's Basecamp page
   * <b>SCENE EXE Path</b>: The location of SCENE's .EXE, used for SCENE automation
   * <b>Google Maps API Keys</b>: Used for create Maps aerial images, <a href="https://developers.google.com/maps/">get them here</a>
   * <b>Google Earth EXE Path</b>: The location of Earth's .EXE, used for Earth automation

## Usage

1. Type the job number to add in the top bar.
2. AutoDM will search for the job on the server. If found, it will be added as a tab.
3. Job folders (scans, drone, etc.) will be automatically discovered.
   * Use the edit button next to the job folder to manually choose its location
   * Use the open button to open the folder in Explorer
4. Use any of the built in job processing tools:
   * <b>SCENE Site/Vehicle</b>: Automated SCENE processing
   * <b>Google Maps</b>: Create a hi-res aerial image in minutes using Google Maps
   * <b>Google Earth</b>: Automatically capture Google Earth images
5. The program will stay open in the system tray, even when closed. To quit the program, right click the system tray icon and choose "Quit".

#### Hotkeys
```Ctrl+Alt+J```: Show window and focus on job number input box

```Ctrl+Alt+O```: Open current job folder

```Ctrl+Alt+B```: Open current job on Basecamp

---


#### Contributors

Jake Cheek - [@jgchk](https://github.com/jgchk)

#### License

MIT
