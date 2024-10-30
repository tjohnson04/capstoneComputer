import trimesh
import numpy as np
import matplotlib.pyplot as plt

# Load the .obj file
mesh = trimesh.load('test.obj')

# Get the bounding box min and max values
min_val, max_val = mesh.bounds[0], mesh.bounds[1]
print(f"Bounding Box Min: {min_val}, Max: {max_val}")

# Find the maximum range across all dimensions (X, Y, Z)
max_range = max(max_val - min_val)  # This gives the largest span (X, Y, or Z)
center = (min_val + max_val) / 2.0

# Function to generate the base grid with rotation around the YZ-plane (x=0, y=0)
def generate_base_grid(cube_size, num_rotations=54, margin=0.1):
    "Generates a base 3D grid of points by rotating a 2D grid around  X=0, Y=0 line"
    # Define the Y and Z ranges based on the cube size
    grid_size = 16
    y_range = np.linspace(center[1] - max_range / 2 - margin, center[1] + max_range / 2 + margin, grid_size)
    z_range = np.linspace(center[2] - max_range / 2 - margin, center[2] + max_range / 2 + margin, grid_size)

    # Create a 2D square grid of points in the ZY plane (aligned along X=0)
    z, y = np.meshgrid(z_range, y_range)
    x = np.zeros_like(z)  # X will be initially zero

    # Stack the points to form a 2D square in the ZY plane
    square_points = np.vstack([x.ravel(), y.ravel(), z.ravel()]).T

    # Rotate the points around the YZ-plane
    angle_increment = 360 / num_rotations
    all_rotated_points = []

    for i in range(num_rotations):
        theta = np.radians(i * angle_increment)

        # Z-axis rotation matrix to rotate around the X=0, Y=0 line (YZ-plane)
        rotation_matrix = np.array([
            [np.cos(theta), -np.sin(theta), 0],  # Rotates Y and Z coordinates
            [np.sin(theta), np.cos(theta), 0],
            [0, 0, 1]  # X remains unchanged
        ])

        # Apply the rotation to the square points
        rotated_points = square_points @ rotation_matrix.T
        all_rotated_points.append(rotated_points)

    # Combine all rotated points into a single 3D grid
    return np.vstack(all_rotated_points)


# Function to scale the grid
def scale_grid(base_grid, scale):
    return base_grid * scale


# Function to perform the scan
def perform_scan(mesh, scaled_grid, location):
    x_center, y_center, z_center = location

    # Adjust the grid based on the location
    adjusted_grid = np.copy(scaled_grid)
    adjusted_grid[:, 0] += x_center  # Move along X-axis
    adjusted_grid[:, 1] += y_center  # Move along Y-axis
    adjusted_grid[:, 2] += z_center  # Move along Z-axis

    # Use mesh.contains to check if points are inside the mesh
    is_inside = mesh.contains(adjusted_grid)

    # Separate the points into inside and outside
    inside_points = adjusted_grid[is_inside]
    outside_points = adjusted_grid[~is_inside]


    # Combine all points in one array
    all_points = np.vstack((inside_points, outside_points))
    new_all_points = []
    for point in all_points:
        new_all_points.append([point[0]-x_center,point[1]-y_center,point[2]-z_center])
    new_inside_points = []
    for point in inside_points:
        new_inside_points.append([point[0] - x_center, point[1] - y_center, point[2] - z_center])
    save_scan_output_to_file(new_all_points, new_inside_points)
    return inside_points, outside_points

# Function to write scan output to a text file
def save_scan_output_to_file(all_points, inside_points, filename="output.txt"):
    all_coords = []
    for point in all_points:
        x, y, z = point
        r = np.sqrt(x ** 2 + y ** 2)  # Radial distance
        theta = round((np.degrees(np.arctan2(y, x))) % 360, 3)  # Angle in degrees
        all_coords.append(((float(r)), theta, z))


    # Unique sorted lists for distances, angles, and heights
    distance_list = sorted(set(x[0] for x in all_coords))
    distance_list = remove_near_duplicates(distance_list)
    angle_list = sorted(set(x[1] for x in all_coords))
    height_list = sorted(set(x[2] for x in all_coords))

    print(len(distance_list),len(angle_list),len(height_list))
    print(distance_list)


    inside_coords = []
    for point in inside_points:
        x, y, z = point
        r = np.sqrt(x ** 2 + y ** 2)  # Radial distance
        theta = round((np.degrees(np.arctan2(y, x))) % 360, 3)  # Angle in degrees
        inside_coords.append(((float(r)), theta, z))
    inside_coords = list(sorted(set(inside_coords)))

    height_coord_list = []
    for h in height_list:
        for r in distance_list:
            first_half = 0  # Use Python's built-in int
            second_half = 0  # Use Python's built-in int
            for c in inside_coords:
                if (c[2] == h) and (c[0] == r):
                    angle_index = angle_list.index(c[1])
                    if angle_index > 31:
                        second_half |= 1 << (angle_index - 32)  # Shifting for second half
                    else:
                        first_half |= 1 << angle_index  # Shifting for first half
            with open('output.txt', 'a') as file:
                # Write the binary strings to the output file
                file.write(f"{bin(first_half)[2:].zfill(32)}{bin(second_half)[2:].zfill(32)}\n")


