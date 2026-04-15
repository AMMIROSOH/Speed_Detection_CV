import argparse
import time
from dataclasses import dataclass



@dataclass
class LineConfig:
    x1: int
    y: int
    x2: int


@dataclass
class DetectorConfig:
    cascade_path: str
    video_path: str
    first_line: LineConfig
    second_line: LineConfig
    line_tolerance: int = 6
    meters_between_lines: float = 9.144


def kmh_from_travel_time(seconds_elapsed: float, meters_traveled: float) -> float:
    """Convert travel time between two lines into km/h."""
    if seconds_elapsed <= 0:
        return 0.0
    # meters/second -> km/hour
    return (meters_traveled / seconds_elapsed) * 3.6


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Estimate vehicle speed from line-crossing timestamps in a video."
    )
    parser.add_argument(
        "--video",
        default="dataset/video3.mp4",
        help="Path to input video file.",
    )
    parser.add_argument(
        "--cascade",
        default="dataset/cars1.xml",
        help="Path to Haar cascade XML file.",
    )
    parser.add_argument(
        "--distance-meters",
        type=float,
        default=9.144,
        help="Estimated real-world distance between the two measurement lines.",
    )
    return parser.parse_args()


def point_in_band(y_value: int, line_y: int, tolerance: int) -> bool:
    return abs(y_value - line_y) <= tolerance


def create_detector_config(args: argparse.Namespace) -> DetectorConfig:
    return DetectorConfig(
        cascade_path=args.cascade,
        video_path=args.video,
        first_line=LineConfig(70, 90, 230),
        second_line=LineConfig(15, 125, 225),
        meters_between_lines=args.distance_meters,
    )


def main() -> None:
    args = parse_args()

    try:
        import cv2
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError("OpenCV is required. Install with `pip install opencv-python`.") from exc
    config = create_detector_config(args)

    cap = cv2.VideoCapture(config.video_path)
    if not cap.isOpened():
        raise FileNotFoundError(f"Unable to open video file: {config.video_path}")

    car_cascade = cv2.CascadeClassifier(config.cascade_path)
    if car_cascade.empty():
        raise FileNotFoundError(f"Unable to load cascade file: {config.cascade_path}")

    start_timestamps = {}
    next_car_id = 1

    while True:
        ret, img = cap.read()
        if not ret or img is None:
            break

        blurred = cv2.blur(img, ksize=(15, 15))
        gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
        cars = car_cascade.detectMultiScale(gray, 1.1, 2)

        cv2.line(
            img,
            (config.first_line.x1, config.first_line.y),
            (config.first_line.x2, config.first_line.y),
            (255, 0, 0),
            2,
        )
        cv2.line(
            img,
            (config.second_line.x1, config.second_line.y),
            (config.second_line.x2, config.second_line.y),
            (255, 0, 0),
            2,
        )

        for (x, y, w, h) in cars:
            center_x = int((x + x + w) / 2)
            center_y = int((y + y + h) / 2)
            car_key = (x // 10, y // 10, w // 10, h // 10)

            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.circle(img, (center_x, center_y), 1, (0, 255, 0), -1)

            if point_in_band(center_y, config.first_line.y, config.line_tolerance):
                if car_key not in start_timestamps:
                    start_timestamps[car_key] = (time.time(), next_car_id)
                    next_car_id += 1

            if point_in_band(center_y, config.second_line.y, config.line_tolerance):
                if car_key in start_timestamps:
                    start_time, car_id = start_timestamps.pop(car_key)
                    speed = kmh_from_travel_time(
                        time.time() - start_time,
                        config.meters_between_lines,
                    )
                    cv2.line(
                        img,
                        (config.second_line.x1, config.second_line.y),
                        (config.second_line.x2, config.second_line.y),
                        (0, 255, 0),
                        2,
                    )
                    label = f"Car #{car_id}: {speed:.1f} km/h"
                    cv2.putText(
                        img,
                        label,
                        (x, max(y - 12, 16)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (255, 0, 0),
                        2,
                    )
                    print(label)
                else:
                    cv2.putText(
                        img,
                        "Calculating...",
                        (100, 200),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 255, 0),
                        3,
                    )

        cv2.imshow("video", img)
        if cv2.waitKey(33) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
