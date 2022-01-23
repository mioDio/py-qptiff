import numpy as np
import xml.etree.ElementTree as ET
import tifffile
import napari


class qptiff_page():
    def __init__(self, page, file_path: str):
        self.page_header = {}
        self.image_description = None
        self.page_header.update({"page_index": })
        for tag in p.tags.values():
            if tag.name == "ImageDescription":
                self.image_description = ET.fromstring(tag.value)
            else:  
                name, value = tag.name, tag.value
                self.page_header[name] = value

class qptiff():
    """
    Data model for a qptiff file.
    qptiff.meta_header
    qptiff.resolution[0].resolution_header
    qptiff.resolution[0].as_array()
    qptiff.resolution[0].pages[0].page_header
    qptiff.resolution[0].pages[0].image_description
    qptiff.resolution[0].pages[0].np_array()
    
    """
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.meta_header = {}
        self.pages = []
        with tifffile.TiffFile(file_path) as tif:
            self.meta_header.update({"num_pages": len(tif.pages),
                                     })

    def parse_header(self):
        pass
