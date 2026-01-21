from PIL import Image, ImageDraw
import numpy as np
from pathlib import Path

def create_sample_styles():
    """Create sample style images using PIL"""
    style_dir = Path(__file__).resolve().parent.parent.parent / "models" / "style_images"
    style_dir.mkdir(parents=True, exist_ok=True)
    
    print("🎨 Creating sample style images...")
    
    # Van Gogh - Swirly blue/yellow pattern
    img = Image.new('RGB', (512, 512))
    pixels = img.load()
    for i in range(512):
        for j in range(512):
            # Create swirly pattern
            val = int((np.sin(i/20) + np.cos(j/20)) * 127 + 128)
            pixels[i, j] = (30, 50, val)  # Blue/yellow tones
    img.save(style_dir / "vangogh.jpg", quality=95)
    print("  ✓ vangogh.jpg")
    
    # Picasso - Geometric cubist pattern
    img = Image.new('RGB', (512, 512), (240, 230, 210))
    draw = ImageDraw.Draw(img)
    colors = [(200, 180, 160), (180, 160, 140), (160, 140, 120), (140, 120, 100)]
    for i in range(0, 512, 64):
        for j in range(0, 512, 64):
            color = colors[(i//64 + j//64) % len(colors)]
            draw.rectangle([i, j, i+64, j+64], fill=color)
    img.save(style_dir / "picasso.jpg", quality=95)
    print("  ✓ picasso.jpg")
    
    # Monet - Soft impressionist colors
    img = Image.new('RGB', (512, 512))
    pixels = img.load()
    for i in range(512):
        for j in range(512):
            r = int(150 + 50 * np.sin(i/30))
            g = int(180 + 50 * np.cos(j/30))
            b = int(200 + 30 * np.sin((i+j)/40))
            pixels[i, j] = (r, g, b)
    img.save(style_dir / "monet.jpg", quality=95)
    print("  ✓ monet.jpg")
    
    # Kandinsky - Abstract bold colors
    img = Image.new('RGB', (512, 512))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, 512, 512], fill=(255, 220, 100))
    draw.ellipse([100, 100, 400, 400], fill=(255, 100, 100))
    draw.polygon([(0, 0), (512, 0), (256, 512)], fill=(100, 100, 255))
    draw.rectangle([200, 0, 312, 512], fill=(50, 200, 150))
    img.save(style_dir / "kandinsky.jpg", quality=95)
    print("  ✓ kandinsky.jpg")
    
    print(f"\n✅ Sample style images created!")
    print(f"📁 Location: {style_dir}\n")

if __name__ == "__main__":
    create_sample_styles()