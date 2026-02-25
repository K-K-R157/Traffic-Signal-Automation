"""
Intersection Module
Manages the 4-sided intersection, vehicle queuing, and movement.

Key responsibilities:
  • Spawn vehicles via TrafficGenerator (time-based).
  • Separate each side's vehicles into *queued* (before stop-line)
    and *through* (already past the stop-line).
  • Queued vehicles maintain MIN_FOLLOWING_DISTANCE and obey signals.
  • Through vehicles always keep moving.
"""

import config
from .traffic_generator import TrafficGenerator


class Intersection:
    """Manages a 4-approach intersection with traffic signals."""

    SIDES = ("NORTH", "SOUTH", "EAST", "WEST")

    def __init__(self, signal_controller):
        self.signal_controller = signal_controller
        self.traffic_generator = TrafficGenerator()

        self.vehicles = {s: [] for s in self.SIDES}
        self.window_size = (1920, 1080)

        # statistics
        self.total_vehicles_crossed = 0
        self.vehicles_crossed_by_type = {"CAR": 0, "TRUCK": 0, "AMBULANCE": 0}

    # ------------------------------------------------------------------ #
    #  Public helpers
    # ------------------------------------------------------------------ #
    def set_window_size(self, w, h):
        self.window_size = (w, h)

    def get_all_vehicles(self):
        return [v for lst in self.vehicles.values() for v in lst]

    def get_vehicle_count(self, side):
        return len(self.vehicles[side])

    def get_total_vehicle_count(self):
        return sum(len(v) for v in self.vehicles.values())

    # ------------------------------------------------------------------ #
    #  Main update  (called once per frame)
    # ------------------------------------------------------------------ #
    def update(self):
        self.signal_controller.update()
        self._spawn_vehicles()

        cx = self.window_size[0] // 2
        cy = self.window_size[1] // 2

        for side in self.SIDES:
            self._update_side(side, cx, cy)

        self._remove_crossed()

    # ------------------------------------------------------------------ #
    #  Spawning
    # ------------------------------------------------------------------ #
    def _spawn_vehicles(self):
        cx, cy = self.window_size[0] // 2, self.window_size[1] // 2
        for side in self.SIDES:
            new_v = self.traffic_generator.generate_vehicle(
                side, len(self.vehicles[side])
            )
            if new_v is not None:
                new_v.setup_path(cx, cy, *self.window_size)
                self.vehicles[side].append(new_v)

    # ------------------------------------------------------------------ #
    #  Per-side movement logic
    # ------------------------------------------------------------------ #
    def _update_side(self, side, cx, cy):
        vehicles = self.vehicles[side]

        # Ensure every vehicle has its path initialised
        for v in vehicles:
            v.setup_path(cx, cy, *self.window_size)

        # Determine whether queued vehicles on this side should be held.
        # • GREEN  → move (after the short start-delay)
        # • YELLOW on the *current* (outgoing) side → still moving
        # • YELLOW on the *next* (get-ready) side   → hold
        # • RED    → hold
        signal_state = self.signal_controller.get_signal_state(side)
        from traffic_signal.signal_state import SignalState

        if signal_state == SignalState.GREEN:
            green_elapsed = self.signal_controller.get_green_elapsed(side)
            hold_queue = (green_elapsed >= 0
                          and green_elapsed < config.GREEN_START_DELAY)
        elif signal_state == SignalState.YELLOW and self.signal_controller.current_side == side:
            # Outgoing yellow — this lane was just green, let traffic pass
            hold_queue = False
        else:
            # RED or incoming "get-ready" yellow → hold
            hold_queue = True

        # Split into "queued" (before stop-line) and "through" (past it)
        queued  = [v for v in vehicles if not v.has_passed_stop_line(cx, cy) and not v.crossed]
        through = [v for v in vehicles if v.has_passed_stop_line(cx, cy) and not v.crossed]

        # Sort queued so that the vehicle closest to stop-line is index 0
        queued.sort(key=lambda v: v.get_distance_from_stop_line(cx, cy))

        for i, v in enumerate(queued):
            v.stopped = False
            dist_to_line = v.get_distance_from_stop_line(cx, cy)

            if i == 0:
                # --- first vehicle in queue ---
                if hold_queue and dist_to_line < v.speed * 5:
                    v.stopped = True
                else:
                    v.move()
            else:
                # --- subsequent vehicles ---
                ahead = queued[i - 1]
                gap = v.distance_to_vehicle_ahead(ahead)

                if gap < config.MIN_FOLLOWING_DISTANCE:
                    v.stopped = True
                elif hold_queue and dist_to_line < v.speed * 5:
                    v.stopped = True
                else:
                    v.move()

        # Through vehicles always keep moving
        for v in through:
            v.stopped = False
            v.move()

    # ------------------------------------------------------------------ #
    #  Cleanup
    # ------------------------------------------------------------------ #
    def _remove_crossed(self):
        for side in self.SIDES:
            for v in self.vehicles[side]:
                if v.crossed:
                    self.total_vehicles_crossed += 1
                    vt = v.vehicle_type
                    if vt in self.vehicles_crossed_by_type:
                        self.vehicles_crossed_by_type[vt] += 1
            self.vehicles[side] = [v for v in self.vehicles[side] if not v.crossed]
