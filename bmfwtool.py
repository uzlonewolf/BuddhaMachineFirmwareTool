import sys
import os.path
import argparse

class crc16:
    def __init__( self, init=0x0, poly=0x1021 ):
        self.poly = poly
        self.initial = init
        self._tab = [ self._initial(i) for i in range(256) ]

    def _initial(self, c):
        crc = 0
        c = c << 8

        for j in range(8):
            if (crc ^ c) & 0x8000:
                crc = (crc << 1) ^ self.poly
            else:
                crc = crc << 1
            c = c << 1
        return crc

    def _update_crc(self, crc, c):
        cc = 0xff & c
        tmp = (crc >> 8) ^ cc
        crc = (crc << 8) ^ self._tab[tmp & 0xff]
        crc = crc & 0xffff
        return crc

    def crc16(self, i):
        crc = self.initial
        for c in i:
            crc = self._update_crc(crc, c)
        return crc


def decode_block( data ):
    xor = 0xEF
    lfsr_taps = 0xe03e
    lfsr_state = 0x84
    lfsr_xor = 0xef
    out = [ ]

    for val in data:
        out.append( val ^ xor )

        newbit = 0
        count = ( lfsr_state & lfsr_taps ) + 1
        while( count ):
            count &= (count - 1)
            newbit += 1

        newbit &= 1
        lfsr_state >>= 1
        lfsr_state |= ( newbit << 15 )

        xor *= 2
        carry = xor >> 8
        xor &= 0xFF

        if( newbit ^ carry ):
            xor ^= 0x21

    return out

def write_single_file( fname, encode, fileheader, files ):
    print( 'Writing: ' + fname )
    with open( fname, 'wb' ) as ofp:

        table_clear = b''
        table_enc = b''

        for thisfile in files:
            table_clear += thisfile.encode_entry( False )
            table_enc += thisfile.encode_entry( True )

        fileheader.data_crc = c16.crc16( table_enc )
        fileheader.crc3 = (fileheader.data_crc << 16) | 0x4452 # "DR"

        ofp.write( fileheader.encode_entry( encode ) )

        if( encode ):
            ofp.write( table_enc )
        else:
            ofp.write( table_clear )

        curpos = ofp.tell()
        odd = (fileheader.start % 0x2000) + (0x2000 - curpos)
        pad = bytes( [ 0xFF ] * odd )
        ofp.write( pad )
        curpos += odd
        pad = bytes( [ 0xFF ] * 0x2000 )

        while curpos < fileheader.start:
            ofp.write( pad )
            curpos += 0x2000



        for thisfile in files:
            if( thisfile.start < ((len(files) + 1) * 0x20) ):
                print( 'Bad start position!' )
            curpos = ofp.tell()

            # ugh, the gap between the last .f1a file and map_table.sys is padded with 0x00's unlike the rest of the file
            if( thisfile.name == 'map_table.sys' and curpos < thisfile.start and (thisfile.start - curpos) < 0x200 ):
                pad = bytes( [ 0x00 ] * (thisfile.start - curpos) )
                ofp.write( pad )

            ofp.seek( thisfile.start )
            ofp.write( thisfile.encode_data( encode ) )


        if( encode ):
            curpos = ofp.tell()
            left = 0x200000 - curpos
            if( left > 0 ):
                odd = left % 0x2000
                left -= odd
                pad = bytes( [ 0xFF ] * odd )
                ofp.write( pad )
                pad = bytes( [ 0xFF ] * 0x2000 )

                while( left > 0 ):
                    ofp.write( pad )
                    left -= 0x2000


