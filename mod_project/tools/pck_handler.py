import struct
import os

class PckArchive:
    """
    Parser and bit-exact builder for Aquaplus / Sting PCK archive format.
    Accurately preserves 0x14 unpadded marker, 8-byte Pack boundary,
    4-byte header pad, and 16-byte relative data alignment.
    """
    def __init__(self, filepath=None):
        self.files = [] # list of (filename, bytearray)
        if filepath:
            self.load(filepath)

    def load(self, filepath):
        with open(filepath, 'rb') as f:
            data = f.read()

        pack_idx = data.find(b'Pack                ')
        if pack_idx == -1:
            raise ValueError(f"Not a valid PCK archive (missing 'Pack' header): {filepath}")

        hdr_size, file_count = struct.unpack('<II', data[pack_idx+20:pack_idx+28])
        
        # Read filenames from table (offsets relative to 0x18)
        filenames = []
        for i in range(file_count):
            fn_rel = struct.unpack('<I', data[0x18 + i*4:0x18 + (i+1)*4])[0]
            fn_abs = 0x18 + fn_rel
            fn_end = data.find(b'\x00', fn_abs)
            filenames.append(data[fn_abs:fn_end].decode('latin-1'))

        # Read file entries
        self.files = []
        entry_pos = pack_idx + 28
        for i in range(file_count):
            off, sz = struct.unpack('<II', data[entry_pos:entry_pos+8])
            self.files.append((filenames[i], bytearray(data[off:off+sz])))
            entry_pos += 8

    def save(self, output_path):
        data = self.build()
        with open(output_path, 'wb') as f:
            f.write(data)

    def build(self):
        file_count = len(self.files)
        table_size = file_count * 4
        fn_offsets = []
        fn_bytes = bytearray()
        cur_fn_offset = table_size

        for fn, _ in self.files:
            fn_offsets.append(cur_fn_offset)
            b = fn.encode('latin-1') + b'\x00'
            fn_bytes.extend(b)
            cur_fn_offset += len(b)

        fn_section = bytearray()
        for o in fn_offsets:
            fn_section.extend(struct.pack('<I', o))
        fn_section.extend(fn_bytes)

        # In Aquaplus PCK:
        # Offset 0x14 stores the unpadded end of filename data: 0x18 + len(fn_section)
        unpadded_end = 0x18 + len(fn_section)
        # Pack header starts at next 8-byte boundary
        pack_offset = (unpadded_end + 7) & ~7
        pad_to_pack = pack_offset - unpadded_end
        fn_section.extend(b'\x00' * pad_to_pack)

        pack_magic = b'Pack                '
        pack_hdr_size = 20 + 8 + file_count * 8
        # Fixed 4-byte pad between pack_hdr and data_start
        data_start = pack_offset + pack_hdr_size + 4

        file_entries = []
        data_section = bytearray()
        cur_off = data_start

        for _, content in self.files:
            # 16-byte alignment relative to data_start
            rel_off = cur_off - data_start
            align_pad = (16 - (rel_off % 16)) % 16
            if align_pad:
                data_section.extend(b'\x00' * align_pad)
                cur_off += align_pad
            file_entries.append((cur_off, len(content)))
            data_section.extend(content)
            cur_off += len(content)

        pack_hdr = bytearray()
        pack_hdr.extend(pack_magic)
        pack_hdr.extend(struct.pack('<II', pack_hdr_size, file_count))
        for o, s in file_entries:
            pack_hdr.extend(struct.pack('<II', o, s))

        # 4-byte pad between header and data
        pack_hdr.extend(b'\x00\x00\x00\x00')

        res = bytearray()
        res.extend(b'Filename            ')
        res.extend(struct.pack('<I', unpadded_end))
        res.extend(fn_section)
        res.extend(pack_hdr)
        res.extend(data_section)

        # Pad total file to 16 bytes
        pad_end = (16 - (len(res) % 16)) % 16
        res.extend(b'\x00' * pad_end)
        return bytes(res)


class SkillHelper:
    """Helper for reading and writing skill .bin structures."""
    
    @staticmethod
    def read_skill(bin_data, category):
        p0, p1 = struct.unpack('<2Q', bin_data[8:24])
        name = bin_data[p0:bin_data.find(b'\x00', p0)].decode('latin-1')
        desc = bin_data[p1:bin_data.find(b'\x00', p1)].decode('latin-1')
        
        lvup = ""
        if category in ['Technique', 'Magic', 'Passive']:
            p2 = struct.unpack('<Q', bin_data[24:32])[0]
            if p2 < len(bin_data):
                lvup = bin_data[p2:bin_data.find(b'\x00', p2)].decode('latin-1')
                
        max_lv = 0
        tp_prog = []
        if category in ['Technique', 'Magic']:
            for off in range(0x5c, 0x84, 4):
                tp_val = struct.unpack('<i', bin_data[off:off+4])[0]
                if 1 <= tp_val <= 100:
                    tp_prog.append(tp_val)
                else:
                    break
            max_lv = len(tp_prog)
            
        return {
            'name': name,
            'desc': desc,
            'lvup': lvup,
            'max_lv': max_lv,
            'tp_prog': tp_prog
        }

    @staticmethod
    def write_skill(bin_data, category, new_desc, new_lvup=None):
        fixed_hdr_size = {
            'Technique': 0x1f0,
            'Magic': 0x238,
            'Passive': 0xd8,
            'Unique': 0x60
        }.get(category, 0x1f0)
        
        fixed_hdr = bin_data[:fixed_hdr_size]
        p0 = struct.unpack('<Q', fixed_hdr[8:16])[0]
        name_bytes = bin_data[p0:bin_data.find(b'\x00', p0)+1]
        
        desc_bytes = new_desc.encode('latin-1') + b'\x00'
        
        new_p0 = fixed_hdr_size
        new_p1 = new_p0 + len(name_bytes)
        pad1 = (8 - (new_p1 % 8)) % 8
        name_bytes += b'\x00' * pad1
        new_p1 += pad1
        
        new_bin = bytearray(fixed_hdr)
        struct.pack_into('<Q', new_bin, 8, new_p0)
        struct.pack_into('<Q', new_bin, 16, new_p1)
        
        if category in ['Technique', 'Magic', 'Passive']:
            lvup_str = new_lvup if new_lvup is not None else ""
            lvup_bytes = lvup_str.encode('latin-1') + b'\x00'
            
            new_p2 = new_p1 + len(desc_bytes)
            pad2 = (8 - (new_p2 % 8)) % 8
            desc_bytes += b'\x00' * pad2
            new_p2 += pad2
            
            new_p3 = new_p2 + len(lvup_bytes)
            pad3 = (8 - (new_p3 % 8)) % 8
            lvup_bytes += b'\x00' * pad3
            new_p3 += pad3
            
            struct.pack_into('<Q', new_bin, 24, new_p2)
            struct.pack_into('<Q', new_bin, 32, new_p3)
            
            new_bin.extend(name_bytes)
            new_bin.extend(desc_bytes)
            new_bin.extend(lvup_bytes)
        else:
            new_bin.extend(name_bytes)
            new_bin.extend(desc_bytes)
            
        pad_total = (8 - (len(new_bin) % 8)) % 8
        new_bin.extend(b'\x00' * pad_total)
        return bytes(new_bin)
