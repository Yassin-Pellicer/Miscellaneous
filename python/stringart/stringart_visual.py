import math
from PIL import Image, ImageOps, ImageDraw, ImageEnhance
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


def circle_crop_grayscale(image_path, size=(500, 500), return_image=False, show=False, contrast=1.5):
    """
    Load an image, crop it into a circular frame with transparency outside,
    convert it to grayscale, and normalize pixel values to [0, 1].
    Flips intensity so that 1 = black and 0 = white.
    Applies strong contrast adjustment.

    Args:
        image_path (str): Path to the input image.
        size (tuple[int, int], optional): Desired size (width, height).
        return_image (bool): If True, also return the PIL RGBA image.
        show (bool): If True, display the image with matplotlib.
        contrast (float): Contrast adjustment factor (>1 = more contrast).

    Returns:
        np.ndarray: 2D numpy array (flipped grayscale values in [0,1], circle only).
        PIL.Image (optional): Grayscale circular image with transparency.
    """
    # Load and optionally resize
    img = Image.open(image_path).convert("L")  # grayscale directly
    if size:
        img = img.resize(size, Image.Resampling.LANCZOS)

    # ⚡ Apply contrast enhancement
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(contrast)

    # Create circular mask
    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, img.size[0], img.size[1]), fill=255)

    # Apply mask as alpha channel
    img = img.convert("LA")  # grayscale + alpha
    img.putalpha(mask)

    # Convert to NumPy (grayscale only, normalize, and flip)
    arr = np.array(img.getchannel("L"), dtype=np.float32) / 255.0
    arr = 1.0 - arr  # 🔄 flip: black = 1, white = 0

    # Get alpha mask
    alpha = np.array(img.getchannel("A"))

    # Keep only circular region in NumPy array (others become NaN)
    arr = np.where(alpha > 0, arr, np.nan)

    if show:
        plt.imshow(arr, cmap="gray", vmin=0, vmax=1)
        plt.axis("off")
        plt.show()

    if return_image:
        return arr, img
    return arr


