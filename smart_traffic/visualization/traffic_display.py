"""
Traffic Display Module
Pygame-based visualisation that renders the intersection, signals,
and vehicles using real photo images from the photo/ folder.
"""

import os
import math
import random
import pygame
import config
from traffic_signal import SignalState


class TrafficDisplay:
    """Fullscreen Pygame display for the traffic simulation."""

    def __init__(self):
        pygame.init()

        if config.FULLSCREEN:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            info = pygame.display.Info()
            self.screen = pygame.display.set_mode(
                (info.current_w - 100, info.current_h - 100)
            )

        self.width  = self.screen.get_width()
        self.height = self.screen.get_height()
        pygame.display.set_caption("Smart Traffic Signal Simulation")
        self.clock = pygame.time.Clock()

        # fonts
        self.font_large      = pygame.font.Font(None, 48)
        self.font_medium     = pygame.font.Font(None, 32)
        self.font_small      = pygame.font.Font(None, 24)
        self.font_vehicle_id = pygame.font.Font(None, 18)

        self.fullscreen = config.FULLSCREEN

        # ----- load vehicle images ----- #
        # { vehicle_type : [surface, surface, …] }
        self.vehicle_images: dict[str, list[pygame.Surface]] = {}
        self._vehicle_image_map: dict[str, pygame.Surface] = {}  # vid → chosen surface
        self._load_vehicle_images()

    # ------------------------------------------------------------------ #
    #  Image loading
    # ------------------------------------------------------------------ #
    def _load_vehicle_images(self):
        """Load, scale, and pre-rotate every image so they all face UP."""
        photo_dir = config.PHOTO_DIR
        # Pre-rotation to normalise every sprite to face UP (north)
        dir_to_angle = {"UP": 0, "RIGHT": 90, "DOWN": 180, "LEFT": -90}

        for vtype, filenames in config.VEHICLE_IMAGES.items():
            w, h = config.VEHICLE_DISPLAY_SIZES.get(vtype, (35, 55))
            surfaces = []
            for fname in filenames:
                # Per-file rotation from IMAGE_DIRECTION (keyed by filename)
                pre_rot = dir_to_angle.get(
                    config.IMAGE_DIRECTION.get(fname, "UP"), 0
                )
                path = os.path.join(photo_dir, fname)
                try:
                    img = pygame.image.load(path).convert_alpha()
                    if pre_rot != 0:
                        img = pygame.transform.rotate(img, pre_rot)
                    img = pygame.transform.smoothscale(img, (w, h))
                    surfaces.append(img)
                except Exception:
                    fallback = pygame.Surface((w, h), pygame.SRCALPHA)
                    fallback.fill((120, 120, 120))
                    surfaces.append(fallback)
            self.vehicle_images[vtype] = surfaces if surfaces else [
                pygame.Surface((w, h), pygame.SRCALPHA)
            ]

    def _get_image_for(self, vehicle) -> pygame.Surface:
        """Return the (unrotated) image assigned to *vehicle*."""
        vid = vehicle.vehicle_id
        if vid not in self._vehicle_image_map:
            pool = self.vehicle_images.get(vehicle.vehicle_type, [])
            if pool:
                self._vehicle_image_map[vid] = random.choice(pool)
            else:
                s = pygame.Surface((30, 50), pygame.SRCALPHA)
                s.fill((120, 120, 120))
                self._vehicle_image_map[vid] = s
        return self._vehicle_image_map[vid]

    # ------------------------------------------------------------------ #
    #  Fullscreen toggle
    # ------------------------------------------------------------------ #
    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            info = pygame.display.Info()
            self.screen = pygame.display.set_mode(
                (info.current_w - 100, info.current_h - 100)
            )
        self.width  = self.screen.get_width()
        self.height = self.screen.get_height()

    # ------------------------------------------------------------------ #
    #  Main draw entry point
    # ------------------------------------------------------------------ #
    def draw(self, intersection):
        intersection.set_window_size(self.width, self.height)
        self.screen.fill(config.COLOR_BACKGROUND)

        self._draw_title()
        self._draw_roads()
        self._draw_signals(intersection.signal_controller)
        self._draw_vehicles(intersection.get_all_vehicles())
        self._draw_statistics(intersection)
        self._draw_controls()
        self._draw_emergency_indicator(intersection)

        pygame.display.flip()
        self.clock.tick(config.FPS)

    # ------------------------------------------------------------------ #
    #  Title
    # ------------------------------------------------------------------ #
    def _draw_title(self):
        title = self.font_large.render(
            "Smart Traffic Signal Simulation", True, config.COLOR_TEXT
        )
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 20))

    # ------------------------------------------------------------------ #
    #  Roads & markings
    # ------------------------------------------------------------------ #
    def _draw_roads(self):
        cx = self.width  // 2
        cy = self.height // 2
        rw = config.ROAD_WIDTH

        # vertical road
        pygame.draw.rect(self.screen, config.COLOR_ROAD,
                         (cx - rw // 2, 0, rw, self.height))
        # horizontal road
        pygame.draw.rect(self.screen, config.COLOR_ROAD,
                         (0, cy - rw // 2, self.width, rw))

        self._draw_road_markings(cx, cy, rw)

    def _draw_road_markings(self, cx, cy, rw):
        dash, gap, lw = 30, 20, 4

        # vertical centre dashes
        for y in range(0, self.height, dash + gap):
            if y < cy - rw // 2 or y > cy + rw // 2:
                pygame.draw.line(self.screen, config.COLOR_ROAD_LINE,
                                 (cx, y), (cx, min(y + dash, self.height)), lw)

        # horizontal centre dashes
        for x in range(0, self.width, dash + gap):
            if x < cx - rw // 2 or x > cx + rw // 2:
                pygame.draw.line(self.screen, config.COLOR_ROAD_LINE,
                                 (x, cy), (min(x + dash, self.width), cy), lw)

        # stop lines (yellow)
        sl = config.STOP_LINE_OFFSET
        slw = 8
        half = rw // 2 - 10

        # north stop line (right half of vertical road — LHT)
        pygame.draw.line(self.screen, config.COLOR_ROAD_MARKING,
                         (cx, cy - sl), (cx + half, cy - sl), slw)
        # south stop line (left half — LHT)
        pygame.draw.line(self.screen, config.COLOR_ROAD_MARKING,
                         (cx - half, cy + sl), (cx, cy + sl), slw)
        # east stop line (bottom half of horizontal road — LHT)
        pygame.draw.line(self.screen, config.COLOR_ROAD_MARKING,
                         (cx + sl, cy), (cx + sl, cy + half), slw)
        # west stop line (top half — LHT)
        pygame.draw.line(self.screen, config.COLOR_ROAD_MARKING,
                         (cx - sl, cy - half), (cx - sl, cy), slw)

    # ------------------------------------------------------------------ #
    #  Traffic signals
    # ------------------------------------------------------------------ #
    def _draw_signals(self, sc):
        cx = self.width  // 2
        cy = self.height // 2
        off = 120

        # Signals near the stop lines (same side as the approaching lane)
        positions = {
            "NORTH": (cx + 50, cy - off),
            "SOUTH": (cx - 50, cy + off),
            "EAST":  (cx + off, cy + 50),
            "WEST":  (cx - off, cy - 50),
        }
        # Timer placed outside the road so it never overlaps vehicles
        rw2 = config.ROAD_WIDTH // 2
        timer_positions = {
            "NORTH": (cx + rw2 + 40, cy - off),
            "SOUTH": (cx - rw2 - 40, cy + off),
            "EAST":  (cx + off, cy + rw2 + 40),
            "WEST":  (cx - off, cy - rw2 - 40),
        }

        for side, pos in positions.items():
            state = sc.get_signal_state(side)
            if   state == SignalState.RED:    color = config.COLOR_SIGNAL_RED
            elif state == SignalState.YELLOW: color = config.COLOR_SIGNAL_YELLOW
            else:                            color = config.COLOR_SIGNAL_GREEN

            # background box
            bg = pygame.Rect(pos[0] - 25, pos[1] - 40, 50, 80)
            pygame.draw.rect(self.screen, (0, 0, 0), bg, border_radius=10)

            # light
            pygame.draw.circle(self.screen, color, pos, config.SIGNAL_SIZE)
            pygame.draw.circle(self.screen, (255, 255, 255), pos,
                               config.SIGNAL_SIZE, 3)

            # side label
            lbl = self.font_small.render(side, True, config.COLOR_TEXT)
            self.screen.blit(lbl, (pos[0] - lbl.get_width() // 2, pos[1] - 65))

            # countdown timer (outside the road, never overlaps vehicles)
            remaining = sc.get_remaining_time()
            # Show timer for the active side AND for the next side
            # during the "get-ready" yellow phase
            next_idx  = (sc.current_side_index + 1) % len(sc.sides)
            next_side = sc.sides[next_idx]
            show_timer = (sc.current_side == side or
                          (next_side == side
                           and state == SignalState.YELLOW
                           and sc.get_signal_state(sc.current_side) == SignalState.YELLOW))
            if show_timer and remaining > 0:
                tp = timer_positions[side]
                txt = self.font_medium.render(f"{int(remaining)}s", True,
                                              config.COLOR_TEXT)
                self.screen.blit(txt, (tp[0] - txt.get_width() // 2,
                                       tp[1] - txt.get_height() // 2))

    # ------------------------------------------------------------------ #
    #  Vehicles (photo images + license plates)
    # ------------------------------------------------------------------ #
    def _draw_vehicles(self, vehicles):
        for v in vehicles:
            self._draw_single_vehicle(v)

    def _draw_single_vehicle(self, v):
        base_img = self._get_image_for(v)

        # --- rotation ---
        # vehicle.angle is atan2 (0°=east, 90°=south, -90°=north, 180°=west)
        # If image faces UP (north), rotation formula:
        if config.IMAGE_FACES == "UP":
            rot_deg = -v.angle - 90
        else:  # image faces RIGHT (east)
            rot_deg = -v.angle

        rotated = pygame.transform.rotate(base_img, rot_deg)
        rect = rotated.get_rect(center=(int(v.x), int(v.y)))
        self.screen.blit(rotated, rect)

        # --- tiny license plate label --- #
        plate = self.font_vehicle_id.render(v.vehicle_id, True, (0, 0, 0))
        pw, ph = plate.get_size()
        bg = pygame.Surface((pw + 4, ph + 2), pygame.SRCALPHA)
        bg.fill((255, 255, 200, 210))
        # position the plate just below the vehicle image
        px = int(v.x) - (pw + 4) // 2
        py = rect.bottom + 1
        self.screen.blit(bg, (px, py))
        self.screen.blit(plate, (px + 2, py + 1))

    # ------------------------------------------------------------------ #
    #  Statistics panel
    # ------------------------------------------------------------------ #
    def _draw_statistics(self, intersection):
        px, py = 20, 100
        pw, ph = 350, 380
        panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
        panel.fill((20, 20, 20, 200))
        self.screen.blit(panel, (px, py))

        y = py + 15
        t = self.font_medium.render("Statistics", True, config.COLOR_TEXT)
        self.screen.blit(t, (px + 15, y)); y += 45

        self.screen.blit(
            self.font_small.render("Vehicles Waiting:", True, config.COLOR_TEXT),
            (px + 15, y)
        ); y += 30

        for side in ("NORTH", "SOUTH", "EAST", "WEST"):
            cnt   = intersection.get_vehicle_count(side)
            state = intersection.signal_controller.get_signal_state(side)
            if   state == SignalState.GREEN:  c = config.COLOR_SIGNAL_GREEN
            elif state == SignalState.YELLOW: c = config.COLOR_SIGNAL_YELLOW
            else:                            c = config.COLOR_SIGNAL_RED
            lbl = self.font_small.render(f"  {side}: {cnt}", True, c)
            self.screen.blit(lbl, (px + 20, y)); y += 28

        y += 15
        total = intersection.get_total_vehicle_count()
        self.screen.blit(
            self.font_small.render(f"Total Active: {total}", True, config.COLOR_TEXT),
            (px + 15, y)
        ); y += 35

        crossed = intersection.total_vehicles_crossed
        self.screen.blit(
            self.font_small.render(f"Vehicles Crossed: {crossed}", True,
                                   config.COLOR_TEXT),
            (px + 15, y)
        ); y += 30

        self.screen.blit(
            self.font_small.render("Crossed by Type:", True, config.COLOR_TEXT),
            (px + 15, y)
        ); y += 28

        type_colors = {"CAR": (0, 180, 255), "TRUCK": (0, 200, 120),
                       "AMBULANCE": (255, 100, 100)}
        for vt, clr in type_colors.items():
            cnt = intersection.vehicles_crossed_by_type.get(vt, 0)
            lbl = self.font_small.render(f"  {vt}: {cnt}", True, clr)
            self.screen.blit(lbl, (px + 20, y)); y += 28

    # ------------------------------------------------------------------ #
    #  Controls footer
    # ------------------------------------------------------------------ #
    def _draw_controls(self):
        txt = "Controls: ESC or Q - Exit  |  F - Toggle Fullscreen"
        lbl = self.font_small.render(txt, True, config.COLOR_TEXT)
        self.screen.blit(lbl, (self.width // 2 - lbl.get_width() // 2,
                               self.height - 40))

    # ------------------------------------------------------------------ #
    #  Emergency indicator
    # ------------------------------------------------------------------ #
    def _draw_emergency_indicator(self, intersection):
        """Show a flashing EMERGENCY banner in the top-right corner."""
        eh = intersection.emergency_handler
        if not eh.active:
            return

        # Flashing effect (toggle every ~0.4 sec)
        import time
        show = int(time.time() * 2.5) % 2 == 0
        if not show:
            return

        banner_w, banner_h = 420, 45
        bx = self.width - banner_w - 20   # 20 px margin from right edge
        by = 20                            # top margin
        bg = pygame.Surface((banner_w, banner_h), pygame.SRCALPHA)
        bg.fill((200, 0, 0, 220))
        self.screen.blit(bg, (bx, by))

        side = eh.emergency_side or "?"
        txt = self.font_medium.render(
            f"EMERGENCY  —  Ambulance on {side}", True, (255, 255, 255)
        )
        self.screen.blit(txt, (bx + banner_w // 2 - txt.get_width() // 2,
                               by + banner_h // 2 - txt.get_height() // 2))

        # Show queued count if more than one waiting
        qlen = len(eh._queue)
        if qlen > 0:
            q_txt = self.font_small.render(
                f"+{qlen} more in queue", True, (255, 200, 200)
            )
            self.screen.blit(q_txt, (bx + banner_w // 2 - q_txt.get_width() // 2,
                                     by + banner_h + 4))

    # ------------------------------------------------------------------ #
    #  Events
    # ------------------------------------------------------------------ #
    def check_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    return True
                if event.key == pygame.K_f:
                    self.toggle_fullscreen()
        return False

    def cleanup(self):
        pygame.quit()