def remove_near_duplicates(numbers, tolerance=0.01):
    # Sort the list to easily identify close numbers
    sorted_numbers = sorted(numbers)

    # Initialize the list with the first element (assuming it is unique)
    unique_numbers = [sorted_numbers[0]]

    # Compare each number with the last unique number in the list
    for num in sorted_numbers[1:]:
        # Calculate the range of the last unique number
        lower_bound = unique_numbers[-1] * (1 - tolerance)
        upper_bound = unique_numbers[-1] * (1 + tolerance)

        # Only add the number if it is outside the tolerance range of the last unique number
        if num < lower_bound or num > upper_bound:
            unique_numbers.append(num)
    return unique_numbers


with open('output.txt', 'w') as file:
    file.write('')  # This clears the file content

# Generate the base grid (use cube_size=16 and num_rotations=54 for example)
base_grid = generate_base_grid(cube_size=16, num_rotations=54)

# Example: Perform a full scan with the unscaled grid (scale=1.0)
location = (center[0], center[1], center[2])  # Use the center of the object
scaled_grid = scale_grid(base_grid, scale=1.0)

# Perform the scan
inside_points, outside_points = perform_scan(mesh, scaled_grid, location)




quadrants = {
    # Near sections
    "Top-Left-Near": (center[0] + max_range / 4, center[1] - max_range / 4, center[2] + max_range / 4),
    "Top-Center-Near": (center[0] + max_range / 4, center[1] - max_range / 4, center[2]),
    "Top-Right-Near": (center[0] + max_range / 4, center[1] - max_range / 4, center[2] - max_range / 4),

    "Middle-Left-Near": (center[0] + max_range / 4, center[1], center[2] + max_range / 4),
    "Middle-Center-Near": (center[0] + max_range / 4, center[1], center[2]),
    "Middle-Right-Near": (center[0] + max_range / 4, center[1], center[2] - max_range / 4),

    "Bottom-Left-Near": (center[0] + max_range / 4, center[1] + max_range / 4, center[2] + max_range / 4),
    "Bottom-Center-Near": (center[0] + max_range / 4, center[1] + max_range / 4, center[2]),
    "Bottom-Right-Near": (center[0] + max_range / 4, center[1] + max_range / 4, center[2] - max_range / 4),

    # Middle sections
    "Top-Left-Middle": (center[0], center[1] - max_range / 4, center[2] + max_range / 4),
    "Top-Center-Middle": (center[0], center[1] - max_range / 4, center[2]),
    "Top-Right-Middle": (center[0], center[1] - max_range / 4, center[2] - max_range / 4),

    "Middle-Left-Middle": (center[0], center[1], center[2] + max_range / 4),
    "Middle-Center-Middle": (center[0], center[1], center[2]),
    "Middle-Right-Middle": (center[0], center[1], center[2] - max_range / 4),

    "Bottom-Left-Middle": (center[0], center[1] + max_range / 4, center[2] + max_range / 4),
    "Bottom-Center-Middle": (center[0], center[1] + max_range / 4, center[2]),
    "Bottom-Right-Middle": (center[0], center[1] + max_range / 4, center[2] - max_range / 4),

    # Far sections
    "Top-Left-Far": (center[0] - max_range / 4, center[1] - max_range / 4, center[2] + max_range / 4),
    "Top-Center-Far": (center[0] - max_range / 4, center[1] - max_range / 4, center[2]),
    "Top-Right-Far": (center[0] - max_range / 4, center[1] - max_range / 4, center[2] - max_range / 4),

    "Middle-Left-Far": (center[0] - max_range / 4, center[1], center[2] + max_range / 4),
    "Middle-Center-Far": (center[0] - max_range / 4, center[1], center[2]),
    "Middle-Right-Far": (center[0] - max_range / 4, center[1], center[2] - max_range / 4),

    "Bottom-Left-Far": (center[0] - max_range / 4, center[1] + max_range / 4, center[2] + max_range / 4),
    "Bottom-Center-Far": (center[0] - max_range / 4, center[1] + max_range / 4, center[2]),
    "Bottom-Right-Far": (center[0] - max_range / 4, center[1] + max_range / 4, center[2] - max_range / 4),
}

quadrant_points = []
for quadrant_label, location in quadrants.items():
    scaled_grid = scale_grid(base_grid, scale=0.5)  # Scale down the grid for quadrants
    inside_q, outside_q = perform_scan(mesh, scaled_grid, location)
    quadrant_points.append((inside_q, outside_q))
