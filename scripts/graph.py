import json

from PIL import Image, ImageDraw, ImageFont, ImageOps
import math
import subprocess
import os
import shutil
import re
import sys



def install(package):
    subprocess.check_call([sys.executable, "-m", "pip3", "install", package])

# Try to import requests, install if not available
try:
    import img2pdf
except ImportError:
    #print("The 'requests' library is not installed. Installing now...")
    install('img2pdf')
    import img2pdf

map_path = "Template.jpg"



def add_corners(im, rad):
    circle = Image.new('L', (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2, rad * 2), fill=255)
    alpha = Image.new('L', im.size, 255)
    w, h = im.size
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    im.putalpha(alpha)
    return im

def wrap_text(text, font, max_width):
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        test_line = ' '.join(current_line + [word])
        if font.getbbox(test_line)[2] - font.getbbox(test_line)[0] <= max_width:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    lines.append(' '.join(current_line))
    return lines

def resize_icon(icon, max_width=120, max_height=140):
    # Calculate the scaling factor to fit within max dimensions
    width_ratio = max_width / icon.width
    height_ratio = max_height / icon.height
    scale_factor = min(width_ratio, height_ratio)

    # Calculate new dimensions
    new_width = int(icon.width * scale_factor)
    new_height = int(icon.height * scale_factor)

    # Resize the icon
    return icon.resize((new_width, new_height), Image.LANCZOS)

def superimpose_icons_on_map(page_index, locations, objects):
    # Open the map image
    template_path = "templates/Template_" + str(page_index + 1) + ".jpg"
    map_image = Image.open(template_path)
    draw = ImageDraw.Draw(map_image)

    pending_items_current_page = len(objects) - page_index*33
    pending_lines = (min(pending_items_current_page,33))//2
    for j in range(pending_lines):
        x, y = outlines[j]['location']
        path = outlines[j]['class'] + "/" + outlines[j]['type'] + ".png"
        icon = Image.open(path)
        icon_x = x - icon.width // 2
        icon_y = y - icon.height // 2
        map_image.paste(icon, (icon_x, icon_y), icon)

    font = ImageFont.truetype("Arial.ttf", 16)
    # Sort objects by rank to ensure correct placement
    sorted_objects = sorted(objects, key=lambda x: x['rank'])

    for index in range(33):
        # Get the corresponding location based on the object's rank
        actual_index = page_index * 33 + index
        if actual_index >= len(sorted_objects):
            break
        
        val = (sorted_objects[actual_index]['rank'] - 1) % 33
        
        x, y = locations[val]  # Subtract 1 as ranks typically start from 1

        # Open the icon image based on the object's type
        # Construct the path
        path = sorted_objects[actual_index]['class'] + "/" + sorted_objects[actual_index]['type'] + ".png"
        icon = Image.open(path)
        if "line" not in sorted_objects[actual_index]['type'].lower() and "transport" not in sorted_objects[actual_index]['class'].lower():
            background = Image.new('RGBA', icon.size, (204, 255, 229, 255))
            background.paste(icon, (0, 0), icon)
            radius = 20
            rounded_icon = add_corners(background, radius)
            icon = rounded_icon
        resized_icon = icon
        if "line" not in sorted_objects[actual_index]['type'].lower():
            if "transport" in sorted_objects[actual_index]['class'].lower():
                resized_icon = resize_icon(icon, max_width=60, max_height=70)
            else:
                resized_icon = resize_icon(icon, max_width=120, max_height=140)

        # Calculate position to center the icon on the location
        icon_x = x - resized_icon.width // 2
        icon_y = y - resized_icon.height // 2

        # Paste the icon onto the map
        map_image.paste(resized_icon, (icon_x, icon_y), resized_icon)

        # Wrap and center text
        label = sorted_objects[actual_index]['label']
        if not label:
            continue

        wrapped_text = wrap_text(label, font, 200)
        line_height = font.getbbox('A')[3] - font.getbbox('A')[1]
        line_spacing = 5  # Adjust this value to increase or decrease the gap between lines
        text_height = len(wrapped_text) * (
                    line_height + line_spacing) - line_spacing  # Subtract line_spacing once to account for the last line

        # Draw rectangle
        rect_width = 220
        rect_height = text_height + 15  # Add padding
        rect_x = x - rect_width // 2
        rect_y = y + resized_icon.height // 2 + 5  # 5px gap between icon and box
        fill_color = (255, 204, 229, 255)
        draw.rounded_rectangle([rect_x, rect_y, rect_x + rect_width, rect_y + rect_height], radius=3, fill=fill_color,
                               outline="grey")

        for i, line in enumerate(wrapped_text):
            line_width = font.getbbox(line)[2] - font.getbbox(line)[0]
            text_x = x - line_width // 2
            text_y = rect_y + 5 + i * (line_height + line_spacing)
            draw.text((text_x, text_y), line, font=font, fill="black")

    # Save or return the modified map image
    map_image.save("output/" + "modified_map"+str(page_index + 1)+".png")
    return map_image

