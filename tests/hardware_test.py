"""
Hardware-oriented sanity checks for HTA2209.
- Tries to detect PCA9685/ServoKit availability.
- Attempts to open a camera index for a single frame.

Exit code:
0 -> hardware checks passed OR hardware missing but not required.
1 -> hardware missing/failing AND REQUIRE_HARDWARE=1 is set.
"""
from __future__ import annotations

import os
import sys
from time import sleep
from typing import Optional

import cv2

REQUIRE_HARDWARE = os.getenv("REQUIRE_HARDWARE", "0").lower() in ("1", "true", "yes", "on")
CAM_INDEX = int(os.getenv("CAMERA_INDEX", "0"))


def check_servokit() -> tuple[bool, Optional[Exception]]:
    try:
        from adafruit_servokit import ServoKit

        ServoKit(channels=16)
        return True, None
    except Exception as exc:  # pragma: no cover - runtime safety
        return False, exc


def check_camera(index: int = 0) -> tuple[bool, Optional[Exception]]:
    cap = cv2.VideoCapture(index, cv2.CAP_V4L2)
    if not cap.isOpened():
        cap.release()
        return False, RuntimeError(f"Camera index {index} could not be opened")
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 10)
    sleep(0.2)
    ok, _ = cap.read()
    cap.release()
    if not ok:
        return False, RuntimeError(f"Camera index {index} could not deliver a frame")
    return True, None


def main() -> None:
    failures: list[str] = []
    warnings: list[str] = []

    servo_ok, servo_err = check_servokit()
    if servo_ok:
        print("[OK] ServoKit initialized (PCA9685 reachable)")
    else:
        msg = f"ServoKit unavailable: {servo_err}"
        if REQUIRE_HARDWARE:
            failures.append(msg)
            print(f"[FAIL] {msg}")
        else:
            warnings.append(msg)
            print(f"[WARN] {msg} (hardware not required)")

    cam_ok, cam_err = check_camera(index=CAM_INDEX)
    if cam_ok:
        print(f"[OK] Camera index {CAM_INDEX} opened and delivered a frame")
    else:
        msg = str(cam_err)
        if REQUIRE_HARDWARE:
            failures.append(msg)
            print(f"[FAIL] {msg}")
        else:
            warnings.append(msg)
            print(f"[WARN] {msg} (hardware not required)")

    if warnings:
        print(f"[WARN] {len(warnings)} warning(s):")
        for item in warnings:
            print(f"       - {item}")

    if failures:
        print(f"[FAIL] Hardware test failed with {len(failures)} error(s).")
        sys.exit(1)

    print(f"[OK] Hardware test completed. Warnings={len(warnings)}")
    sys.exit(0)


if __name__ == "__main__":
    main()
