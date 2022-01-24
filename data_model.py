import numpy as np
import xml.etree.ElementTree as ET
import tifffile
import argparse

from typing import Tuple, List


class qptiff_page():
    """
    page_header
    image_description
    
    """
    def __init__(self, file_path: str, page: tifffile.tifffile.TiffPage, 
                 page_index: int):
        self.file_path = file_path
        self.page_index = page_index
        self.page_header = {}
        self.image_description = None
        # self.page_header.update({"page_index": })
        for tag in page.tags.values():
            if tag.name == "ImageDescription":
                self.image_description = ET.fromstring(tag.value)
            else:
                name, value = tag.name, tag.value
                self.page_header[name] = value


    def get_array(self) -> np.ndarray:
        """
        Get the page array as numpy array.

        Parameters
        ----------
        file_path : str
            File path of the qptiff file. Needed to allow lazy loading
            of the arrays when needed.

        Returns
        -------
        arr: np.ndarray
            Numpy array of the page.

        """
        with tifffile.TiffFile(self.file_path) as tif:
            p = tif.pages[self.page_index]
            arr = p.asarray()
        return arr


class qptiff_resolution():
    """
    Groups several pages having the same resolution.
    """
    def __init__(self, file_path, tif: tifffile.tifffile.TiffFile, 
                 resolution: Tuple[int, int], 
                 page_indices: List[int]):
        self._width = resolution[0]
        self._height = resolution[1]
        self.pages = []
        for p_idx in page_indices:
            p = tif.pages[p_idx]
            self.pages.append(qptiff_page(file_path, p, p_idx))

    def get_array(self):
        arr = np.zeros((len(self.pages), self._width, self._height), 
                       dtype=np.uint8)
        for i, p in enumerate(self.pages):
            arr[i, :, :] = p.get_array().T
        return arr



class qptiff():
    """
    Data model for a qptiff file. Tile data is stored in pages 
    in the tiff files, and the data model keeps this convention. 
    However, several pages with the same resolution are grouped together.
    
    Resolutions are sorted highest to lowest.
    
    qptiff.meta_header
    qptiff.resolution[0].resolution_header
    qptiff.resolution[0].get_array()
    qptiff.resolution[0].pages[0].page_header
    qptiff.resolution[0].pages[0].image_description
    qptiff.resolution[0].pages[0].get_array()
    
    """
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.meta_header = {}
        self.resolutions = []
        with tifffile.TiffFile(file_path) as tif:
            self.meta_header.update({"num_pages": len(tif.pages)})
            res_set, resolutions_dict = self.group_pages_by_resolution(tif)
            res_ls = sorted(list(res_set), key = lambda x: x[0], reverse=True)
            page_idx_ls = []
            for res in res_ls:
               page_idx_ls.append([int(key) for key, val in resolutions_dict.items() if val[0] == res[0] and val[1] == res[1]])
            multiplex_first = sorted(zip(res_ls, page_idx_ls), 
                                     key = lambda x: len(x[1]),
                                     reverse=True)
            for res in multiplex_first:
                self.resolutions.append(qptiff_resolution(file_path, tif, 
                                                          res[0], res[1]))
        print(self.meta_header)
        

    def group_pages_by_resolution(self, tif: tifffile.tifffile.TiffFile) -> Tuple[set, dict]:
        """
        For each page get the ImageWidth and compute the height to
        determine the dimensions.

        Parameters
        ----------
        tif : tifffile.tifffile.TiffFile
            Buffer object of the tiff file.

        Returns
        -------
        res_set : set
            Unique resolutions.
        resolution_dict : dict
            Resolution for each page index.

        """
        resolution_dict = {}
        res_set = set()
        for i, p in enumerate(tif.pages):
            for tag in p.tags.values():
                if tag.name == "ImageWidth":
                    width = tag.value
                    height = int(p.size / width)
            res = (width, height)
            p_res = {str(i): res}
            res_set.update([res])
            resolution_dict.update(p_res)
        return res_set, resolution_dict


parser = argparse.ArgumentParser()
parser.add_argument("--file_path", required=True)

if __name__ == "__main__":
    args = parser.parse_args()
    qp = qptiff(str(args.file_path))
    print(len(qp.resolutions))
    res4 = qp.resolutions[3].get_array()
    print(res4.shape)
    