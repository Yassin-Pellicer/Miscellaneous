import math
from PIL import Image, ImageDraw, ImageEnhance
import numpy as np
import matplotlib.pyplot as plt

def circle_crop_grayscale(image_path, size=(500, 500), return_image=False, show=False, contrast=3.0):
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
    base_score = darkness_score - overlap_penalty*0.10
    
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
            canvas[y, x] = min(1.0, canvas[y, x] + 0.5)  # Line pixels get 0.5
    
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
                    # Only add influence if not already heavily marked
                    if canvas[ny, nx] < 0.7:
                        canvas[ny, nx] = min(1.0, canvas[ny, nx] + 0.4)  # Surrounding pixels get 0.2
    
    return canvas

def visualize_lineart(solution, size=(500, 500)):
    for i in solution:
        print(i)
    """
    Visualizes the line art using matplotlib.

    Parameters
    ----------
    solution : list of tuples
        List of (x, y) coordinates from greedy_lineart.
    size : tuple, optional
        Size of the canvas. Defaults to (500, 500).
    """
    plt.figure(figsize=(8, 8))
    plt.xlim(0, size[0])
    plt.ylim(0, size[1])
    plt.gca().invert_yaxis()  # Because image coordinates have y=0 at top
    plt.axis('off')

    # Draw each line
    for i in range(len(solution)-1):
        x0, y0 = solution[i]
        x1, y1 = solution[i+1]
        plt.plot([x0, x1], [y0, y1], color='black', linewidth=0.5, alpha=0.5)
    plt.show()

def greedy_lineart(points, img_route, size=(500, 500), lines=400):
    """
    Draws a line art given a source image and the number of points to sample from its circumference.

    Parameters
    ----------
    points : int
        Number of points to sample from the circumference of the image.
    img_route : str
        Path to the image file.
    size : tuple, optional
        Size of the output image. Defaults to (500, 500).
    lines : int, optional
        Maximum number of lines to draw. Defaults to 5000.

    Returns
    -------
    list
        List of (x, y) coordinates of the drawn line art.
    """
    if (points * (points - 1) / 2) < lines:
        print("Too many lines. Limiting to", points * (points - 1) / 2)
        lines = points * (points - 1) / 2

    arr, img = circle_crop_grayscale(img_route, size=size, return_image=True)
    plt.imshow(img)
    plt.axis('off')
    plt.show()
    nodes = get_circunference_points(arr, num_points=points)
    canvas = np.full((size[1], size[0]), np.float32(0.0))

    done = set()
    solution = [(nodes[0][0], nodes[0][1])]

    while len(solution) < lines + 1:
        edgeDict = {}
        for node in nodes:
            edge = (solution[-1], node)
            if frozenset(edge) in done:
                continue
            if node == solution[-1]:
                continue
            if math.dist(node[:2], solution[-1]) < 100:
                continue
            edgeDict[edge] = score(arr, solution[-1], node, canvas)
        best_edge = max(edgeDict, key=edgeDict.get)
        canvas = updateCanvas(best_edge[0], best_edge[1], canvas)

        print("nº",len(solution),"->", solution[-1]) 
        solution.append((best_edge[1][0], best_edge[1][1]))
        done.add(frozenset(best_edge))
     
    return solution

solution = greedy_lineart(250, "image.png", size=(500, 500), lines=2000)
visualize_lineart(solution)