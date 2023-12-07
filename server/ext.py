from imagededup.utils.logger import return_logger
from imagededup.utils.image_utils import preprocess_image
import numpy as np
from PIL import Image
from typing import BinaryIO, Union, Tuple, List
from pathlib import PurePath
from PIL import Image
from imagededup.methods import CNN

IMG_FORMATS = ['JPEG', 'PNG', 'BMP', 'MPO', 'PPM', 'TIFF', 'GIF', 'WEBP']
logger = return_logger(__name__)  
  
def load_image(
    image_file: Union[PurePath, str, BinaryIO],
    target_size: Tuple[int, int] = None,
    grayscale: bool = False,
    img_formats: List[str] = IMG_FORMATS,
) -> np.ndarray:
    """
    Load an image given its path. Returns an array version of optionally resized and grayed image. Only allows images
    of types described by img_formats argument.

    Args:
        image_file: Path to the image file.
        target_size: Size to resize the input image to.
        grayscale: A boolean indicating whether to grayscale the image.
        img_formats: List of allowed image formats that can be loaded.
    """
    try:
        img = Image.open(image_file)

        # validate image format
        if img.format not in img_formats:
            raise ValueError('Invalid image format')

        else:
            if img.mode != 'RGB':
                # convert to RGBA first to avoid warning
                # we ignore alpha channel if available
                img = img.convert('RGBA').convert('RGB')

            img = preprocess_image(img, target_size=target_size, grayscale=grayscale)

            return img

    except Exception as e:
        raise ValueError(f'Invalid image file: {e}')

################################  

class CNNext(CNN):

  def cnn_encode_stream(
        self,
        image_stream: BinaryIO = None,
    ) -> np.ndarray:

        image_pp = load_image(
          image_file=image_stream, target_size=None, grayscale=False
        )

        return (
            self._get_cnn_features_single(image_pp)
            if isinstance(image_pp, np.ndarray)
            else None
        )
