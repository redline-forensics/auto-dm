import sys

from cx_Freeze import setup, Executable

build_exe_options = {"packages": ["idna"]}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(name="AutoDM",
      version="0.1",
      description="AutoDM",
      options={"build_exe": build_exe_options},
      executables=[Executable("main_app.py",
                              base=base,
                              icon="resources\\icons\\icons8_traffic_jam_80.ico",
                              shortcutName="AutoDM",
                              shortcutDir="StartMenuFolder")])
