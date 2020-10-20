#!/usr/bin/env python
# -*- coding: latin-1 -*-
# ****************************************************************************
# * Software: FPDF for python                                                *
# * Version:  2.0.5                                                          *
# * Date:     2010-09-10                                                     *
# * Last update: 2018-11-13                                                  *
# * License:  LGPL v3.0                                                      *
# *                                                                          *
# * Original Author (PHP):  Olivier PLATHEY 2004-12-31                       *
# * Ported to Python 2.4 by Max (maxpat78@yahoo.it) on 2006-05               *
# * Maintainer of FPDF in this single file:Elumalai  (enataraj@cisco.com     *
# ****************************************************************************
"""fpdf module (in fpdf package housing FPDF class)

This module contains FPDF class inspiring this library. The version number is
updated here (above and below in variable).
"""
from __future__ import division, with_statement

# from future.utils import raise_from
import errno
import math
import os
import re
import struct
import sys
import tempfile
import zlib
from collections import OrderedDict as o_dict
from datetime import datetime
from functools import wraps

PY3K = sys.version_info >= (3, 0)

#RR from PIL import Image
from hashlib import md5  # python <2.6 not supported
from io import BytesIO  # python <2.6 not supported

import pickle
try:
  import cPickle as pickle
except ImportError as e:
  pass

from struct import pack, unpack, unpack_from
import warnings


''' #RR
from image_parsing import (
    get_img_info, load_resource as image_parsing_load_resource
)
'''

# Global variables
FPDF_VERSION = '2.0.1'
#FPDF_FONT_DIR = os.path.join(os.path.dirname(__file__), 'font')
FPDF_FONT_DIR = None
FPDF_CACHE_MODE = 0  # 0 - in same folder, 1 - none, 2 - hash
FPDF_CACHE_DIR = None
SYSTEM_TTFONTS = None

PAGE_FORMATS = {
  "a3"     : (841.89, 1190.55),
  "a4"     : (595.28, 841.89),
  "a5"     : (420.94, 595.28),
  "letter" : (612, 792),
  "legal"  : (612, 1008),
}

#### from util.syntax.py

py3k = sys.version_info >= (3, 0)

#def create_name(name):
def pdf_name(name):
  if name.startswith('/'):
    name = name[1:]
  return ''.join(['/', name[0].upper(), name[1:]])

def clear_empty_fields(d):
  return o_dict((k, v) for k, v in d.items() if v)

#def create_dictionary_string(dict_, open_dict='<<', close_dict='>>',
#    field_join='\n', key_value_join=' ', has_empty_fields=False):
def pdf_d(dict_, open_dict='<<', close_dict='>>',
          field_join='\n', key_value_join=' ', has_empty_fields=False):
  """format ordered dictionary as PDF dictionary

  @param dict_: dictionary of values to render
  @param open: string to open PDF dictionary
  @param close: string to close PDF dictionary
  @param field_join: string to join fields with
  @param key_value_join: string to join key to value with
  @param has_empty_fields: whether or not to clear_empty_fields first.
  """
  if has_empty_fields:
    dict_ = clear_empty_fields(dict_)

  return ''.join([
    open_dict,
    field_join.join([key_value_join.join(f) for f in dict_.items()]),
    close_dict
  ])

#def create_list_string(list_):
def pdf_l(list_):
  """format list of strings as PDF array"""
  return '[' + ' '.join(list_) + ']'

#def iobj_ref(n):
def pdf_ref(n):
  """format an indirect PDF Object reference from its id number"""
  return str(n) + ' 0 R'

#def create_stream(stream):
def pdf_stream(stream):
  if py3k and bytes == type(stream):
    stream = str(stream, 'latin-1')
  return '\n'.join(['stream', stream, 'endstream'])


### from util
#def freadint(f):
def read_integer(f):
  "Read a 4-byte integer from file"
  try:
    return struct.unpack('>I', f.read(4))[0]
  except:
    return None

#def textstring(s):
def enclose_in_parens(s):
  "Format a text string"
  if s:
    return '(' + escape(s) + ')'
  else:
    return ''

def escape(s):
  "Add \ before \, ( and )"
  return s.replace('\\', '\\\\') \
    .replace(')', '\\)') \
    .replace('(', '\\(') \
    .replace('\r', '\\r')

def escape_parens(s):
  "Add \ before \, ( and )"
  return s.replace('\\', '\\\\') \
    .replace(')', '\\)') \
    .replace('(', '\\(') \
    .replace('\r', '\\r')
### From errors.py
def fpdf_error(message):
  raise RuntimeError('FPDF error: ' + message)

class FPDFException(Exception):
  pass

class FPDFPageFormatException(FPDFException):
  # """Error is thrown when a bad page format is given"""
  def __init__(self, argument, unknown=False, one=False):
    super(FPDFPageFormatException, self).__init__()

    if unknown and one:
      raise TypeError('FPDF Page Format Exception cannot be both for '
                      'unknown type and for wrong number of arguments')

    self.argument = argument
    self.unknown = unknown
    self.one = one

  def _f(self, message):
    return 'FPDFPageFormatException: ' + message

  def format_unknown(self, argument):
    return self._f("Unknown page format: " + argument)

  def format_one(self, a):
    return self._f('Only one argument given: %s. Need (height,width)' % a)

  def __repr__(self):
    inputs = [self.argument, self.unknown, self.one]
    arguments = ', '.join(list(map(lambda x: repr(x), inputs)))
    return ''.join(['FPDFPageFormatException(', arguments, ')'])

  def __str__(self):
    if self.unknown:
      return self.format_unknown(self.argument)
    elif self.one:
      return self.format_one(self.argument)
    else:
      return self._f(self.argument)

#### From fonts.py
# Fonts:
fpdf_charwidths = {}

fpdf_charwidths['courier'] = {}

for i in range(0,256):
  fpdf_charwidths['courier'][chr(i)] = 600
  fpdf_charwidths['courierB']        = fpdf_charwidths['courier']
  fpdf_charwidths['courierI']        = fpdf_charwidths['courier']
  fpdf_charwidths['courierBI']       = fpdf_charwidths['courier']

fpdf_charwidths['helvetica']={
  '\x00':278,'\x01':278,'\x02':278,'\x03':278,'\x04':278,'\x05':278,'\x06':278,'\x07':278,'\x08':278,'\t':278,'\n':278,'\x0b':278,'\x0c':278,'\r':278,'\x0e':278,'\x0f':278,'\x10':278,'\x11':278,'\x12':278,'\x13':278,'\x14':278,'\x15':278,
  '\x16':278,'\x17':278,'\x18':278,'\x19':278,'\x1a':278,'\x1b':278,'\x1c':278,'\x1d':278,'\x1e':278,'\x1f':278,' ':278,'!':278,'"':355,'#':556,'$':556,'%':889,'&':667,'\'':191,'(':333,')':333,'*':389,'+':584,
  ',':278,'-':333,'.':278,'/':278,'0':556,'1':556,'2':556,'3':556,'4':556,'5':556,'6':556,'7':556,'8':556,'9':556,':':278,';':278,'<':584,'=':584,'>':584,'?':556,'@':1015,'A':667,
  'B':667,'C':722,'D':722,'E':667,'F':611,'G':778,'H':722,'I':278,'J':500,'K':667,'L':556,'M':833,'N':722,'O':778,'P':667,'Q':778,'R':722,'S':667,'T':611,'U':722,'V':667,'W':944,
  'X':667,'Y':667,'Z':611,'[':278,'\\':278,']':278,'^':469,'_':556,'`':333,'a':556,'b':556,'c':500,'d':556,'e':556,'f':278,'g':556,'h':556,'i':222,'j':222,'k':500,'l':222,'m':833,
  'n':556,'o':556,'p':556,'q':556,'r':333,'s':500,'t':278,'u':556,'v':500,'w':722,'x':500,'y':500,'z':500,'{':334,'|':260,'}':334,'~':584,'\x7f':350,'\x80':556,'\x81':350,'\x82':222,'\x83':556,
  '\x84':333,'\x85':1000,'\x86':556,'\x87':556,'\x88':333,'\x89':1000,'\x8a':667,'\x8b':333,'\x8c':1000,'\x8d':350,'\x8e':611,'\x8f':350,'\x90':350,'\x91':222,'\x92':222,'\x93':333,'\x94':333,'\x95':350,'\x96':556,'\x97':1000,'\x98':333,'\x99':1000,
  '\x9a':500,'\x9b':333,'\x9c':944,'\x9d':350,'\x9e':500,'\x9f':667,'\xa0':278,'\xa1':333,'\xa2':556,'\xa3':556,'\xa4':556,'\xa5':556,'\xa6':260,'\xa7':556,'\xa8':333,'\xa9':737,'\xaa':370,'\xab':556,'\xac':584,'\xad':333,'\xae':737,'\xaf':333,
  '\xb0':400,'\xb1':584,'\xb2':333,'\xb3':333,'\xb4':333,'\xb5':556,'\xb6':537,'\xb7':278,'\xb8':333,'\xb9':333,'\xba':365,'\xbb':556,'\xbc':834,'\xbd':834,'\xbe':834,'\xbf':611,'\xc0':667,'\xc1':667,'\xc2':667,'\xc3':667,'\xc4':667,'\xc5':667,
  '\xc6':1000,'\xc7':722,'\xc8':667,'\xc9':667,'\xca':667,'\xcb':667,'\xcc':278,'\xcd':278,'\xce':278,'\xcf':278,'\xd0':722,'\xd1':722,'\xd2':778,'\xd3':778,'\xd4':778,'\xd5':778,'\xd6':778,'\xd7':584,'\xd8':778,'\xd9':722,'\xda':722,'\xdb':722,
  '\xdc':722,'\xdd':667,'\xde':667,'\xdf':611,'\xe0':556,'\xe1':556,'\xe2':556,'\xe3':556,'\xe4':556,'\xe5':556,'\xe6':889,'\xe7':500,'\xe8':556,'\xe9':556,'\xea':556,'\xeb':556,'\xec':278,'\xed':278,'\xee':278,'\xef':278,'\xf0':556,'\xf1':556,
  '\xf2':556,'\xf3':556,'\xf4':556,'\xf5':556,'\xf6':556,'\xf7':584,'\xf8':611,'\xf9':556,'\xfa':556,'\xfb':556,'\xfc':556,'\xfd':500,'\xfe':556,'\xff':500}

fpdf_charwidths['helveticaB']={
  '\x00':278,'\x01':278,'\x02':278,'\x03':278,'\x04':278,'\x05':278,'\x06':278,'\x07':278,'\x08':278,'\t':278,'\n':278,'\x0b':278,'\x0c':278,'\r':278,'\x0e':278,'\x0f':278,'\x10':278,'\x11':278,'\x12':278,'\x13':278,'\x14':278,'\x15':278,
  '\x16':278,'\x17':278,'\x18':278,'\x19':278,'\x1a':278,'\x1b':278,'\x1c':278,'\x1d':278,'\x1e':278,'\x1f':278,' ':278,'!':333,'"':474,'#':556,'$':556,'%':889,'&':722,'\'':238,'(':333,')':333,'*':389,'+':584,
  ',':278,'-':333,'.':278,'/':278,'0':556,'1':556,'2':556,'3':556,'4':556,'5':556,'6':556,'7':556,'8':556,'9':556,':':333,';':333,'<':584,'=':584,'>':584,'?':611,'@':975,'A':722,
  'B':722,'C':722,'D':722,'E':667,'F':611,'G':778,'H':722,'I':278,'J':556,'K':722,'L':611,'M':833,'N':722,'O':778,'P':667,'Q':778,'R':722,'S':667,'T':611,'U':722,'V':667,'W':944,
  'X':667,'Y':667,'Z':611,'[':333,'\\':278,']':333,'^':584,'_':556,'`':333,'a':556,'b':611,'c':556,'d':611,'e':556,'f':333,'g':611,'h':611,'i':278,'j':278,'k':556,'l':278,'m':889,
  'n':611,'o':611,'p':611,'q':611,'r':389,'s':556,'t':333,'u':611,'v':556,'w':778,'x':556,'y':556,'z':500,'{':389,'|':280,'}':389,'~':584,'\x7f':350,'\x80':556,'\x81':350,'\x82':278,'\x83':556,
  '\x84':500,'\x85':1000,'\x86':556,'\x87':556,'\x88':333,'\x89':1000,'\x8a':667,'\x8b':333,'\x8c':1000,'\x8d':350,'\x8e':611,'\x8f':350,'\x90':350,'\x91':278,'\x92':278,'\x93':500,'\x94':500,'\x95':350,'\x96':556,'\x97':1000,'\x98':333,'\x99':1000,
  '\x9a':556,'\x9b':333,'\x9c':944,'\x9d':350,'\x9e':500,'\x9f':667,'\xa0':278,'\xa1':333,'\xa2':556,'\xa3':556,'\xa4':556,'\xa5':556,'\xa6':280,'\xa7':556,'\xa8':333,'\xa9':737,'\xaa':370,'\xab':556,'\xac':584,'\xad':333,'\xae':737,'\xaf':333,
  '\xb0':400,'\xb1':584,'\xb2':333,'\xb3':333,'\xb4':333,'\xb5':611,'\xb6':556,'\xb7':278,'\xb8':333,'\xb9':333,'\xba':365,'\xbb':556,'\xbc':834,'\xbd':834,'\xbe':834,'\xbf':611,'\xc0':722,'\xc1':722,'\xc2':722,'\xc3':722,'\xc4':722,'\xc5':722,
  '\xc6':1000,'\xc7':722,'\xc8':667,'\xc9':667,'\xca':667,'\xcb':667,'\xcc':278,'\xcd':278,'\xce':278,'\xcf':278,'\xd0':722,'\xd1':722,'\xd2':778,'\xd3':778,'\xd4':778,'\xd5':778,'\xd6':778,'\xd7':584,'\xd8':778,'\xd9':722,'\xda':722,'\xdb':722,
  '\xdc':722,'\xdd':667,'\xde':667,'\xdf':611,'\xe0':556,'\xe1':556,'\xe2':556,'\xe3':556,'\xe4':556,'\xe5':556,'\xe6':889,'\xe7':556,'\xe8':556,'\xe9':556,'\xea':556,'\xeb':556,'\xec':278,'\xed':278,'\xee':278,'\xef':278,'\xf0':611,'\xf1':611,
  '\xf2':611,'\xf3':611,'\xf4':611,'\xf5':611,'\xf6':611,'\xf7':584,'\xf8':611,'\xf9':611,'\xfa':611,'\xfb':611,'\xfc':611,'\xfd':556,'\xfe':611,'\xff':556
}

fpdf_charwidths['helveticaBI']={
  '\x00':278,'\x01':278,'\x02':278,'\x03':278,'\x04':278,'\x05':278,'\x06':278,'\x07':278,'\x08':278,'\t':278,'\n':278,'\x0b':278,'\x0c':278,'\r':278,'\x0e':278,'\x0f':278,'\x10':278,'\x11':278,'\x12':278,'\x13':278,'\x14':278,'\x15':278,
  '\x16':278,'\x17':278,'\x18':278,'\x19':278,'\x1a':278,'\x1b':278,'\x1c':278,'\x1d':278,'\x1e':278,'\x1f':278,' ':278,'!':333,'"':474,'#':556,'$':556,'%':889,'&':722,'\'':238,'(':333,')':333,'*':389,'+':584,
  ',':278,'-':333,'.':278,'/':278,'0':556,'1':556,'2':556,'3':556,'4':556,'5':556,'6':556,'7':556,'8':556,'9':556,':':333,';':333,'<':584,'=':584,'>':584,'?':611,'@':975,'A':722,
  'B':722,'C':722,'D':722,'E':667,'F':611,'G':778,'H':722,'I':278,'J':556,'K':722,'L':611,'M':833,'N':722,'O':778,'P':667,'Q':778,'R':722,'S':667,'T':611,'U':722,'V':667,'W':944,
  'X':667,'Y':667,'Z':611,'[':333,'\\':278,']':333,'^':584,'_':556,'`':333,'a':556,'b':611,'c':556,'d':611,'e':556,'f':333,'g':611,'h':611,'i':278,'j':278,'k':556,'l':278,'m':889,
  'n':611,'o':611,'p':611,'q':611,'r':389,'s':556,'t':333,'u':611,'v':556,'w':778,'x':556,'y':556,'z':500,'{':389,'|':280,'}':389,'~':584,'\x7f':350,'\x80':556,'\x81':350,'\x82':278,'\x83':556,
  '\x84':500,'\x85':1000,'\x86':556,'\x87':556,'\x88':333,'\x89':1000,'\x8a':667,'\x8b':333,'\x8c':1000,'\x8d':350,'\x8e':611,'\x8f':350,'\x90':350,'\x91':278,'\x92':278,'\x93':500,'\x94':500,'\x95':350,'\x96':556,'\x97':1000,'\x98':333,'\x99':1000,
  '\x9a':556,'\x9b':333,'\x9c':944,'\x9d':350,'\x9e':500,'\x9f':667,'\xa0':278,'\xa1':333,'\xa2':556,'\xa3':556,'\xa4':556,'\xa5':556,'\xa6':280,'\xa7':556,'\xa8':333,'\xa9':737,'\xaa':370,'\xab':556,'\xac':584,'\xad':333,'\xae':737,'\xaf':333,
  '\xb0':400,'\xb1':584,'\xb2':333,'\xb3':333,'\xb4':333,'\xb5':611,'\xb6':556,'\xb7':278,'\xb8':333,'\xb9':333,'\xba':365,'\xbb':556,'\xbc':834,'\xbd':834,'\xbe':834,'\xbf':611,'\xc0':722,'\xc1':722,'\xc2':722,'\xc3':722,'\xc4':722,'\xc5':722,
  '\xc6':1000,'\xc7':722,'\xc8':667,'\xc9':667,'\xca':667,'\xcb':667,'\xcc':278,'\xcd':278,'\xce':278,'\xcf':278,'\xd0':722,'\xd1':722,'\xd2':778,'\xd3':778,'\xd4':778,'\xd5':778,'\xd6':778,'\xd7':584,'\xd8':778,'\xd9':722,'\xda':722,'\xdb':722,
  '\xdc':722,'\xdd':667,'\xde':667,'\xdf':611,'\xe0':556,'\xe1':556,'\xe2':556,'\xe3':556,'\xe4':556,'\xe5':556,'\xe6':889,'\xe7':556,'\xe8':556,'\xe9':556,'\xea':556,'\xeb':556,'\xec':278,'\xed':278,'\xee':278,'\xef':278,'\xf0':611,'\xf1':611,
  '\xf2':611,'\xf3':611,'\xf4':611,'\xf5':611,'\xf6':611,'\xf7':584,'\xf8':611,'\xf9':611,'\xfa':611,'\xfb':611,'\xfc':611,'\xfd':556,'\xfe':611,'\xff':556}

