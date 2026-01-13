from PIL import Image
import os

def optimize_image(filename, max_width=300):
    try:
        if not os.path.exists(filename):
            print(f"File not found: {filename}")
            return

        img = Image.open(filename)
        w_percent = (max_width / float(img.size[0]))
        h_size = int((float(img.size[1]) * float(w_percent)))
        
        # High quality resizing
        img = img.resize((max_width, h_size), Image.Resampling.LANCZOS)
        
        # Save as optimized web version
        new_filename = filename.replace(".png", "_web.png")
        img.save(new_filename, "PNG", optimize=True)
        print(f"Optimized: {filename} -> {new_filename} ({img.size})")
        
    except Exception as e:
        print(f"Error optimizing {filename}: {e}")

if __name__ == "__main__":
    optimize_image("logo_muni.png", max_width=200)
    optimize_image("CiviumTech.png", max_width=300)
