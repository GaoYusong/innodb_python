#!/usr/local/bin/python2.7

# Author by GaoYusong, yusong.gao@gmail.com
# All rights reserved

import struct
import binascii

# deault size of innodb page
g_page_size = 16384

class PageHeader:
    def __init__(self, byte_page):
        self.checksum = "0x" + binascii.hexlify(byte_page[0:4])
        self.offset = struct.unpack('>i', byte_page[4:8])[0]
        self.previous = struct.unpack('>i', byte_page[8:12])[0]
        self.next = struct.unpack('>i', byte_page[12:16])[0]

class PageTrailer:
    def __init__(self, byte_page):
        pass
    
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

if __name__ == "__main__":
    byte_pages = read_pages("/home/jianchuan.gys/code/innodb/t.ibd")
    for i in range(20):
        print vars(Page(byte_pages[i]).header)