fpdf_charwidths['helveticaI']={
  '\x00':278,'\x01':278,'\x02':278,'\x03':278,'\x04':278,'\x05':278,'\x06':278,'\x07':278,'\x08':278,'\t':278,'\n':278,'\x0b':278,'\x0c':278,'\r':278,'\x0e':278,'\x0f':278,'\x10':278,'\x11':278,'\x12':278,'\x13':278,'\x14':278,'\x15':278,
  '\x16':278,'\x17':278,'\x18':278,'\x19':278,'\x1a':278,'\x1b':278,'\x1c':278,'\x1d':278,'\x1e':278,'\x1f':278,' ':278,'!':278,'"':355,'#':556,'$':556,'%':889,'&':667,'\'':191,'(':333,')':333,'*':389,'+':584,
  ',':278,'-':333,'.':278,'/':278,'0':556,'1':556,'2':556,'3':556,'4':556,'5':556,'6':556,'7':556,'8':556,'9':556,':':278,';':278,'<':584,'=':584,'>':584,'?':556,'@':1015,'A':667,
  'B':667,'C':722,'D':722,'E':667,'F':611,'G':778,'H':722,'I':278,'J':500,'K':667,'L':556,'M':833,'N':722,'O':778,'P':667,'Q':778,'R':722,'S':667,'T':611,'U':722,'V':667,'W':944,
  'X':667,'Y':667,'Z':611,'[':278,'\\':278,']':278,'^':469,'_':556,'`':333,'a':556,'b':556,'c':500,'d':556,'e':556,'f':278,'g':556,'h':556,'i':222,'j':222,'k':500,'l':222,'m':833,
  'n':556,'o':556,'p':556,'q':556,'r':333,'s':500,'t':278,'u':556,'v':500,'w':722,'x':500,'y':500,'z':500,'{':334,'|':260,'}':334,'~':584,'\x7f':350,'\x80':556,'\x81':350,'\x82':222,'\x83':556,
  '\x84':333,'\x85':1000,'\x86':556,'\x87':556,'\x88':333,'\x89':1000,'\x8a':667,'\x8b':333,'\x8c':1000,'\x8d':350,'\x8e':611,'\x8f':350,'\x90':350,'\x91':222,'\x92':222,'\x93':333,'\x94':333,'\x95':350,'\x96':556,'\x97':1000,'\x98':333,'\x99':1000,
  '\x9a':500,'\x9b':333,'\x9c':944,'\x9d':350,'\x9e':500,'\x9f':667,'\xa0':278,'\xa1':333,'\xa2':556,'\xa3':556,'\xa4':556,'\xa5':556,'\xa6':260,'\xa7':556,'\xa8':333,'\xa9':737,'\xaa':370,'\xab':556,'\xac':584,'\xad':333,'\xae':737,'\xaf':333,
  '\xb0':400,'\xb1':584,'\xb2':333,'\xb3':333,'\xb4':333,'\xb5':556,'\xb6':537,'\xb7':278,'\xb8':333,'\xb9':333,'\xba':365,'\xbb':556,'\xbc':834,'\xbd':834,'\xbe':834,'\xbf':611,'\xc0':667,'\xc1':667,'\xc2':667,'\xc3':667,'\xc4':667,'\xc5':667,
  '\xc6':1000,'\xc7':722,'\xc8':667,'\xc9':667,'\xca':667,'\xcb':667,'\xcc':278,'\xcd':278,'\xce':278,'\xcf':278,'\xd0':722,'\xd1':722,'\xd2':778,'\xd3':778,'\xd4':778,'\xd5':778,'\xd6':778,'\xd7':584,'\xd8':778,'\xd9':722,'\xda':722,'\xdb':722,
  '\xdc':722,'\xdd':667,'\xde':667,'\xdf':611,'\xe0':556,'\xe1':556,'\xe2':556,'\xe3':556,'\xe4':556,'\xe5':556,'\xe6':889,'\xe7':500,'\xe8':556,'\xe9':556,'\xea':556,'\xeb':556,'\xec':278,'\xed':278,'\xee':278,'\xef':278,'\xf0':556,'\xf1':556,
  '\xf2':556,'\xf3':556,'\xf4':556,'\xf5':556,'\xf6':556,'\xf7':584,'\xf8':611,'\xf9':556,'\xfa':556,'\xfb':556,'\xfc':556,'\xfd':500,'\xfe':556,'\xff':500}

fpdf_charwidths['symbol']={
  '\x00':250,'\x01':250,'\x02':250,'\x03':250,'\x04':250,'\x05':250,'\x06':250,'\x07':250,'\x08':250,'\t':250,'\n':250,'\x0b':250,'\x0c':250,'\r':250,'\x0e':250,'\x0f':250,'\x10':250,'\x11':250,'\x12':250,'\x13':250,'\x14':250,'\x15':250,
  '\x16':250,'\x17':250,'\x18':250,'\x19':250,'\x1a':250,'\x1b':250,'\x1c':250,'\x1d':250,'\x1e':250,'\x1f':250,' ':250,'!':333,'"':713,'#':500,'$':549,'%':833,'&':778,'\'':439,'(':333,')':333,'*':500,'+':549,
  ',':250,'-':549,'.':250,'/':278,'0':500,'1':500,'2':500,'3':500,'4':500,'5':500,'6':500,'7':500,'8':500,'9':500,':':278,';':278,'<':549,'=':549,'>':549,'?':444,'@':549,'A':722,
  'B':667,'C':722,'D':612,'E':611,'F':763,'G':603,'H':722,'I':333,'J':631,'K':722,'L':686,'M':889,'N':722,'O':722,'P':768,'Q':741,'R':556,'S':592,'T':611,'U':690,'V':439,'W':768,
  'X':645,'Y':795,'Z':611,'[':333,'\\':863,']':333,'^':658,'_':500,'`':500,'a':631,'b':549,'c':549,'d':494,'e':439,'f':521,'g':411,'h':603,'i':329,'j':603,'k':549,'l':549,'m':576,
  'n':521,'o':549,'p':549,'q':521,'r':549,'s':603,'t':439,'u':576,'v':713,'w':686,'x':493,'y':686,'z':494,'{':480,'|':200,'}':480,'~':549,'\x7f':0,'\x80':0,'\x81':0,'\x82':0,'\x83':0,
  '\x84':0,'\x85':0,'\x86':0,'\x87':0,'\x88':0,'\x89':0,'\x8a':0,'\x8b':0,'\x8c':0,'\x8d':0,'\x8e':0,'\x8f':0,'\x90':0,'\x91':0,'\x92':0,'\x93':0,'\x94':0,'\x95':0,'\x96':0,'\x97':0,'\x98':0,'\x99':0,
  '\x9a':0,'\x9b':0,'\x9c':0,'\x9d':0,'\x9e':0,'\x9f':0,'\xa0':750,'\xa1':620,'\xa2':247,'\xa3':549,'\xa4':167,'\xa5':713,'\xa6':500,'\xa7':753,'\xa8':753,'\xa9':753,'\xaa':753,'\xab':1042,'\xac':987,'\xad':603,'\xae':987,'\xaf':603,
  '\xb0':400,'\xb1':549,'\xb2':411,'\xb3':549,'\xb4':549,'\xb5':713,'\xb6':494,'\xb7':460,'\xb8':549,'\xb9':549,'\xba':549,'\xbb':549,'\xbc':1000,'\xbd':603,'\xbe':1000,'\xbf':658,'\xc0':823,'\xc1':686,'\xc2':795,'\xc3':987,'\xc4':768,'\xc5':768,
  '\xc6':823,'\xc7':768,'\xc8':768,'\xc9':713,'\xca':713,'\xcb':713,'\xcc':713,'\xcd':713,'\xce':713,'\xcf':713,'\xd0':768,'\xd1':713,'\xd2':790,'\xd3':790,'\xd4':890,'\xd5':823,'\xd6':549,'\xd7':250,'\xd8':713,'\xd9':603,'\xda':603,'\xdb':1042,
  '\xdc':987,'\xdd':603,'\xde':987,'\xdf':603,'\xe0':494,'\xe1':329,'\xe2':790,'\xe3':790,'\xe4':786,'\xe5':713,'\xe6':384,'\xe7':384,'\xe8':384,'\xe9':384,'\xea':384,'\xeb':384,'\xec':494,'\xed':494,'\xee':494,'\xef':494,'\xf0':0,'\xf1':329,
  '\xf2':274,'\xf3':686,'\xf4':686,'\xf5':686,'\xf6':384,'\xf7':384,'\xf8':384,'\xf9':384,'\xfa':384,'\xfb':384,'\xfc':494,'\xfd':494,'\xfe':494,'\xff':0}

fpdf_charwidths['times']={
  '\x00':250,'\x01':250,'\x02':250,'\x03':250,'\x04':250,'\x05':250,'\x06':250,'\x07':250,'\x08':250,'\t':250,'\n':250,'\x0b':250,'\x0c':250,'\r':250,'\x0e':250,'\x0f':250,'\x10':250,'\x11':250,'\x12':250,'\x13':250,'\x14':250,'\x15':250,
  '\x16':250,'\x17':250,'\x18':250,'\x19':250,'\x1a':250,'\x1b':250,'\x1c':250,'\x1d':250,'\x1e':250,'\x1f':250,' ':250,'!':333,'"':408,'#':500,'$':500,'%':833,'&':778,'\'':180,'(':333,')':333,'*':500,'+':564,
  ',':250,'-':333,'.':250,'/':278,'0':500,'1':500,'2':500,'3':500,'4':500,'5':500,'6':500,'7':500,'8':500,'9':500,':':278,';':278,'<':564,'=':564,'>':564,'?':444,'@':921,'A':722,
  'B':667,'C':667,'D':722,'E':611,'F':556,'G':722,'H':722,'I':333,'J':389,'K':722,'L':611,'M':889,'N':722,'O':722,'P':556,'Q':722,'R':667,'S':556,'T':611,'U':722,'V':722,'W':944,
  'X':722,'Y':722,'Z':611,'[':333,'\\':278,']':333,'^':469,'_':500,'`':333,'a':444,'b':500,'c':444,'d':500,'e':444,'f':333,'g':500,'h':500,'i':278,'j':278,'k':500,'l':278,'m':778,
  'n':500,'o':500,'p':500,'q':500,'r':333,'s':389,'t':278,'u':500,'v':500,'w':722,'x':500,'y':500,'z':444,'{':480,'|':200,'}':480,'~':541,'\x7f':350,'\x80':500,'\x81':350,'\x82':333,'\x83':500,
  '\x84':444,'\x85':1000,'\x86':500,'\x87':500,'\x88':333,'\x89':1000,'\x8a':556,'\x8b':333,'\x8c':889,'\x8d':350,'\x8e':611,'\x8f':350,'\x90':350,'\x91':333,'\x92':333,'\x93':444,'\x94':444,'\x95':350,'\x96':500,'\x97':1000,'\x98':333,'\x99':980,
  '\x9a':389,'\x9b':333,'\x9c':722,'\x9d':350,'\x9e':444,'\x9f':722,'\xa0':250,'\xa1':333,'\xa2':500,'\xa3':500,'\xa4':500,'\xa5':500,'\xa6':200,'\xa7':500,'\xa8':333,'\xa9':760,'\xaa':276,'\xab':500,'\xac':564,'\xad':333,'\xae':760,'\xaf':333,
  '\xb0':400,'\xb1':564,'\xb2':300,'\xb3':300,'\xb4':333,'\xb5':500,'\xb6':453,'\xb7':250,'\xb8':333,'\xb9':300,'\xba':310,'\xbb':500,'\xbc':750,'\xbd':750,'\xbe':750,'\xbf':444,'\xc0':722,'\xc1':722,'\xc2':722,'\xc3':722,'\xc4':722,'\xc5':722,
  '\xc6':889,'\xc7':667,'\xc8':611,'\xc9':611,'\xca':611,'\xcb':611,'\xcc':333,'\xcd':333,'\xce':333,'\xcf':333,'\xd0':722,'\xd1':722,'\xd2':722,'\xd3':722,'\xd4':722,'\xd5':722,'\xd6':722,'\xd7':564,'\xd8':722,'\xd9':722,'\xda':722,'\xdb':722,
  '\xdc':722,'\xdd':722,'\xde':556,'\xdf':500,'\xe0':444,'\xe1':444,'\xe2':444,'\xe3':444,'\xe4':444,'\xe5':444,'\xe6':667,'\xe7':444,'\xe8':444,'\xe9':444,'\xea':444,'\xeb':444,'\xec':278,'\xed':278,'\xee':278,'\xef':278,'\xf0':500,'\xf1':500,
  '\xf2':500,'\xf3':500,'\xf4':500,'\xf5':500,'\xf6':500,'\xf7':564,'\xf8':500,'\xf9':500,'\xfa':500,'\xfb':500,'\xfc':500,'\xfd':500,'\xfe':500,'\xff':500}

fpdf_charwidths['timesB']={
  '\x00':250,'\x01':250,'\x02':250,'\x03':250,'\x04':250,'\x05':250,'\x06':250,'\x07':250,'\x08':250,'\t':250,'\n':250,'\x0b':250,'\x0c':250,'\r':250,'\x0e':250,'\x0f':250,'\x10':250,'\x11':250,'\x12':250,'\x13':250,'\x14':250,'\x15':250,
  '\x16':250,'\x17':250,'\x18':250,'\x19':250,'\x1a':250,'\x1b':250,'\x1c':250,'\x1d':250,'\x1e':250,'\x1f':250,' ':250,'!':333,'"':555,'#':500,'$':500,'%':1000,'&':833,'\'':278,'(':333,')':333,'*':500,'+':570,
  ',':250,'-':333,'.':250,'/':278,'0':500,'1':500,'2':500,'3':500,'4':500,'5':500,'6':500,'7':500,'8':500,'9':500,':':333,';':333,'<':570,'=':570,'>':570,'?':500,'@':930,'A':722,
  'B':667,'C':722,'D':722,'E':667,'F':611,'G':778,'H':778,'I':389,'J':500,'K':778,'L':667,'M':944,'N':722,'O':778,'P':611,'Q':778,'R':722,'S':556,'T':667,'U':722,'V':722,'W':1000,
  'X':722,'Y':722,'Z':667,'[':333,'\\':278,']':333,'^':581,'_':500,'`':333,'a':500,'b':556,'c':444,'d':556,'e':444,'f':333,'g':500,'h':556,'i':278,'j':333,'k':556,'l':278,'m':833,
  'n':556,'o':500,'p':556,'q':556,'r':444,'s':389,'t':333,'u':556,'v':500,'w':722,'x':500,'y':500,'z':444,'{':394,'|':220,'}':394,'~':520,'\x7f':350,'\x80':500,'\x81':350,'\x82':333,'\x83':500,
  '\x84':500,'\x85':1000,'\x86':500,'\x87':500,'\x88':333,'\x89':1000,'\x8a':556,'\x8b':333,'\x8c':1000,'\x8d':350,'\x8e':667,'\x8f':350,'\x90':350,'\x91':333,'\x92':333,'\x93':500,'\x94':500,'\x95':350,'\x96':500,'\x97':1000,'\x98':333,'\x99':1000,
  '\x9a':389,'\x9b':333,'\x9c':722,'\x9d':350,'\x9e':444,'\x9f':722,'\xa0':250,'\xa1':333,'\xa2':500,'\xa3':500,'\xa4':500,'\xa5':500,'\xa6':220,'\xa7':500,'\xa8':333,'\xa9':747,'\xaa':300,'\xab':500,'\xac':570,'\xad':333,'\xae':747,'\xaf':333,
  '\xb0':400,'\xb1':570,'\xb2':300,'\xb3':300,'\xb4':333,'\xb5':556,'\xb6':540,'\xb7':250,'\xb8':333,'\xb9':300,'\xba':330,'\xbb':500,'\xbc':750,'\xbd':750,'\xbe':750,'\xbf':500,'\xc0':722,'\xc1':722,'\xc2':722,'\xc3':722,'\xc4':722,'\xc5':722,
  '\xc6':1000,'\xc7':722,'\xc8':667,'\xc9':667,'\xca':667,'\xcb':667,'\xcc':389,'\xcd':389,'\xce':389,'\xcf':389,'\xd0':722,'\xd1':722,'\xd2':778,'\xd3':778,'\xd4':778,'\xd5':778,'\xd6':778,'\xd7':570,'\xd8':778,'\xd9':722,'\xda':722,'\xdb':722,
  '\xdc':722,'\xdd':722,'\xde':611,'\xdf':556,'\xe0':500,'\xe1':500,'\xe2':500,'\xe3':500,'\xe4':500,'\xe5':500,'\xe6':722,'\xe7':444,'\xe8':444,'\xe9':444,'\xea':444,'\xeb':444,'\xec':278,'\xed':278,'\xee':278,'\xef':278,'\xf0':500,'\xf1':556,
  '\xf2':500,'\xf3':500,'\xf4':500,'\xf5':500,'\xf6':500,'\xf7':570,'\xf8':500,'\xf9':556,'\xfa':556,'\xfb':556,'\xfc':556,'\xfd':500,'\xfe':556,'\xff':500}