locations = [
             (125, 1098), (206, 882), (450, 729), (300, 685), (270, 545),#5
             (183, 446), (272, 252), (379, 165), (559, 96), (723, 132),#10
             (812, 309), (688, 357), (600, 456), (633, 616), (729, 745),#15
             (614, 986), (829, 1010), (1021, 1024), (1069, 815), (1019, 675),#20
             (1071, 533), (1062, 420), (1144, 228), (1357, 231), (1470, 508),#25
             (1298, 759), (1433, 859), (1323, 1037), (1440, 1083), (1588, 950),#30
             (1876, 895), (1714, 689), (1895, 495)#33
            ]

outlines = [
    {"rank": 1, "class":"connector", "type": "line_1", "location":(291, 929)},
    {"rank": 2, "class":"connector", "type": "line_2", "location":(338, 666)},
    {"rank": 3, "class":"connector", "type": "line_3", "location":(213, 457)},
    {"rank": 4, "class":"connector", "type": "line_4", "location": (371, 178)},
    {"rank": 5, "class":"connector", "type": "line_5", "location":(701, 173)},
    {"rank": 6, "class":"connector", "type": "line_6", "location":(680, 360)},
    {"rank": 7, "class":"connector", "type": "line_7", "location":(671, 600)},
    {"rank": 8, "class":"connector", "type": "line_8", "location":(685, 953)},
    {"rank": 9, "class":"connector", "type": "line_9", "location":(986, 992)},
    {"rank": 10, "class":"connector", "type": "line_10", "location":(1062, 670)},
    {"rank": 11, "class":"connector", "type": "line_11", "location":(1073, 442)},
    {"rank": 12, "class":"connector", "type": "line_12", "location":(1328, 260)},
    {"rank": 13, "class":"connector", "type": "line_13", "location":(1390, 730)},
    {"rank": 14, "class":"connector", "type": "line_14", "location":(1390, 1020)},
    {"rank": 15, "class":"connector", "type": "line_15", "location":(1650, 1014)},
    {"rank": 16, "class":"connector", "type": "line_16", "location":(1860, 731)}
]

def create_template_copies(x, source_file, destination_folder):
    # Ensure the destination folder exists
    os.makedirs(destination_folder, exist_ok=True)

    # Get the base name and extension of the source file
    base_name, extension = os.path.splitext(os.path.basename(source_file))

    # Create x copies of the template
    for i in range(1, x + 1):
        new_filename = f"{base_name}_{i}{extension}"
        destination_path = os.path.join(destination_folder, new_filename)
        shutil.copy2(source_file, destination_path)
        #print(f"Created: {new_filename}")

def natural_sort_key(s):
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', s)]


def clear_folder(folder_path):
    # Check if the folder exists
    if os.path.exists(folder_path):
        # Iterate through all files in the folder
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            # Check if it's a file (not a subdirectory)
            if os.path.isfile(file_path):
                try:
                    os.remove(file_path)
                    #print(f"Deleted: {file_path}")
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}",file=sys.stderr)
        #print(f"All files in '{folder_path}' have been deleted.")
    else:
        print(f"Error The folder '{folder_path}' does not exist.",file=sys.stderr)

def main():
    with open('input.json', 'r') as file:
        objects = json.load(file)

    pages = math.ceil(len(objects) / 33)
    source_file = "Template.jpg"
    destination_folder = "templates"
    create_template_copies(pages, source_file, destination_folder)

    # Example usage
    folder_to_clear = "output"
    clear_folder(folder_to_clear)


    for i in range(pages):
        superimpose_icons_on_map(i, locations, objects)

    output_folder = "output"


    # List all files in the directory and filter only JPG images
    image_files = [os.path.join(output_folder, f) for f in os.listdir(output_folder) if f.endswith('.png')]
    image_files.sort(key=natural_sort_key)

    # Convert the list of JPG images to a single PDF file
    pdf_data = img2pdf.convert(image_files)

    # Write the PDF content to a file
    with open(output_folder + "/" + "output.pdf", "wb") as file:
        file.write(pdf_data)
    
    # Send the PDF file URL to the client
    # pdf_url = "/output/output.pdf"
    # return {"pdf_url": pdf_url}
    # pdf_url = "/output/output.pdf"  
    # print(json.dumps({"pdf_url": pdf_url}))  # Print JSON string


if __name__ == "__main__":
    main()