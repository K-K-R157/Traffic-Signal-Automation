# Smart Traffic Signal Simulation

## Project Structure

```
traffic_simulation_implementation/
├── main.py                          # Run this file to start simulation
├── config.py                        # Configuration settings
├── traffic_signal/
│   ├── __init__.py
│   ├── signal_state.py              # Signal states (RED, YELLOW, GREEN)
│   └── signal_controller.py         # Signal timing control
├── traffic_simulation/
│   ├── __init__.py
│   ├── vehicle.py                   # Vehicle class with types
│   ├── traffic_generator.py         # Random vehicle generation
│   └── intersection.py              # Intersection management
└── visualization/
    ├── __init__.py
    └── traffic_display.py           # Fullscreen GUI display
```

## How to Run

```bash
cd traffic_simulation_implementation
python main.py
```

## Run API Backend For React UI

```bash
cd smart_traffic
pip install flask
python api_server.py
```

API server starts on `http://127.0.0.1:5000` and exposes:

- `GET /api/state` - live simulation state
- `POST /api/control/running` - pause/resume simulation
- `POST /api/control/reset` - reset simulation
- `POST /api/control/speed` - update simulation speed
- `POST /api/control/timings` - update green/yellow timings
- `POST /api/control/manual-override` - force one side GREEN
- `POST /api/control/emergency` - trigger emergency priority by side

## Controls

- **ESC** or **Q** - Exit simulation
- **F** - Toggle fullscreen/windowed mode

## Features

✓ Fullscreen display
✓ Different vehicle types (Car, Truck, Bus) with distinct appearances
✓ Each vehicle has unique number ID
✓ Sequential traffic signal control
✓ Vehicles stop at red signals
✓ Vehicles move when signal is green
✓ Real-time statistics display
