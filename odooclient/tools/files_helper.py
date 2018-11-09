# -*- coding: utf-8 -*-

import os
import csv
import xlrd
import pprint
import base64
import logging
import itertools
import traceback
import cStringIO
import PIL.Image


FORMAT = "%(asctime)-15s - %(url)s - %(user)s :: "
#logging.basicConfig(format=FORMAT, level=logging.DEBUG)

_logger = logging.getLogger("OdooClient ")


pp = pprint.PrettyPrinter(indent=4)


def _read_csv_data(path):
    """
    Reads CSV from given path and Return list of dict with Mapping
    """
    data = csv.reader(open(path))
    # Read the column names from the first line of the file
    fields = data.next()
    data_lines = []
    for row in data:
        items = dict(zip(fields, row))
        data_lines.append(items)
    return data_lines

def _get_field_mapping(values, mapping):
    """
    Final Field Mapper for the Preparing Data for the Import Data
    use for def load in orm
    """
    fields=[]
    data_lst = []
    for key,val in mapping.items():
        if key not in fields and values:
            fields.append(key)
            value = values.get(val)
            data_lst.append(value)
    return fields, data_lst

def _read_xls(fname):
    """ Read file content, using xlrd lib """
    return xlrd.open_workbook(fname)

def _read_xls_sheet(sheet):
    for row in itertools.imap(sheet.row, range(sheet.nrows)):
        values = []
        for cell in row:
            if cell.ctype is xlrd.XL_CELL_NUMBER:
                is_float = cell.value % 1 != 0.0
                values.append(
                    unicode(cell.value)
                    if is_float
                    else unicode(int(cell.value))
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
    print 'Found {:6} files in dir "{}" .'.format(len(file_map), walk_dir)
    return file_map

def read_image_data(file_path):
    img = PIL.Image.open(file_path)
    image_buffer = cStringIO.StringIO()
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
    print 'Cached {:6} records of moodel {} .'.format(len(record_ids), model)
    return record_ids
