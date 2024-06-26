import numpy as np
import json
from plyfile import PlyData, PlyElement

# Generate a unique color for each instance
def generate_colors(num_colors):
    colors = np.random.rand(num_colors, 3)
    return colors

# Function to color the point cloud based on instance segmentation
def colorize_point_cloud(vertices, labels):
    colors = generate_colors(max(labels)+1)
    colored_vertices = []
    for i in range(len(vertices)):
        color = colors [labels[i]]
        colored_vertices.append(np.hstack((vertices[i], color)))

    return np.array(colored_vertices), colors 

def clamp_color_value(value):
    return max(0, min(255, int(value*255)))

def save_colored_ply(vertices, file_path):
    vertex_dtype = [('x', 'f4'), ('y', 'f4'), ('z', 'f4'),
                    ('red', 'u1'), ('green', 'u1'), ('blue', 'u1')]
    
    vertex_array = np.array([(vertex[0], vertex[1], vertex[2],
                              clamp_color_value(vertex[3]), clamp_color_value(vertex[4]), clamp_color_value(vertex[5]))
                             for vertex in vertices], dtype=vertex_dtype)

    el = PlyElement.describe(vertex_array, 'vertex')
    PlyData([el]).write(file_path)
    print(f"Colored point cloud saved to {file_path}")

def generate_colored_caption(caption, caption_positive, instance_colors):

    html_caption = caption
    colored_segments = []
    # print(caption_positive)
    # Process each segment
    for obj_id, segments in caption_positive.items():
        color = instance_colors[obj_id]# .get(int(obj_id), [0, 0, 0])
        color_str = f"rgb({int(color[0] * 255)}, {int(color[1] * 255)}, {int(color[2] * 255)})"

        for start, end in segments:
            colored_segments.append((start, end, color_str))

    # Sort segments by their start position
    colored_segments.sort()
    # print(colored_segments)
    # Combine overlapping or adjacent segments and assign colors
    combined_segments = []
    current_start, current_end, current_colors = colored_segments[0]
    current_colors = [current_colors]
    for start, end, color in colored_segments[1:]:
        if start == current_start and end == current_end:
            if color not in current_colors:
                current_colors.append(color)
        else:
            combined_segments.append((current_start, current_end, current_colors))
            current_start, current_end, current_colors = start, end, [color]

    combined_segments.append((current_start, current_end, current_colors))

    # Generate the HTML with colored segments
    last_end = 0
    html_parts = []
    for start, end, colors in combined_segments:
        html_parts.append(html_caption[last_end:start])
        segment_length = end - start
        num_colors = len(colors)
        if num_colors > 1:
            subsegment_length = segment_length // num_colors
            for i, color in enumerate(colors):
                part_start = start + (subsegment_length * i)
                part_end = start + (subsegment_length * (i + 1)) if i != num_colors - 1 else end
                html_parts.append(f'<span style="color: {color};">{html_caption[part_start:part_end]}</span>')
        else:
            html_parts.append(f'<span style="color: {colors[0]};">{html_caption[start:end]}</span>')
        last_end = end
    html_parts.append(html_caption[last_end:])

    return ''.join(html_parts)

