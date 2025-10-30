#!/usr/bin/env python3
import os
import base64
import sys
import json
from mcp.server.fastmcp import FastMCP
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastMCP server
mcp = FastMCP("Plant Detector Pro")

class GrokAnalyzer:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv('XAI_API_KEY'),
            base_url="https://api.x.ai/v1"
        )
        self.model = "grok-2-vision-1212"
    
    def analyze_plant_image(self, image_path: str) -> str:
        """Analyze plant image using Grok Vision AI with structured JSON output"""
        try:
            # Check if image exists
            if not os.path.exists(image_path):
                return "Error: Image file not found. Please check the path."
            
            print(f"Analyzing image: {image_path}", file=sys.stderr)
            
            # Encode image to base64
            with open(image_path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Create detailed prompt for plant disease analysis
            prompt = """**Situation**
You are deploying an AI agent in AWS Lambda for automated plant disease detection to support agricultural diagnostics. The system needs to analyze plant images with high accuracy to provide reliable disease identification and treatment recommendations for farmers, agricultural consultants, or plant health monitoring systems.

**Task**
Analyze the provided plant image and perform comprehensive plant pathology assessment. Identify the specific plant part shown, detect any diseases or health issues present, determine the type of pathogen involved, and provide actionable treatment recommendations. Return your analysis in a structured JSON format with confidence scoring.

**Objective**
Achieve maximum diagnostic accuracy (targeting >85% confidence) in plant disease detection to enable reliable automated plant health monitoring and early intervention strategies that can prevent crop losses and optimize agricultural outcomes.

**Knowledge**
Your life depends on you providing the most accurate disease identification possible, as incorrect diagnoses could lead to crop failures and significant agricultural losses.

Key diagnostic criteria:
- Examine visual symptoms systematically: leaf spots, discoloration, wilting, growth abnormalities, lesions, color of the mold, cankers, or unusual growths
- Differentiate between fungal infections (often showing spots, mold, or fuzzy growth), bacterial infections (different kind of spots, typically water-soaked lesions, oozing), and viral infections (mosaic patterns, stunting, distortion)
- Consider environmental factors that may mimic disease symptoms (nutrient deficiencies, water stress, physical damage)
- If the plant is healthy detect any appearance phenomenas in disease detected
- Only identify specific diseases when visual evidence strongly supports the diagnosis - use "None" when symptoms are unclear or could indicate multiple conditions
- Provide treatment recommendations that are practical, cost-effective, and consider integrated pest management principles
- Include specific application rates, timing, and safety measures for any chemical treatments recommended

Critical requirements:
- Confidence scores below 0.7 should trigger more conservative disease identification (use "None" if uncertain)
- Recommendations must be actionable within typical agricultural settings
- Chemical treatment advice must include proper application methods and safety precautions
- Consider both immediate treatment and long-term prevention strategies

**Examples**
    "Input Image URL: https://content.ces.ncsu.edu/media/images/IMG_1301.JPG
    "Output:
    {
        "health_status": "unhealthy",
        "fungal_status": "present",
        "plant_part": "fruit",
        "disease_detected": "Early blight",
        "recommendations": [
            "Remove affected fruits immediately to prevent spread",
            "Apply a copper-based fungicide weekly",
            "Avoid overhead watering to reduce moisture on leaves"
        ],
        "confidence_score": 0.89
    }

Analyze the image systematically and respond ONLY in valid JSON format with exactly these keys: `health_status`, `fungal_status`, `plant_part`, `disease_detected`, `recommendations`, `confidence_score`.
For health_status, use: "healthy", "unhealthy", or "uncertain"
For fungal_status, use: "present", "absent", or "uncertain"
For plant_part, specify: "fruit", "leaves", "stem", "roots", "flowers", or "whole_plant"
For disease_detected, provide the specific disease name or "None"
For recommendations, provide 2–4 practical, actionable steps including specific chemical treatments with application details when applicable
For confidence_score, provide a decimal between 0.0 and 1.0 reflecting your diagnostic certainty"""
            
            # Call Grok Vision API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{encoded_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=2000
            )
            
            analysis = response.choices[0].message.content

            # Try to parse as JSON, if it fails return the raw response
            try:
                # Extract JSON from the response if it's wrapped in text
                if "{" in analysis and "}" in analysis:
                    json_start = analysis.find("{")
                    json_end = analysis.rfind("}") + 1
                    json_str = analysis[json_start:json_end]
                    parsed_json = json.loads(json_str)
                    return json.dumps(parsed_json, indent=2)
                else:
                    # If no JSON found, return structured error
                    return json.dumps({
                        "error": "Response not in expected JSON format",
                        "raw_response": analysis
                    }, indent=2)
            except json.JSONDecodeError:
                return json.dumps({
                    "error": "Failed to parse JSON response",
                    "raw_response": analysis
                }, indent=2)
            
        except Exception as e:
            return json.dumps({
                "error": f"API Error: {str(e)}",
                "checklist": [
                    "Verify XAI_API_KEY in .env file",
                    "Check xAI account has credits", 
                    "Confirm image path is correct"
                ]
            }, indent=2)
        
# Create analyzer instance
analyzer = GrokAnalyzer()

@mcp.tool()
def analyze_plant(image_path: str) -> str:
    """Analyze a plant image for diseases using Grok Vision AI.
    
    This uses real AI vision analysis to detect diseases, spots, mold, 
    and other health issues in plant images.
    
    Args:
        image_path: Full path to the plant image file (JPEG, PNG, etc.)
    """
    return analyzer.analyze_plant_image(image_path)

# Run the server
if __name__ == "__main__":
    mcp.run()