def write_multi_files( prefix, force, fileheader, files ):
    fname = prefix + '.filetable.bin'
    print( 'Writing: ' + fname )
    with open( fname, 'wb' ) as ofp:
        table_clear = b''
        table_enc = b''

        for thisfile in files:
            table_clear += thisfile.encode_entry( False )
            table_enc += thisfile.encode_entry( True )

        fileheader.data_crc = c16.crc16( table_enc )
        fileheader.crc3 = (fileheader.data_crc << 16) | 0x4452 # "DR"                                                                                                                                      

        ofp.write( fileheader.encode_entry( False ) )
        ofp.write( table_clear )

    for thisfile in files:
        fname = '%s.%02d.%s.bin' % (prefix, thisfile.index, thisfile.name)
        print( 'Writing: ' + fname )
        with open( fname, 'wb' ) as ofp:
            ofp.write( thisfile.encode_data( False ) )

        if( thisfile.type == 'app' ):
            first_entry = None
            for entry in thisfile.data.entries:
                if( not first_entry ):
                    fname = '%s.%02d.%s.part-%02d.bin' % (prefix, thisfile.index, thisfile.name, entry.index)
                else:
                    fname = '%s.%02d.%s.part-%02d-%02d.bin' % (prefix, thisfile.index, thisfile.name, first_entry.index, entry.index)

                if( entry.length == 0 ):
                    print( 'Skipping 0-length section: ' + fname )
                    continue

                print( 'Writing: ' + fname )
                with open( fname, 'wb' ) as ofp:
                    ofp.write( bytes( [ 0x02 ] ) + entry.load.to_bytes(2, 'big') )

                    if( first_entry ):
                        ofp.seek( first_entry.load )
                        ofp.write( bytes( first_entry.data ) )

                    ofp.seek( entry.load )
                    ofp.write( bytes( entry.data ) )

                if( not first_entry ):
                    first_entry = entry


class FileTypeRaw:
    def __init__( self, data, filetable ):
        self.type = 'raw'
        self.data = data

    def encode( self, encode ):
        return self.data # never encoded

class AppTableEntry:
    def __init__( self, data=None ):
        self.index = 0
        self.length = 0
        self.zero1 = 0
        self.load = 0
        self.zero2 = 0
        self.offset = 0
        self.data_crc = 0
        self.data_crc_calculated = 0
        self.table_crc = 0
        self.table_crc_calculated = 0
        self.data = ''

        if( data ):
            self.decode_entry( data )

    def decode_entry( self, data ):
        if( len(data) != 16 ):
            raise ValueError('App table entry block must be 16 bytes long')

        data = decode_block( data )
        self.table_crc_calculated = c16.crc16( data[:-2] )

        self.index = data[0] << 8 | data[1]
        self.length = data[2] << 8 | data[3]
        self.zero1 = data[4] << 8 | data[5]
        self.load = data[6] << 8 | data[7]
        self.zero2 = data[8] << 8 | data[9]
        self.start = data[10] << 8 | data[11]
        self.data_crc = data[12] << 8 | data[13]
        self.table_crc = data[14] << 8 | data[15]

    def encode_entry( self, encode ):
        block = self.index.to_bytes(2, 'big') + self.length.to_bytes(2, 'big')
        block += self.zero1.to_bytes(2, 'big') + self.load.to_bytes(2, 'big') + self.zero2.to_bytes(2, 'big')
        block += self.start.to_bytes(2, 'big') + self.data_crc.to_bytes(2, 'big')

        self.table_crc = c16.crc16( block )
        block += self.table_crc.to_bytes(2, 'big')

        if( encode ):
            return bytes( decode_block( block ) )

        return block

    def decode_data( self, data ):
        if( len(data) != self.length ):
            raise ValueError('App table data block # %d must be %d bytes long' % (self.index, self.length))

        self.data = decode_block( data )
        self.data_crc_calculated = c16.crc16( self.data )

    def encode_data( self, encode ):
        self.data_crc = c16.crc16( self.data )

        #if( encode ):
        return bytes( decode_block( self.data ) )

