from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, filename):
    # Create a high-res image with background color
    img = Image.new('RGBA', (size, size), color='#000000')
    draw = ImageDraw.Draw(img)
    
    # Simple text or logo placeholder (MAICA)
    text = "M"
    # Draw a clean centered circle / text
    margin = size // 8
    draw.ellipse([margin, margin, size - margin, size - margin], fill="#ffffff")
    
    # Save file
    img.save(filename, 'PNG')
    print(f"Created {filename} ({size}x{size})")

# Path to static images directory inside your Django app
target_dir = "/home/ec2-user/updated_maicagroups/production/myapp/static/images"
os.makedirs(target_dir, exist_ok=True)

create_icon(192, os.path.join(target_dir, "icon-192.png"))
create_icon(512, os.path.join(target_dir, "icon-512.png"))
