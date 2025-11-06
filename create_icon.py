#!/usr/bin/env python3
"""
Icon creation/download helper script for GAM Admin Tool.

This script helps you prepare an icon for the application.
"""

import os
import sys
import urllib.request


def download_icon():
    """Download Google Workspace icon from web."""
    icon_url = "https://cdn.jim-nielsen.com/ios/512/google-2015-10-22.png?rf=1024"
    output_path = "assets/icon.png"

    print("Downloading icon from:", icon_url)

    try:
        # Create assets directory if it doesn't exist
        os.makedirs("assets", exist_ok=True)

        # Download the file
        urllib.request.urlretrieve(icon_url, output_path)

        # Check file size
        size = os.path.getsize(output_path)
        if size < 1000:
            print(f"Warning: Downloaded file is only {size} bytes - may not be a valid image")
            print("Please download the icon manually and place it in assets/icon.png")
            return False

        print(f"✓ Icon downloaded successfully to {output_path} ({size} bytes)")
        print("\nNext steps:")
        print("1. Convert to ICO format (see assets/icon_instructions.txt)")
        print("2. Or use PNG directly during development")
        return True

    except Exception as e:
        print(f"✗ Failed to download icon: {e}")
        print("\nPlease download manually:")
        print(f"1. Visit: {icon_url}")
        print("2. Save as: assets/icon.png")
        print("3. Convert to ICO (see assets/icon_instructions.txt)")
        return False


def create_placeholder_ico():
    """Create a simple placeholder ICO file."""
    try:
        from PIL import Image, ImageDraw, ImageFont

        # Create a simple colored icon
        size = 256
        img = Image.new('RGBA', (size, size), color='#4285f4')  # Google Blue
        draw = ImageDraw.Draw(img)

        # Draw a simple "G" or "GAM" text
        try:
            # Try to use a font
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 120)
        except:
            # Fallback to default
            font = ImageFont.load_default()

        # Draw text
        text = "G"
        draw.text((size//2, size//2), text, fill='white', font=font, anchor='mm')

        # Save as ICO with multiple sizes
        os.makedirs("assets", exist_ok=True)
        img.save('assets/icon.ico', format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])

        print("✓ Placeholder icon created: assets/icon.ico")
        return True

    except ImportError:
        print("✗ Pillow (PIL) not installed. Cannot create placeholder icon.")
        print("Install with: pip install Pillow")
        return False
    except Exception as e:
        print(f"✗ Failed to create placeholder icon: {e}")
        return False


def convert_png_to_ico():
    """Convert existing PNG to ICO format."""
    png_path = "assets/icon.png"
    ico_path = "assets/icon.ico"

    if not os.path.exists(png_path):
        print(f"✗ PNG file not found: {png_path}")
        return False

    try:
        from PIL import Image

        img = Image.open(png_path)

        # Resize if needed
        if img.size[0] > 256:
            img = img.resize((256, 256), Image.Resampling.LANCZOS)

        # Save as ICO with multiple sizes
        img.save(ico_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])

        print(f"✓ Icon converted successfully: {ico_path}")
        return True

    except ImportError:
        print("✗ Pillow (PIL) not installed. Cannot convert icon.")
        print("Install with: pip install Pillow")
        return False
    except Exception as e:
        print(f"✗ Failed to convert icon: {e}")
        return False


def main():
    """Main function."""
    print("=" * 60)
    print("GAM Admin Tool - Icon Helper")
    print("=" * 60)

    print("\nChoose an option:")
    print("1. Download Google Workspace icon")
    print("2. Convert existing PNG to ICO")
    print("3. Create simple placeholder icon")
    print("4. Skip (build without custom icon)")

    choice = input("\nEnter choice (1-4): ").strip()

    if choice == "1":
        download_icon()
        print("\nTo convert to ICO, run this script again and choose option 2")
    elif choice == "2":
        convert_png_to_ico()
    elif choice == "3":
        create_placeholder_ico()
    elif choice == "4":
        print("Skipping icon creation. Application will use default icon.")
    else:
        print("Invalid choice")
        return 1

    print("\n" + "=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
