# Eye Tracking Experiment Tool

A Python-based tool for conducting eye tracking experiments using smooth pursuit and random saccade patterns.

## Features

- **Two Pattern Types:**
  - Smooth Pursuit Pattern: Sequential points following a continuous path
  - Random Saccade Pattern: Points appearing randomly in a grid layout

- **Customizable Configuration:**
  - Grid size (rows × columns)
  - Number of points to display
  - Display duration for each point
  - Initial countdown timer
  - Screen margins
  - Colors and sizes
  - Direction indicators
  - Countdown display options

- **Visual Feedback:**
  - Real-time countdown display
  - Direction arrows to next point
  - Current point highlighting
  - Random fun messages at completion
  - Centered thank-you display with heart icon

- **Data Logging:**
  - Timestamps (ms)
  - Point coordinates (X, Y)
  - Next point coordinates
  - Screen dimensions
  - CSV format output

## Prerequisites

```bash
pip install opencv-python numpy screeninfo pyyaml
```

## Usage

1. **Configuration Setup:**
   Create a config file (`config.yaml`) with your desired settings:

   ```yaml
   pattern:
     type: "saccade"               # or "pursuit"
     num_rows: 8                   # Grid rows
     num_cols: 8                   # Grid columns
     num_points: 30                # Points to display
     margin: 50                    # Screen margin
     seed: 42                      # Random seed
     show_countdown: true          # Show countdown
     show_direction: true          # Show direction arrows
     initial_countdown: 3          # Initial countdown seconds

   timing:
     countdown_seconds: 3
     point_duration: 1.0
     thank_you_duration: 3
   ```

2. **Running the Experiment:**
   ```bash
   python eye_tracking.py
   ```

3. **Controls:**
   - Press 'ESC' to exit at any time
   - Full-screen display automatically activates

4. **Output:**
   - Data is logged to `saccade_log.csv` or `pursuit_log.csv`
   - CSV format includes timestamps and coordinates

## Configuration Options

### Pattern Settings
```yaml
pattern:
  type: Choose between "saccade" or "pursuit"
  num_rows: Number of rows in the grid
  num_cols: Number of columns in the grid
  num_points: Number of points to display (must be ≤ rows × cols)
  margin: Screen margin in pixels
  seed: Random seed for reproducible patterns
  show_countdown: Enable/disable countdown display
  show_direction: Enable/disable direction arrows
```

### Timing Settings
```yaml
timing:
  countdown_seconds: Duration of initial countdown
  point_duration: How long each point displays
  thank_you_duration: Duration of thank you screen
```

### Visual Settings
```yaml
colors:
  background: [255, 255, 255]   # White
  point: [0, 0, 255]           # Red (BGR)
  current_point: [255, 0, 0]    # Blue (BGR)
  direction_arrow: [0, 255, 0]  # Green (BGR)
```

## Output Format

The CSV output includes:
- `Timestamp_ms`: Time since start in milliseconds
- `Point_Index`: Sequential point number
- `X, Y`: Current point coordinates
- `Next_X, Next_Y`: Next point coordinates
- `Screen_Width, Screen_Height`: Display dimensions

## License

This project is open-source and available under the MIT License.

## Contributing

Feel free to submit issues and enhancement requests!

## Credits

Developed for eye tracking research and experiments.
