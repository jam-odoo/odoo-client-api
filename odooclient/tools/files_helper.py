# -*- coding: utf-8 -*-
import io
import os
import csv
import xlrd
import pprint
import base64
import logging
from urllib.parse import urlparse
import requests
import itertools
import traceback
import importlib
import io
from PIL import Image

FORMAT = "%(asctime)-15s - %(url)s - %(user)s :: "
#logging.basicConfig(format=FORMAT, level=logging.DEBUG)
_logger = logging.getLogger("OdooClient ")

DEFAULT_IMAGE_TIMEOUT = 100
DEFAULT_IMAGE_MAXBYTES = 25 * 1024 * 1024
DEFAULT_IMAGE_CHUNK_SIZE = 32768

pp = pprint.PrettyPrinter(indent=4)

def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]

def read_csv_data(path):
    """
    Reads CSV from given path and Return list of dict with Mapping
    """
    data = csv.reader(open(path, encoding='ISO-8859-1'))
    # Read the column names from the first line of the file
    fields = next(data)
    data_lines = []
    for row in data:
        items = dict(zip(fields, row))
        data_lines.append(items)
    return data_lines

def get_field_mapping(values, mapping):
    """
    Final Field Mapper for the Preparing Data for the Import Data
    use for def load in orm
    """
    fields=[]
    data_lst = []
    for key, val in mapping.items():
        if key not in fields and values:
            fields.append(key)
            value = values.get(val)
            if value == None:
                value = ''
            data_lst.append(value)
    return fields, data_lst

def read_xls(fname):
    """ Read file content, using xlrd lib """
    return xlrd.open_workbook(fname)

def read_xls_sheet(sheet):
    for row in map(sheet.row, range(sheet.nrows)):
        values = []
        for cell in row:
            if cell.ctype is xlrd.XL_CELL_NUMBER:
                is_float = cell.value % 1 != 0.0
                values.append(
                    str(cell.value)
                    if is_float
                    else int(cell.value)
                )
            elif cell.ctype is xlrd.XL_CELL_DATE:
                is_datetime = cell.value % 1 != 0.0
                # emulate xldate_as_datetime for pre-0.9.3
                dt = datetime.datetime(*xlrd.xldate.xldate_as_tuple(cell.value, book.datemode))
                values.append(
                    dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                    if is_datetime
                    else dt.strftime(DEFAULT_SERVER_DATE_FORMAT)
                )
            elif cell.ctype is xlrd.XL_CELL_BOOLEAN:
                values.append(u'True' if cell.value else u'False')
            elif cell.ctype is xlrd.XL_CELL_ERROR:
                raise ValueError(
                    _("Error cell found while reading XLS/XLSX file: %s") %
                    xlrd.error_text_from_code.get(
                        cell.value, "unknown error code %s" % cell.value)
                )
            else:
                values.append(cell.value)
        if any(x for x in values if x.strip()):
            yield values

def read_filemap(walk_dir):
    file_map = dict([
        (filename, os.path.join(root, filename))
            for root, subdirs, files in os.walk(walk_dir)
                for filename in files
    ])
    print ('Found {:6} files in dir "{}" .'.format(len(file_map), walk_dir))
    return file_map

def read_image_data(file_path):
    img = PIL.Image.open(file_path)
    image_buffer = io.StringIO()
    img.save(image_buffer, format="JPEG")
    image_data = base64.b64encode(image_buffer.getvalue())
    return image_data

def cache_model_data(conn, model, key_field=None, value_field=None):
    """
    This help in caching model in dict in running script so
    for getting some id for relations, wea are not forced to query db
    """
    if key_field == None:
        key_field = 'name'
    if value_field == None:
        value_field = 'id'
    record_ids = {}
    for record in conn.SearchRead(model, [],fields=[ key_field, value_field ]):
        record_ids.update({record[key_field]: record[value_field]})
    print ('Cached {:6} records of model `{}`.'.format(len(record_ids), model))
    return record_ids

def import_image_by_url(url, limit_large_image=False):
    """ Imports an image by URL
    :param str url: the original field value
    :return: the replacement value
    :rtype: bytes
    """
    maxsize = DEFAULT_IMAGE_MAXBYTES
    try:
        response = requests.get(url, timeout=DEFAULT_IMAGE_TIMEOUT)
        response.raise_for_status()

        if response.headers.get('Content-Length') and int(response.headers['Content-Length']) > maxsize:
            raise ValueError("File size exceeds configured maximum (%s bytes)") % maxsize

        content = bytearray()
        for chunk in response.iter_content(DEFAULT_IMAGE_CHUNK_SIZE):
            content += chunk
            if len(content) > maxsize:
                print ("File size exceeds configured maximum (%s bytes)" % maxsize)

        # Image resolution check incase if we do not want to allow large image file.
        if limit_large_image:
            image = Image.open(io.BytesIO(content))
            w, h = image.size
            if w * h > 42e6:  # Nokia Lumia 1020 photo resolution
                print ("Image size excessive, imported images must be smaller than 42 million pixel")
                return False
        image_file_name =  os.path.basename(urlparse(url).path)

        return image_file_name, base64.b64encode(content)
    except Exception as e:
        print ("Could not retrieve URL: %(url)s: %(error)s"%{'url': url, 'error': e})
        return False