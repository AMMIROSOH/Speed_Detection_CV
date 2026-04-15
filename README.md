# Speed Detection (OpenCV)

A simple computer-vision demo that estimates vehicle speed by measuring how long detected cars take to move between two horizontal reference lines.

## What was improved

- Added a clearer and safer program structure (`main()` + helper functions).
- Fixed the default video path casing (`video3.mp4`) to match the repository dataset.
- Replaced the old speed formula with a direct, unit-safe conversion (`m/s` to `km/h`).
- Added command-line arguments for:
  - input video path
  - cascade XML path
  - distance between measurement lines (in meters)
- Added basic runtime validation for missing video/cascade files.
- Improved speed labels and console output formatting.

## Run

```bash
python3 main.py
```

Optional arguments:

```bash
python3 main.py --video dataset/video3.mp4 --cascade dataset/cars1.xml --distance-meters 9.144
```

## Notes

- The estimated speed depends heavily on the `--distance-meters` calibration and camera perspective.
- The demo uses Haar-cascade detections and simple line-crossing logic, so it is best treated as an educational baseline.
