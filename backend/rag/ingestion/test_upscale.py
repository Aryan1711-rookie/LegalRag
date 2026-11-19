from pathlib import Path
from PIL import Image

image_path = Path("rag/test/4.png")

with Image.open(image_path) as image:

    image = image.convert("RGB")

    for scale in [2, 3]:

        resized = image.resize(
            (
                image.width * scale,
                image.height * scale
            ),
            Image.Resampling.LANCZOS
        )

        output_path = image_path.with_name(
            f"4_upscaled_{scale}x.png"
        )

        resized.save(output_path)

        print(
            f"Saved: {output_path} | "
            f"Resolution: {resized.size}"
        )