def get_circunference_points(arr, num_points=250):
    """
    Get pixel coordinates + values along a circular perimeter.

    Args:
        arr (np.ndarray): 2D NumPy array (grayscale, 250x250).
        num_points (int): Number of points around circumference.

    Returns:
        list of tuples: [(x, y, value), ...]
    """
    h, w = arr.shape
    center = (w // 2, h // 2)
    radius = min(w, h) // 2 - 1

    points = []
    for theta in np.linspace(0, 2 * np.pi, num_points, endpoint=False):
        x = int(center[0] + radius * np.cos(theta))
        y = int(center[1] + radius * np.sin(theta))
        value = arr[y, x]
        points.append((x, y, value))

    return points


def get_line(x0, y0, x1, y1):
    points = []

    dx = abs(x1 - x0)
    dy = abs(y1 - y0)

    x, y = x0, y0

    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1

    if dx > dy:
        err = dx / 2.0
        while x != x1:
            points.append([x, y])
            err -= dy
            if err < 0:
                y += sy
                err += dx
            x += sx
    else:
        err = dy / 2.0
        while y != y1:
            points.append([x, y])
            err -= dx
            if err < 0:
                x += sx
                err += dy
            y += sy

    points.append([x1, y1])
    return points

def score(array, source, destination, canvas):
    """
    Enhanced scoring function with better canvas integration.
    
    Args:
        array: Original image array (black=1, white=0)
        source: Starting point (x, y)
        destination: Ending point (x, y) 
        canvas: Current state of drawn lines
    
    Returns:
        float: Score for this line (higher = better)
    """
    linePoints = get_line(source[0], source[1], destination[0], destination[1])
    
    darkness_score = 0      # How much darkness this line covers
    overlap_penalty = 0     # How much it overlaps existing lines
    valid_pixels = 0        # Count of valid pixels on this line
    
    for point in linePoints:
        x, y = point[0], point[1]
        
        # Bounds checking
        if not (0 <= y < array.shape[0] and 0 <= x < array.shape[1]):
            continue
            
        # Get original image darkness
        img_val = array[y, x]
        if np.isnan(img_val):
            img_val = 0  # Outside circle
        
        # Get current canvas state
        canvas_val = canvas[y, x]
        
        # Score components
        darkness_score += img_val
        
        # Progressive overlap penalty (harder penalty for darker overlaps)
        if canvas_val > 0:
            overlap_penalty += canvas_val
        
        valid_pixels += 1
    
    if valid_pixels == 0:
        return -1000  # Very bad score for invalid lines
    
    # Final score with multiple components
    base_score = darkness_score - overlap_penalty*0.125
    
    # Normalize by line length and add connectivity
    final_score = (base_score / valid_pixels)
    
    return final_score

def updateCanvas(source, destination, canvas):
    """
    Enhanced canvas update with graduated influence around lines.
    
    Args:
        source: Starting point (x, y)
        destination: Ending point (x, y)
        canvas: Canvas to update
    
    Returns:
        Updated canvas
    """
    linePoints = get_line(source[0], source[1], destination[0], destination[1])
    
    # First pass: mark the actual line pixels
    for point in linePoints:
        x, y = point[0], point[1]
        if 0 <= y < canvas.shape[0] and 0 <= x < canvas.shape[1]:
            canvas[y, x] = canvas[y, x] + 0.5  # Line pixels get 0.5
    
    # Second pass: mark surrounding pixels
    for point in linePoints:
        x, y = point[0], point[1]
        
        # Add influence to surrounding pixels
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:  # Skip center pixel (already handled)
                    continue
                    
                nx, ny = x + dx, y + dy
                if 0 <= ny < canvas.shape[0] and 0 <= nx < canvas.shape[1]:
                    canvas[ny, nx] = canvas[ny, nx] + 0.2
    
    return canvas

class RealTimeLineArt:
    def __init__(self, points, img_route, size=(500, 500), lines=400, update_interval=50):
        """
        Initialize the real-time line art generator.
        
        Args:
            points: Number of circumference points
            img_route: Path to image
            size: Canvas size
            lines: Number of lines to draw
            update_interval: How often to update display (in milliseconds)
        """
        self.points = points
        self.img_route = img_route
        self.size = size
        self.lines = lines
        self.update_interval = update_interval
        
        # Check line limit
        if (points * (points - 1) / 2) < lines:
            print(f"Too many lines. Limiting to {int(points * (points - 1) / 2)}")
            self.lines = int(points * (points - 1) / 2)
        
        # Initialize data
        self.arr, self.img = circle_crop_grayscale(img_route, size=size, return_image=True)
        self.nodes = get_circunference_points(self.arr, num_points=points)
        self.canvas = np.full((size[1], size[0]), np.float32(0.0))
        
        # Initialize algorithm state
        self.done = set()
        self.solution = [(self.nodes[0][0], self.nodes[0][1])]
        self.current_line = 0
        
        # Set up the plot
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # Left plot: Original image
        self.ax1.imshow(self.img)
        self.ax1.set_title("Original Image")
        self.ax1.axis('off')
        
        # Right plot: Line art in progress
        self.ax2.set_xlim(0, size[0])
        self.ax2.set_ylim(0, size[1])
        self.ax2.invert_yaxis()
        self.ax2.set_title(f"Line Art Progress: 0/{self.lines} lines")
        self.ax2.axis('off')
        self.ax2.set_facecolor('white')
        
        # Store line objects for efficient updating
        self.line_objects = []
        
    def update_plot(self, frame):
        """Update function called by matplotlib animation"""
        if self.current_line >= self.lines:
            return self.line_objects
        
        # Find best edge
        edgeDict = {}
        current_pos = self.solution[-1]
        
        for node in self.nodes:
            edge = (current_pos, node)
            if frozenset(edge) in self.done:
                continue
            if node == current_pos:
                continue
            node_xy = node[:2]  # take only (x, y)
            if math.dist(node_xy, current_pos) < 100:
                continue
            edgeDict[edge] = score(self.arr, current_pos, node, self.canvas)
        
        if not edgeDict:  # No more edges available
            return self.line_objects
        
        best_edge = max(edgeDict, key=edgeDict.get)
        self.canvas = updateCanvas(best_edge[0], best_edge[1], self.canvas)
        
        # Add new point to solution
        new_point = (best_edge[1][0], best_edge[1][1])
        self.solution.append(new_point)
        self.done.add(frozenset(best_edge))
        
        # Draw the new line
        if len(self.solution) > 1:
            x0, y0 = self.solution[-2]
            x1, y1 = self.solution[-1]
            line, = self.ax2.plot([x0, x1], [y0, y1], color='black', linewidth=0.5, alpha=0.7)
            self.line_objects.append(line)
        
        # Update title
        self.current_line += 1
        self.ax2.set_title(f"Line Art Progress: {self.current_line}/{self.lines} lines")
        
        # Print progress
        if self.current_line % 50 == 0:
            print(f"Progress: {self.current_line}/{self.lines} lines drawn")
        
        return self.line_objects
    
    def start_animation(self):
        """Start the real-time animation"""
        print("Starting real-time line art generation...")
        print("Close the plot window to stop the animation.")
        
        # Create animation
        self.anim = FuncAnimation(
            self.fig, 
            self.update_plot, 
            interval=self.update_interval,
            blit=False,
            repeat=False,
            cache_frame_data=False
        )
        
        plt.tight_layout()
        plt.show()
        
        return self.solution


def greedy_lineart_realtime(points, img_route, size=(500, 500), lines=400, update_interval=5):
    """
    Create a real-time line art visualization.
    
    Args:
        points: Number of circumference points
        img_route: Path to image
        size: Canvas size
        lines: Number of lines to draw
        update_interval: Animation update interval in milliseconds
    
    Returns:
        List of (x, y) coordinates of the final line art
    """
    generator = RealTimeLineArt(points, img_route, size, lines, update_interval)
    return generator.start_animation()


def visualize_final_lineart(solution, size=(500, 500)):
    """
    Visualizes the completed line art.
    """
    plt.figure(figsize=(10, 10))
    plt.xlim(0, size[0])
    plt.ylim(0, size[1])
    plt.gca().invert_yaxis()
    plt.axis('off')
    plt.title('Final Line Art')

    # Draw each line
    for i in range(len(solution)-1):
        x0, y0 = solution[i]
        x1, y1 = solution[i+1]
        plt.plot([x0, x1], [y0, y1], color='black', linewidth=0.5, alpha=0.8)
    
    plt.tight_layout()
    plt.show()


# Example usage:
if __name__ == "__main__":
    # Generate real-time line art (this will show the animation)
    solution = greedy_lineart_realtime(
        points=200, 
        img_route="gauss_easy.png", 
        size=(600, 600), 
        lines=2000,
    )
    
    # Optionally show the final result in a separate window
    # visualize_final_lineart(solution)