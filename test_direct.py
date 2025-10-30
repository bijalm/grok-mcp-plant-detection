#!/usr/bin/env python3
import os
import sys
from mcp_fast_grok_real import GrokAnalyzer

def test_plant_analysis():
    """Test the plant analyzer directly from terminal"""
    
    # Initialize the analyzer
    analyzer = GrokAnalyzer()
    
    # Test with your bitter rot image
    test_image = "images_test/BitterRott.jpg"  # Change this path as needed
    
    if not os.path.exists(test_image):
        print(f"❌ Test image not found: {test_image}")
        print("Available test images:")
        if os.path.exists("images_tests"):
            for file in os.listdir("images_tests"):
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    print(f"  - images_test/{file}")
        return
    
    print(f"🧪 Testing plant analyzer with: {test_image}")
    print("=" * 60)
    
    # Analyze the image
    result = analyzer.analyze_plant_image(test_image)
    
    print("🔬 ANALYSIS RESULT:")
    print("=" * 60)
    print(result)
    print("=" * 60)

if __name__ == "__main__":
    test_plant_analysis()