class FileTypeApp:
    def __init__( self, data, filetable ):
        self.type = 'app'
        self.entries = [ ]

        self.decode_file( data )

    def decode_file( self, data ):
        entry = AppTableEntry( data[:16] )
        entry_position = 16
        entry.decode_data( data[entry.start:entry.start+entry.length] )
        num_entries = entry.index
        self.entries.append( entry )
        print( '  Added App entry # %d' % entry.index )

        while( num_entries ):
            num_entries -= 1
            entry = AppTableEntry( data[entry_position:entry_position+16] )
            entry_position += 16
            entry.decode_data( data[entry.start:entry.start+entry.length] )
            self.entries.append( entry )

            if( entry.table_crc_calculated == entry.table_crc ):
                tabcheck = 'pass'
            else:
                tabcheck = 'BAD, 0x%04X != 0x%04X' % (entry.table_crc_calculated, entry.table_crc)

            if( entry.data_crc_calculated == entry.data_crc ):
                datcheck = 'pass'
            else:
                datcheck = 'BAD, 0x%04X != 0x%04X' % (entry.data_crc_calculated, entry.data_crc)

            print( '  Added App entry # %d, Table Checksum: %s, Data Checksum: %s' % (entry.index, tabcheck, datcheck) )

    def encode( self, encode ):
        num_entries = len( self.entries ) - 1
        start = (num_entries + 1) * 16
        idx = None
        header = b''
        body = b''

        for e in self.entries:
            thisblock = e.encode_data( encode )
            e.start = start
            e.length = len( thisblock )
            start += e.length
            body += thisblock

            if idx is None:
                e.index = num_entries
                idx = 0
            else:
                e.index = idx
                idx += 1

            header += e.encode_entry( encode )

        return header + body

class FileTypeAudio:
    def __init__( self, data, filetable ):
        self.type = 'f1a'
       	self.data = data

    def encode( self, encode ):
        #if( encode ):
        return self.data


class FileTableEntry:
    def __init__( self, data=None ):
        self.table_crc = 0
        self.table_crc_calculated = 0
        self.data_crc = 0
        self.start = 0
        self.length = 0
        self.crc3 = None
        self.index = 0
        self.name = ''
        self.type = ''
        self.data = ''

        if( data ):
            self.decode_entry( data )

    def decode_entry( self, data ):
        if( len(data) != 32 ):
            raise ValueError('File table data block must be 32 bytes long')

        data = decode_block( data )
        self.table_crc_calculated = c16.crc16( data[2:] )

        self.table_crc = data[0] << 8 | data[1]
        self.data_crc = data[2] << 8 | data[3]
        self.start = data[4] << 24 | data[5] << 16 | data[6] << 8 | data[7]
        self.length = data[8] << 24 | data[9] << 16 | data[10] << 8 | data[11]
        self.index = data[12] << 24 | data[13] << 16 | data[14] << 8 | data[15]

        if( self.length > 0xFFFFF ):
            self.crc3 = self.length
            self.length = self.index * 0x20
            self.type = 'header'
            for c in data[16:]:
                self.name += chr(c)
        else:
            for c in data[16:]:
                if( c == 0xFF ):
                    continue
                if( c == 0x00 ):
                    break
                self.name += chr(c)

            self.type = self.name.split( '.' )[-1].lower()

    def encode_entry( self, encode ):
        block = self.data_crc.to_bytes(2, 'big') + self.start.to_bytes(4, 'big')

        if self.crc3 is None:
            block += self.length.to_bytes(4, 'big')
        else:
            block += self.crc3.to_bytes(4, 'big')

        block += self.index.to_bytes(4, 'big')

        name = self.name
        if( len( name ) < 16 ):
            name += chr( 0 )
        if( len( name ) < 16 ):
            name += chr( 0xFF ) * (16 - len( name ))

        #for c in name:
        #    block += ord( c ).to_bytes(1, 'big')
        block += bytes( [ ord( c ) for c in name ] )

        if self.crc3 is None:
            crc = 0
        else:
            crc = c16.crc16( block )

        block = crc.to_bytes(2, 'big') + block

        if( encode ):
            return bytes( decode_block( block ) )

        return block

    def decode_data( self, data ):
        # .bin and .sys files are not encoded
        if( self.type == 'header' or self.type == 'bin' or self.type == 'sys' ):
            self.data = FileTypeRaw( data, self )
            return

        if( self.type == 'app' ):
            self.data = FileTypeApp( data, self )
            return

        if( self.type == 'f1a' ):
            self.data = FileTypeAudio( data, self )
            return

        raise NotImplementedError( 'Data handler for file type ' + self.type + ' not implemented!' )

    def encode_data( self, encode ):
        return self.data.encode( encode )

