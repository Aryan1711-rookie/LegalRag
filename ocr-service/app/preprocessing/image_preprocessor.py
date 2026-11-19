from PIL import Image


class ImagePreprocessor:

    def __init__(
        self,
        enabled: bool = True,
        max_dimension: int = 2400,
    ):
        self.enabled = enabled
        self.max_dimension = max_dimension

    def preprocess(
        self,
        image: Image.Image,
    ) -> tuple[Image.Image, dict]:

        image = image.convert("RGB")

        width, height = image.size

        scale = 1.0

        if self.enabled:

            if width < 600:
                scale = 3.0

            elif width < 1000:
                scale = 2.0

            if scale > 1:

                scale = min(
                    scale,
                    self.max_dimension / max(width, height)
                )

                scale = max(1.0, scale)

        new_width = round(width * scale)
        new_height = round(height * scale)

        if scale > 1:

            image = image.resize(
                (new_width, new_height),
                Image.Resampling.LANCZOS,
            )

        metadata = {
            "method": (
                "lanczos" if scale > 1 else "none"
            ),
            "upscaled": scale > 1,
            "scale_factor": round(scale, 4),
            "original_width": width,
            "original_height": height,
            "processed_width": new_width,
            "processed_height": new_height,
        }

        return image, metadata