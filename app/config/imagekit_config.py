from imagekitio import ImageKit

from app.config.app_config import getAppConfig

app_config = getAppConfig()
imagekit = ImageKit(private_key=app_config.imagekit_private_key)
URL_ENDPOINT = app_config.imagekit_url_endpoint
