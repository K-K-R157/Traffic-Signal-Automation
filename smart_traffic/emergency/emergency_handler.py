"""
Emergency Handler Module

Monitors all lanes for emergency vehicles (AMBULANCE type).
When an ambulance is detected approaching a stop-line, it is added to
a first-come-first-served queue.  The handler processes the queue one
at a time:

  • If the ambulance's lane is already GREEN → no signal change needed,
    just track it until it crosses.
  • Otherwise → request a signal preemption (yellow transition,
    then green for that lane).

After each ambulance crosses, the next queued one is processed.
"""

import time
import config


class EmergencyHandler:
    """Detects ambulances and coordinates signal preemption (FCFS)."""

    def __init__(self, signal_controller):
        self.signal_controller = signal_controller
        self.detection_distance = config.EMERGENCY_DETECTION_DISTANCE

        # ---- public state (read by display) ---- #
        self.active = False            # True while ANY emergency is being handled
        self.emergency_side = None     # Side of the ambulance currently being served
        self.emergency_vehicle = None  # Reference to that ambulance
        self.needs_signal_change = False  # True only when a signal preemption is running

        # ---- FCFS queue ---- #
        # Each entry: (side, vehicle_ref, detection_time)
        self._queue: list = []
        self._queued_ids: set = set()   # vehicle ids already queued (dedup)

        # ---- saved normal-cycle state ---- #
        self._saved_side_index = None
        self._saved_side = None

    # ------------------------------------------------------------------ #
    #  Called every frame by Intersection.update()
    # ------------------------------------------------------------------ #
    def check_for_emergency(self, vehicles_by_side: dict, cx: int, cy: int):
        # 1) Scan for NEW approaching ambulances and enqueue them
        for side, vehicles in vehicles_by_side.items():
            for v in vehicles:
                if v.vehicle_type != 'AMBULANCE':
                    continue
                if v.crossed or v.vehicle_id in self._queued_ids:
                    continue
                dist = v.get_distance_from_stop_line(cx, cy)
                if 0 < dist < self.detection_distance:
                    self._queue.append((side, v, time.time()))
                    self._queued_ids.add(v.vehicle_id)

        # 2) If we are handling one, check if it's resolved
        if self.active:
            self._check_resolved(cx, cy)
            return

        # 3) If nothing active but queue is non-empty, serve next
        if self._queue:
            self._serve_next()

    # ------------------------------------------------------------------ #
    #  Serve the next ambulance in the FCFS queue
    # ------------------------------------------------------------------ #
    def _serve_next(self):
        side, vehicle, _ = self._queue.pop(0)

        # If the vehicle already crossed while waiting in queue, skip it
        if vehicle.crossed:
            self._queued_ids.discard(vehicle.vehicle_id)
            return                     # next frame will try again

        self.active = True
        self.emergency_side = side
        self.emergency_vehicle = vehicle

        sc = self.signal_controller

        # If this side is ALREADY green → no signal change at all
        if sc.is_green(side):
            self.needs_signal_change = False
            return

        # Otherwise, save state and request preemption
        self.needs_signal_change = True
        self._saved_side_index = sc.current_side_index
        self._saved_side = sc.current_side
        sc.start_emergency(side)

    # ------------------------------------------------------------------ #
    #  Check whether the current ambulance has passed
    # ------------------------------------------------------------------ #
    def _check_resolved(self, cx: int, cy: int):
        v = self.emergency_vehicle
        if v is None or v.crossed or v.has_passed_stop_line(cx, cy):
            # Before deactivating, check if more ambulances on the SAME side
            # are waiting in the queue — let them pass in the same green.
            vid = v.vehicle_id if v else None
            if vid:
                self._queued_ids.discard(vid)

            same_side = self.emergency_side
            next_same = None
            remaining = []
            for entry in self._queue:
                s, veh, t = entry
                if veh.crossed:
                    self._queued_ids.discard(veh.vehicle_id)
                    continue
                if next_same is None and s == same_side:
                    next_same = entry
                else:
                    remaining.append(entry)

            if next_same is not None:
                # Swap to the next ambulance on the same side — keep green
                self._queue = remaining
                _, next_veh, _ = next_same
                self.emergency_vehicle = next_veh
                # active, emergency_side, needs_signal_change stay the same
                return

            # No more on this side — deactivate normally
            self._deactivate()

    # ------------------------------------------------------------------ #
    #  Deactivate current emergency, resume normal cycle if needed
    # ------------------------------------------------------------------ #
    def _deactivate(self):
        if self.needs_signal_change:
            sc = self.signal_controller
            sc.end_emergency(
                resume_side_index=self._saved_side_index,
                resume_side=self._saved_side,
            )

        self.active = False
        self.emergency_side = None
        self.emergency_vehicle = None
        self.needs_signal_change = False
