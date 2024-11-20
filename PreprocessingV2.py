import trimesh
import numpy as np
import matplotlib.pyplot as plt
import os
import shutil

def clear_file(filename):
    # Open the file in write mode to clear its contents
    with open(filename, 'w') as file:
        pass  # Opening in 'w' mode clears the file, so no need to write anything

def scan_obj(obj_file):
    mesh = trimesh.load(obj_file)
    # Get the bounding box min and max values
    min_val, max_val = mesh.bounds[0], mesh.bounds[1]
    #print(f"Bounding Box Min: {min_val}, Max: {max_val}")

    min_val = min_val
    max_val = max_val

    # Find the maximum range across all dimensions (X, Y, Z)
    max_range = max(max_val - min_val)  # This gives the largest span (X, Y, or Z)
    center = (min_val + max_val) / 2.0
    quadrants = get_quadrants(center=center,max_range=max_range)

    output_dir = 'output_folder'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    clear_folder(output_dir)
    # Generate the base grid
    base_grid = generate_base_grid(cube_size=16, center=center,max_range=max_range)


    location = (center[0], center[1], center[2])  # Use the center of the object
    inside_points, outside_points = perform_scan(mesh, base_grid, location, label="full_obj")

    quadrant_points = []
    for quadrant_label, location in quadrants.items():
        scaled_grid = base_grid * 0.5  # Scale down the grid for quadrants
        inside_q, outside_q = perform_scan(mesh, scaled_grid, location, label=quadrant_label)
        quadrant_points.append((inside_q, outside_q))
    return output_dir

# Function to generate the base grid with rotation around the YZ-plane (x=0, y=0)
def generate_base_grid(cube_size, num_rotations=55, center=[0,0,0], max_range=0, margin=0.1):
    grid_size = 16
    y_range = np.linspace(0 - max_range / 2 - margin, 0 + max_range / 2 + margin, grid_size)
    z_range = np.linspace(0 - max_range / 2 - margin, 0 + max_range / 2 + margin, grid_size)
    z, y = np.meshgrid(z_range, y_range)
    x = np.zeros_like(z)


    square_points = np.vstack([x.ravel(), y.ravel(), z.ravel()]).T

    # Rotate the points around the YZ-plane
    angle_increment = 360 / num_rotations
    all_rotated_points = []
    for i in range(num_rotations):
        theta = np.radians(i * angle_increment)
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

# Function to perform the scan
def perform_scan(mesh, scaled_grid, location, label):
    x_center, y_center, z_center = location

    # Adjust the grid based on the location
    adjusted_grid = []
    for point in scaled_grid:
        adjusted_grid.append([point[0]+x_center,point[1]+y_center,point[2]+z_center])

    # Use mesh.contains to check if points are inside the mesh
    is_inside = mesh.contains(adjusted_grid)
    index = 0
    inside_points = []
    outside_points = []
    for x in is_inside:
        if x == True:
            inside_points.append(adjusted_grid[index])
        else:
            outside_points.append(adjusted_grid[index])
        index+=1


    # Combine all points in one array
    all_points = adjusted_grid

    new_all_points = []
    for point in all_points:
        new_all_points.append([point[0]-x_center,point[1]-y_center,point[2]-z_center])
    new_inside_points = []
    for point in inside_points:
        new_inside_points.append([point[0]-x_center,point[1]-y_center,point[2]-z_center])

    save_scan_output_to_file(new_all_points, new_inside_points, label=label)

    return inside_points, outside_points

