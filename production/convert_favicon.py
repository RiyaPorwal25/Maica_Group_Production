from PIL import Image
import os

SOURCE_FAVICON = "/home/ec2-user/updated_maicagroups/production/static/images/favicon.ico"
TARGET_DIR = "/home/ec2-user/updated_maicagroups/production/myapp/static/images"

os.makedirs(TARGET_DIR, exist_ok=True)

if not os.path.exists(SOURCE_FAVICON):
    print(f"Error: Could not find favicon at {SOURCE_FAVICON}")
else:
    # Open original ICO and convert to RGBA
    img = Image.open(SOURCE_FAVICON).convert("RGBA")

    # Generate 192x192 PNG
    icon_192 = img.resize((192, 192), Image.Resampling.LANCZOS)
    icon_192.save(os.path.join(TARGET_DIR, "icon-192.png"), "PNG")
    print("Generated icon-192.png from favicon.ico successfully!")

    # Generate 512x512 PNG
    icon_512 = img.resize((512, 512), Image.Resampling.LANCZOS)
    icon_512.save(os.path.join(TARGET_DIR, "icon-512.png"), "PNG")
    print("Generated icon-512.png from favicon.ico successfully!")
