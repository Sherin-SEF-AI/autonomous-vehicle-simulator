# Advanced Autonomous Vehicle Simulation

A sophisticated autonomous vehicle simulator built with PyQt5 featuring advanced sensor systems, 3D visualization, and real-time simulation capabilities.

## Features

### Core Simulation
- **3D Visualization Engine**: Real-time 3D environment with PyOpenGL/VTK integration
- **Advanced Sensor Systems**: LiDAR, cameras (RGB/depth/thermal/stereo), radar, ultrasonic, IMU/GPS
- **Vehicle Physics**: Realistic vehicle dynamics with configurable parameters
- **Multi-vehicle Support**: Multiple autonomous vehicles with V2V communication

### Sensor Systems
- **LiDAR**: Configurable range, resolution, and point cloud visualization
- **Cameras**: Multiple camera types with real-time image processing
- **Radar**: Range-doppler visualization and target tracking
- **Ultrasonic**: Close-proximity detection
- **IMU/GPS**: Noise modeling and sensor fusion

### Advanced Features
- **Path Planning**: A*, RRT, PRM algorithms with visualization
- **Autonomous Algorithms**: Waypoint following, lane keeping, obstacle avoidance
- **Traffic Scenarios**: Generation and playback system
- **Data Recording**: Sensor data recording and replay functionality
- **Performance Metrics**: Real-time dashboard with graphs

### GUI Components
- **Modern Dark Theme**: Professional interface with customizable layouts
- **Central 3D Viewport**: Camera controls (orbit, pan, zoom, first-person)
- **Sensor Panels**: Live feeds from cameras and processed data
- **Control Panel**: Simulation parameters and vehicle settings
- **Timeline Scrubber**: Scenario playback and analysis
- **Real-time Plots**: Vehicle telemetry and sensor data visualization

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd robotics-simulation
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python main.py
```

## Project Structure

```
robotics-simulation/
├── main.py                 # Main application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── config/                # Configuration files
│   ├── settings.yaml      # Application settings
│   └── scenarios/         # Pre-built scenarios
├── src/                   # Source code
│   ├── core/             # Core application components
│   ├── gui/              # GUI components and widgets
│   ├── simulation/       # Simulation engine
│   ├── sensors/          # Sensor models and processing
│   ├── visualization/    # 3D visualization engine
│   ├── algorithms/       # Path planning and AI algorithms
│   └── utils/            # Utility functions and helpers
├── assets/               # Resources (icons, models, textures)
├── data/                 # Data storage and exports
└── tests/                # Unit tests
```

## Usage

### Basic Operation
1. Launch the application
2. Load a scenario or create a new one
3. Configure vehicle and sensor parameters
4. Start the simulation
5. Monitor sensor data and vehicle performance

### Advanced Features
- **Custom Scenarios**: Create and save custom simulation scenarios
- **Sensor Configuration**: Adjust sensor parameters in real-time
- **Data Export**: Export sensor data in standard formats (PCD, rosbag-like)
- **Plugin System**: Extend functionality with custom plugins

## Development

### Architecture
The application follows a modular architecture with clear separation of concerns:
- **Core**: Application lifecycle and main coordination
- **GUI**: User interface components and event handling
- **Simulation**: Physics engine and world simulation
- **Sensors**: Sensor models and data processing
- **Visualization**: 3D rendering and graphics
- **Algorithms**: Path planning and autonomous driving algorithms

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- PyQt5 for the GUI framework
- PyOpenGL/VTK for 3D visualization
- NumPy/SciPy for scientific computing
- OpenCV for computer vision algorithms 