if __name__ == '__main__':
    infile = outfile = None
    c16 = crc16()

    arg_parser = argparse.ArgumentParser( description='Buddha Machine firmware tool', epilog="https://old.reddit.com/r/BigCliveDotCom/comments/pmt390/buddha_machine_teardown_with_flash_dump/ \nYoutube video of BigClive's teardown: https://youtube.com/watch?v=LNpbvyLIvN0" )

    arg_parser.add_argument( 'infile', help='Input file', metavar='INFILE' )
    arg_parser.add_argument( '-f', '--force', help='Force (allow) overwriting of the output file(s)', action='store_true' )
    arg_parser.add_argument( '-c', '--clear', help='Outputs the dump as a single file in the clear', metavar='CLEAR' )
    arg_parser.add_argument( '-e', '--encode', help='Outputs the dump as a single encoded file', metavar='ENCODED' )
    arg_parser.add_argument( '-p', '--prefix', help='Outputs the multiple parts as different files named with this prefix', metavar='PREFIX' )

    args = arg_parser.parse_args()
    #print(args)
    infile = str(args.infile)

    if not os.path.exists( infile ):
        print( 'Input file "' + infile + '" not found!' )
        sys.exit( 1 )

    with open( infile, 'rb' ) as ifp:
        good = True
        fileheader = FileTableEntry( ifp.read( 0x20 ) )
        files = [ ]

        block = ifp.read( fileheader.length )

        if( len( block ) != (fileheader.length) ):
            raise EOFError( 'Input file too small!' )

        if( fileheader.table_crc != fileheader.table_crc_calculated ):
            print( 'Header Checksum: BAD, 0x%04X != 0x%04X' % (fileheader.table_crc_calculated, fileheader.table_crc) )
            good = False
        else:
            print( 'Header Checksum: pass' )

        tablecrc = c16.crc16( block )
        if( tablecrc != fileheader.data_crc and tablecrc != fileheader.crc3 >> 16 ):
            print( 'Table Checksum: BAD, 0x%04X != 0x%04X' % (tablecrc, fileheader.data_crc) )
            good = False
        else:
            print( 'Table Checksum: pass' )

        while( len( block ) > 0 ):
            thisfile = FileTableEntry( block[:0x20] )
            fname = 'File # %d "%s"' % (thisfile.index, thisfile.name)
            block = block[0x20:]
            ifp.seek( thisfile.start )
            data = ifp.read( thisfile.length )

            if( len( data ) != (thisfile.length) ):
                print( fname + ' data too small!' )
                break

            datacrc = c16.crc16( data )

            if( datacrc != thisfile.data_crc ):
                print( fname + ' Checksum: BAD, 0x%04X != 0x%04X [data length: %04X]' % (datacrc, thisfile.data_crc, thisfile.length) )
                good = False
            else:
                print( fname + ' Checksum: pass' )

            thisfile.decode_data( data )
            files.append( thisfile )



    if( args.clear is None and args.encode is None and args.prefix is None ):
        print( 'No output file(s) specified, not saving' )

    if( args.clear is not None ):
        filename = str(args.clear)

        if( os.path.exists( filename ) and not args.force ):
            print( 'Clear output file "' + filename + '" exists but --force not specified, not writing file!' )
        else:
            write_single_file( filename, False, fileheader, files )

    if( args.encode is not None ):
        filename = str(args.encode)

        if( os.path.exists( filename ) and not args.force ):
            print( 'Clear output file "' + filename + '" exists but --force not specified, not writing file!' )
        else:
            write_single_file( filename, True, fileheader, files )

    if( args.prefix is not None ):
        prefix = str(args.prefix)

        if( os.path.exists( prefix + '.filetable.bin' ) and not args.force ):
            print( 'Files with the prefix "' + prefix + '" already exist but --force not specified, not writing files!' )
        else:
            write_multi_files( prefix, args.force, fileheader, files )