fpdf_charwidths['timesBI']={
  '\x00':250,'\x01':250,'\x02':250,'\x03':250,'\x04':250,'\x05':250,'\x06':250,'\x07':250,'\x08':250,'\t':250,'\n':250,'\x0b':250,'\x0c':250,'\r':250,'\x0e':250,'\x0f':250,'\x10':250,'\x11':250,'\x12':250,'\x13':250,'\x14':250,'\x15':250,
  '\x16':250,'\x17':250,'\x18':250,'\x19':250,'\x1a':250,'\x1b':250,'\x1c':250,'\x1d':250,'\x1e':250,'\x1f':250,' ':250,'!':389,'"':555,'#':500,'$':500,'%':833,'&':778,'\'':278,'(':333,')':333,'*':500,'+':570,
  ',':250,'-':333,'.':250,'/':278,'0':500,'1':500,'2':500,'3':500,'4':500,'5':500,'6':500,'7':500,'8':500,'9':500,':':333,';':333,'<':570,'=':570,'>':570,'?':500,'@':832,'A':667,
  'B':667,'C':667,'D':722,'E':667,'F':667,'G':722,'H':778,'I':389,'J':500,'K':667,'L':611,'M':889,'N':722,'O':722,'P':611,'Q':722,'R':667,'S':556,'T':611,'U':722,'V':667,'W':889,
  'X':667,'Y':611,'Z':611,'[':333,'\\':278,']':333,'^':570,'_':500,'`':333,'a':500,'b':500,'c':444,'d':500,'e':444,'f':333,'g':500,'h':556,'i':278,'j':278,'k':500,'l':278,'m':778,
  'n':556,'o':500,'p':500,'q':500,'r':389,'s':389,'t':278,'u':556,'v':444,'w':667,'x':500,'y':444,'z':389,'{':348,'|':220,'}':348,'~':570,'\x7f':350,'\x80':500,'\x81':350,'\x82':333,'\x83':500,
  '\x84':500,'\x85':1000,'\x86':500,'\x87':500,'\x88':333,'\x89':1000,'\x8a':556,'\x8b':333,'\x8c':944,'\x8d':350,'\x8e':611,'\x8f':350,'\x90':350,'\x91':333,'\x92':333,'\x93':500,'\x94':500,'\x95':350,'\x96':500,'\x97':1000,'\x98':333,'\x99':1000,
  '\x9a':389,'\x9b':333,'\x9c':722,'\x9d':350,'\x9e':389,'\x9f':611,'\xa0':250,'\xa1':389,'\xa2':500,'\xa3':500,'\xa4':500,'\xa5':500,'\xa6':220,'\xa7':500,'\xa8':333,'\xa9':747,'\xaa':266,'\xab':500,'\xac':606,'\xad':333,'\xae':747,'\xaf':333,
  '\xb0':400,'\xb1':570,'\xb2':300,'\xb3':300,'\xb4':333,'\xb5':576,'\xb6':500,'\xb7':250,'\xb8':333,'\xb9':300,'\xba':300,'\xbb':500,'\xbc':750,'\xbd':750,'\xbe':750,'\xbf':500,'\xc0':667,'\xc1':667,'\xc2':667,'\xc3':667,'\xc4':667,'\xc5':667,
  '\xc6':944,'\xc7':667,'\xc8':667,'\xc9':667,'\xca':667,'\xcb':667,'\xcc':389,'\xcd':389,'\xce':389,'\xcf':389,'\xd0':722,'\xd1':722,'\xd2':722,'\xd3':722,'\xd4':722,'\xd5':722,'\xd6':722,'\xd7':570,'\xd8':722,'\xd9':722,'\xda':722,'\xdb':722,
  '\xdc':722,'\xdd':611,'\xde':611,'\xdf':500,'\xe0':500,'\xe1':500,'\xe2':500,'\xe3':500,'\xe4':500,'\xe5':500,'\xe6':722,'\xe7':444,'\xe8':444,'\xe9':444,'\xea':444,'\xeb':444,'\xec':278,'\xed':278,'\xee':278,'\xef':278,'\xf0':500,'\xf1':556,
  '\xf2':500,'\xf3':500,'\xf4':500,'\xf5':500,'\xf6':500,'\xf7':570,'\xf8':500,'\xf9':556,'\xfa':556,'\xfb':556,'\xfc':556,'\xfd':444,'\xfe':500,'\xff':444}

fpdf_charwidths['timesI']={
  '\x00':250,'\x01':250,'\x02':250,'\x03':250,'\x04':250,'\x05':250,'\x06':250,'\x07':250,'\x08':250,'\t':250,'\n':250,'\x0b':250,'\x0c':250,'\r':250,'\x0e':250,'\x0f':250,'\x10':250,'\x11':250,'\x12':250,'\x13':250,'\x14':250,'\x15':250,
  '\x16':250,'\x17':250,'\x18':250,'\x19':250,'\x1a':250,'\x1b':250,'\x1c':250,'\x1d':250,'\x1e':250,'\x1f':250,' ':250,'!':333,'"':420,'#':500,'$':500,'%':833,'&':778,'\'':214,'(':333,')':333,'*':500,'+':675,
  ',':250,'-':333,'.':250,'/':278,'0':500,'1':500,'2':500,'3':500,'4':500,'5':500,'6':500,'7':500,'8':500,'9':500,':':333,';':333,'<':675,'=':675,'>':675,'?':500,'@':920,'A':611,
  'B':611,'C':667,'D':722,'E':611,'F':611,'G':722,'H':722,'I':333,'J':444,'K':667,'L':556,'M':833,'N':667,'O':722,'P':611,'Q':722,'R':611,'S':500,'T':556,'U':722,'V':611,'W':833,
  'X':611,'Y':556,'Z':556,'[':389,'\\':278,']':389,'^':422,'_':500,'`':333,'a':500,'b':500,'c':444,'d':500,'e':444,'f':278,'g':500,'h':500,'i':278,'j':278,'k':444,'l':278,'m':722,
  'n':500,'o':500,'p':500,'q':500,'r':389,'s':389,'t':278,'u':500,'v':444,'w':667,'x':444,'y':444,'z':389,'{':400,'|':275,'}':400,'~':541,'\x7f':350,'\x80':500,'\x81':350,'\x82':333,'\x83':500,
  '\x84':556,'\x85':889,'\x86':500,'\x87':500,'\x88':333,'\x89':1000,'\x8a':500,'\x8b':333,'\x8c':944,'\x8d':350,'\x8e':556,'\x8f':350,'\x90':350,'\x91':333,'\x92':333,'\x93':556,'\x94':556,'\x95':350,'\x96':500,'\x97':889,'\x98':333,'\x99':980,
  '\x9a':389,'\x9b':333,'\x9c':667,'\x9d':350,'\x9e':389,'\x9f':556,'\xa0':250,'\xa1':389,'\xa2':500,'\xa3':500,'\xa4':500,'\xa5':500,'\xa6':275,'\xa7':500,'\xa8':333,'\xa9':760,'\xaa':276,'\xab':500,'\xac':675,'\xad':333,'\xae':760,'\xaf':333,
  '\xb0':400,'\xb1':675,'\xb2':300,'\xb3':300,'\xb4':333,'\xb5':500,'\xb6':523,'\xb7':250,'\xb8':333,'\xb9':300,'\xba':310,'\xbb':500,'\xbc':750,'\xbd':750,'\xbe':750,'\xbf':500,'\xc0':611,'\xc1':611,'\xc2':611,'\xc3':611,'\xc4':611,'\xc5':611,
  '\xc6':889,'\xc7':667,'\xc8':611,'\xc9':611,'\xca':611,'\xcb':611,'\xcc':333,'\xcd':333,'\xce':333,'\xcf':333,'\xd0':722,'\xd1':667,'\xd2':722,'\xd3':722,'\xd4':722,'\xd5':722,'\xd6':722,'\xd7':675,'\xd8':722,'\xd9':722,'\xda':722,'\xdb':722,
  '\xdc':722,'\xdd':556,'\xde':611,'\xdf':500,'\xe0':500,'\xe1':500,'\xe2':500,'\xe3':500,'\xe4':500,'\xe5':500,'\xe6':667,'\xe7':444,'\xe8':444,'\xe9':444,'\xea':444,'\xeb':444,'\xec':278,'\xed':278,'\xee':278,'\xef':278,'\xf0':500,'\xf1':500,
  '\xf2':500,'\xf3':500,'\xf4':500,'\xf5':500,'\xf6':500,'\xf7':675,'\xf8':500,'\xf9':500,'\xfa':500,'\xfb':500,'\xfc':500,'\xfd':444,'\xfe':500,'\xff':444}

fpdf_charwidths['zapfdingbats']={
  '\x00':0,'\x01':0,'\x02':0,'\x03':0,'\x04':0,'\x05':0,'\x06':0,'\x07':0,'\x08':0,'\t':0,'\n':0,'\x0b':0,'\x0c':0,'\r':0,'\x0e':0,'\x0f':0,'\x10':0,'\x11':0,'\x12':0,'\x13':0,'\x14':0,'\x15':0,
  '\x16':0,'\x17':0,'\x18':0,'\x19':0,'\x1a':0,'\x1b':0,'\x1c':0,'\x1d':0,'\x1e':0,'\x1f':0,' ':278,'!':974,'"':961,'#':974,'$':980,'%':719,'&':789,'\'':790,'(':791,')':690,'*':960,'+':939,
  ',':549,'-':855,'.':911,'/':933,'0':911,'1':945,'2':974,'3':755,'4':846,'5':762,'6':761,'7':571,'8':677,'9':763,':':760,';':759,'<':754,'=':494,'>':552,'?':537,'@':577,'A':692,
  'B':786,'C':788,'D':788,'E':790,'F':793,'G':794,'H':816,'I':823,'J':789,'K':841,'L':823,'M':833,'N':816,'O':831,'P':923,'Q':744,'R':723,'S':749,'T':790,'U':792,'V':695,'W':776,
  'X':768,'Y':792,'Z':759,'[':707,'\\':708,']':682,'^':701,'_':826,'`':815,'a':789,'b':789,'c':707,'d':687,'e':696,'f':689,'g':786,'h':787,'i':713,'j':791,'k':785,'l':791,'m':873,
  'n':761,'o':762,'p':762,'q':759,'r':759,'s':892,'t':892,'u':788,'v':784,'w':438,'x':138,'y':277,'z':415,'{':392,'|':392,'}':668,'~':668,'\x7f':0,'\x80':390,'\x81':390,'\x82':317,'\x83':317,
  '\x84':276,'\x85':276,'\x86':509,'\x87':509,'\x88':410,'\x89':410,'\x8a':234,'\x8b':234,'\x8c':334,'\x8d':334,'\x8e':0,'\x8f':0,'\x90':0,'\x91':0,'\x92':0,'\x93':0,'\x94':0,'\x95':0,'\x96':0,'\x97':0,'\x98':0,'\x99':0,
  '\x9a':0,'\x9b':0,'\x9c':0,'\x9d':0,'\x9e':0,'\x9f':0,'\xa0':0,'\xa1':732,'\xa2':544,'\xa3':544,'\xa4':910,'\xa5':667,'\xa6':760,'\xa7':760,'\xa8':776,'\xa9':595,'\xaa':694,'\xab':626,'\xac':788,'\xad':788,'\xae':788,'\xaf':788,
  '\xb0':788,'\xb1':788,'\xb2':788,'\xb3':788,'\xb4':788,'\xb5':788,'\xb6':788,'\xb7':788,'\xb8':788,'\xb9':788,'\xba':788,'\xbb':788,'\xbc':788,'\xbd':788,'\xbe':788,'\xbf':788,'\xc0':788,'\xc1':788,'\xc2':788,'\xc3':788,'\xc4':788,'\xc5':788,
  '\xc6':788,'\xc7':788,'\xc8':788,'\xc9':788,'\xca':788,'\xcb':788,'\xcc':788,'\xcd':788,'\xce':788,'\xcf':788,'\xd0':788,'\xd1':788,'\xd2':788,'\xd3':788,'\xd4':894,'\xd5':838,'\xd6':1016,'\xd7':458,'\xd8':748,'\xd9':924,'\xda':748,'\xdb':918,
  '\xdc':927,'\xdd':928,'\xde':928,'\xdf':834,'\xe0':873,'\xe1':828,'\xe2':924,'\xe3':924,'\xe4':917,'\xe5':930,'\xe6':931,'\xe7':463,'\xe8':883,'\xe9':836,'\xea':836,'\xeb':867,'\xec':867,'\xed':696,'\xee':696,'\xef':874,'\xf0':0,'\xf1':874,
  '\xf2':760,'\xf3':946,'\xf4':771,'\xf5':865,'\xf6':771,'\xf7':888,'\xf8':967,'\xf9':888,'\xfa':831,'\xfb':873,'\xfc':927,'\xfd':970,'\xfe':918,'\xff':0}


#### From php.py
#RR from py3k import PY3K, basestring, unicode
# fpdf php helpers:

def substr(s, start, length = -1):
  if length < 0: length = len(s) - start
  return s[start:start + length]

def sprintf(fmt, *args): return fmt % args

def print_r(array):
  if not isinstance(array, dict):
    array = dict([(k, k) for k in array])
  for k, v in sorted(array.items(), key=lambda x: str(x[0])):
    print("[%s] => %s " % (k, v))

def UTF8ToUTF16BE(instr, setbom = True):
  "Converts UTF-8 strings to UTF16-BE."
  outstr = "".encode()
  if (setbom):
    outstr += "\xFE\xFF".encode("latin1")
  if not isinstance(instr, unicode):
    instr = instr.decode('UTF-8')
  outstr += instr.encode('UTF-16BE')

  # convert bytes back to fake unicode string
  # until PEP461-like is implemented
  #RR if PY3K:
  #RR    outstr = outstr.decode("latin1")
  return outstr

def UTF8StringToArray(instr):
  "Converts UTF-8 strings to codepoints array"
  return [ord(c) for c in instr]

# ttfints php helpers:

def die(msg):
  raise RuntimeError(msg)

def str_repeat(s, count):
  return s * count

def str_pad(s, pad_length=0, pad_char= " ", pad_type= +1 ):
  # pad left
  if pad_type < 0:   return s.rjust(pad_length,  pad_char)
  # pad right
  elif pad_type > 0: return s.ljust(pad_length,  pad_char)
  # pad both
  else:              return s.center(pad_length, pad_char)

strlen = count = lambda s: len(s)


#### From py3k.py
"Special module to handle differences between Python 2 and 3 versions"

def hashpath(fn):
  h = md5()
  if PY3K:
    h.update(fn.encode("UTF-8"))
  else:
    h.update(fn)
  return h.hexdigest()

def unescape2(*args, **kwargs):
  return HTMLParser().unescape(*args, **kwargs)

def unescape3(*args, **kwargs):
  import html
  return html.unescape(*args, **kwargs)

unescape = unescape3 if PY3K else unescape2

# why is this next part like this?
try:
  from HTMLParser import HTMLParser
except ImportError as e:
  from html.parser import HTMLParser

if PY3K:
  basestring = str
  unicode = str
  ord = lambda x: x
else:
  basestring = basestring
  unicode = unicode
  ord = ord

# shortcut to bytes conversion (b prefix)
def b(s):
  if isinstance(s, basestring):
    return s.encode("latin1")
  elif isinstance(s, int):
    if PY3K:
      return bytes([s])  # http://bugs.python.org/issue4588
    else:
      return chr(s)

##### from ttfonts.py
#******************************************************************************
# TTFontFile class
#
# This class is based on The ReportLab Open Source PDF library
# written in Python - http://www.reportlab.com/software/opensource/
# together with ideas from the OpenOffice source code and others.
#
# Version:  1.04
# Date:     2011-09-18
# Author:   Ian Back <ianb@bpm1.com>
# License:  LGPL
# Copyright (c) Ian Back, 2010
# Ported to Python 2.7 by Mariano Reingart (reingart@gmail.com) on 2012
# This header must be retained in any redistribution or
# modification of the file.
#
#******************************************************************************

# Define the value used in the "head" table of a created TTF file
# 0x74727565 "true" for Mac
# 0x00010000 for Windows
# Either seems to work for a font embedded in a PDF file
# when read by Adobe Reader on a Windows PC(!)
_TTF_MAC_HEADER = False


# TrueType Font Glyph operators
GF_WORDS = (1 << 0)
GF_SCALE = (1 << 3)
GF_MORE  = (1 << 5)
GF_XYSCALE  = (1 << 6)
GF_TWOBYTWO = (1 << 7)


def sub32(x, y):
  xlo = x[1]
  xhi = x[0]
  ylo = y[1]
  yhi = y[0]
  if (ylo > xlo):
    xlo += 1 << 16
    yhi += 1
  reslo = xlo-ylo
  if (yhi > xhi):
    xhi += 1 << 16
  reshi = xhi-yhi
  reshi = reshi & 0xFFFF
  return (reshi, reslo)

def calcChecksum(data):
  if (strlen(data) % 4):
    data += str_repeat(b("\0"), (4-(len(data) % 4)))
  hi=0x0000
  lo=0x0000
  for i in range(0, len(data), 4):
    hi += (ord(data[i])<<8) + ord(data[i+1])
    lo += (ord(data[i+2])<<8) + ord(data[i+3])
    hi += lo >> 16
    lo = lo & 0xFFFF
    hi = hi & 0xFFFF
  return (hi, lo)


