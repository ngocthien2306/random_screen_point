import cv2
import numpy as np
import time
from screeninfo import get_monitors
import yaml
import csv
import random

class SaccadePattern:
    def __init__(self, config_path="config.yaml"):
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                self.config = yaml.safe_load(file)
        except Exception as e:
            print(f"Error reading config file: {e}")
            raise

        # Get screen dimensions
        self.monitor = get_monitors()[0]
        self.width = self.monitor.width
        self.height = self.monitor.height
        
        # Initialize pattern parameters from config
        pattern_config = self.config['pattern']
        
        self.num_rows = pattern_config['num_rows']
        self.num_cols = pattern_config['num_cols']
        self.num_points = min(pattern_config['num_points'], self.num_rows * self.num_cols)
        self.margin = pattern_config['margin']
        self.seed = pattern_config['seed']
        self.show_countdown = pattern_config['show_countdown']
        self.show_direction = pattern_config['show_direction']
        
        # Initialize timing parameters
        timing_config = self.config['timing']
        self.point_duration = timing_config['point_duration']
        self.initial_countdown = timing_config['countdown_seconds']
        self.thank_you_duration = timing_config['thank_you_duration']
        
        # Initialize window
        window_config = self.config['window']
        self.window_name = window_config['name']
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        if window_config['fullscreen']:
            cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        # Initialize logging
        self.log_file = f"saccade_log.csv"
        with open(self.log_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp_ms', 'Point_Index', 'X', 'Y', 'Next_X', 'Next_Y', 'Screen_Width', 'Screen_Height'])

        # Generate random points with fixed seed
        random.seed(self.seed)
        self.points = self._generate_grid_points()

    def _generate_grid_points(self):
        """Generate grid points and select random required number of points"""
        points = []
        row_spacing = (self.height - 2 * self.margin) / (self.num_rows - 1)
        col_spacing = (self.width - 2 * self.margin) / (self.num_cols - 1)
        
        for row in range(self.num_rows):
            y = self.margin + row * row_spacing
            for col in range(self.num_cols):
                x = self.margin + col * col_spacing
                points.append((int(x), int(y)))
        
        # Randomly select required points
        random.shuffle(points)
        return points[:self.num_points]

    def _draw_countdown_at_point(self, image, point, time_left, is_initial=False):
        """Draw countdown text at specified point"""
        x, y = point
        font = getattr(cv2, self.config['font']['type'])
        font_scale = 2 if is_initial else 1  # Larger font for initial countdown
        thickness = 3 if is_initial else 2
        text = f"{time_left:.1f}" if not is_initial else f"{int(time_left)}"
        
        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
        text_x = x - text_size[0] // 2
        text_y = y - 20 if not is_initial else y + text_size[1] // 2
        
        cv2.putText(image, text, (text_x, text_y), font, font_scale,
                   tuple(self.config['colors']['text']), thickness)

    def _draw_countdown_and_direction(self, image, current_point, next_point, time_left):
        """Draw countdown and direction arrow"""
        if self.show_countdown:
            self._draw_countdown_at_point(image, current_point, time_left)

        if self.show_direction and next_point is not None:
            # Draw direction arrow
            arrow_color = tuple(self.config['colors']['direction_arrow'])
            cv2.arrowedLine(image, current_point, next_point, arrow_color, 2, 
                          tipLength=0.2)

    def _show_initial_countdown(self, first_point):
        """Show initial countdown at the first point"""
        colors = self.config['colors']
        point_config = self.config['point']

        for i in range(self.initial_countdown, 0, -1):
            start_time = time.time()
            while (time.time() - start_time) < 1.0:  # 1 second intervals
                current_frame = np.array(colors['background'], dtype=np.uint8) * \
                              np.ones((self.height, self.width, 3))
                
                # Draw first point
                cv2.circle(current_frame, first_point,
                         int(point_config['size'] * point_config['size_multiplier']),
                         tuple(colors['current_point']),
                         point_config['thickness'])

                # Draw countdown
                self._draw_countdown_at_point(current_frame, first_point, i, True)
                
                cv2.imshow(self.window_name, current_frame)
                
                if cv2.waitKey(1) & 0xFF == 27:
                    return False
                
        return True

    def log_point(self, timestamp_ms, point_index, current_point, next_point=None):
        """Log point information to CSV file"""
        with open(self.log_file, 'a', newline='') as file:
            writer = csv.writer(file)
            next_x = next_point[0] if next_point else None
            next_y = next_point[1] if next_point else None
            writer.writerow([timestamp_ms, point_index, current_point[0], current_point[1], 
                           next_x, next_y, self.width, self.height])

    def run(self):
        """Run the main program"""
        point_config = self.config['point']
        colors = self.config['colors']
        
        try:
            # Show initial countdown at first point
            if not self._show_initial_countdown(self.points[0]):
                return

            point_count = 0
            
            for i, current_point in enumerate(self.points):
                # Get next point
                next_point = self.points[i + 1] if i < len(self.points) - 1 else None
                
                timestamp_ms = int(point_count * self.point_duration * 1000)
                point_count += 1
                
                self.log_point(timestamp_ms, i, current_point, next_point)

                start_time = time.time()
                while (time.time() - start_time) < self.point_duration:
                    current_frame = np.array(colors['background'], dtype=np.uint8) * \
                                  np.ones((self.height, self.width, 3))
                    
                    # Draw current point
                    cv2.circle(current_frame, current_point,
                             int(point_config['size'] * point_config['size_multiplier']),
                             tuple(colors['current_point']),
                             point_config['thickness'])

                    # Show countdown and direction
                    time_left = self.point_duration - (time.time() - start_time)
                    self._draw_countdown_and_direction(current_frame, current_point, 
                                                    next_point, time_left)
                    
                    cv2.imshow(self.window_name, current_frame)
                    
                    if cv2.waitKey(1) & 0xFF == 27:
                        return
            
            self.show_thank_you()
                
        finally:
            cv2.destroyAllWindows()
            
    def _wait_key(self, duration):
        """Chờ phím trong khoảng thời gian duration"""
        start_time = time.time()
        while (time.time() - start_time) < duration:
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                return False
        return True
            
    def draw_heart(self, image, center, size):
        heart_color = tuple(self.config['colors']['heart'])
        x, y = center
        radius = size // 2
        
        cv2.circle(image, (x - radius, y), radius, heart_color, -1)
        cv2.circle(image, (x + radius, y), radius, heart_color, -1)
        
        triangle_pts = np.array([
            [x - size, y],
            [x + size, y],
            [x, y + size]
        ])
        cv2.fillPoly(image, [triangle_pts], heart_color)

    def _create_blank_image(self):
        """Create a blank white image"""
        bg_color = self.config['colors']['background']
        return np.array(bg_color, dtype=np.uint8) * np.ones((self.height, self.width, 3))

    def show_thank_you(self):
        """Show random thank you message in the center of screen with heart icon"""
        text_config = self.config['thank_you_text']
        heart_config = self.config['heart']
        colors = self.config['colors']
        
        image = self._create_blank_image()
        
        # Get random message
        messages = text_config['messages']
        text = random.choice(messages)
        
        # Get text size
        font = getattr(cv2, self.config['font']['type'])
        font_scale = text_config['font_scale']
        thickness = text_config['thickness']
        
        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
        heart_size = heart_config['size']
        
        # Calculate total width including text, heart and offset
        total_width = text_size[0] + heart_config['offset'] + heart_size * 2
        
        # Calculate center positions
        center_x = self.width // 2
        center_y = self.height // 2
        
        # Calculate text starting position
        text_x = center_x - total_width // 2
        text_y = center_y + text_size[1] // 2  # Add half text height to center vertically
        
        # Draw text
        cv2.putText(image, text,
                    (text_x, text_y),
                    font,
                    font_scale,
                    tuple(colors['text']),
                    thickness)
        
        # Calculate heart position
        heart_x = text_x + text_size[0] + heart_config['offset']
        heart_y = text_y - text_size[1] // 2  # Align with text center
        self.draw_heart(image, (heart_x, heart_y), heart_size)
        
        cv2.imshow(self.window_name, image)
        start_time = time.time()
        while (time.time() - start_time) < self.thank_you_duration:
            if cv2.waitKey(1) & 0xFF == 27:
                break

def main():
    pattern = SaccadePattern("config_random.yaml")
    pattern.run()

if __name__ == "__main__":
    main()