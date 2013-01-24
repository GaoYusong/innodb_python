#!/usr/local/bin/python2.7

# Author by GaoYusong, yusong.gao@gmail.com
# All rights reserved

import struct
import binascii
from pprint import pprint

# deault size of innodb page
g_page_size = 16384

# page_type is defined by innodb source fil0fil.h
# next code is from innodb_ruby author by Jeremy Cole (https://github.com/jeremycole)
g_page_type = {
    0     : 'ALLOCATED',      # Freshly allocated page
    2     : 'UNDO_LOG',       # Undo log page
    3     : 'INODE',          # Index node
    4     : 'IBUF_FREE_LIST', # Insert buffer free list
    5     : 'IBUF_BITMAP',    # Insert buffer bitmap
    6     : 'SYS',            # System page
    7     : 'TRX_SYS',        # Transaction system data
    8     : 'FSP_HDR',        # File space header
    9     : 'XDES',           # Extent descriptor page
    10    : 'BLOB',           # Uncompressed BLOB page
    11    : 'ZBLOB',          # First compressed BLOB page
    12    : 'ZBLOB2',         # Subsequent compressed BLOB page
    17855 : 'INDEX',          # B-tree node
    }

class PageHeader:
    def __init__(self, byte_page):
        self.checksum  = struct.unpack('>I', byte_page[0:4])[0]
        self.offset    = struct.unpack('>I', byte_page[4:8])[0]
        self.previous  = struct.unpack('>I', byte_page[8:12])[0]
        self.next      = struct.unpack('>I', byte_page[12:16])[0]
        self.lsn64     = struct.unpack('>Q', byte_page[16:24])[0]
        self.page_type = g_page_type[struct.unpack('>H', byte_page[24:26])[0]]
        self.flush_lsn = struct.unpack('>Q', byte_page[26:34])[0]
        self.space_id  = struct.unpack('>I', byte_page[34:38])[0]

class PageTrailer:
    def __init__(self, byte_page):
        self.old_checksum = struct.unpack(">I", byte_page[16376:16380])[0]
        self.lsn32        = struct.unpack(">I", byte_page[16380:16384])[0]
        
# Page
# attribute
#     byte_page
#     header    type: PageHeader
#     trailer   type: PageTrailer
class Page:
    def __init__(self, byte_page):
        self.byte_page = byte_page
        self.header = PageHeader(byte_page)
        self.trailer = PageTrailer(byte_page)

# @in FilePath = ibd file path
# @out byte pages list in this ibd file, every page's size is g_page_size
def read_pages(file_path):
    f = open(file_path, "rb")
    byte_pages = []
    while True:
        byte_page = f.read(g_page_size)
        if not byte_page: break
        byte_pages.append(byte_page)
    f.close()
    return byte_pages

def pages(byte_pages):
    pages = []
    for byte_page in byte_pages:
        pages.append(Page(byte_page))
    return pages

# order unique pages depend by page type
# like [index, index, allocated, index] -> [index, allocated, index]
def space_page_type_regions(pages):
    if len(pages) == 1:
        return []
    regions = []
    n = len(pages)
    start = 0
    for x in range(1, n + 1):
        if x == n or pages[x].header.page_type != pages[x - 1].header.page_type:
            region = {
                "start" : start,
                "end"   : x - 1,
                "count" : x - start,
                "type"  : pages[x - 1].header.page_type
                }
            regions.append(region)
            start = x
    return regions

def format_space_page_type_regions(regions):
    print "start\tend\tcount\ttype"
    for region in regions:
        print "%d\t%d\t%d\t%s" % (region["start"], region["end"],
                                  region["count"], region["type"])
    
if __name__ == "__main__":
    byte_pages = read_pages("/home/jianchuan.gys/code/innodb/t.ibd")
    regions = space_page_type_regions(pages(byte_pages))
    format_space_page_type_regions(regions)





