"""
Traffic Generator Module — Time-based vehicle spawning

Instead of a per-frame probability (which spawns far too many vehicles at
60 fps), this generator uses wall-clock intervals of 2–4 seconds.
"""

import time
import random
from .vehicle import Vehicle
import config


class TrafficGenerator:
    """Time-based traffic generator for each approach lane."""

    SIDES = ("NORTH", "SOUTH", "EAST", "WEST")

    def __init__(self):
        self.vehicle_types  = list(config.VEHICLE_PROBABILITIES.keys())
        self.probabilities  = list(config.VEHICLE_PROBABILITIES.values())
        self.max_vehicles   = config.MAX_VEHICLES_PER_SIDE

        # per-side cooldown timers
        now = time.time()
        self._last_spawn = {s: now for s in self.SIDES}
        self._next_interval = {
            s: random.uniform(config.SPAWN_INTERVAL_MIN, config.SPAWN_INTERVAL_MAX)
            for s in self.SIDES
        }

    # ------------------------------------------------------------------ #
    def generate_vehicle(self, side: str, current_count: int):
        """
        Return a new Vehicle for *side* if the cooldown has elapsed and
        the queue isn't full.  Otherwise return None.
        """
        if current_count >= self.max_vehicles:
            return None

        now = time.time()
        elapsed = now - self._last_spawn[side]
        if elapsed < self._next_interval[side]:
            return None

        # Reset timer with a fresh random interval
        self._last_spawn[side] = now
        self._next_interval[side] = random.uniform(
            config.SPAWN_INTERVAL_MIN, config.SPAWN_INTERVAL_MAX
        )

        vtype = random.choices(self.vehicle_types, weights=self.probabilities)[0]
        return Vehicle(side, vtype, queue_position=current_count)
