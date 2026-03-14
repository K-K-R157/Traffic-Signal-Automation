"""
Traffic Violation Logger

Logs side-lane violations to a MySQL database and prints an alert
in the terminal.
"""

import mysql.connector
import config


class TrafficViolationLogger:
    """MySQL logger for lane-violation events."""

    def __init__(self):
        self._conn = None
        self._cursor = None
        self._connected = False

    def _connect(self):
        if self._connected and self._conn and self._cursor:
            return
        self._conn = mysql.connector.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME,
        )
        self._cursor = self._conn.cursor()
        self._connected = True
        self._ensure_table()

    def _ensure_table(self):
        self._cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS traffic_violations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                vehicle_id VARCHAR(32) NOT NULL,
                vehicle_type VARCHAR(16) NOT NULL,
                side VARCHAR(8) NOT NULL,
                violation_type VARCHAR(32) NOT NULL,
                in_middle TINYINT(1) NOT NULL,
                out_middle TINYINT(1) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        self._conn.commit()

    def log_violation(self, vehicle):
        try:
            self._connect()
            self._cursor.execute(
                """
                INSERT INTO traffic_violations
                    (vehicle_id, vehicle_type, side, violation_type,
                     in_middle, out_middle)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    vehicle.vehicle_id,
                    vehicle.vehicle_type,
                    vehicle.original_side,
                    "SIDE_LANE",
                    1 if vehicle.in_middle else 0,
                    1 if vehicle.out_middle else 0,
                ),
            )
            self._conn.commit()
            print(
                f"[VIOLATION] {vehicle.vehicle_id} ({vehicle.vehicle_type}) "
                f"side={vehicle.original_side} in_middle={vehicle.in_middle} "
                f"out_middle={vehicle.out_middle}"
            )
        except Exception as exc:
            print(f"[VIOLATION][ERROR] Failed to log: {exc}")
