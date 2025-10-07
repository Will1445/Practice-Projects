# Welcome to my practice projects

These are small, self-contained projects that I work on to further my coding skills across multiple languages. Here's an outline of each project

## Year 1

### Epicycles

- A visualisation of how Fourier can be used to model 2D images
- Simply run the file and click to begin drawing out a shape
- Click again to finish drawing and the program will automatically draw out the shape using rotating circles of constant rotational velocity

### Planet orbits

- A collection of Pygame simulations of the interactions of planets
- There are some preset scenarios like the 2- and 3-planet systems, a 3-body binary star system, and a model for the solar system
- The `n_planet_system` files can be used to simulate any number of planets, even with your mouse acting as a point of gravitational attraction

### Superconductor Modelling

- A collection of files modelling the behaviour of a superconductor around and below its critical temperature
- `Super_conductor_count.py` can be used to find an estimate of the critical temperature of a super conductor given its rough composition

## Year 2

### C++ practice

- A set of files for developing the basic skills of c++ alongside some simple applications

### Digital clock

- A Pygame program displaying a digital 7 segment display clock using analogue clocks
- The clocks have three main phases which can be adjusted in length
- Variations of the moving phase as well as fading in an out of the unused hands is to be added later

### Duolingo

- A bot to automatically solve Spanish Duolingo exercises
- To use, open Chrome in debug mode and start a practice session before starting the file
- Current only a few questions have automatic answers, shown in the utils folder
- `Fill_in_the_blank.py` is currently not functioning, a new sentence structure model with an API is needed
- The questions and languages available to be solved will be expanded

### Hand tracking

- A simple ML program to track hand motion through the provided camera
- By raising your first two fingers on your right hand, you can send scroll right and scroll left commands on macOS by moving your hand in that direction
- The amount of possible hand-based input commands will be expanded

### Remote access

- The client half of a remote desktop and keylogger application
- This is set to receive data from a c++ compiled executable on the target machine
- The code and executable on the target machine are not present on this repository but may be added later
- This directory contains its own README to explain how to use the code for the desired effect

### TTS

- A system for automatically making tik-tok style videos using a tts program 
- currently uses Google Cloud TTS (https://console.cloud.google.com/iam-admin/quotas?inv=1&invt=AbyXFw&project=snappy-climber-460918-v0)
- Remember to activate the credentials before running the program (export export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-file.json") 