class TTFontFile:

  def __init__(self):
    self.maxStrLenRead = 200000    # Maximum size of glyf table to read in as string (otherwise reads each glyph from file)

  def getMetrics(self, file):
    self.filename = file
    with open(file,'rb') as self.fh:
      self._pos = 0
      self.charWidths = []
      self.glyphPos = {}
      self.charToGlyph = {}
      self.tables = {}
      self.otables = {}
      self.ascent = 0
      self.descent = 0
      self.TTCFonts = {}
      self.version = version = self.read_ulong()
      if (version==0x4F54544F):
        die("Postscript outlines are not supported")
      if (version==0x74746366):
        die("ERROR - TrueType Fonts Collections not supported")
      if (version not in (0x00010000,0x74727565)):
        die("Not a TrueType font: version=" + str(version))
      self.readTableDirectory()
      self.extractInfo()

  def readTableDirectory(self, ):
    self.numTables = self.read_ushort()
    self.searchRange = self.read_ushort()
    self.entrySelector = self.read_ushort()
    self.rangeShift = self.read_ushort()
    self.tables = {}
    for i in range(self.numTables):
      record = {}
      record['tag'] = self.read_tag()
      record['checksum'] = (self.read_ushort(),self.read_ushort())
      record['offset'] = self.read_ulong()
      record['length'] = self.read_ulong()
      self.tables[record['tag']] = record

  def get_table_pos(self, tag):
    offset = self.tables[tag]['offset']
    length = self.tables[tag]['length']
    return (offset, length)

  def seek(self, pos):
    self._pos = pos
    self.fh.seek(self._pos)

  def skip(self, delta):
    self._pos = self._pos + delta
    self.fh.seek(self._pos)

  def seek_table(self, tag, offset_in_table = 0):
    tpos = self.get_table_pos(tag)
    self._pos = tpos[0] + offset_in_table
    self.fh.seek(self._pos)
    return self._pos

  def read_tag(self):
    self._pos += 4
    return self.fh.read(4).decode("latin1")

  def read_short(self):
    self._pos += 2
    s = self.fh.read(2)
    a = (ord(s[0])<<8) + ord(s[1])
    if (a & (1 << 15) ):
      a = (a - (1 << 16))
    return a

  def unpack_short(self, s):
    a = (ord(s[0])<<8) + ord(s[1])
    if (a & (1 << 15) ):
      a = (a - (1 << 16))
    return a

  def read_ushort(self):
    self._pos += 2
    s = self.fh.read(2)
    return (ord(s[0])<<8) + ord(s[1])

  def read_ulong(self):
    self._pos += 4
    s = self.fh.read(4)
    # if large uInt32 as an integer, PHP converts it to -ve
    return (ord(s[0])*16777216) + (ord(s[1])<<16) + (ord(s[2])<<8) + ord(s[3]) #     16777216  = 1<<24

  def get_ushort(self, pos):
    self.fh.seek(pos)
    s = self.fh.read(2)
    return (ord(s[0])<<8) + ord(s[1])

  def get_ulong(self, pos):
    self.fh.seek(pos)
    s = self.fh.read(4)
    # iF large uInt32 as an integer, PHP converts it to -ve
    return (ord(s[0])*16777216) + (ord(s[1])<<16) + (ord(s[2])<<8) + ord(s[3]) #     16777216  = 1<<24

  def pack_short(self, val):
    if (val<0):
      val = abs(val)
      val = ~val
      val += 1
    return pack(">H",val)

  def splice(self, stream, offset, value):
    return substr(stream,0,offset) + value + substr(stream,offset+strlen(value))

  def _set_ushort(self, stream, offset, value):
    up = pack(">H", value)
    return self.splice(stream, offset, up)

  def _set_short(self, stream, offset, val):
    if (val<0):
      val = abs(val)
      val = ~val
      val += 1
    up = pack(">H",val)
    return self.splice(stream, offset, up)

  def get_chunk(self, pos, length):
    self.fh.seek(pos)
    if (length <1):  return ''
    return (self.fh.read(length))

  def get_table(self, tag):
    (pos, length) = self.get_table_pos(tag)
    if (length == 0):
      die('Truetype font (' + self.filename + '): error reading table: ' + tag)
    self.fh.seek(pos)
    return (self.fh.read(length))

  def add(self, tag, data):
    if (tag == 'head') :
      data = self.splice(data, 8, b("\0\0\0\0"))
    self.otables[tag] = data

  ############################################/
  ############################################/

  ############################################/

  def extractInfo(self):
    #################/
    # name - Naming table
    #################/
    self.sFamilyClass = 0
    self.sFamilySubClass = 0

    name_offset = self.seek_table("name")
    format = self.read_ushort()
    if (format != 0):
      die("Unknown name table format " + format)
    numRecords = self.read_ushort()
    string_data_offset = name_offset + self.read_ushort()
    names = {1:'',2:'',3:'',4:'',6:''}
    K = list(names.keys())
    nameCount = len(names)
    for i in range(numRecords):
      platformId = self.read_ushort()
      encodingId = self.read_ushort()
      languageId = self.read_ushort()
      nameId = self.read_ushort()
      length = self.read_ushort()
      offset = self.read_ushort()
      if (nameId not in K): continue
      N = ''
      if (platformId == 3 and encodingId == 1 and languageId == 0x409):  # Microsoft, Unicode, US English, PS Name
        opos = self._pos
        self.seek(string_data_offset + offset)
        if (length % 2 != 0):
          die("PostScript name is UTF-16BE string of odd length")
        length //= 2
        N = ''
        while (length > 0):
          char = self.read_ushort()
          N += (chr(char))
          length -= 1
        self._pos = opos
        self.seek(opos)

      elif (platformId == 1 and encodingId == 0 and languageId == 0):  # Macintosh, Roman, English, PS Name
        opos = self._pos
        N = self.get_chunk(string_data_offset + offset, length).decode("latin1")
        self._pos = opos
        self.seek(opos)

      if (N and names[nameId]==''):
        names[nameId] = N
        nameCount -= 1
        if (nameCount==0): break


    if (names[6]):
      psName = names[6]
    elif (names[4]):
      psName = re.sub(' ','-',names[4])
    elif (names[1]):
      psName = re.sub(' ','-',names[1])
    else:
      psName = ''
    if (not psName):
      die("Could not find PostScript font name")
    self.name = psName
    if (names[1]):
      self.familyName = names[1]
    else:
      self.familyName = psName
    if (names[2]):
      self.styleName = names[2]
    else:
      self.styleName = 'Regular'
    if (names[4]):
      self.fullName = names[4]
    else:
      self.fullName = psName
    if (names[3]):
      self.uniqueFontID = names[3]
    else:
      self.uniqueFontID = psName
    if (names[6]):
      self.fullName = names[6]

      #################/
    # head - Font header table
    #################/
    self.seek_table("head")
    self.skip(18)
    self.unitsPerEm = unitsPerEm = self.read_ushort()
    scale = 1000 / float(unitsPerEm)
    self.skip(16)
    xMin = self.read_short()
    yMin = self.read_short()
    xMax = self.read_short()
    yMax = self.read_short()
    self.bbox = [(xMin*scale), (yMin*scale), (xMax*scale), (yMax*scale)]
    self.skip(3*2)
    indexToLocFormat = self.read_ushort()
    glyphDataFormat = self.read_ushort()
    if (glyphDataFormat != 0):
      die('Unknown glyph data format ' + glyphDataFormat)

    #################/
    # hhea metrics table
    #################/
    # ttf2t1 seems to use this value rather than the one in OS/2 - so put in for compatibility
    if ("hhea" in self.tables):
      self.seek_table("hhea")
      self.skip(4)
      hheaAscender = self.read_short()
      hheaDescender = self.read_short()
      self.ascent = (hheaAscender *scale)
      self.descent = (hheaDescender *scale)


    #################/
    # OS/2 - OS/2 and Windows metrics table
    #################/
    if ("OS/2" in self.tables):
      self.seek_table("OS/2")
      version = self.read_ushort()
      self.skip(2)
      usWeightClass = self.read_ushort()
      self.skip(2)
      fsType = self.read_ushort()
      if (fsType == 0x0002 or (fsType & 0x0300) != 0):
        die('ERROR - Font file ' + self.filename + ' cannot be embedded due to copyright restrictions.')
        self.restrictedUse = True

      self.skip(20)
      sF = self.read_short()
      self.sFamilyClass = (sF >> 8)
      self.sFamilySubClass = (sF & 0xFF)
      self._pos += 10  #PANOSE = 10 byte length
      panose = self.fh.read(10)
      self.skip(26)
      sTypoAscender = self.read_short()
      sTypoDescender = self.read_short()
      if (not self.ascent):
        self.ascent = (sTypoAscender*scale)
      if (not self.descent):
        self.descent = (sTypoDescender*scale)
      if (version > 1):
        self.skip(16)
        sCapHeight = self.read_short()
        self.capHeight = (sCapHeight*scale)
      else:
        self.capHeight = self.ascent

    else:
      usWeightClass = 500
      if (not self.ascent): self.ascent = (yMax*scale)
      if (not self.descent): self.descent = (yMin*scale)
      self.capHeight = self.ascent

    self.stemV = 50 + int(pow((usWeightClass / 65.0),2))

    #################/
    # post - PostScript table
    #################/
    self.seek_table("post")
    self.skip(4)
    self.italicAngle = self.read_short() + self.read_ushort() / 65536.0
    self.underlinePosition = self.read_short() * scale
    self.underlineThickness = self.read_short() * scale
    isFixedPitch = self.read_ulong()

    self.flags = 4

    if (self.italicAngle!= 0):
      self.flags = self.flags | 64
    if (usWeightClass >= 600):
      self.flags = self.flags | 262144
    if (isFixedPitch):
      self.flags = self.flags | 1

    #################/
    # hhea - Horizontal header table
    #################/
    self.seek_table("hhea")
    self.skip(32)
    metricDataFormat = self.read_ushort()
    if (metricDataFormat != 0):
      die('Unknown horizontal metric data format '.metricDataFormat)
    numberOfHMetrics = self.read_ushort()
    if (numberOfHMetrics == 0):
      die('Number of horizontal metrics is 0')

    #################/
    # maxp - Maximum profile table
    #################/
    self.seek_table("maxp")
    self.skip(4)
    numGlyphs = self.read_ushort()

    #################/
    # cmap - Character to glyph index mapping table
    #################/
    cmap_offset = self.seek_table("cmap")
    self.skip(2)
    cmapTableCount = self.read_ushort()
    unicode_cmap_offset = 0
    unicode_cmap_offset12 = 0

    for i in range(cmapTableCount):
      platformID = self.read_ushort()
      encodingID = self.read_ushort()
      offset = self.read_ulong()
      save_pos = self._pos
      if platformID == 3 and encodingID == 10:  # Microsoft, UCS-4
        format = self.get_ushort(cmap_offset + offset)
        if (format == 12):
          if not unicode_cmap_offset12:
            unicode_cmap_offset12 = cmap_offset + offset
          break
      if ((platformID == 3 and encodingID == 1) or platformID == 0):  # Microsoft, Unicode
        format = self.get_ushort(cmap_offset + offset)
        if (format == 4):
          if (not unicode_cmap_offset):
            unicode_cmap_offset = cmap_offset + offset
          break

      self.seek(save_pos)

    if not unicode_cmap_offset and not unicode_cmap_offset12:
      die('Font (' + self.filename + ') does not have cmap for Unicode (platform 3, encoding 1, format 4, or platform 3, encoding 10, format 12, or platform 0, any encoding, format 4)')

    glyphToChar = {}
    charToGlyph = {}
    if unicode_cmap_offset12:
      self.getCMAP12(unicode_cmap_offset12, glyphToChar, charToGlyph)
    else:
      self.getCMAP4(unicode_cmap_offset, glyphToChar, charToGlyph)

    #################/
    # hmtx - Horizontal metrics table
    #################/
    self.getHMTX(numberOfHMetrics, numGlyphs, glyphToChar, scale)


  ############################################/
  ############################################/

  def makeSubset(self, file, subset):
    self.filename = file
    with open(file ,'rb') as self.fh:
      self._pos = 0
      self.charWidths = []
      self.glyphPos = {}
      self.charToGlyph = {}
      self.tables = {}
      self.otables = {}
      self.ascent = 0
      self.descent = 0
      self.skip(4)
      self.maxUni = 0
      self.readTableDirectory()

      #################/
      # head - Font header table
      #################/
      self.seek_table("head")
      self.skip(50)
      indexToLocFormat = self.read_ushort()
      glyphDataFormat = self.read_ushort()

      #################/
      # hhea - Horizontal header table
      #################/
      self.seek_table("hhea")
      self.skip(32)
      metricDataFormat = self.read_ushort()
      orignHmetrics = numberOfHMetrics = self.read_ushort()

      #################/
      # maxp - Maximum profile table
      #################/
      self.seek_table("maxp")
      self.skip(4)
      numGlyphs = self.read_ushort()

      #################/
      # cmap - Character to glyph index mapping table
      #################/
      cmap_offset = self.seek_table("cmap")
      self.skip(2)
      cmapTableCount = self.read_ushort()
      unicode_cmap_offset = 0
      unicode_cmap_offset12 = 0
      for i in range(cmapTableCount):
        platformID = self.read_ushort()
        encodingID = self.read_ushort()
        offset = self.read_ulong()
        save_pos = self._pos
        if platformID == 3 and encodingID == 10:  # Microsoft, UCS-4
          format = self.get_ushort(cmap_offset + offset)
          if (format == 12):
            if not unicode_cmap_offset12:
              unicode_cmap_offset12 = cmap_offset + offset
            break
        if ((platformID == 3 and encodingID == 1) or platformID == 0):  # Microsoft, Unicode
          format = self.get_ushort(cmap_offset + offset)
          if (format == 4):
            unicode_cmap_offset = cmap_offset + offset
            break

        self.seek(save_pos )

      if not unicode_cmap_offset and not unicode_cmap_offset12:
        die('Font (' + self.filename + ') does not have cmap for Unicode (platform 3, encoding 1, format 4, or platform 3, encoding 10, format 12, or platform 0, any encoding, format 4)')

      glyphToChar = {}
      charToGlyph = {}
      if unicode_cmap_offset12:
        self.getCMAP12(unicode_cmap_offset12, glyphToChar, charToGlyph)
      else:
        self.getCMAP4(unicode_cmap_offset, glyphToChar, charToGlyph)

      self.charToGlyph = charToGlyph

      #################/
      # hmtx - Horizontal metrics table
      #################/
      scale = 1    # not used
      self.getHMTX(numberOfHMetrics, numGlyphs, glyphToChar, scale)

      #################/
      # loca - Index to location
      #################/
      self.getLOCA(indexToLocFormat, numGlyphs)

      subsetglyphs = [(0, 0)]     # special "sorted dict"!
      subsetCharToGlyph = {}
      for code in subset:
        if (code in self.charToGlyph):
          if (self.charToGlyph[code], code) not in subsetglyphs:
            subsetglyphs.append((self.charToGlyph[code], code))   # Old Glyph ID => Unicode
          subsetCharToGlyph[code] = self.charToGlyph[code]    # Unicode to old GlyphID
        self.maxUni = max(self.maxUni, code)
      (start,dummy) = self.get_table_pos('glyf')

      subsetglyphs.sort()
      glyphSet = {}
      n = 0
      fsLastCharIndex = 0    # maximum Unicode index (character code) in this font, according to the cmap subtable for platform ID 3 and platform- specific encoding ID 0 or 1.
      for originalGlyphIdx, uni in subsetglyphs:
        fsLastCharIndex = max(fsLastCharIndex , uni)
        glyphSet[originalGlyphIdx] = n    # old glyphID to new glyphID
        n += 1

      codeToGlyph = {}
      for uni, originalGlyphIdx in sorted(subsetCharToGlyph.items()):
        codeToGlyph[uni] = glyphSet[originalGlyphIdx]

      self.codeToGlyph = codeToGlyph

      for originalGlyphIdx, uni in subsetglyphs:
        nonlocals = {'start': start, 'glyphSet': glyphSet,
                     'subsetglyphs': subsetglyphs}
        self.getGlyphs(originalGlyphIdx, nonlocals)

      numGlyphs = numberOfHMetrics = len(subsetglyphs)

      #tables copied from the original
      tags = ['name']
      for tag in tags:
        self.add(tag, self.get_table(tag))
      tags = ['cvt ', 'fpgm', 'prep', 'gasp']
      for tag in tags:
        if (tag in self.tables):
          self.add(tag, self.get_table(tag))

          # post - PostScript
      opost = self.get_table('post')
      post = b("\x00\x03\x00\x00") + substr(opost,4,12) + b("\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
      self.add('post', post)

      # Sort CID2GID map into segments of contiguous codes
      if 0 in codeToGlyph:
        del codeToGlyph[0]
      #unset(codeToGlyph[65535])
      rangeid = 0
      range_ = {}
      prevcid = -2
      prevglidx = -1
      # for each character
      for cid, glidx in sorted(codeToGlyph.items()):
        if (cid == (prevcid + 1) and glidx == (prevglidx + 1)):
          range_[rangeid].append(glidx)
        else:
          # new range
          rangeid = cid
          range_[rangeid] = []
          range_[rangeid].append(glidx)
        prevcid = cid
        prevglidx = glidx

      # cmap - Character to glyph mapping - Format 4 (MS / )
      segCount = len(range_) + 1    # + 1 Last segment has missing character 0xFFFF
      searchRange = 1
      entrySelector = 0
      while (searchRange * 2 <= segCount ):
        searchRange = searchRange * 2
        entrySelector = entrySelector + 1

      searchRange = searchRange * 2
      rangeShift = segCount * 2 - searchRange
      length = 16 + (8*segCount ) + (numGlyphs+1)
      cmap = [0, 1,        # Index : version, number of encoding subtables
              3, 1,                # Encoding Subtable : platform (MS=3), encoding (Unicode)
              0, 12,            # Encoding Subtable : offset (hi,lo)
              4, length, 0,         # Format 4 Mapping subtable: format, length, language
              segCount*2,
              searchRange,
              entrySelector,
              rangeShift]

      range_ = sorted(range_.items())

      # endCode(s)
      for start, subrange in range_:
        endCode = start + (len(subrange)-1)
        cmap.append(endCode)    # endCode(s)

      cmap.append(0xFFFF)    # endCode of last Segment
      cmap.append(0)    # reservedPad

      # startCode(s)
      for start, subrange in range_:
        cmap.append(start)    # startCode(s)

      cmap.append(0xFFFF)    # startCode of last Segment
      # idDelta(s)
      for start, subrange in range_:
        idDelta = -(start-subrange[0])
        n += count(subrange)
        cmap.append(idDelta)    # idDelta(s)

      cmap.append(1)    # idDelta of last Segment
      # idRangeOffset(s)
      for subrange in range_:
        cmap.append(0)    # idRangeOffset[segCount]      Offset in bytes to glyph indexArray, or 0

      cmap.append(0)    # idRangeOffset of last Segment
      for subrange, glidx in range_:
        cmap.extend(glidx)

      cmap.append(0)    # Mapping for last character
      cmapstr = b('')
      for cm in cmap:
        if cm >= 0:
          cmapstr += pack(">H", cm)
        else:
          try:
            cmapstr += pack(">h", cm)
          except:
            warnings.warn("cmap value too big/small: %s" % cm)
            cmapstr += pack(">H", -cm)
      self.add('cmap', cmapstr)

      # glyf - Glyph data
      (glyfOffset,glyfLength) = self.get_table_pos('glyf')
      if (glyfLength < self.maxStrLenRead):
        glyphData = self.get_table('glyf')

      offsets = []
      glyf = b('')
      pos = 0

      hmtxstr = b('')
      xMinT = 0
      yMinT = 0
      xMaxT = 0
      yMaxT = 0
      advanceWidthMax = 0
      minLeftSideBearing = 0
      minRightSideBearing = 0
      xMaxExtent = 0
      maxPoints = 0            # points in non-compound glyph
      maxContours = 0            # contours in non-compound glyph
      maxComponentPoints = 0    # points in compound glyph
      maxComponentContours = 0    # contours in compound glyph
      maxComponentElements = 0    # number of glyphs referenced at top level
      maxComponentDepth = 0        # levels of recursion, set to 0 if font has only simple glyphs
      self.glyphdata = {}

      for originalGlyphIdx, uni in subsetglyphs:
        # hmtx - Horizontal Metrics
        hm = self.getHMetric(orignHmetrics, originalGlyphIdx)
        hmtxstr += hm

        offsets.append(pos)
        try:
          glyphPos = self.glyphPos[originalGlyphIdx]
          glyphLen = self.glyphPos[originalGlyphIdx + 1] - glyphPos
        except IndexError:
          warnings.warn("missing glyph %s" % (originalGlyphIdx))
          glyphLen = 0

        if (glyfLength < self.maxStrLenRead):
          data = substr(glyphData,glyphPos,glyphLen)
        else:
          if (glyphLen > 0):
            data = self.get_chunk(glyfOffset+glyphPos,glyphLen)
          else:
            data = b('')

        if (glyphLen > 0):
          up = unpack(">H", substr(data,0,2))[0]
        if (glyphLen > 2 and (up & (1 << 15)) ):     # If number of contours <= -1 i.e. composite glyph
          pos_in_glyph = 10
          flags = GF_MORE
          nComponentElements = 0
          while (flags & GF_MORE):
            nComponentElements += 1    # number of glyphs referenced at top level
            up = unpack(">H", substr(data,pos_in_glyph,2))
            flags = up[0]
            up = unpack(">H", substr(data,pos_in_glyph+2,2))
            glyphIdx = up[0]
            self.glyphdata.setdefault(originalGlyphIdx, {}).setdefault('compGlyphs', []).append(glyphIdx)
            try:
              data = self._set_ushort(data, pos_in_glyph + 2, glyphSet[glyphIdx])
            except KeyError:
              data = 0
              warnings.warn("missing glyph data %s" % glyphIdx)
            pos_in_glyph += 4
            if (flags & GF_WORDS):
              pos_in_glyph += 4
            else:
              pos_in_glyph += 2
            if (flags & GF_SCALE):
              pos_in_glyph += 2
            elif (flags & GF_XYSCALE):
              pos_in_glyph += 4
            elif (flags & GF_TWOBYTWO):
              pos_in_glyph += 8

          maxComponentElements = max(maxComponentElements, nComponentElements)

        glyf += data
        pos += glyphLen
        if (pos % 4 != 0):
          padding = 4 - (pos % 4)
          glyf += str_repeat(b("\0"),padding)
          pos += padding

      offsets.append(pos)
      self.add('glyf', glyf)

      # hmtx - Horizontal Metrics
      self.add('hmtx', hmtxstr)

      # loca - Index to location
      locastr = b('')
      if (((pos + 1) >> 1) > 0xFFFF):
        indexToLocFormat = 1        # long format
        for offset in offsets:
          locastr += pack(">L",offset)
      else:
        indexToLocFormat = 0        # short format
        for offset in offsets:
          locastr += pack(">H",offset//2)

      self.add('loca', locastr)

      # head - Font header
      head = self.get_table('head')
      head = self._set_ushort(head, 50, indexToLocFormat)
      self.add('head', head)

      # hhea - Horizontal Header
      hhea = self.get_table('hhea')
      hhea = self._set_ushort(hhea, 34, numberOfHMetrics)
      self.add('hhea', hhea)

      # maxp - Maximum Profile
      maxp = self.get_table('maxp')
      maxp = self._set_ushort(maxp, 4, numGlyphs)
      self.add('maxp', maxp)

      # OS/2 - OS/2
      os2 = self.get_table('OS/2')
      self.add('OS/2', os2 )

    # Put the TTF file together
    stm = self.endTTFile('')
    return stm


    #########################################
  # Recursively get composite glyph data
  def getGlyphData(self, originalGlyphIdx, nonlocals):
    # &maxdepth, &depth, &points, &contours
    nonlocals['depth'] += 1
    nonlocals['maxdepth'] = max(nonlocals['maxdepth'], nonlocals['depth'])
    if (len(self.glyphdata[originalGlyphIdx]['compGlyphs'])):
      for glyphIdx in self.glyphdata[originalGlyphIdx]['compGlyphs']:
        self.getGlyphData(glyphIdx, nonlocals)

    elif ((self.glyphdata[originalGlyphIdx]['nContours'] > 0) and nonlocals['depth'] > 0):     # simple
      contours += self.glyphdata[originalGlyphIdx]['nContours']
      points += self.glyphdata[originalGlyphIdx]['nPoints']

    nonlocals['depth'] -= 1


  #########################################
  # Recursively get composite glyphs
  def getGlyphs(self, originalGlyphIdx, nonlocals):
    # &start, &glyphSet, &subsetglyphs)

    try:
      glyphPos = self.glyphPos[originalGlyphIdx]
      glyphLen = self.glyphPos[originalGlyphIdx + 1] - glyphPos
    except IndexError:
      warnings.warn("missing glyph %s" % (originalGlyphIdx))
      return

    if (not glyphLen):
      return

    self.seek(nonlocals['start'] + glyphPos)
    numberOfContours = self.read_short()
    if (numberOfContours < 0):
      self.skip(8)
      flags = GF_MORE
      while (flags & GF_MORE):
        flags = self.read_ushort()
        glyphIdx = self.read_ushort()
        if (glyphIdx not in nonlocals['glyphSet']):
          nonlocals['glyphSet'][glyphIdx] = len(nonlocals['subsetglyphs'])    # old glyphID to new glyphID
          nonlocals['subsetglyphs'].append((glyphIdx, 1))

        savepos = self.fh.tell()
        self.getGlyphs(glyphIdx, nonlocals)
        self.seek(savepos)
        if (flags & GF_WORDS):
          self.skip(4)
        else:
          self.skip(2)
        if (flags & GF_SCALE):
          self.skip(2)
        elif (flags & GF_XYSCALE):
          self.skip(4)
        elif (flags & GF_TWOBYTWO):
          self.skip(8)

  #########################################

  def getHMTX(self, numberOfHMetrics, numGlyphs, glyphToChar, scale):
    start = self.seek_table("hmtx")
    aw = 0
    self.charWidths = []
    def resize_cw(size, default):
      size = (((size + 1) // 1024) + 1) * 1024
      delta = size - len(self.charWidths)
      if delta > 0:
        self.charWidths += [default] * delta
    nCharWidths = 0
    if ((numberOfHMetrics*4) < self.maxStrLenRead):
      data = self.get_chunk(start,(numberOfHMetrics*4))
      arr = unpack(">%dH" % (len(data)//2), data)
    else:
      self.seek(start)
    for glyph in range(numberOfHMetrics):
      if ((numberOfHMetrics*4) < self.maxStrLenRead):
        aw = arr[(glyph*2)] # PHP starts arrays from index 0!? +1
      else:
        aw = self.read_ushort()
        lsb = self.read_ushort()

      if (glyph in glyphToChar or glyph == 0):
        if (aw >= (1 << 15) ):
          aw = 0     # 1.03 Some (arabic) fonts have -ve values for width
          # although should be unsigned value - comes out as e.g. 65108 (intended -50)
        if (glyph == 0):
          self.defaultWidth = scale*aw
          continue

        for char in glyphToChar[glyph]:
          if (char != 0 and char != 65535):
            w = int(round(scale*aw+0.001))   # ROUND_HALF_UP in PY3K (like php)
            if (w == 0):  w = 65535
            if (char < 196608):
              if char >= len(self.charWidths):
                resize_cw(char, self.defaultWidth)
              self.charWidths[char] = w
              nCharWidths += 1


    data = self.get_chunk((start+numberOfHMetrics*4),(numGlyphs*2))
    arr = unpack(">%dH" % (len(data)//2), data)
    diff = numGlyphs-numberOfHMetrics
    for pos in range(diff):
      glyph = pos + numberOfHMetrics
      if (glyph in glyphToChar):
        for char in glyphToChar[glyph]:
          if (char != 0 and char != 65535):
            w = int(round(scale*aw+0.001))  # ROUND_HALF_UP in PY3K (like php)
            if (w == 0):  w = 65535
            if (char < 196608):
              if char >= len(self.charWidths):
                resize_cw(char, self.defaultWidth)
              self.charWidths[char] = w
              nCharWidths += 1


              # NB 65535 is a set width of 0
    # First bytes define number of chars in font
    self.charWidths[0] = nCharWidths


  def getHMetric(self, numberOfHMetrics, gid):
    start = self.seek_table("hmtx")
    if (gid < numberOfHMetrics):
      self.seek(start+(gid*4))
      hm = self.fh.read(4)
    else:
      self.seek(start+((numberOfHMetrics-1)*4))
      hm = self.fh.read(2)
      self.seek(start+(numberOfHMetrics*2)+(gid*2))
      hm += self.fh.read(2)
    return hm


  def getLOCA(self, indexToLocFormat, numGlyphs):
    start = self.seek_table('loca')
    self.glyphPos = []
    if (indexToLocFormat == 0):
      data = self.get_chunk(start,(numGlyphs*2)+2)
      arr = unpack(">%dH" % (len(data)//2), data)
      for n in range(numGlyphs):
        self.glyphPos.append((arr[n] * 2))  # n+1 !?
    elif (indexToLocFormat == 1):
      data = self.get_chunk(start,(numGlyphs*4)+4)
      arr = unpack(">%dL" % (len(data)//4), data)
      for n in range(numGlyphs):
        self.glyphPos.append((arr[n]))  # n+1 !?
    else:
      die('Unknown location table format ' + indexToLocFormat)

  # CMAP Format 4
  def getCMAP4(self, unicode_cmap_offset, glyphToChar, charToGlyph):
    self.maxUniChar = 0
    self.seek(unicode_cmap_offset + 2)
    length = self.read_ushort()
    limit = unicode_cmap_offset + length
    self.skip(2)

    segCount = self.read_ushort() // 2
    self.skip(6)
    endCount = []
    for i in range(segCount):
      endCount.append(self.read_ushort())
    self.skip(2)
    startCount = []
    for i in range(segCount):
      startCount.append(self.read_ushort())
    idDelta = []
    for i in range(segCount):
      idDelta.append(self.read_short())         # ???? was unsigned short
    idRangeOffset_start = self._pos
    idRangeOffset = []
    for i in range(segCount):
      idRangeOffset.append(self.read_ushort())

    for n in range(segCount):
      endpoint = (endCount[n] + 1)
      for unichar in range(startCount[n], endpoint, 1):
        if (idRangeOffset[n] == 0):
          glyph = (unichar + idDelta[n]) & 0xFFFF
        else:
          offset = (unichar - startCount[n]) * 2 + idRangeOffset[n]
          offset = idRangeOffset_start + 2 * n + offset
          if (offset >= limit):
            glyph = 0
          else:
            glyph = self.get_ushort(offset)
            if (glyph != 0):
              glyph = (glyph + idDelta[n]) & 0xFFFF

        charToGlyph[unichar] = glyph
        if (unichar < 196608):
          self.maxUniChar = max(unichar,self.maxUniChar)
        glyphToChar.setdefault(glyph, []).append(unichar)

  # CMAP Format 12
  def getCMAP12(self, unicode_cmap_offset, glyphToChar, charToGlyph):
    self.maxUniChar = 0
    # table (skip format version, should be 12)
    self.seek(unicode_cmap_offset + 2)
    # reserved
    self.skip(2)
    # table length
    length = self.read_ulong()
    # language (should be 0)
    self.skip(4)
    # groups count
    grpCount = self.read_ulong()

    if 2 + 2 + 4 + 4 + 4 + grpCount * 3 * 4 > length:
      die("TTF format 12 cmap table too small")
    for n in range(grpCount):
      startCharCode = self.read_ulong()
      endCharCode = self.read_ulong()
      glyph = self.read_ulong()
      for unichar in range(startCharCode, endCharCode + 1):
        charToGlyph[unichar] = glyph
        if (unichar < 196608):
          self.maxUniChar = max(unichar, self.maxUniChar)
        glyphToChar.setdefault(glyph, []).append(unichar)
        glyph += 1



  # Put the TTF file together
  def endTTFile(self, stm):
    stm = b('')
    numTables = count(self.otables)
    searchRange = 1
    entrySelector = 0
    while (searchRange * 2 <= numTables):
      searchRange = searchRange * 2
      entrySelector = entrySelector + 1

    searchRange = searchRange * 16
    rangeShift = numTables * 16 - searchRange

    # Header
    if (_TTF_MAC_HEADER):
      stm += (pack(">LHHHH", 0x74727565, numTables, searchRange, entrySelector, rangeShift))    # Mac
    else:
      stm += (pack(">LHHHH", 0x00010000 , numTables, searchRange, entrySelector, rangeShift))    # Windows


    # Table directory
    tables = self.otables

    offset = 12 + numTables * 16
    sorted_tables = sorted(tables.items())
    for tag, data in sorted_tables:
      if (tag == 'head'):
        head_start = offset
      stm += tag.encode("latin1")
      checksum = calcChecksum(data)
      stm += pack(">HH", checksum[0],checksum[1])
      stm += pack(">LL", offset, strlen(data))
      paddedLength = (strlen(data)+3)&~3
      offset = offset + paddedLength

    # Table data
    for tag, data in sorted_tables:
      data += b("\0\0\0")
      stm += substr(data,0,(strlen(data)&~3))

    checksum = calcChecksum(stm)
    checksum = sub32((0xB1B0,0xAFBA), checksum)
    chk = pack(">HH", checksum[0],checksum[1])
    stm = self.splice(stm,(head_start + 8),chk)
    return stm




  ######

def get_page_format(format, k=None):
  """Return page width and height size in points.

  Throws FPDFPageFormatException

  `format` can be either a 2-tuple or one of 'a3', 'a4', 'a5', 'letter', or
  'legal'.

  If format is a tuple, then the return value is the tuple's values
  given in the units specified on this document in the constructor,
  multiplied by the corresponding scale factor `k`, taken from instance
  variable `self.k`.

  If format is a string, the (width, height) tuple returned is in points.
  For a width and height of 8.5 * 11, 72 dpi is assumed, so the value
  returned is (8.5 * 72, 11 * 72), or (612, 792). Additional formats can be
  added by adding fields to the `fpdf.fpdf.PAGE_FORMATS` dictionary with a
  case insensitive key (the name of the new format) and 2-tuple value of
  (width, height) in dots per inch with a 72 dpi resolution.
  """
  if isinstance(format, basestring):
    format = format.lower()
    if format in PAGE_FORMATS:
      return PAGE_FORMATS[format]
    else:
      raise FPDFPageFormatException(format, unknown=True)

  if k is None:
    raise FPDFPageFormatException(format, one=True)

  try:
    return (format[0] * k, format[1] * k)
  except Exception as e:
    args = str(format) + ', ' + str(k)
    ours = FPDFPageFormatException('Arguments must be numbers: ' + args)
    #raise_from(ours, e)


def load_cache(filename):
  """Return unpickled object, or None if cache unavailable"""
  if not filename:
    return None
  try:
    with open(filename, "rb") as fh:
      return pickle.load(fh)
  # File missing, unsupported pickle, etc
  except (IOError, ValueError):
    return None


class FPDF(object):
  "PDF Generation class"

  def __init__(self, orientation = 'P', unit = 'mm', format = 'A4'):
    # Initialization of properties
    self.offsets = {}               # array of object offsets
    self.page = 0                   # current page number
    self.n = 2                      # current object number
    self.buffer = ''                # buffer holding in-memory PDF
    self.pages = {}                 # array containing pages and metadata
    self.state = 0                  # current document state
    self.fonts = {}                 # array of used fonts
    self.font_files = {}            # array of font files
    self.diffs = {}                 # array of encoding differences
    self.images = {}                # array of used images
    self.page_links = {}            # array of links in pages
    self.links = {}                 # array of internal links
    self.in_footer = 0              # flag set when processing footer
    self.lastw = 0
    self.lasth = 0                  # height of last cell printed
    self.font_family = ''           # current font family
    self.font_style = ''            # current font style
    self.font_size_pt = 12          # current font size in points
    self.font_stretching = 100      # current font stretching
    self.underline = 0              # underlining flag
    self.draw_color = '0 G'
    self.fill_color = '0 g'
    self.text_color = '0 g'
    # indicates whether fill and text colors are different
    self.color_flag = 0
    self.ws = 0                     # word spacing
    self.angle = 0

    # Standard fonts
    self.core_fonts = {'courier': 'Courier', 'courierB': 'Courier-Bold',
                       'courierI': 'Courier-Oblique',
                       'courierBI': 'Courier-BoldOblique',
                       'helvetica': 'Helvetica',
                       'helveticaB': 'Helvetica-Bold',
                       'helveticaI': 'Helvetica-Oblique',
                       'helveticaBI': 'Helvetica-BoldOblique',
                       'times': 'Times-Roman',
                       'timesB': 'Times-Bold',
                       'timesI': 'Times-Italic',
                       'timesBI': 'Times-BoldItalic',
                       'symbol': 'Symbol', 'zapfdingbats': 'ZapfDingbats'}
    self.core_fonts_encoding = "latin-1"

    # Scale factor
    if unit == "pt":
      self.k = 1
    elif unit == "mm":
      self.k = 72 / 25.4
    elif unit == "cm":
      self.k = 72 / 2.54
    elif unit == 'in':
      self.k = 72.
    else:
      fpdf_error("Incorrect unit: " + unit)

    # Page format
    self.fw_pt, self.fh_pt = get_page_format(format, self.k)
    self.dw_pt = self.fw_pt
    self.dh_pt = self.fh_pt
    self.fw = self.fw_pt / self.k
    self.fh = self.fh_pt / self.k

    # Page orientation
    orientation = orientation.lower()
    if orientation in ('p', 'portrait'):
      self.def_orientation = 'P'
      self.w_pt = self.fw_pt
      self.h_pt = self.fh_pt
    elif orientation in ('l', 'landscape'):
      self.def_orientation = 'L'
      self.w_pt = self.fh_pt
      self.h_pt = self.fw_pt
    else:
      fpdf_error('Incorrect orientation: ' + orientation)
    self.cur_orientation = self.def_orientation
    self.w = self.w_pt / self.k
    self.h = self.h_pt / self.k

    # Page spacing
    # Page margins (1 cm)
    margin = 28.35 / self.k
    self.set_margins(margin, margin)
    self.c_margin = margin / 10.0            # Interior cell margin (1 mm)
    self.line_width = .567 / self.k          # line width (0.2 mm)
    self.set_auto_page_break(1, 2 * margin)  # Automatic page break
    self.set_display_mode('fullwidth')       # Full width display mode
    self.set_compression(1)                  # Enable compression
    self.pdf_version = '1.3'                 # Set default PDF version No.

  def check_page(fn):
    "Decorator to protect drawing methods"
    @wraps(fn)
    def wrapper(self, *args, **kwargs):
      if not self.page and not kwargs.get('split_only'):
        fpdf_error("No page open, you need to call add_page() first")
      else:
        return fn(self, *args, **kwargs)
    return wrapper

  def set_margins(self, left, top, right=-1):
    "Set left, top and right margins"
    self.l_margin = left
    self.t_margin = top
    if (right == -1):
      right = left
    self.r_margin = right

  def set_left_margin(self, margin):
    "Set left margin"
    self.l_margin = margin
    if (self.page > 0 and self.x < margin):
      self.x = margin

  def set_top_margin(self, margin):
    "Set top margin"
    self.t_margin = margin

  def set_right_margin(self, margin):
    "Set right margin"
    self.r_margin = margin

  def set_auto_page_break(self, auto, margin=0):
    "Set auto page break mode and triggering margin"
    self.auto_page_break = auto
    self.b_margin = margin
    self.page_break_trigger = self.h - margin

  def set_display_mode(self, zoom, layout = 'continuous'):
    """Set display mode in viewer

    The "zoom" argument may be 'fullpage', 'fullwidth', 'real',
    'default', or a number, interpreted as a percentage.
    """
    if zoom in ['fullpage', 'fullwidth', 'real', 'default']:
      self.zoom_mode = zoom
    elif not isinstance(zoom, basestring):
      self.zoom_mode = zoom
    else:
      fpdf_error('Incorrect zoom display mode: ' + zoom)

    if layout in ['single', 'continuous', 'two', 'default']:
      self.layout_mode = layout
    else:
      fpdf_error('Incorrect layout display mode: ' + layout)

  def set_compression(self, compress):
    "Set page compression"
    self.compress = compress

  def set_title(self, title):
    "Title of document"
    self.title = title

  def set_subject(self, subject):
    "Subject of document"
    self.subject = subject

  def set_author(self, author):
    "Author of document"
    self.author = author

  def set_keywords(self, keywords):
    "Keywords of document"
    self.keywords = keywords

  def set_creator(self, creator):
    "Creator of document"
    self.creator = creator

  def set_creation_date(self, date = None):
    """Sets Creation of Date time, or current time if None given."""
    self.creation_date = datetime.now() if date is None else date

  def set_doc_option(self, opt, value):
    "Set document option"
    if opt == "core_fonts_encoding":
      self.core_fonts_encoding = value
    else:
      fpdf_error("Unknown document option \"%s\"" % str(opt))

  def alias_nb_pages(self, alias = '{nb}'):
    "Define an alias for total number of pages"
    self.str_alias_nb_pages = alias
    return alias

  def open(self):
    "Begin document"
    self.state = 1

  def close(self):
    "Terminate document"
    if (self.state == 3):
      return
    if (self.page == 0):
      self.add_page()

    # Page footer
    self.in_footer = 1
    self.footer()
    self.in_footer = 0

    self._endpage()  # close page
    self._enddoc()   # close document

  def add_page(self, orientation = '', format = '', same = False):
    "Start a new page, if same page format will be same as previous"
    if (self.state == 0): self.open()
    family = self.font_family
    style  = self.font_style + 'U' if self.underline else self.font_style
    size   = self.font_size_pt
    lw     = self.line_width
    dc     = self.draw_color
    fc     = self.fill_color
    tc     = self.text_color
    cf     = self.color_flag
    stretching = self.font_stretching
    if (self.page > 0):
      # Page footer
      self.in_footer = 1
      self.footer()
      self.in_footer = 0
      # close page
      self._endpage()

    # Start new page
    self._beginpage(orientation, format, same)
    self._out('2 J')      # Set line cap style to square
    self.line_width = lw  # Set line width
    self._out(sprintf('%.2f w', lw * self.k))

    # Set font
    if (family): self.set_font(family, style, size)

    # Set colors
    self.draw_color = dc
    if dc != '0 G': self._out(dc)
    self.fill_color = fc
    if fc != '0 g': self._out(fc)
    self.text_color = tc
    self.color_flag = cf

    """ BEGIN Page header """
    self.header()

    if (self.line_width != lw):                       # Restore line width
      self.line_width = lw
      self._out(sprintf('%.2f w', lw * self.k))

    if (family): self.set_font(family, style, size)  # Restore font

    if (self.draw_color != dc):                      # Restore colors
      self.draw_color = dc
      self._out(dc)
    if (self.fill_color != fc):
      self.fill_color = fc
      self._out(fc)
    self.text_color = tc
    self.color_flag = cf

    if (stretching != 100):                          # Restore stretching
      self.set_stretching(stretching)
    """ END Page header """

  def header(self):
    "Header to be implemented in your own inherited class"
    pass

  def footer(self):
    "Footer to be implemented in your own inherited class"
    pass

  def page_no(self):
    "Get current page number"
    return self.page

  def set_draw_color(self, r, g =- 1, b =- 1):
    "Set color for all stroking operations"
    if ((r == 0 and g == 0 and b == 0) or g == -1):
      self.draw_color = sprintf('%.3f G', r / 255.0)
    else:
      self.draw_color = sprintf('%.3f %.3f %.3f RG',
                                r / 255.0, g / 255.0, b / 255.0)
    if (self.page > 0):
      self._out(self.draw_color)

  def set_fill_color(self, r, g = -1, b = -1):
    "Set color for all filling operations"
    if ((r == 0 and g == 0 and b == 0) or g == -1):
      self.fill_color = sprintf('%.3f g', r / 255.0)
    else:
      self.fill_color = sprintf('%.3f %.3f %.3f rg',
                                r / 255.0, g / 255.0, b / 255.0)
    self.color_flag = (self.fill_color != self.text_color)
    if (self.page > 0):
      self._out(self.fill_color)

  def set_text_color(self, r, g =- 1, b =- 1):
    "Set color for text"
    if ((r == 0 and g == 0 and b == 0) or g == -1):
      self.text_color = sprintf('%.3f g', r / 255.0)
    else:
      self.text_color = sprintf('%.3f %.3f %.3f rg',
                                r / 255.0, g / 255.0, b / 255.0)
    self.color_flag = (self.fill_color != self.text_color)

  def get_string_width(self, s, normalized = False):
    "Get width of a string in the current font"
    # normalized is parameter for internal use
    s = s if normalized else self.normalize_text(s)
    cw = self.current_font['cw']
    w  = 0
    l  = len(s)
    if self.unifontsubset:
      for char in s:
        char = ord(char)
        if len(cw) > char:
          w += cw[char]
        elif (self.current_font['desc']['MissingWidth']):
          w += self.current_font['desc']['MissingWidth']
        else:
          w += 500
    else:
      for i in range(0, l):
        w += cw.get(s[i], 0)
    if self.font_stretching != 100:
      w = w * self.font_stretching / 100.0
    return w * self.font_size / 1000.0

  def set_line_width(self, width):
    "Set line width"
    self.line_width = width
    if (self.page > 0):
      self._out(sprintf('%.2f w', width * self.k))

  @check_page
  def line(self, x1, y1, x2, y2):
    "Draw a line"
    self._out(sprintf('%.2f %.2f m %.2f %.2f l S',
                      x1 * self.k, (self.h - y1) * self.k,
                      x2 * self.k, (self.h - y2) * self.k))

  def _set_dash(self, dash_length = False, space_length = False):
    if (dash_length and space_length):
      s = sprintf('[%.3f %.3f] 0 d',
                  dash_length * self.k, space_length * self.k)
    else:
      s = '[] 0 d'
    self._out(s)

  @check_page
  def dashed_line(self, x1, y1, x2, y2, dash_length = 1, space_length = 1):
    """Draw a dashed line. Same interface as line() except:
       - dash_length: Length of the dash
       - space_length: Length of the space between dashes"""
    self._set_dash(dash_length, space_length)
    self.line(x1, y1, x2, y2)
    self._set_dash()

  @check_page
  def rect(self, x, y, w, h, style = None):
    "Draw a rectangle"
    style_to_operators = {
      'F': 'f',
      'FD': 'B',
      'DF': 'B'
    }
    op = style_to_operators.get(style, 'S')
    self._out(sprintf('%.2f %.2f %.2f %.2f re %s',
                      x * self.k, (self.h - y) * self.k,
                      w * self.k, -h * self.k, op))

  @check_page
  def ellipse(self, x, y, w, h, style = None):
    "Draw a ellipse"
    style_to_operators = {
      'F': 'f',
      'FD': 'B',
      'DF': 'B'
    }
    op = style_to_operators.get(style, 'S')

    cx = x + w / 2.0
    cy = y + h / 2.0
    rx = w / 2.0
    ry = h / 2.0

    lx = 4.0 / 3.0 * (math.sqrt(2) - 1) * rx
    ly = 4.0 / 3.0 * (math.sqrt(2) - 1) * ry

    self._out(sprintf('%.2f %.2f m %.2f %.2f %.2f %.2f %.2f %.2f c',
                      (cx + rx) * self.k, (self.h - cy)        * self.k,
                      (cx + rx) * self.k, (self.h - (cy - ly)) * self.k,
                      (cx + lx) * self.k, (self.h - (cy - ry)) * self.k,
                      cx * self.k,        (self.h - (cy - ry)) * self.k))
    self._out(sprintf('%.2f %.2f %.2f %.2f %.2f %.2f c',
                      (cx - lx) * self.k, (self.h - (cy - ry)) * self.k,
                      (cx - rx) * self.k, (self.h - (cy - ly)) * self.k,
                      (cx - rx) * self.k, (self.h - cy)        * self.k))
    self._out(sprintf('%.2f %.2f %.2f %.2f %.2f %.2f c',
                      (cx - rx) * self.k, (self.h - (cy + ly)) * self.k,
                      (cx - lx) * self.k, (self.h - (cy + ry)) * self.k,
                      cx * self.k,        (self.h - (cy + ry)) * self.k))
    self._out(sprintf('%.2f %.2f %.2f %.2f %.2f %.2f c %s',
                      (cx + lx) * self.k, (self.h - (cy + ry)) * self.k,
                      (cx + rx) * self.k, (self.h - (cy + ly)) * self.k,
                      (cx + rx) * self.k, (self.h - cy) * self.k, op))

  def add_font(self, family, style = '', fname = None, uni = False):
    "Add a TrueType or Type1 font"
    family = family.lower()
    if not fname:
      fname = family.replace(' ', '') + style.lower() + '.pkl'

    if (family == 'arial'): family = 'helvetica'
    style = style.upper()
    if (style == 'IB'): style = 'BI'
    fontkey = family + style

    # Font already added!
    if fontkey in self.fonts: return
    if (uni):
      global SYSTEM_TTFONTS, FPDF_CACHE_MODE, FPDF_CACHE_DIR
      if os.path.exists(fname):
        ttffilename = fname
      elif (FPDF_FONT_DIR and
            os.path.exists(os.path.join(FPDF_FONT_DIR, fname))):
        ttffilename = os.path.join(FPDF_FONT_DIR, fname)
      elif (SYSTEM_TTFONTS and
            os.path.exists(os.path.join(SYSTEM_TTFONTS, fname))):
        ttffilename = os.path.join(SYSTEM_TTFONTS, fname)
      else:
        raise RuntimeError("TTF Font file not found: %s" % fname)
      name = ''  # noqa: F841
      if FPDF_CACHE_MODE == 0:
        unifilename = os.path.splitext(ttffilename)[0] + '.pkl'
      elif FPDF_CACHE_MODE == 2:
        unifilename = os.path.join(FPDF_CACHE_DIR,
                                   hashpath(ttffilename) + ".pkl")
      else:
        unifilename = None

      font_dict = load_cache(unifilename)
      if font_dict is None:
        ttf = TTFontFile()
        ttf.getMetrics(ttffilename)
        desc = {
          'Ascent'       : int(round(ttf.ascent, 0)),
          'Descent'      : int(round(ttf.descent, 0)),
          'CapHeight'    : int(round(ttf.capHeight, 0)),
          'Flags'        : ttf.flags,
          'FontBBox'     : "[%s %s %s %s]" % (
            int(round(ttf.bbox[0], 0)),
            int(round(ttf.bbox[1], 0)),
            int(round(ttf.bbox[2], 0)),
            int(round(ttf.bbox[3], 0))),
          'ItalicAngle'  : int(ttf.italicAngle),
          'StemV'        : int(round(ttf.stemV, 0)),
          'MissingWidth' : int(round(ttf.defaultWidth, 0)),
        }

        # Generate metrics .pkl file
        font_dict = {
          'name'         : re.sub('[ ()]', '', ttf.fullName),
          'type'         : 'TTF',
          'desc'         : desc,
          'up'           : round(ttf.underlinePosition),
          'ut'           : round(ttf.underlineThickness),
          'ttffile'      : ttffilename,
          'fontkey'      : fontkey,
          'originalsize' : os.stat(ttffilename).st_size,
          'cw'           : ttf.charWidths,
        }

        if unifilename:
          try:
            with open(unifilename, "wb") as fh:
              pickle.dump(font_dict, fh)
          except IOError as e:
            if not e.errno == errno.EACCES:
              raise  # Not a permission error.
        del ttf

      # include numbers in the subset! (if alias present)
      have_page_alias = lambda: hasattr(self, 'str_alias_nb_pages')
      sbarr = list(range(0, 57 if have_page_alias() else 32))

      self.fonts[fontkey] = {
        'i'           : len(self.fonts) + 1,
        'type'        : font_dict['type'],
        'name'        : font_dict['name'],
        'desc'        : font_dict['desc'],
        'up'          : font_dict['up'],
        'ut'          : font_dict['ut'],
        'cw'          : font_dict['cw'],
        'ttffile'     : font_dict['ttffile'],
        'fontkey'     : fontkey,
        'subset'      : sbarr,
        'unifilename' : unifilename
      }
      self.font_files[fontkey] = {'length1': font_dict['originalsize'],
                                  'type': "TTF", 'ttffile': ttffilename}
      self.font_files[fname]   = {'type': "TTF"}
    else:
      with open(fname, 'rb') as fontfile:
        font_dict = pickle.load(fontfile)
      self.fonts[fontkey] = {'i': len(self.fonts) + 1}
      self.fonts[fontkey].update(font_dict)
      diff = font_dict.get('diff')
      if (diff):
        # Search existing encodings
        d  = 0
        nb = len(self.diffs)
        for i in range(1, nb + 1):
          if (self.diffs[i] == diff):
            d = i
            break
        if (d == 0):
          d = nb + 1
          self.diffs[d] = diff
        self.fonts[fontkey]['diff'] = d
      filename = font_dict.get('filename')
      if (filename):
        if (font_dict['type'] == 'TrueType'):
          originalsize = font_dict['originalsize']
          self.font_files[filename] = {'length1': originalsize}
        else:
          self.font_files[filename] = {'length1': font_dict['size1'],
                                       'length2': font_dict['size2']}

  def set_font(self, family, style='', size=0):
    "Select a font; size given in points"
    family = family.lower()
    if (family == ''):
      family = self.font_family
    if (family == 'arial'):
      family = 'helvetica'
    elif (family == 'symbol' or family == 'zapfdingbats'):
      style = ''
    style = style.upper()
    if ('U' in style):
      self.underline = 1
      style = style.replace('U', '')
    else:
      self.underline = 0
    if (style == 'IB'):
      style = 'BI'
    if (size == 0):
      size = self.font_size_pt

    # Test if font is already selected
    if (self.font_family == family and
            self.font_style == style and
            self.font_size_pt == size): return

    # Test if used for the first time
    fontkey = family + style
    if fontkey not in self.fonts:
      # Check if one of standard fonts
      if fontkey in self.core_fonts:
        if fontkey not in fpdf_charwidths:
          # Load metric file
          name = os.path.join(FPDF_FONT_DIR, family)
          if (family == 'times' or family == 'helvetica'):
            name += style.lower()
          with open(name + '.font') as file:
            exec(compile(file.read(), name + '.font', 'exec'))
          if fontkey not in fpdf_charwidths:
            fpdf_error('Could not include font metric file for' +
                       fontkey)
        i = len(self.fonts) + 1
        self.fonts[fontkey] = {
          'i'    : i,
          'type' : 'core',
          'name' : self.core_fonts[fontkey],
          'up'   : -100,
          'ut'   : 50,
          'cw'   : fpdf_charwidths[fontkey]
        }
      else:
        fpdf_error('Undefined font: ' + family + ' ' + style)

    # Select it
    self.font_family   = family
    self.font_style    = style
    self.font_size_pt  = size
    self.font_size     = size / self.k
    self.current_font  = self.fonts[fontkey]
    self.unifontsubset = (self.fonts[fontkey]['type'] == 'TTF')
    if (self.page > 0):
      self._out(sprintf('BT /F%d %.2f Tf ET',
                        self.current_font['i'],
                        self.font_size_pt))

  def set_font_size(self, size):
    "Set font size in points"
    if (self.font_size_pt == size): return
    self.font_size_pt = size
    self.font_size    = size / self.k
    if (self.page > 0):
      self._out(sprintf('BT /F%d %.2f Tf ET',
                        self.current_font['i'],
                        self.font_size_pt))

  def set_stretching(self, factor):
    "Set from stretch factor percents (default: 100.0)"
    if (self.font_stretching == factor): return
    self.font_stretching = factor
    if (self.page > 0):
      self._out(sprintf('BT %.2f Tz ET', self.font_stretching))

  def add_link(self):
    "Create a new internal link"
    n = len(self.links) + 1
    self.links[n] = (0, 0)
    return n

  def set_link(self, link, y = 0, page = -1):
    "Set destination of internal link"
    if (y    == -1): y    = self.y
    if (page == -1): page = self.page

    self.links[link] = [page, y]

  def link(self, x, y, w, h, link):
    "Put a link on the page"
    if self.page not in self.page_links:
      self.page_links[self.page] = []
    self.page_links[self.page] += [(
      x * self.k, self.h_pt - y * self.k,
      w * self.k, h             * self.k, link
    )]

  @check_page
  def text(self, x, y, txt = ''):
    "Output a string"
    txt = self.normalize_text(txt)
    if (self.unifontsubset):
      txt2 = escape_parens(UTF8ToUTF16BE(txt, False))
      for uni in UTF8StringToArray(txt):
        self.current_font['subset'].append(uni)
    else:
      txt2 = escape_parens(txt)
    s = sprintf('BT %.2f %.2f Td (%s) Tj ET',
                x            * self.k,
                (self.h - y) * self.k,
                txt2)
    if (self.underline and txt != ''):
      s += ' ' + self._dounderline(x, y, txt)
    if (self.color_flag):
      s = 'q ' + self.text_color + ' ' + s + ' Q'
    self._out(s)

  @check_page
  def rotate(self, angle, x = None, y = None):
    if x is None: x = self.x
    if y is None: y = self.y

    if self.angle != 0:
      self._out('Q')
    self.angle = angle
    if angle != 0:
      angle *= math.pi / 180
      c      = math.cos(angle)
      s      = math.sin(angle)
      cx     = x            * self.k
      cy     = (self.h - y) * self.k
      s = sprintf('q %.5F %.5F %.5F %.5F %.2F %.2F ' +
                  'cm 1 0 0 1 %.2F %.2F cm',
                  c, s, -s, c, cx, cy, -cx, -cy)
      self._out(s)

  @property
  def accept_page_break(self):
    "Accept automatic page break or not"
    return self.auto_page_break

  @check_page
  def cell(self, w, h = 0, txt = '', border = 0, ln = 0, align = '',
           fill = 0, link = ''):
    "Output a cell, return boolean if triggered auto page break"
    page_break_triggered = False
    txt = self.normalize_text(txt)
    k = self.k
    if ((self.y + h > self.page_break_trigger and
         not self.in_footer and
         self.accept_page_break)):

      # Automatic page break
      page_break_triggered = True
      x  = self.x
      ws = self.ws
      if (ws > 0):
        self.ws = 0
        self._out('0 Tw')
      self.add_page(same = True)
      self.x = x  # restore x but not y after drawing header

      if (ws > 0):
        self.ws = ws
        self._out(sprintf('%.3f Tw', ws * k))
    if (w == 0):
      w = self.w - self.r_margin - self.x
    s = ''

    if (fill == 1 or border == 1):
      if (fill == 1):
        if border == 1:
          op = 'B'
        else:
          op = 'f'
      else:
        op = 'S'
      s = sprintf('%.2f %.2f %.2f %.2f re %s ',
                  self.x            * k,
                  (self.h - self.y) * k,
                  w * k, -h * k, op)

    if (isinstance(border, basestring)):
      x = self.x
      y = self.y
      if ('L' in border):
        s += sprintf('%.2f %.2f m %.2f %.2f l S ',
                     x * k, (self.h - y)       * k,
                     x * k, (self.h - (y + h)) * k)
      if ('T' in border):
        s += sprintf('%.2f %.2f m %.2f %.2f l S ',
                     x * k,       (self.h - y) * k,
                     (x + w) * k, (self.h - y) * k)
      if ('R' in border):
        s += sprintf('%.2f %.2f m %.2f %.2f l S ',
                     (x + w) * k, (self.h - y)       * k,
                     (x + w) * k, (self.h - (y + h)) * k)
      if ('B' in border):
        s += sprintf('%.2f %.2f m %.2f %.2f l S ',
                     x       * k, (self.h - (y + h)) * k,
                     (x + w) * k, (self.h - (y + h)) * k)

    if (txt != ''):
      if (align == 'R'):
        dx = w - self.c_margin - self.get_string_width(txt, True)
      elif (align == 'C'):
        dx = (w - self.get_string_width(txt, True)) / 2.0
      else:
        dx = self.c_margin
      if (self.color_flag): s += 'q ' + self.text_color + ' '

      # If multibyte, Tw has no effect - do word spacing using an
      # adjustment before each space
      if (self.ws and self.unifontsubset):
        for uni in UTF8StringToArray(txt):
          self.current_font['subset'].append(uni)
        space = escape_parens(UTF8ToUTF16BE(' ', False))

        s += sprintf('BT 0 Tw %.2F %.2F Td [',
                     (self.x + dx)                                            * k,
                     (self.h - (self.y + (0.5 * h) + (0.3 * self.font_size))) * k)


        t = txt.split(' ')
        numt = len(t)
        for i in range(numt):
          tx = t[i]
          tx = enclose_in_parens(
            escape_parens(UTF8ToUTF16BE(tx, False))
          )
          s += sprintf('%s ', tx)
          if ((i + 1) < numt):
            adj = -(self.ws * self.k) * 1000 / self.font_size_pt
            s += sprintf('%d(%s) ', adj, space)
        s += '] TJ'
        s += ' ET'
      else:
        if (self.unifontsubset):
          txt2 = escape_parens(UTF8ToUTF16BE(txt, False))
          for uni in UTF8StringToArray(txt):
            self.current_font['subset'].append(uni)
        else:
          txt2 = escape_parens(txt)

        s += sprintf('BT %.2f %.2f Td (%s) Tj ET',
                     (self.x + dx)                                          * k,
                     (self.h - (self.y + (.5 * h) + (.3 * self.font_size))) * k,
                     txt2)

      if (self.underline): s += ' ' + \
                                self._dounderline(self.x + dx,
                                                  self.y + (.5 * h) + (.3 * self.font_size),
                                                  txt)
      if (self.color_flag): s += ' Q'
      if (link):
        self.link(self.x + dx,
                  self.y + (.5 * h) - (.5 * self.font_size),
                  self.get_string_width(txt,  True),
                  self.font_size,
                  link)

    if (s): self._out(s)
    self.lasth = h

    if (ln > 0):
      self.y += h  # Go to next line
      if (ln == 1):
        self.x = self.l_margin
    else:
      self.x += w

    return page_break_triggered

  @check_page
  def multi_cell(self, w, h, txt = '', border = 0, align = 'J',
                 fill = 0, split_only = False, link = '', ln = 0):
    """Output text with automatic or explicit line breaks, returns
    boolean if page break triggered in output mode
    """
    page_break_triggered = False
    if split_only:
      _out, _add_page = self._out, self.add_page
      self._out = lambda *args, **kwargs: None
      self.add_page = lambda *args, **kwargs: None

    # Store this information for manipulating position.
    location = (self.get_x(), self.get_y())

    # If width is 0, set width to available width between margins
    if (w == 0):
      w = self.w - self.r_margin - self.x
    wmax = (w - 2 * self.c_margin) * 1000.0 / self.font_size

    # Calculate text length
    txt = self.normalize_text(txt)
    s  = txt.replace("\r", '')
    normalized_string_length = len(s)
    if (normalized_string_length > 0 and s[-1] == "\n"):
      normalized_string_length -= 1

    b = 0
    if (border):
      if (border == 1):
        border = 'LTRB'
        b      = 'LRT'
        b2     = 'LR'
      else:
        b2 = ''
        if ('L' in border): b2 += 'L'
        if ('R' in border): b2 += 'R'
        if ('T' in border): b = b2 + 'T'
        else: b = b2

    character_widths = self.current_font['cw']
    text_cells = []
    sep = -1
    i   = 0
    j   = 0
    l   = 0
    ns  = 0
    nl  = 1
    while(i < normalized_string_length):
      # Get next character
      c = s[i]

      # Explicit line break
      if (c == "\n"):
        if (self.ws > 0):
          self.ws = 0
          self._out('0 Tw')

        new_page = self.cell(w, h = h, txt = substr(s, j, i - j),
                             border = b, ln = 2, align = align,
                             fill = fill, link = link)
        page_break_triggered = page_break_triggered or new_page
        text_cells.append(substr(s, j, i - j))

        i   += 1
        sep  = -1
        j    = i
        l    = 0
        ns   = 0
        nl  += 1
        if (border and nl == 2):
          b = b2
        continue

      if (c == ' '):
        sep  = i
        ls   = l
        ns  += 1
      if self.unifontsubset:
        l += self.get_string_width(c, True) / self.font_size * 1000.0
      else:
        l += character_widths.get(c, 0)

      # Automatic line break
      if (l > wmax):
        if (sep == -1):
          if (i == j):
            i += 1
          if (self.ws > 0):
            self.ws = 0
            self._out('0 Tw')

          new_page = self.cell(w, h = h, txt = substr(s, j, i - j),
                               border = b, ln = 2, align = align,
                               fill = fill, link = link)
          page_break_triggered = page_break_triggered or new_page
          text_cells.append(substr(s, j, i - j))

        else:
          if (align == 'J'):
            if ns > 1:
              self.ws = ((wmax - ls) / 1000.0 *
                         self.font_size / (ns - 1))
            else:
              self.ws = 0
            self._out(sprintf('%.3f Tw', self.ws * self.k))

          new_page = self.cell(w, h = h, txt = substr(s, j, sep - j),
                               border = b, ln = 2, align = align,
                               fill = fill, link = link)
          page_break_triggered = page_break_triggered or new_page
          text_cells.append(substr(s, j, sep - j))

          i = sep + 1
        sep  = -1
        j    = i
        l    = 0
        ns   = 0
        nl  += 1
        if (border and nl == 2):
          b = b2
      else:
        i += 1

    # Last chunk
    if (self.ws > 0):
      self.ws = 0
      self._out('0 Tw')
    if (border and 'B' in border):
      b += 'B'

    new_page = self.cell(w, h = h, txt = substr(s, j, i - j),
                         border = b, ln = 2, align = align,
                         fill = fill, link = link)
    page_break_triggered = page_break_triggered or new_page
    text_cells.append(substr(s, j, i - j))

    location_options = {
      0: lambda : self.set_xy(location[0] + w, location[1]),
      1: lambda : self.set_x(self.l_margin),  # could control y
      2: lambda : None
    }
    location_options.get(ln, lambda : None)()

    if split_only:
      # restore writing functions
      self._out, self.add_page = _out, _add_page
      self.set_xy(*location)  # restore location
      return text_cells

    return page_break_triggered

  @check_page
  def write(self, h, txt = '', link = ''):
    "Output text in flowing mode"
    txt  = self.normalize_text(txt)
    cw   = self.current_font['cw']
    w    = self.w - self.r_margin - self.x
    wmax = (w - 2 * self.c_margin) * 1000.0 / self.font_size
    s    = txt.replace("\r", '')
    nb   = len(s)
    sep  = -1
    i    = 0
    j    = 0
    l    = 0
    nl   = 1
    while(i < nb):
      # Get next character
      c = s[i]
      if (c == "\n"):
        # Explicit line break
        self.cell(w, h, substr(s, j, i - j), 0, 2, '', 0, link)
        i   += 1
        sep  = -1
        j    = i
        l    = 0
        if (nl == 1):
          self.x = self.l_margin
          w      = self.w - self.r_margin - self.x
          wmax   = (w - 2 * self.c_margin) * 1000.0 / self.font_size
        nl += 1
        continue
      if (c == ' '):
        sep = i
      if self.unifontsubset:
        l += self.get_string_width(c, True) / self.font_size * 1000.0
      else:
        l += cw.get(c, 0)
      if (l > wmax):
        # Automatic line break
        if (sep == -1):
          if (self.x > self.l_margin):
            # Move to next line
            self.x  = self.l_margin
            self.y += h
            w    = self.w - self.r_margin - self.x
            wmax = ((w - 2 * self.c_margin) *
                    1000.0 / self.font_size)
            i    += 1
            nl   += 1
            continue
          if (i == j):
            i += 1
          self.cell(w, h, substr(s, j, i   - j), 0, 2, '', 0, link)
        else:
          self.cell(w, h, substr(s, j, sep - j), 0, 2, '', 0, link)
          i = sep + 1
        sep = -1
        j   = i
        l   = 0
        if (nl == 1):
          self.x = self.l_margin
          w      = self.w - self.r_margin - self.x
          wmax   = (w - 2 * self.c_margin) * 1000.0 / self.font_size
        nl += 1
      else:
        i += 1
    # Last chunk
    if (i != j):
      self.cell(l / 1000.0 * self.font_size,
                h, substr(s, j), 0, 0, '', 0, link)

  @check_page
  def image(self, name, x = None, y = None, w = 0, h = 0, type = '', link = ''):  # noqa: E501
    "Put an image on the page"
    return #RR
    if name not in self.images:
      info = get_img_info(image_parsing_load_resource(name))
      info['i'] = len(self.images) + 1
      self.images[name] = info
    else:
      info = self.images[name]

    # Automatic width and height calculation if needed
    if (w == 0 and h == 0):
      # Put image at 72 dpi
      w = info['w'] / self.k
      h = info['h'] / self.k
    elif (w == 0):
      w = h * info['w'] / info['h']
    elif (h == 0):
      h = w * info['h'] / info['w']

    # Flowing mode
    if y is None:
      if (self.y + h > self.page_break_trigger
              and not self.in_footer
              and self.accept_page_break):
        # Automatic page break
        x = self.x
        self.add_page(same = True)
        self.x = x
      y = self.y
      self.y += h

    if x is None: x = self.x
    self._out(sprintf('q %.2f 0 0 %.2f %.2f %.2f cm /I%d Do Q',
                      w * self.k, h                  * self.k,
                      x * self.k, (self.h - (y + h)) * self.k,
                      info['i']))
    if (link):
      self.link(x, y, w, h, link)

  @check_page
  def ln(self, h = None):
    "Line Feed; default value is last cell height"
    self.x = self.l_margin
    if h is None: self.y += self.lasth
    else:         self.y += h

  def get_x(self):
    "Get x position"
    return self.x

  def set_x(self, x):
    "Set x position"
    if (x >= 0): self.x = x
    else:        self.x = self.w + x

  def get_y(self):
    "Get y position"
    return self.y

  def set_y(self, y):
    "Set y position and reset x"
    self.x = self.l_margin
    if (y >= 0): self.y = y
    else:        self.y = self.h + y

  def set_xy(self, x, y):
    "Set x and y positions"
    self.set_y(y)
    self.set_x(x)

  def output(self, name = '', dest = ''):
    """Output PDF to some destination

    By default the PDF is written to sys.stdout. If a name is given, the
    PDF is written to a new file. If dest='S' is given, the PDF data is
    returned as a byte string."""

    # Finish document if necessary
    if (self.state < 3):
      self.close()
    dest                      = dest.upper()
    if (dest == ''):
      if (name == ''): dest = 'I'
      else:            dest = 'F'

    if PY3K:
      # manage binary data as latin1 until PEP461 or similar is
      # implemented
      buffer = self.buffer.encode("latin1")
    else:
      buffer = self.buffer
    if dest in ('I', 'D'):
      # Python < 3 writes byte data transparently without "buffer"
      stdout = getattr(sys.stdout, 'buffer', sys.stdout)
      stdout.write(buffer)
    elif dest == 'F':
      # Save to local file
      with open(name, 'wb') as f:
        f.write(buffer)
    # Return as a byte string
    elif dest == 'S': return buffer

    else:
      fpdf_error('Incorrect output destination: ' + dest)

  def normalize_text(self, txt):
    "Check that text input is in the correct format/encoding"
    # - for TTF unicode fonts: unicode object (utf8 encoding)
    # - for built-in fonts: string instances (encoding: latin-1, cp1252)
    if not PY3K:
      if self.unifontsubset and isinstance(txt, str):
        return txt.decode("utf-8")
      elif not self.unifontsubset and isinstance(txt, unicode):
        return txt.encode(self.core_fonts_encoding)
    else:
      if not self.unifontsubset and self.core_fonts_encoding:
        return txt.encode(self.core_fonts_encoding).decode("latin-1")
    return txt

  def _putpage(self, page, page_links):
    pass

  def _putpages(self):
    nb = self.page
    if hasattr(self, 'str_alias_nb_pages'):
      # Replace number of pages in fonts using subsets (unicode)
      alias = UTF8ToUTF16BE(self.str_alias_nb_pages, False)
      r = UTF8ToUTF16BE(str(nb), False)
      for n in range(1, nb + 1):
        self.pages[n]["content"] = \
          self.pages[n]["content"].replace(alias, r)
      # Now repeat for no pages in non-subset fonts
      for n in range(1, nb + 1):
        self.pages[n]["content"] = \
          self.pages[n]["content"] \
            .replace(self.str_alias_nb_pages, str(nb))
    if self.def_orientation == 'P':
      dw_pt = self.dw_pt
      dh_pt = self.dh_pt
    else:
      dw_pt = self.dh_pt
      dh_pt = self.dw_pt
    if self.compress:
      filter = '/Filter /FlateDecode '
    else:
      filter = ''
    for n in range(1, nb + 1):
      # page object from pages[n]
      # page object from pages[n]#w_pt
      # page object from pages[n]#h_pt
      # page object from page_links[n] if page_links and page_links[n]
      # Page
      self._newobj()
      self._out('<</Type /Page')
      self._out('/Parent 1 0 R')
      w_pt = self.pages[n]["w_pt"]
      h_pt = self.pages[n]["h_pt"]
      if w_pt != dw_pt or h_pt != dh_pt:
        self._out(sprintf('/MediaBox [0 0 %.2f %.2f]', w_pt, h_pt))
      self._out('/Resources 2 0 R')

      if self.page_links and n in self.page_links:
        # Links
        annots = '/Annots ['
        for pl in self.page_links[n]:
          # first four things in 'link' list are coordinates?
          rect = sprintf('%.2f %.2f %.2f %.2f', pl[0], pl[1],
                         pl[0] + pl[2], pl[1] - pl[3])

          # start the annotation entry
          annots += '<</Type /Annot /Subtype /Link /Rect [' + \
                    rect + '] /Border [0 0 0] '

          # HTML ending of annotation entry
          if isinstance(pl[4], basestring):
            annots += '/A <</S /URI /URI ' + \
                      enclose_in_parens(pl[4]) + '>>>>'

          # Dest type ending of annotation entry
          else:
            l = self.links[pl[4]]
            # if l[0] in self.orientation_changes: h = w_pt
            # else:                                h = h_pt
            h = h_pt
            annots += sprintf('/Dest [%d 0 R /XYZ 0 %.2f null]>>',
                              1 + 2 * l[0], h - l[1] * self.k)

        # End links list
        self._out(annots + ']')
      if self.pdf_version > '1.3':
        self._out("/Group <</Type /Group /S /Transparency"
                  "/CS /DeviceRGB>>")
      self._out('/Contents ' + str(self.n + 1) + ' 0 R>>')
      self._out('endobj')

      # Page content
      content = self.pages[n]["content"]
      if self.compress:
        # manage binary data as latin1 until PEP461 or similar is
        # implemented
        p = content.encode("latin1") if PY3K else content
        p = zlib.compress(p)
      else:
        p = content
      self._newobj()
      self._out('<<' + filter + '/Length ' + str(len(p)) + '>>')
      self._out(pdf_stream(p))
      self._out('endobj')
    # Pages root
    self.offsets[1] = len(self.buffer)
    self._out('1 0 obj')
    self._out('<</Type /Pages')
    kids = '/Kids ['
    for i in range(0, nb): kids += str(3 + 2 * i) + ' 0 R '
    self._out(kids + ']')
    self._out('/Count ' + str(nb))
    self._out(sprintf('/MediaBox [0 0 %.2f %.2f]', dw_pt, dh_pt))
    self._out('>>')
    self._out('endobj')

  def _putfonts(self):
    nf = self.n
    for diff in self.diffs:
      # Encodings
      self._newobj()
      self._out(('<</Type /Encoding /BaseEncoding /WinAnsiEncoding ' +
                 '/Differences [' + self.diffs[diff] + ']>>'))
      self._out('endobj')

    for name, info in self.font_files.items():
      if 'type' in info and info['type'] != 'TTF':
        # Font file embedding
        self._newobj()
        self.font_files[name]['n'] = self.n
        with open(os.path.join(FPDF_FONT_DIR, name), 'rb', 1) as f:
          font = f.read()
        compressed = (substr(name, -2) == '.z')
        if (not compressed and 'length2' in info):
          header = (ord(font[0]) == 128)
          if (header):
            # Strip first binary header
            font = substr(font, 6)
          if (header and ord(font[info['length1']]) == 128):
            # Strip second binary header
            font = (substr(font, 0, info['length1']) +
                    substr(font,    info['length1'] + 6))

        self._out('<</Length '    + str(len(font)))
        if (compressed): self._out('/Filter /FlateDecode')
        self._out('/Length1 '     + str(info['length1']))
        if ('length2' in info):
          self._out('/Length2 ' + str(info['length2']) + ' /Length3 0')  # noqa: E501
        self._out('>>')
        self._out(pdf_stream(font))
        self._out('endobj')

    # Font objects
    flist = [(x[1]["i"], x[0], x[1]) for x in self.fonts.items()]
    flist.sort()
    for idx, k, font in flist:
      self.fonts[k]['n'] = self.n + 1
      my_type = font['type']
      name = font['name']
      # Standard font
      if (my_type == 'core'):
        self._newobj()
        self._out('<</Type /Font')
        self._out('/BaseFont /' + name)
        self._out('/Subtype /Type1')
        if (name != 'Symbol' and name != 'ZapfDingbats'):
          self._out('/Encoding /WinAnsiEncoding')
        self._out('>>')
        self._out('endobj')

      # Additional Type1 or TrueType font
      elif (my_type == 'Type1' or my_type == 'TrueType'):
        self._newobj()
        self._out('<</Type /Font')
        self._out('/BaseFont /' + name)
        self._out('/Subtype /' + my_type)
        self._out('/FirstChar 32 /LastChar 255')
        self._out('/Widths ' + str(self.n + 1) + ' 0 R')
        self._out('/FontDescriptor ' + str(self.n + 2) + ' 0 R')
        if (font['enc']):
          if ('diff' in font):
            self._out('/Encoding ' + str(nf + font['diff']) + ' 0 R')  # noqa: E501
          else:
            self._out('/Encoding /WinAnsiEncoding')
        self._out('>>')
        self._out('endobj')

        # Widths
        self._newobj()
        cw = font['cw']
        s  = '['
        for i in range(32, 256):
          # Get doesn't raise exception;
          # returns 0 instead of None if not set
          s += str(cw.get(chr(i), 0)) + ' '
        self._out(s + ']')
        self._out('endobj')

        # Descriptor
        self._newobj()
        s = '<</Type /FontDescriptor /FontName /' + name
        for k in ('Ascent', 'Descent', 'CapHeight', 'Flags',
                  'FontBBox', 'ItalicAngle', 'StemV', 'MissingWidth'):
          s += ' /%s %s' % (k, font['desc'][k])

        filename = font['file']
        if (filename):
          s += ' /FontFile'
          if my_type != 'Type1': s += '2'
          s += ' ' + str(self.font_files[filename]['n']) + ' 0 R'
        self._out(s + '>>')
        self._out('endobj')
      elif (my_type == 'TTF'):
        self.fonts[k]['n'] = self.n + 1
        ttf = TTFontFile()
        fontname     = 'MPDFAA' + '+' + font['name']
        subset       = font['subset']
        del subset[0]
        ttfontstream = ttf.makeSubset(font['ttffile'], subset)
        ttfontsize   = len(ttfontstream)
        fontstream   = zlib.compress(ttfontstream)
        codeToGlyph  = ttf.codeToGlyph
        # del codeToGlyph[0]

        # Type0 Font
        # A composite font - a font composed of other fonts,
        # organized hierarchically
        self._newobj()
        self._out('<</Type /Font')
        self._out('/Subtype /Type0')
        self._out('/BaseFont /' + fontname + '')
        self._out('/Encoding /Identity-H')
        self._out('/DescendantFonts [' + str(self.n + 1) + ' 0 R' + ']')
        self._out('/ToUnicode ' + str(self.n + 2) + ' 0 R')
        self._out('>>')
        self._out('endobj')

        # CIDFontType2
        # A CIDFont whose glyph descriptions are based on
        # TrueType font technology
        self._newobj()
        self._out('<</Type /Font')
        self._out('/Subtype /CIDFontType2')
        self._out('/BaseFont /' + fontname + '')
        self._out('/CIDSystemInfo ' + str(self.n + 2) + ' 0 R')
        self._out('/FontDescriptor ' + str(self.n + 3) + ' 0 R')
        if (font['desc'].get('MissingWidth')):
          self._out('/DW %d' % font['desc']['MissingWidth'])
        self._putTTfontwidths(font, ttf.maxUni)
        self._out('/CIDToGIDMap ' + str(self.n + 4) + ' 0 R')
        self._out('>>')
        self._out('endobj')

        # ToUnicode
        self._newobj()
        toUni = "/CIDInit /ProcSet findresource begin\n" \
                "12 dict begin\n" \
                "begincmap\n" \
                "/CIDSystemInfo\n" \
                "<</Registry (Adobe)\n" \
                "/Ordering (UCS)\n" \
                "/Supplement 0\n" \
                ">> def\n" \
                "/CMapName /Adobe-Identity-UCS def\n" \
                "/CMapType 2 def\n" \
                "1 begincodespacerange\n" \
                "<0000> <FFFF>\n" \
                "endcodespacerange\n" \
                "1 beginbfrange\n" \
                "<0000> <FFFF> <0000>\n" \
                "endbfrange\n" \
                "endcmap\n" \
                "CMapName currentdict /CMap defineresource pop\n" \
                "end\n" \
                "end"
        self._out('<</Length ' + str(len(toUni)) + '>>')
        self._out(pdf_stream(toUni))
        self._out('endobj')

        # CIDSystemInfo dictionary
        self._newobj()
        self._out('<</Registry (Adobe)')
        self._out('/Ordering (UCS)')
        self._out('/Supplement 0')
        self._out('>>')
        self._out('endobj')

        # Font descriptor
        self._newobj()
        self._out('<</Type /FontDescriptor')
        self._out('/FontName /' + fontname)
        for kd in ('Ascent', 'Descent', 'CapHeight', 'Flags',
                   'FontBBox', 'ItalicAngle', 'StemV',
                   'MissingWidth'):
          v = font['desc'][kd]
          if (kd == 'Flags'):
            v = v | 4
            v = v & ~32  # SYMBOLIC font flag
          self._out(' /%s %s' % (kd, v))
        self._out('/FontFile2 ' + str(self.n + 2) + ' 0 R')
        self._out('>>')
        self._out('endobj')

        # Embed CIDToGIDMap
        # A specification of the mapping from CIDs to glyph indices
        cidtogidmap = ''
        cidtogidmap = ["\x00"] * 256 * 256 * 2
        for cc, glyph in codeToGlyph.items():
          cidtogidmap[cc * 2] = chr(glyph >> 8)
          cidtogidmap[cc * 2 + 1] = chr(glyph & 0xFF)
        cidtogidmap = ''.join(cidtogidmap)
        if PY3K:
          # manage binary data as latin1 until PEP461-like function
          # is implemented
          cidtogidmap = cidtogidmap.encode("latin1")
        cidtogidmap = zlib.compress(cidtogidmap)
        self._newobj()
        self._out('<</Length ' + str(len(cidtogidmap)) + '')
        self._out('/Filter /FlateDecode')
        self._out('>>')
        self._out(pdf_stream(cidtogidmap))
        self._out('endobj')

        # Font file
        self._newobj()
        self._out('<</Length ' + str(len(fontstream)))
        self._out('/Filter /FlateDecode')
        self._out('/Length1 ' + str(ttfontsize))
        self._out('>>')
        self._out(pdf_stream(fontstream))
        self._out('endobj')
        del ttf
      else:
        # Allow for additional types
        mtd = '_put' + my_type.lower()
        # check if self has a attr mtd which is callable (method)
        if (not callable(getattr(self, mtd, None))):
          fpdf_error('Unsupported font type: ' + my_type)
        self.mtd(font)

  def _putTTfontwidths(self, font, maxUni):
    if font['unifilename']:
      ops = os.path.splitext
      cw127fname = ops(font['unifilename'])[0] + '.cw127.pkl'
    else:
      cw127fname = None
    font_dict = load_cache(cw127fname)
    if font_dict is None:
      rangeid        = 0
      range_         = {}
      range_interval = {}
      prevcid        = -2
      prevwidth      = -1
      interval       = False
      startcid       = 1
    else:
      rangeid        = font_dict['rangeid']
      range_         = font_dict['range']
      prevcid        = font_dict['prevcid']
      prevwidth      = font_dict['prevwidth']
      interval       = font_dict['interval']
      range_interval = font_dict['range_interval']
      startcid       = 128
    cwlen = maxUni + 1

    # for each character
    subset = set(font['subset'])
    for cid in range(startcid, cwlen):
      if cid == 128 and cw127fname and not os.path.exists(cw127fname):
        try:
          with open(cw127fname, "wb") as fh:
            font_dict = {}
            font_dict['rangeid']        = rangeid
            font_dict['prevcid']        = prevcid
            font_dict['prevwidth']      = prevwidth
            font_dict['interval']       = interval
            font_dict['range_interval'] = range_interval
            font_dict['range']          = range_
            pickle.dump(font_dict, fh)
        except IOError as e:
          if not e.errno == errno.EACCES:
            raise  # Not a permission error.

      if cid > 255 and (cid not in subset): continue
      width = font['cw'][cid]
      if (width == 0): continue
      if (width == 65535): width = 0

      if ('dw' not in font or (font['dw'] and width != font['dw'])):
        if (cid == (prevcid + 1)):
          if (width == prevwidth):
            if (width == range_[rangeid][0]):
              range_.setdefault(rangeid, []).append(width)
            else:
              range_[rangeid].pop()
              # new range
              rangeid = prevcid
              range_[rangeid] = [prevwidth, width]
            interval = True
            range_interval[rangeid] = True
          else:
            if (interval):
              # new range
              rangeid = cid
              range_[rangeid] = [width]
            else:
              range_[rangeid].append(width)
            interval = False
        else:
          rangeid = cid
          range_[rangeid] = [width]
          interval = False
        prevcid = cid
        prevwidth = width
    prevk = -1
    nextk = -1
    prevint = False

    ri = range_interval
    for k, ws in sorted(range_.items()):
      cws = len(ws)
      if (k == nextk and not prevint and (k not in ri or cws < 3)):
        if (k in ri):
          del ri[k]
        range_[prevk] = range_[prevk] + range_[k]
        del range_[k]
      else:
        prevk = k
      nextk = k + cws
      if (k in ri):
        prevint = (cws > 3)
        del ri[k]
        nextk -= 1
      else:
        prevint = False
    w = []
    for k, ws in sorted(range_.items()):
      if (len(set(ws)) == 1):
        w.append(' %s %s %s' % (k, k + len(ws) - 1, ws[0]))
      else:
        w.append(' %s [ %s ]\n' %
                 (k, ' '.join([str(int(h)) for h in ws])))
    self._out('/W [%s]' % ''.join(w))

  def _putimages(self):
    filter = '' if not self.compress else '/Filter /FlateDecode '   # noqa: F841

    i = [(x[1]["i"], x[1]) for x in self.images.items()]
    i.sort()
    for idx, info in i:
      self._putimage(info)
      del info['data']
      if 'smask' in info:
        del info['smask']

  def _putimage(self, info):
    if 'data' in info:
      self._newobj()
      info['n'] = self.n
      self._out('<</Type /XObject')
      self._out('/Subtype /Image')
      self._out('/Width ' + str(info['w']))
      self._out('/Height ' + str(info['h']))

      if (info['cs'] == 'Indexed'):
        self._out('/ColorSpace [/Indexed /DeviceRGB '  +
                  str(len(info['pal']) // 3 - 1) + ' ' +
                  str(self.n + 1) + ' 0 R]')
      else:
        self._out('/ColorSpace /' + info['cs'])
        if (info['cs'] == 'DeviceCMYK'):
          self._out('/Decode [1 0 1 0 1 0 1 0]')

      self._out('/BitsPerComponent ' + str(info['bpc']))

      if 'f' in info:  self._out('/Filter /' + info['f'])
      if 'dp' in info: self._out('/DecodeParms <<' + info['dp'] + '>>')

      if ('trns' in info and isinstance(info['trns'], list)):
        trns = ''
        for i in range(0, len(info['trns'])):
          trns += str(info['trns'][i]) + ' ' + \
                  str(info['trns'][i]) + ' '
        self._out('/Mask [' + trns + ']')

      if ('smask' in info):
        self._out('/SMask ' + str(self.n + 1) + ' 0 R')

      self._out('/Length ' + str(len(info['data'])) + '>>')
      self._out(pdf_stream(info['data']))
      self._out('endobj')

      # Soft mask
      if ('smask' in info):
        dp = '/Predictor 15 /Colors 1 /BitsPerComponent 8 ' + \
             '/Columns ' + str(info['w'])
        smask = {
          'w'    : info['w'],    'h'    : info['h'],
          'cs'   : 'DeviceGray', 'bpc'  : 8,
          'f'    : info['f'],    'dp'   : dp,
          'data' : info['smask']
        }
        self._putimage(smask)

      # Palette
      if (info['cs'] == 'Indexed'):
        self._newobj()
        filter = self.compress and '/Filter /FlateDecode ' or ''
        if self.compress:
          pal = zlib.compress(info['pal'])
        else:
          pal = info['pal']
        self._out('<<' + filter + '/Length ' + str(len(pal)) + '>>')
        self._out(pdf_stream(pal))
        self._out('endobj')

  def _putxobjectdict(self):
    i = [(x["i"], x["n"]) for x in self.images.values()]
    i.sort()
    for idx, n in i:
      self._out('/I' + str(idx) + ' ' + str(n) + ' 0 R')

  def _putresourcedict(self):
    self._out('/ProcSet [/PDF /Text /ImageB /ImageC /ImageI]')
    self._out('/Font <<')
    f = [(x["i"], x["n"]) for x in self.fonts.values()]
    f.sort()
    for idx, n in f:
      self._out('/F' + str(idx) + ' ' + pdf_ref(n))
    self._out('>>')
    self._out('/XObject <<')
    self._putxobjectdict()
    self._out('>>')

  def _putresources(self):
    self._putfonts()
    self._putimages()

    # Resource dictionary
    self.offsets[2] = len(self.buffer)
    self._out('2 0 obj')
    self._out('<<')
    self._putresourcedict()
    self._out('>>')
    self._out('endobj')

  def _putinfo(self):
    ts = lambda a: enclose_in_parens(a)

    info_d = o_dict()
    # info_d[pdf_name('producer')] = ts('PyFPDF ' + FPDF_VERSION + \
    #     ' https://github.com/alexanderankin/pyfpdf')
    info_d[pdf_name('title')] = ts(getattr(self, 'title', None))
    info_d[pdf_name('subject')] = ts(getattr(self, 'subject', None))
    info_d[pdf_name('author')] = ts(getattr(self, 'author', None))
    info_d[pdf_name('keywords')] = ts(getattr(self, 'keywords', None))
    info_d[pdf_name('creator')] = ts(getattr(self, 'creator', None))

    if hasattr(self, 'creation_date'):
      try:
        creation_date = self.creation_date
        date_string = creation_date.strftime('%Y%m%d%H%M%S')
      except Exception as e:
        fpdf_error('Could not format date: ' + str(creation_date))
    else:
      date_string = datetime.now().strftime('%Y%m%d%H%M%S')
    info_d[pdf_name('CreationDate')] = ts('D:' + date_string)

    return pdf_d(info_d, open_dict='<<\n', close_dict='\n>>',
                 has_empty_fields=True)

  def _putcatalog(self):
    catalog_d = o_dict()
    catalog_d[pdf_name('type')] = pdf_name('catalog')
    catalog_d[pdf_name('pages')] = pdf_ref(1)

    zoom_configs = {
      'default': ['/Fit'],  # TODO FIXME
      'fullpage': ['/Fit'],
      'fullwidth': ['/FitH', 'null'],
      'real': ['/XYZ', 'null', 'null', '1']
    }
    zoom_config = [pdf_ref(3)]
    zoom_config.extend(zoom_configs.get(self.zoom_mode, []))

    # zoom_config is a number, not one of the allowed strings
    if not zoom_config:
      zoom_config = ['/XYZ', 'null', 'null', str(self.zoom_mode / 100)]

    catalog_d[pdf_name('OpenAction')] = pdf_l(zoom_config)

    layout_names = {
      'single': pdf_name('SinglePage'),
      'continuous': pdf_name('OneColumn'),
      'two': pdf_name('TwoColumnLeft')
    }

    if self.layout_mode in layout_names:
      catalog_d[pdf_name('PageLayout')] = layout_names[self.layout_mode]

    return pdf_d(catalog_d, open_dict='<<\n', close_dict='\n>>')

  def _putheader(self):
    self._out('%PDF-' + self.pdf_version)

  def _puttrailer(self):
    self._out('/Size ' + str(self.n + 1))
    self._out('/Root ' + pdf_ref(self.n))
    self._out('/Info ' + pdf_ref(self.n - 1))

  def _enddoc(self):
    self._putheader()
    self._putpages()
    self._putresources()
    # Info
    self._newobj()
    self._out(self._putinfo())
    self._out('endobj')
    # Catalog
    self._newobj()
    self._out(self._putcatalog())
    self._out('endobj')
    # Cross-ref
    o = len(self.buffer)
    self._out('xref')
    self._out('0 ' + (str(self.n + 1)))
    self._out('0000000000 65535 f ')
    for i in range(1, self.n + 1):
      self._out(sprintf('%010d 00000 n ', self.offsets[i]))
    # Trailer
    self._out('trailer')
    self._out('<<')
    self._puttrailer()
    self._out('>>')
    self._out('startxref')
    self._out(o)
    self._out('%%EOF')
    self.state = 3

  def _beginpage(self, orientation, format, same):
    self.page             += 1
    self.pages[self.page]  = {"content": ""}
    self.state             = 2
    self.x                 = self.l_margin
    self.y                 = self.t_margin
    self.font_family       = ''
    self.font_stretching   = 100
    if not same:
      # Page format
      if format:
        # Change page format
        self.fw_pt, self.fh_pt = get_page_format(format, self.k)
      else:
        # Set to default format
        self.fw_pt = self.dw_pt
        self.fh_pt = self.dh_pt
      self.fw = self.fw_pt / self.k
      self.fh = self.fh_pt / self.k
      # Page orientation
      if not orientation:
        orientation = self.def_orientation
      else:
        orientation = orientation[0].upper()
      if orientation == 'P':
        self.w_pt = self.fw_pt
        self.h_pt = self.fh_pt
      else:
        self.w_pt = self.fh_pt
        self.h_pt = self.fw_pt
      self.w = self.w_pt / self.k
      self.h = self.h_pt / self.k
      self.cur_orientation = orientation
      self.page_break_trigger = self.h - self.b_margin
      self.cur_orientation = orientation
    self.pages[self.page]["w_pt"] = self.w_pt
    self.pages[self.page]["h_pt"] = self.h_pt

  def _endpage(self):
    # End of page contents
    self.state = 1

  def _newobj(self):
    # Begin a new object
    self.n += 1
    self.offsets[self.n] = len(self.buffer)
    self._out(str(self.n) + ' 0 obj')

  def _dounderline(self, x, y, txt):
    # Underline text
    up = self.current_font['up']
    ut = self.current_font['ut']
    w  = self.get_string_width(txt, True) + self.ws * txt.count(' ')
    return sprintf('%.2f %.2f %.2f %.2f re f',
                   x * self.k,
                   (self.h - (y - up / 1000.0 * self.font_size)) * self.k,
                   w * self.k,
                   -ut / 1000.0 * self.font_size_pt)

  def _out(self, s):
    # Add a line to the document
    if PY3K and isinstance(s, bytes):
      # manage binary data as latin1 until PEP461-like function is
      # implemented
      s = s.decode("latin1")
    elif not PY3K and isinstance(s, unicode):
      # default encoding (font name and similar)
      s = s.encode("latin1")
    elif not isinstance(s, basestring):
      s = str(s)
    if (self.state == 2):
      self.pages[self.page]["content"] += (s + "\n")
    else:
      self.buffer += (s + "\n")

__all__ = [
  'FPDF', 'load_cache', 'get_page_format', 'PAGE_FORMATS'
]
