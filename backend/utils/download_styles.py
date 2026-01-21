import requests
from pathlib import Path
import time

# Alternative URLs that are more download-friendly
STYLE_URLS = {
    "vangogh": "https://www.artic.edu/iiif/2/25c31d8d-21a4-9ea1-1d73-6a2eca4dda7e/full/843,/0/default.jpg",
    "picasso": "https://www.artic.edu/iiif/2/831a05de-d3f6-f4fa-a460-23008dd58dda/full/843,/0/default.jpg",
    "monet": "https://www.artic.edu/iiif/2/3c27b499-af56-f0d5-93b5-a7f2f1ad5813/full/843,/0/default.jpg",
    "kandinsky": "https://www.artic.edu/iiif/2/40646d6f-3b9b-527c-a4be-ad7ecf823f67/full/843,/0/default.jpg"
}

def download_style_images():
    """Download style reference images"""
    style_dir = Path(__file__).resolve().parent.parent.parent / "models" / "style_images"
    style_dir.mkdir(parents=True, exist_ok=True)
    
    print("📥 Downloading style images from Art Institute of Chicago...")
    
    # Add headers to mimic a browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.artic.edu/',
    }
    
    for style_name, url in STYLE_URLS.items():
        output_path = style_dir / f"{style_name}.jpg"
        
        if output_path.exists():
            print(f"  ✓ {style_name}.jpg already exists")
            continue
        
        try:
            print(f"  ⬇ Downloading {style_name}...", end=" ", flush=True)
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            print(f"✓ ({len(response.content) // 1024} KB)")
            
            # Small delay to be respectful to the server
            time.sleep(0.5)
            
        except Exception as e:
            print(f"✗ Error: {e}")
            print(f"     URL: {url}")
    
    print("\n✅ Download complete!\n")
    
    # Verify downloads
    print("📋 Verification:")
    for style_name in STYLE_URLS.keys():
        path = style_dir / f"{style_name}.jpg"
        if path.exists():
            size_kb = path.stat().st_size // 1024
            print(f"  ✓ {style_name}.jpg ({size_kb} KB)")
        else:
            print(f"  ✗ {style_name}.jpg - MISSING!")

if __name__ == "__main__":
    download_style_images()