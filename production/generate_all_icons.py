from PIL import Image
import os

# Source path to your favicon
SOURCE_LOGO = "/home/ec2-user/updated_maicagroups/production/static/images/favicon.ico"

# Target static directories
TARGET_DIRS = [
    "/home/ec2-user/updated_maicagroups/production/myapp/static/images",
    "/home/ec2-user/updated_maicagroups/production/static/images",
    "/home/ec2-user/updated_maicagroups/production/myapp/static/images/icons"
]

for directory in TARGET_DIRS:
    os.makedirs(directory, exist_ok=True)

if not os.path.exists(SOURCE_LOGO):
    print(f"Error: Could not find favicon at {SOURCE_LOGO}")
else:
    base_img = Image.open(SOURCE_LOGO).convert("RGBA")

    # Icon configurations (browsers, iOS, and PWA)
    sizes = {
        "favicon.ico": (32, 32),
        "favicon-16x16.png": (16, 16),
        "favicon-32x32.png": (32, 32),
        "apple-touch-icon.png": (180, 180),
        "icon-192.png": (192, 192),
        "icon-192x192.png": (192, 192),
        "icon-512.png": (512, 512),
        "icon-512x512.png": (512, 512)
    }

    print("Generating icons across all paths...")
    for filename, (width, height) in sizes.items():
        resized_img = base_img.resize((width, height), Image.Resampling.LANCZOS)
        
        for directory in TARGET_DIRS:
            save_path = os.path.join(directory, filename)
            if filename.endswith(".ico"):
                resized_img.save(save_path, format="ICO", sizes=[(32, 32)])
            else:
                resized_img.save(save_path, format="PNG", optimize=True)

    print("✅ All icons generated successfully!")
