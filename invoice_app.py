import json
import os

from dotenv import load_dotenv
from google import genai
from PIL import Image

load_dotenv()


def analyze_invoice_images(image_paths):
    """
    Analyze invoice images using Google's Gemini model
    Args:
        image_paths (list): List of paths to image files
    Returns:
        dict: Structured invoice data and analytics
    """
    try:
        client = genai.Client(api_key=os.environ.get("API_KEY"))
        images = [Image.open(path) for path in image_paths]

        prompt = """
        You are analyzing images of a single commercial invoice. 

        Create multiple markdown tables of different types of entities, values and data extracted.

        Return only clear markdown tables, intelligently split as per content type available.

        DO NOT RETURN ANYTHING ELSE EXCEPT THE EXTRACTED TABLES.

        NO DESCRIPTION OR EXTRA INFORMATION NEEDED 

        """

        contents = [prompt] + images

        response = client.models.generate_content(
            model=os.environ.get("GEMINI_MODEL"), contents=contents
        )

        res = json.loads(response.model_dump_json())["candidates"][0]["content"][
            "parts"
        ][0]["text"]

        return res

    except Exception as e:
        return {"error": f"Error during analysis: {str(e)}"}
