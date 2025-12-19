# import json
# import os

# from dotenv import load_dotenv
# from google import genai
# from PIL import Image

# load_dotenv()


# def analyze_invoice_images(image_paths):
#     """
#     Analyze invoice images using Google's Gemini model
#     Args:
#         image_paths (list): List of paths to image files
#     Returns:
#         dict: Structured invoice data and analytics
#     """
#     try:
#         client = genai.Client(api_key=os.environ.get("API_KEY"))
#         images = [Image.open(path) for path in image_paths]

#         prompt = """
#         You are analyzing images of a single commercial invoice. 

#         Create multiple markdown tables of different types of entities, values and data extracted.

#         Return only clear markdown tables, intelligently split as per content type available.

#         DO NOT RETURN ANYTHING ELSE OTHER THAN JSON FORMAT.

#         NO DESCRIPTION OR EXTRA INFORMATION NEEDED 

#         """

#         contents = [prompt] + images

#         response = client.models.generate_content(
#             model=os.environ.get("GEMINI_MODEL"), contents=contents
#         )

#         res = json.loads(response.model_dump_json())["candidates"][0]["content"][
#             "parts"
#         ][0]["text"]

#         return res

#     except Exception as e:
#         return {"error": f"Error during analysis: {str(e)}"}


import base64
import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def _encode_image(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def analyze_invoice_images(image_paths):
    try:
        client = OpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            base_url=f"{os.getenv('AZURE_OPENAI_ENDPOINT')}/openai/deployments/{os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')}",
            default_query={"api-version": os.getenv("AZURE_OPENAI_API_VERSION")},
        )

        prompt = """
You are analyzing images of a single commercial invoice.
Extract all invoice fields and return STRICT JSON only.
"""

        content = [{"type": "text", "text": prompt}]

        for path in image_paths:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{_encode_image(path)}"
                }
            })

        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),  
            messages=[{"role": "user", "content": content}],
            temperature=1
        )

        return response.choices[0].message.content

    except Exception as e:
        return {"error": f"Error during analysis: {str(e)}"}
