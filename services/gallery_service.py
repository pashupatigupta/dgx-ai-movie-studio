from pathlib import Path

IMAGE_DIR = Path("generated/images")


class GalleryService:

    def get_images(self):

        IMAGE_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        images = []

        for image in sorted(
            IMAGE_DIR.glob("*.png"),
            reverse=True
        ):

            images.append({

                "filename": image.name,

                "path": str(image),

                "size_mb": round(
                    image.stat().st_size / (1024 * 1024),
                    2
                )

            })

        return images
