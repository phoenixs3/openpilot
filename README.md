Smart Roadster Openpilot Fork
=======================

Hardware Setup:
------
* Braking: Tesla Model S/X iBooster
* Throttle: Ocelot throttle interceptor
* Steering: Custom EPAS ECU
* Radar: Ford Focus ST
* Harness/Power: Ocelot Distribution Board
* CAN Bridge: Comma.ai Black Panda
* Compute Device: Leco LePro 3, 6GB RAM, ABS Case

[![](https://i.imgur.com/5YcHkQ7.jpg)](#)

Modified Files
------
* selfdrive>opendbc
* selfdrive>car>ocelot
* selfdrive>ui>qt>sidebar.cc
* selfdrive>ui>qt>widgets>drive_stats.cc
* selfdrive>ui>qt>widgets>setup.cc
* selfdrive>athena>registration.py
* common>api>__init__.py
* selfdrive>assets>images/button_home.png
* panda>SConscript
* panda>board/boards/black.h
* selfdrive>controls>lib>events.py

Useful SSH Commands
------
* SSH Using Mac:
  * ssh root@<IP> -p 8022 -i “/Users/<user>/.ssh/openpilot_rsa”
* Remove stock OP and install this fork & branch:
  * cd .. && rm -rf openpilot && mkdir openpilot && cd openpilot && git clone https://www.github.com/seb43654/openpilot.git .
  * git checkout devel
  * Or use this install link: https://smiskol.com/fork/seb43654/devel
* cd selfdrive/debug ./dump.py <value below>
  * carParams
  * carState
  * carControl
  * carEvents
* cd panda/tests ./debug_console.py
* Remove GPS logfiles
  * find . -type f -name gps-data\* -exec rm {} \;

Directory Structure
------
    .
    ├── cereal              # The messaging spec and libs used for all logs
    ├── common              # Library like functionality we've developed here
    ├── installer/updater   # Manages auto-updates of NEOS
    ├── opendbc             # Files showing how to interpret data from cars
    ├── panda               # Code used to communicate on CAN
    ├── phonelibs           # Libraries used on NEOS devices
    ├── pyextra             # Libraries used on NEOS devices
    └── selfdrive           # Code needed to drive the car
        ├── assets          # Fonts, images and sounds for UI
        ├── athena          # Allows communication with the app
        ├── boardd          # Daemon to talk to the board
        ├── camerad         # Driver to capture images from the camera sensors
        ├── car             # Car specific code to read states and control actuators
        ├── common          # Shared C/C++ code for the daemons
        ├── controls        # Perception, planning and controls
        ├── debug           # Tools to help you debug and do car ports
        ├── locationd       # Soon to be home of precise location
        ├── logcatd         # Android logcat as a service
        ├── loggerd         # Logger and uploader of car data
        ├── modeld          # Driving and monitoring model runners
        ├── proclogd        # Logs information from proc
        ├── sensord         # IMU / GPS interface code
        ├── test            # Unit tests, system tests and a car simulator
        └── ui              # The UI

Licensing
------

openpilot is released under the MIT license. Some parts of the software are released under other licenses as specified.

Any user of this software shall indemnify and hold harmless comma.ai, Inc. and its directors, officers, employees, agents, stockholders, affiliates, subcontractors and customers from and against all allegations, claims, actions, suits, demands, damages, liabilities, obligations, losses, settlements, judgments, costs and expenses (including without limitation attorneys’ fees and costs) which arise out of, relate to or result from any use of this software by user.

**THIS IS ALPHA QUALITY SOFTWARE FOR RESEARCH PURPOSES ONLY. THIS IS NOT A PRODUCT.
YOU ARE RESPONSIBLE FOR COMPLYING WITH LOCAL LAWS AND REGULATIONS.
NO WARRANTY EXPRESSED OR IMPLIED.**

---

<img src="https://d1qb2nb5cznatu.cloudfront.net/startups/i/1061157-bc7e9bf3b246ece7322e6ffe653f6af8-medium_jpg.jpg?buster=1458363130" width="75"></img> <img src="https://cdn-images-1.medium.com/max/1600/1*C87EjxGeMPrkTuVRVWVg4w.png" width="225"></img>

[![openpilot tests](https://github.com/commaai/openpilot/workflows/openpilot%20tests/badge.svg?event=push)](https://github.com/commaai/openpilot/actions)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/commaai/openpilot.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/commaai/openpilot/alerts/)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/commaai/openpilot.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/commaai/openpilot/context:python)
[![Language grade: C/C++](https://img.shields.io/lgtm/grade/cpp/g/commaai/openpilot.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/commaai/openpilot/context:cpp)
[![codecov](https://codecov.io/gh/commaai/openpilot/branch/master/graph/badge.svg)](https://codecov.io/gh/commaai/openpilot)
