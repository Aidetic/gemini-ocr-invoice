import os

from dotenv import load_dotenv
from google import genai
from PIL import Image

load_dotenv()


def analyze_car_images(image_paths):
    """
    Analyze car images using Google's Gemini model
    Args:
        image_paths (list): List of paths to image files
    Returns:
        str: Analysis results from the model
    """
    try:
        client = genai.Client(api_key=os.environ.get("API_KEY"))

        # Load all images
        images = [Image.open(path) for path in image_paths]

        # Prepare the prompt and images for the model
        contents = (
            [
                """
            You are analyzing images of a single vehicle. All the images provided are of the same vehicle, showing different views (front, rear, left, and right).

            Perform the following tasks:
            1. Analyze the images for quality (e.g., clarity, lighting, and resolution).
            2. Inspect the vehicle for any structural damages (e.g., dents, scratches, or broken parts).
            3. Identify and return the number plate of the vehicle.

            Compile your observations in a clear table format, ensuring that all details correspond to the same vehicle.

            Example format for the response:
            | Aspect           | Observation                          |
            |------------------|--------------------------------------|
            | Image Quality    | [Your analysis of image quality]    |
            | Structural Damage| [Your analysis of damages]          |
            | Number Plate     | [Identified number plate]            |
            """
            ]
            + images
        )

        response = client.models.generate_content(
            model=os.environ.get("GEMINI_MODEL"), contents=contents
        )
        return response.model_dump_json()

    except Exception as e:
        return f"Error during analysis: {str(e)}"
