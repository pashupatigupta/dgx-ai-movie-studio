from services.gallery_service import GalleryService

gallery = GalleryService()

images = gallery.get_images()

print(images)