# Function to write scan output to a text file
def save_scan_output_to_file(all_points, inside_points, output_folder="output_folder", label="error"):
    # Generate the filename based on the label
    filename = os.path.join(output_folder, f"{label}_output.txt")

    all_coords = []
    for point in all_points:
        x, y, z = point
        r = np.sqrt(x ** 2 + y ** 2)  # Radial distance
        theta = round((np.degrees(np.arctan2(y, x))), 3)  # Angle in degrees
        all_coords.append(((float(r)), theta, z,x,y,z))

    temp_list = []
    for x in all_coords:
        temp_list.append(x[3:])

    # Unique sorted lists for distances, angles, and heights
    distance_list = sorted(set(x[0] for x in all_coords))
    distance_list = remove_near_duplicates(distance_list)
    angle_list = sorted(set(x[1] for x in all_coords))
    height_list = list(sorted(set(x[2] for x in all_coords)))

    #print(len(distance_list),len(angle_list),len(height_list))
    #print(distance_list)
    #print(angle_list)
    #print(height_list)

    inside_coords = []
    for point in inside_points:
        x, y, z = point
        r = np.sqrt(x ** 2 + y ** 2)  # Radial distance
        theta = round((np.degrees(np.arctan2(y, x))) % 360, 3)  # Angle in degrees
        inside_coords.append(((float(r)), theta, z,x,y,z))
    inside_coords = list(sorted(set(inside_coords)))
    reversed_height_list = height_list[::-1]


    temp_distance_list = []
    for x in distance_list:
        temp_distance_list.append(round(float(x), 5))
    distance_list = temp_distance_list

    temp_angle_list = []
    for x in angle_list:
        temp_angle_list.append(round((float(x)+180),3))
    angle_list = temp_angle_list

    temp_height_list = []
    for x in height_list:
        temp_height_list.append(round(float(x), 3))
    height_list = temp_height_list


    #print(distance_list)
    #print(angle_list)
    #print(height_list)



    temp_inside_coords = []
    for c in inside_coords:
        temp_inside_coords.append((round(c[0],5),float(c[1]),round(float(c[2]),3),c[3],c[4],c[5]))
    inside_coords = temp_inside_coords

    #print(f'len of inside_coords = {len(inside_coords)}')
    #print(f'len of all_coords = {len(all_coords)}')
    #print(f'len of angle list = {len(angle_list)}')

    everyother_angle_list = []
    index = 0
    for i in angle_list:
        if index % 2 == 0:
            everyother_angle_list.append(i)
        index += 1

    temp_index = 0
    for a in angle_list[:int(len(angle_list)/2)]:
        temp_list = []
        for c in inside_coords:
            if (c[1] == a) or (c[1] == round(a - 180,3)) or (c[1] == round(a + 180, 3)):
                temp_list.append(c)
                temp_index +=1
            temp2_list = []
            for y in temp_list:
                temp2_list.append(y[3:])
        #plot_3d_points(temp2_list)

        with open(filename, 'a') as file:
            file.write(f"{a}\n")

        for h in reversed_height_list:
            to_write = 0
            h = round(h,3)
            for y in temp_list:
                if y[2] == h:
                    if y[1] == a:
                        distance_index = distance_list.index(y[0])
                        to_write |= 1 << distance_index+8
                    else:
                        distance_index = distance_list.index(y[0])
                        to_write |= 1 << 7-distance_index
            with open(filename, 'a') as file:
                file.write(f"{bin(to_write)[2:].zfill(16)}\n")

    #if len(inside_points) > 1:
        #plot_3d_points(inside_points)




def remove_near_duplicates(numbers, tolerance=0.01):
    if len(numbers) > 0:
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
    else:
        return numbers


def get_quadrants(center,max_range):
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

    return quadrants


def plot_3d_points(points):
    # Separate the x, y, and z coordinates from the list of points
    x_coords = [point[0] for point in points]
    y_coords = [point[1] for point in points]
    z_coords = [point[2] for point in points]

    # Determine the range for each axis using the min and max of the points
    x_min, x_max = min(x_coords), max(x_coords)
    y_min, y_max = min(y_coords), max(y_coords)
    z_min, z_max = min(z_coords), max(z_coords)

    # Calculate the middle and range for each axis
    x_range = x_max - x_min
    y_range = y_max - y_min
    z_range = z_max - z_min

    # Find the overall range to ensure equal scaling
    max_range = max(x_range, y_range, z_range)
    mid_x = (x_max + x_min) / 2
    mid_y = (y_max + y_min) / 2
    mid_z = (z_max + z_min) / 2

    # Create a 3D plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Plot the points
    ax.scatter(x_coords, y_coords, z_coords, c='blue', marker='o', alpha=0.3)

    # Set axis labels
    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    ax.set_zlabel('Z Coordinate')
    ax.set_title('3D Point Plot')

    # Set the limits for each axis using the same scaling range
    ax.set_xlim([mid_x - max_range / 2, mid_x + max_range / 2])
    ax.set_ylim([mid_y - max_range / 2, mid_y + max_range / 2])
    ax.set_zlim([mid_z - max_range / 2, mid_z + max_range / 2])

    # Add a grid and display the plot
    ax.grid(True)
    plt.show()


def clear_folder(folder_path):
    # Check if the folder exists
    if os.path.exists(folder_path):
        #Iterate through all files and directories in the folder
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)

            try:
                # Remove a file or a directory
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)  # Remove file or symbolic link
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # Remove directory and all its contents
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}'

