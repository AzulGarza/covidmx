#!/usr/bin/env python
# coding: utf-8

from pathlib import Path
from typing import Tuple, Union
import logging

import requests
import zipfile
import subprocess
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def download_file(directory: Union[str, Path], source_url: str, decompress: bool = False) -> None:
    """Download data from source_ulr inside directory.

    Parameters
    ----------
    directory: str, Path
        Custom directory where data will be downloaded.
    source_url: str
        URL where data is hosted.
    decompress: bool
        Wheter decompress downloaded file. Default False.
    """
    if isinstance(directory, str):
        directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)

    filename = source_url.split('/')[-1]
    filepath = directory / filename

    # Streaming, so we can iterate over the response.
    r = requests.get(source_url, stream=True)
    # Total size in bytes.
    total_size = int(r.headers.get('content-length', 0))
    block_size = 1024 #1 Kibibyte

    t = tqdm(total=total_size, unit='iB', unit_scale=True)
    with open(filepath, 'wb') as f:
        for data in r.iter_content(block_size):
            t.update(len(data))
            f.write(data)
    t.close()

    if total_size != 0 and t.n != total_size:
        logger.error('ERROR, something went wrong downloading data')

    size = filepath.stat().st_size
    logger.info(f'Successfully downloaded {filename}, {size}, bytes.')

    if decompress:
        with zipfile.ZipFile(filepath, 'r') as zip_ref:
            extracted = zip_ref.namelist()
            zip_ref.extractall(directory)
        
        extracted = [directory / file for file in extracted]

        logger.info(f'Successfully decompressed {filepath}')
        
        return extracted


translate_serendipia = {
    'confirmed': 'positivos',
    'suspects': 'sospechosos'
}

translate_romero = {
    'confirmed': 'confirmed',
    'deaths': 'deaths',
    'negatives': 'negatives',
    'suspects': 'suspects'
}

translate_flores = {
    'confirmed': 'confirmed',
    'deaths': 'deaths',
    'negatives': 'negatives',
    'suspects': 'probables'
}
