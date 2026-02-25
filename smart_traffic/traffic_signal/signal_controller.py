"""
Signal Controller Module
Controls traffic signal timing and state changes for all sides
"""

import time
from .signal_state import SignalState
from config import GREEN_LIGHT_DURATION, YELLOW_LIGHT_DURATION

class SignalController:
    """
    Controls traffic signals for a 4-sided intersection
    Cycles through sides sequentially: North -> East -> South -> West -> repeat (clockwise)
    """
    
    def __init__(self):
        """Initialize signal controller with all sides starting as RED"""
        self.sides = ["NORTH", "EAST", "SOUTH", "WEST"]  # clockwise order
        self.current_side_index = 0
        self.current_side = self.sides[0]
        
        # All signals start as RED
        self.signals = {
            "NORTH": SignalState.RED,
            "SOUTH": SignalState.RED,
            "EAST": SignalState.RED,
            "WEST": SignalState.RED
        }
        
        # Set first side to GREEN
        self.signals[self.current_side] = SignalState.GREEN
        
        # Timing
        self.last_change_time = time.time()
        self.green_duration = GREEN_LIGHT_DURATION
        self.yellow_duration = YELLOW_LIGHT_DURATION
        
    def update(self):
        """
        Update signal states based on elapsed time.

        Cycle for the *current* side:  GREEN → YELLOW → RED
        When current goes YELLOW the *next* side also turns YELLOW
        ("get-ready" indicator).  When the yellow period ends the
        current side goes RED and the next side goes GREEN.
        """
        current_time = time.time()
        elapsed = current_time - self.last_change_time

        current_state = self.signals[self.current_side]
        next_index = (self.current_side_index + 1) % len(self.sides)
        next_side  = self.sides[next_index]

        # GREEN → YELLOW  (both current *and* next side turn yellow)
        if current_state == SignalState.GREEN and elapsed >= self.green_duration:
            self.signals[self.current_side] = SignalState.YELLOW
            self.signals[next_side]         = SignalState.YELLOW
            self.last_change_time = current_time

        # YELLOW → current goes RED, next goes GREEN
        elif current_state == SignalState.YELLOW and elapsed >= self.yellow_duration:
            self.signals[self.current_side] = SignalState.RED
            self.signals[next_side]         = SignalState.GREEN

            # Advance pointer
            self.current_side_index = next_index
            self.current_side       = next_side
            self.last_change_time   = current_time
    
    def get_signal_state(self, side):
        """
        Get current signal state for a specific side
        
        Args:
            side (str): Side name ("NORTH", "SOUTH", "EAST", "WEST")
            
        Returns:
            SignalState: Current state of the signal
        """
        return self.signals.get(side, SignalState.RED)
    
    def is_green(self, side):
        """Check if signal is green for given side"""
        return self.signals.get(side) == SignalState.GREEN
    
    def is_red(self, side):
        """Check if signal is red for given side"""
        return self.signals.get(side) == SignalState.RED

    def get_green_elapsed(self, side):
        """Return seconds since *side* turned green, or -1 if not green."""
        if self.signals.get(side) != SignalState.GREEN:
            return -1
        return time.time() - self.last_change_time
    
    def get_remaining_time(self):
        """Get remaining time for current state"""
        current_time = time.time()
        elapsed = current_time - self.last_change_time
        
        current_state = self.signals[self.current_side]
        if current_state == SignalState.GREEN:
            return max(0, self.green_duration - elapsed)
        elif current_state == SignalState.YELLOW:
            return max(0, self.yellow_duration - elapsed)
        return 0
