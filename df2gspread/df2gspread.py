#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Eduard Trott
# @Date:   2015-09-16 11:28:21
# @Email:  etrott@redhat.com
# @Last modified by:   etrott
# @Last Modified time: 2016-03-08 12:35:42


from string import ascii_uppercase
from itertools import islice

import pandas as pd
import gspread

from .utils import get_credentials
from .gfiles import get_file_id, get_worksheet

try:
    input = raw_input
except NameError:  # Python 3
    pass


def upload(df, gfile="/New Spreadsheet", wks_name=None, chunk_size=1000,
           col_names=True, row_names=True, clean=True, credentials=None,
           df_size = False, new_sheet_dimensions = (1000,100)):
    '''
        Upload given Pandas DataFrame to Google Drive and returns 
        gspread Worksheet object

        :param df: Pandas DataFrame
        :param gfile: path to Google Spreadsheet or gspread ID
        :param wks_name: worksheet name
        :param chunk_size: size of chunk to upload
        :param col_names: assing top row to column names for Pandas DataFrame
        :param row_names: assing left column to row names for Pandas DataFrame
        :param clean: clean all data in worksheet before uploading 
        :param credentials: provide own credentials
        :param df_size: 
            -If True and worksheet name does NOT exist, will create 
            a new worksheet that is the size of the df; otherwise, by default, 
            creates sheet of 1000x100 cells. 
            -If True and worksheet does exist, will resize larger or smaller to 
            fit new dataframe. 
            -If False and dataframe is larger than existing sheet, will resize 
            the sheet larger.
            -If False and dataframe is smaller than existing sheet, does not resize.
        :param new_sheet_dimensions: tuple of (row, cols) for size of a new sheet
        :type df: class 'pandas.core.frame.DataFrame'
        :type gfile: str
        :type wks_name: str
        :type chunk_size: int
        :type col_names: bool
        :type row_names: bool
        :type clean: bool
        :type credentials: class 'oauth2client.client.OAuth2Credentials'
        :type df_size: bool
        :type df_size: tuple
        :returns: gspread Worksheet
        :rtype: class 'gspread.models.Worksheet'

        :Example:

            >>> from df2gspread import df2gspread as d2g
            >>> import pandas as pd
            >>> df = pd.DataFrame([1 2 3])
            >>> wks = d2g.upload(df, wks_name='Example worksheet')
            >>> wks.title
            'Example worksheet'
    '''
    # access credentials
    credentials = get_credentials(credentials)
    # auth for gspread
    gc = gspread.authorize(credentials)

    try:
        # if gfile is file_id
        gc.open_by_key(gfile)
        gfile_id = gfile
    except Exception:
        # else look for file_id in drive
        gfile_id = get_file_id(credentials, gfile, write_access=True)

    # Tuple of rows, cols in the dataframe.
    # If user did not explicitly specify to resize sheet to dataframe size
    # then for new sheets set it to new_sheet_dimensions, which is by default 1000x100
    if df_size:
        new_sheet_dimensions = (len(df), len(df.columns))
    else:
        new_sheet_dimensions = new_sheet_dimensions

    wks = get_worksheet(gc, gfile_id, wks_name, write_access=True, 
        new_sheet_dimensions=new_sheet_dimensions)
    if clean:
        wks = clean_worksheet(wks, gfile_id, wks_name, credentials)

    # find last index and column name (A B ... Z AA AB ... AZ BA)
    last_idx = len(df.index) if col_names else len(df.index) - 1

    seq_num = len(df.columns) if row_names else len(df.columns) - 1
    last_col = ''
    while seq_num >= 0:
        last_col = ascii_uppercase[seq_num % len(ascii_uppercase)] + last_col
        seq_num = seq_num // len(ascii_uppercase) - 1

    # If user requested to resize sheet to fit dataframe, go ahead and 
    # resize larger or smaller to better match new size of pandas dataframe.
    # Otherwise, leave it the same size unless the sheet needs to be expanded
    # to accomodate a larger dataframe.
    extra_col = 1 if col_names else 0
    extra_row = 1 if row_names else 0
    if df_size:
        wks.resize(rows=len(df.index) + extra_row, cols=len(df.columns) + extra_col)
    if len(df.index) + extra_row > wks.row_count:
        wks.add_rows(len(df.index) - wks.row_count + extra_row)
    if len(df.columns) + extra_col > wks.col_count:
        wks.add_cols(len(df.columns) - wks.col_count + extra_col)

    # Define first cell for rows and columns
    first_col = 'B1' if row_names else 'A1'
    first_row = 'A2' if col_names else 'A1'

    # Addition of col names
    if col_names:
        cell_list = wks.range('%s:%s1' % (first_col, last_col))
        for idx, cell in enumerate(cell_list):
            cell.value = df.columns.values[idx]
        wks.update_cells(cell_list)

    # Addition of row names
    if row_names:
        cell_list = wks.range('%s:A%d' % (first_row, last_idx + 1))
        for idx, cell in enumerate(cell_list):
            cell.value = df.index[idx]
        wks.update_cells(cell_list)

    # Addition of cell values
    cell_list = wks.range('%s%s:%s%d' % (
        first_col[0], first_row[1], last_col, last_idx + 1))
    for j, idx in enumerate(df.index):
        for i, col in enumerate(df.columns.values):
            cell_list[i + j * len(df.columns.values)].value = df[col][idx]
    for cells in grouper(chunk_size, cell_list):
        wks.update_cells(list(cells))

    return wks


def grouper(n, iterable):
    it = iter(iterable)
    while True:
        chunk = tuple(islice(it, n))
        if not chunk:
            return
        yield chunk


def clean_worksheet(wks, gfile_id, wks_name, credentials):
    """DOCS..."""

    values = wks.get_all_values()
    if values:
        df_ = pd.DataFrame(index=range(len(values)),
                           columns=range(len(values[0])))
        df_ = df_.fillna('')
        wks = upload(df_, gfile_id, wks_name=wks_name,
                     col_names=False, row_names=False, clean=False,
                     credentials=credentials)
    return wks
