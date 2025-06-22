"""Uses the 'Search and Recolor' API to generate a new image based on the provided image and new paint prompt."""

import logging
import os

import httpx
from fastapi import HTTPException

logger = logging.getLogger(__name__)

STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
if not STABILITY_API_KEY:
    raise RuntimeError("STABILITY_API_KEY não configurada no ambiente.")

API_URL = "https://api.stability.ai/v2beta/stable-image/edit/search-and-recolor"


def _base64_to_bytes(base64_str: str) -> bytes:
    """Convert base64 string to bytes"""
    import base64

    if "," in base64_str:
        base64_str = base64_str.split(",")[1]
    return base64.b64decode(base64_str)


async def simulate_paint_on_image(image_base64: str, new_paint_prompt: str) -> bytes:
    """
    Uses the 'Search and Recolor' API to generate a new image based on the provided image and new paint prompt.
    """
    logger.info("Initing simulation with Stability API AI 'Search and Recolor'...")

    # Convert base64 string to bytes
    image_bytes = _base64_to_bytes(image_base64)

    headers = {"authorization": f"Bearer {STABILITY_API_KEY}", "accept": "image/*"}

    files = {"image": ("original_image.png", image_bytes, "image/png")}

    data = {
        "prompt": new_paint_prompt,
        "select_prompt": "wall",
        "output_format": "png",
    }

    logger.info(
        f"Stability AI. Prompt sended: '{new_paint_prompt}', Select Prompt: 'wall'"
    )

    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(
                API_URL, headers=headers, files=files, data=data
            )

            if response.status_code == 200:
                logger.info(
                    "Image generated successfully with Stability API 'Search and Recolor'."
                )
                return response.content
            else:
                try:
                    error_details = response.json()
                    logger.error(
                        f"Error from Stability API: {error_details.get('errors', [str(response.text)])[0]}",
                    )
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Error from Stability API: {error_details.get('errors', [str(response.text)])[0]}",
                    )
                except Exception:
                    logger.error(
                        f"Error from Stability API: {response.status_code} - {response.text}"
                    )
                    raise HTTPException(
                        status_code=response.status_code,
                        detail="Unknown error communicating with Stability API.",
                    )

        except httpx.RequestError as e:
            logger.error(f"Error connecting with Stability API: {e}")
            raise HTTPException(
                status_code=500,
                detail="Unable to connect to Stability API.",
            )
