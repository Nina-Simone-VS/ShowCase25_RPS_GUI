# 🤖 Robotics Control GUI & HMI Interface

**A Human-Machine Interface (HMI) and Game-Based Control System for a Robotic Hand named Handy.**

## 🎯 Project Goal

To develop a user-friendly and robust control interface for a robotic hand, enabling both direct assistive **mimicry functionality** and engaging **game-based interaction** (Rock, Paper, Scissors). This project serves as a foundational platform for future assistive and interactive robotics development.

## 🗝 Key Features & Functionality (My Contribution)

The High-Level Interface (HMI) was developed entirely in Python, utilizing the **Kivy** and **KivyMD** frameworks for a modern, cross-platform design.

* **Custom HMI Development:** Engineered a full-screen, user-centric GUI across two primary screens, allowing for intuitive control and display of real-time camera feed.
* **Asynchronous Command Thread:** Designed and implemented the main application logic to manage the UI thread independently from the command thread, ensuring the interface remains responsive while sending commands to the robotic system.
* **Game State Management:** Developed the complete logic for the three-round **Rock, Paper, Scissors game**, including a custom **color-changing countdown widget** and an interactive **scoreboard** to track results.
* **Gesture Trigger Interfacing:** Created the command calls from the UI that securely activate the external gesture recognition module (`gestures.py`) to execute specific hand movements.

## 💻 Technical Stack

| Component | Technology | Files |
| :--- | :--- | :--- |
| **HMI / GUI** (Your Work) | **Python** (Kivy, KivyMD), Procedural Programming | `handymain.kv`, `HandyMain.py` |
| **Control Logic** (Partner's Work) | **Python** (Servo Control, Gesture Recognition) | `Hand_Gesture_Recognition02.41.py` |
| **Databases** | SQL (Foundational Knowledge) | *N/A (Project Management)* |
| **Underlying Concepts** | Control Systems (Theory), Logic Gates, Microcontrollers | *N/A (Hardware Implementation)* |

## 🧑‍🤝‍🧑 Project Team & Attribution (Crucial)

This project was a collaborative effort. **My primary role was the design, development, and implementation of the full Python HMI/GUI.**

| Developer | Primary Role | Key Contributions |
| :--- | :--- | :--- |
| **Nina-Simone van Staden** | **Lead HMI/GUI Developer & Project Manager** | UI Design, Command Thread Logic, Game State Management, Project Documentation, Assisted Mini Robot Construction |
| **Buhle Ndzamela** | **Core Control Logic & Gesture Recognition** | Development of the Servo Control, Hand Mimicry, and Gesture Recognition Python modules, Command Thread Logic |
| **Joshua Naidoo** | **Showcase Design and Aesthetics** | Slideshow presentation, Mini-Robot construction, Showcase table setup & design, Project Documentation|
| **Bryan Marte** | **Physical Hand Design** | Design actual hand, 3D Print design, Construction|
| **Bea Botha** | **General Assistance** | Resource procurement, Assisted RPS Code, Present at showcase|

## 🖼️ Visual Demonstration

> A brief video demonstrating the HMI in action: (not currently available)

## ▶️ Setup and Execution

To run the HMI locally, you will need the following dependencies:

1.  Clone this repository: `git clone https://github.com/Nina-Simone-VS/ShowCase25_RPS_GUI/tree/main`
2.  Install Kivy and KivyMD dependencies: `pip install kivy kivymd`
3.  Execute the main application file: `python HandyMain.py`
