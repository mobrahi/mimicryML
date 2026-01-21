import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
from PIL import Image
from pathlib import Path
import time

# Load the style transfer model (this happens once when module is imported)
print("🔄 Loading TensorFlow Hub style transfer model...")
MODEL_URL = "https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2"
hub_model = hub.load(MODEL_URL)
print("✅ Model loaded successfully!")

class StyleTransfer:
    """Handle neural style transfer operations"""
    
    def __init__(self, max_dim=512):
        self.max_dim = max_dim
    
    def load_image(self, image_path: Path) -> tf.Tensor:
        """
        Load and preprocess image for the model
        
        Args:
            image_path: Path to image file
            
        Returns:
            Preprocessed image tensor
        """
        # Load image
        img = Image.open(image_path)
        
        # Convert RGBA to RGB if necessary
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        
        # Resize while maintaining aspect ratio
        img = self._resize_image(img)
        
        # Convert to array and normalize to [0, 1]
        img_array = np.array(img) / 255.0
        
        # Add batch dimension and convert to float32
        img_tensor = tf.convert_to_tensor(img_array, dtype=tf.float32)
        img_tensor = tf.expand_dims(img_tensor, 0)
        
        return img_tensor
    
    def _resize_image(self, image: Image.Image) -> Image.Image:
        """
        Resize image to max_dim while maintaining aspect ratio
        
        Args:
            image: PIL Image
            
        Returns:
            Resized PIL Image
        """
        width, height = image.size
        
        # Calculate new dimensions
        if width > height:
            new_width = self.max_dim
            new_height = int(height * (self.max_dim / width))
        else:
            new_height = self.max_dim
            new_width = int(width * (self.max_dim / height))
        
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    def tensor_to_image(self, tensor: tf.Tensor) -> Image.Image:
        """
        Convert tensor back to PIL Image
        
        Args:
            tensor: Image tensor
            
        Returns:
            PIL Image
        """
        # Remove batch dimension
        tensor = tensor[0]
        
        # Clip values to [0, 1] and convert to [0, 255]
        tensor = tf.clip_by_value(tensor, 0, 1)
        tensor = tensor * 255
        
        # Convert to numpy array
        array = tensor.numpy().astype(np.uint8)
        
        # Create PIL image
        return Image.fromarray(array)
    
    def apply_style(self, content_path: Path, style_path: Path, 
                    output_path: Path) -> dict:
        """
        Apply artistic style to content image
        
        Args:
            content_path: Path to content image
            style_path: Path to style image
            output_path: Path to save result
            
        Returns:
            Dictionary with processing info
        """
        start_time = time.time()
        
        try:
            # Load images
            print(f"  📷 Loading content image: {content_path.name}")
            content_image = self.load_image(content_path)
            
            print(f"  🎨 Loading style image: {style_path.name}")
            style_image = self.load_image(style_path)
            
            # Apply style transfer
            print(f"  🔄 Applying style transfer...")
            stylized_image = hub_model(content_image, style_image)[0]
            
            # Convert back to PIL Image
            result_image = self.tensor_to_image(stylized_image)
            
            # Save result
            print(f"  💾 Saving result to: {output_path.name}")
            result_image.save(output_path, quality=95)
            
            processing_time = time.time() - start_time
            
            print(f"  ✅ Style transfer completed in {processing_time:.2f}s")
            
            return {
                "success": True,
                "processing_time": processing_time,
                "output_path": str(output_path),
                "output_size": output_path.stat().st_size,
                "dimensions": result_image.size
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            print(f"  ❌ Error during style transfer: {str(e)}")
            
            return {
                "success": False,
                "processing_time": processing_time,
                "error": str(e)
            }


# For testing the module directly
def test_style_transfer():
    """Test function to verify style transfer works"""
    from config import UPLOAD_DIR, OUTPUT_DIR
    
    print("\n🧪 Testing Style Transfer Module\n")
    print("=" * 50)
    
    # Check if we have style images
    style_dir = Path(__file__).resolve().parent.parent / "models" / "style_images"
    
    if not style_dir.exists() or not list(style_dir.glob("*.jpg")):
        print("❌ No style images found!")
        print("   Run: python backend/utils/download_styles.py")
        return
    
    print("✅ Style images found")
    
    # List available styles
    styles = [f.stem for f in style_dir.glob("*.jpg")]
    print(f"📋 Available styles: {', '.join(styles)}\n")
    
    # Check if we have a test image
    test_images = list(UPLOAD_DIR.glob("*.*"))
    
    if not test_images:
        print("⚠️  No test images in uploads folder")
        print("   Upload an image to test, or create a sample")
        return
    
    # Use first uploaded image as test
    test_image = test_images[0]
    print(f"🖼️  Using test image: {test_image.name}")
    
    # Create style transfer instance
    st = StyleTransfer(max_dim=512)
    
    # Test with first available style
    style_name = styles[0]
    style_path = style_dir / f"{style_name}.jpg"
    output_path = OUTPUT_DIR / f"test_{style_name}_{test_image.name}"
    
    print(f"\n🎨 Applying {style_name} style...")
    print("-" * 50)
    
    result = st.apply_style(test_image, style_path, output_path)
    
    print("\n" + "=" * 50)
    if result["success"]:
        print("✅ TEST PASSED!")
        print(f"   Output: {result['output_path']}")
        print(f"   Time: {result['processing_time']:.2f}s")
        print(f"   Size: {result['dimensions']}")
    else:
        print("❌ TEST FAILED!")
        print(f"   Error: {result['error']}")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    test_style_transfer()