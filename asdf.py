import trimesh
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Load the .obj file
mesh = trimesh.load('test.obj')

print("done")
# Calculate the bounding box of the object
bounding_box = mesh.bounds
max_distance = np.linalg.norm(bounding_box, axis=1).max()
max_distance = .5
# Define the grid size and the range based on max distance
grid_size = 16
grid_range = np.linspace(-max_distance, max_distance, grid_size)

# Create a 2D square grid of points in the ZY plane
z, y = np.meshgrid(grid_range, grid_range)
x = np.zeros_like(z)

# Stack the x, y, and z coordinates to create a list of points in the Z-Y plane
square_points = np.vstack([x.ravel(), y.ravel(), z.ravel()]).T

# Define the number of rotation steps and the angle increment for rotation around the Z-axis
num_rotations = 55  # Number of steps to rotate the square
angle_increment = 360 / num_rotations  # Degrees between each rotation

# Initialize an empty list to store the rotated points
cylinder_points = []


for i in range(num_rotations):
    # Compute the rotation angle for this step
    theta = np.radians(i * angle_increment)

    # Define the Z-axis rotation matrix
    rotation_matrix = np.array([
        [np.cos(theta), -np.sin(theta), 0],
        [np.sin(theta), np.cos(theta), 0],
        [0, 0, 1]
    ])
    #print(rotation_matrix)

    rotated_points = square_points @ rotation_matrix.T
    cylinder_points.append(rotated_points)

cylinder_points = np.vstack(cylinder_points)


# Use the `contains` method to check if each point is inside the mesh
is_inside = mesh.contains(cylinder_points)

# Separate the points into inside and outside points
inside_points = cylinder_points[is_inside]
#print(inside_points[0:200])
outside_points = cylinder_points[~is_inside]

polar_coords = []
for point in inside_points:
    x, y, z = point
    r = np.sqrt(x ** 2 + y ** 2)  # Radial distance
    theta = np.arctan2(y, x)  # Angle in radians (atan2 handles the quadrant)
    polar_coords.append((round((float(r)*15),1), float(np.degrees(theta)), round((z+0.5)*15)))

templist = []
for x in polar_coords:
    templist.append(round((x[1]),2))
print(len(sorted(set(templist))))





# Create a 3D plot to visualize the points
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Plot inside points in green
ax.scatter(inside_points[:, 0], inside_points[:, 1], inside_points[:, 2], color='g', label='Inside', alpha=0.6)

# Plot outside points in red
ax.scatter(outside_points[:, 0], outside_points[:, 1], outside_points[:, 2], color='r', label='Outside', alpha=0.005)

# Set labels and title
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('3D Visualization of Cylinder Points (Square in YZ Plane, Rotated around Z-axis)')

# Show legend and plot
ax.legend()
plt.show()
