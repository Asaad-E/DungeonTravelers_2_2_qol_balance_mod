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


class ItemHelper:
    """Helper for reading and writing ItemData .bin structures safely."""
    
    @staticmethod
    def read_item(bin_data):
        p0, p1 = struct.unpack('<2Q', bin_data[8:24])
        p60 = struct.unpack('<Q', bin_data[0x60:0x68])[0]
        name = bin_data[p0:bin_data.find(b'\x00', p0)].decode('latin-1')
        desc = bin_data[p1:bin_data.find(b'\x00', p1)].decode('latin-1')
        name2 = bin_data[p60:bin_data.find(b'\x00', p60)].decode('latin-1') if p60 < len(bin_data) else ""
        return {'name': name, 'desc': desc, 'name2': name2}

    @staticmethod
    def write_item(bin_data, new_desc):
        fixed_hdr = bytearray(bin_data[:0x70])
        p0, p1 = struct.unpack('<2Q', bin_data[8:24])
        p60 = struct.unpack('<Q', bin_data[0x60:0x68])[0]
        
        name_str = bin_data[p0:bin_data.find(b'\x00', p0)].decode('latin-1')
        name2_str = bin_data[p60:bin_data.find(b'\x00', p60)].decode('latin-1') if p60 < len(bin_data) else name_str
        
        name_bytes = name_str.encode('latin-1') + b'\x00'
        desc_bytes = new_desc.encode('latin-1') + b'\x00'
        name2_bytes = name2_str.encode('latin-1') + b'\x00'
        
        new_p0 = 0x70
        pad0 = (8 - (len(name_bytes) % 8)) % 8
        name_bytes += b'\x00' * pad0
        
        new_p1 = new_p0 + len(name_bytes)
        pad1 = (8 - (len(desc_bytes) % 8)) % 8
        desc_bytes += b'\x00' * pad1
        
        new_p60 = new_p1 + len(desc_bytes)
        pad60 = (8 - (len(name2_bytes) % 8)) % 8
        name2_bytes += b'\x00' * pad60
        
        struct.pack_into('<Q', fixed_hdr, 8, new_p0)
        struct.pack_into('<Q', fixed_hdr, 16, new_p1)
        struct.pack_into('<Q', fixed_hdr, 0x60, new_p60)
        
        res = bytearray(fixed_hdr)
        res.extend(name_bytes)
        res.extend(desc_bytes)
        res.extend(name2_bytes)
        pad_end = (8 - (len(res) % 8)) % 8
        res.extend(b'\x00' * pad_end)
        return bytes(res)


class SealScrollHelper:
    """Helper for reading and writing SealScrollData .bin structures safely."""
    
    @staticmethod
    def read_seal(bin_data):
        p0 = struct.unpack('<I', bin_data[8:12])[0]
        p1 = struct.unpack('<I', bin_data[16:20])[0]
        p38 = struct.unpack('<I', bin_data[0x38:0x3c])[0]
        name = bin_data[p0:bin_data.find(b'\x00', p0)].decode('latin-1')
        desc = bin_data[p1:bin_data.find(b'\x00', p1)].decode('latin-1')
        name2 = bin_data[p38:bin_data.find(b'\x00', p38)].decode('latin-1') if p38 < len(bin_data) else ""
        return {'name': name, 'desc': desc, 'name2': name2}

    @staticmethod
    def write_seal(bin_data, new_desc):
        fixed_hdr = bytearray(bin_data[:0x48])
        p0 = struct.unpack('<I', bin_data[8:12])[0]
        p38 = struct.unpack('<I', bin_data[0x38:0x3c])[0]
        name_str = bin_data[p0:bin_data.find(b'\x00', p0)].decode('latin-1')
        name2_str = bin_data[p38:bin_data.find(b'\x00', p38)].decode('latin-1') if p38 < len(bin_data) else name_str

        name_bytes = name_str.encode('latin-1') + b'\x00'
        desc_bytes = new_desc.encode('latin-1') + b'\x00'
        name2_bytes = name2_str.encode('latin-1') + b'\x00'

        new_p0 = 0x48
        pad0 = (8 - (len(name_bytes) % 8)) % 8
        name_bytes += b'\x00' * pad0

        new_p1 = new_p0 + len(name_bytes)
        pad1 = (8 - (len(desc_bytes) % 8)) % 8
        desc_bytes += b'\x00' * pad1

        new_p38 = new_p1 + len(desc_bytes)
        pad38 = (8 - (len(name2_bytes) % 8)) % 8
        name2_bytes += b'\x00' * pad38

        struct.pack_into('<I', fixed_hdr, 8, new_p0)
        struct.pack_into('<I', fixed_hdr, 16, new_p1)
        struct.pack_into('<I', fixed_hdr, 0x38, new_p38)

        res = bytearray(fixed_hdr)
        res.extend(name_bytes)
        res.extend(desc_bytes)
        res.extend(name2_bytes)
        pad_end = (16 - (len(res) % 16)) % 16
        res.extend(b'\x00' * pad_end)
        return bytes(res)


class JoinSkillHelper:
    """Helper for reading and writing JoinSkillData .bin structures safely."""
    
    @staticmethod
    def read_joint(bin_data):
        p0 = struct.unpack('<I', bin_data[8:12])[0]
        p1 = struct.unpack('<I', bin_data[16:20])[0]
        name = bin_data[p0:bin_data.find(b'\x00', p0)].decode('latin-1')
        desc = bin_data[p1:bin_data.find(b'\x00', p1)].decode('latin-1')
        return {'name': name, 'desc': desc}

    @staticmethod
    def write_joint(bin_data, new_desc):
        fixed_hdr = bytearray(bin_data[:0x98])
        p0 = struct.unpack('<I', bin_data[8:12])[0]
        name_str = bin_data[p0:bin_data.find(b'\x00', p0)].decode('latin-1')

        name_bytes = name_str.encode('latin-1') + b'\x00'
        desc_bytes = new_desc.encode('latin-1') + b'\x00'

        new_p0 = 0x98
        pad0 = (8 - (len(name_bytes) % 8)) % 8
        name_bytes += b'\x00' * pad0

        new_p1 = new_p0 + len(name_bytes)
        pad1 = (8 - (len(desc_bytes) % 8)) % 8
        desc_bytes += b'\x00' * pad1

        struct.pack_into('<I', fixed_hdr, 8, new_p0)
        struct.pack_into('<I', fixed_hdr, 16, new_p1)

        res = bytearray(fixed_hdr)
        res.extend(name_bytes)
        res.extend(desc_bytes)

        # 0x20 is unpadded length before 8-byte align pad
        struct.pack_into('<I', res, 0x20, len(res))
        pad_end = (8 - (len(res) % 8)) % 8
        if pad_end == 0:
            pad_end = 8
        res.extend(b'\x00' * pad_end)
        return bytes(res)


class EnchantHelper:
    """Helper for reading and writing EnchantData .bin structures safely."""
    
    @staticmethod
    def read_enchant(bin_data):
        p0 = struct.unpack('<I', bin_data[8:12])[0]
        p1 = struct.unpack('<I', bin_data[16:20])[0]
        p2 = struct.unpack('<I', bin_data[24:28])[0] if len(bin_data) > 28 else 0
        name = bin_data[p0:bin_data.find(b'\x00', p0)].decode('latin-1') if p0 < len(bin_data) else ""
        prefix = bin_data[p1:bin_data.find(b'\x00', p1)].decode('latin-1') if p1 < len(bin_data) else ""
        suffix = bin_data[p2:bin_data.find(b'\x00', p2)].decode('latin-1') if p2 < len(bin_data) else ""
        return {'name': name, 'prefix': prefix, 'suffix': suffix}

    @staticmethod
    def write_enchant(bin_data, new_name):
        fixed_hdr = bytearray(bin_data[:0x38])
        p1 = struct.unpack('<I', bin_data[16:20])[0]
        p2 = struct.unpack('<I', bin_data[24:28])[0]
        prefix_str = bin_data[p1:bin_data.find(b'\x00', p1)].decode('latin-1') if p1 < len(bin_data) else ""
        suffix_str = bin_data[p2:bin_data.find(b'\x00', p2)].decode('latin-1') if p2 < len(bin_data) else ""

        name_bytes = new_name.encode('latin-1') + b'\x00'
        prefix_bytes = prefix_str.encode('latin-1') + b'\x00'
        suffix_bytes = suffix_str.encode('latin-1') + b'\x00'

        new_p0 = 0x38
        pad0 = (8 - (len(name_bytes) % 8)) % 8
        name_bytes += b'\x00' * pad0

        new_p1 = new_p0 + len(name_bytes)
        pad1 = (8 - (len(prefix_bytes) % 8)) % 8
        prefix_bytes += b'\x00' * pad1

        new_p2 = new_p1 + len(prefix_bytes)
        pad2 = (8 - (len(suffix_bytes) % 8)) % 8
        suffix_bytes += b'\x00' * pad2

        struct.pack_into('<I', fixed_hdr, 8, new_p0)
        struct.pack_into('<I', fixed_hdr, 16, new_p1)
        struct.pack_into('<I', fixed_hdr, 24, new_p2)

        res = bytearray(fixed_hdr)
        res.extend(name_bytes)
        res.extend(prefix_bytes)
        res.extend(suffix_bytes)
        pad_end = (16 - (len(res) % 16)) % 16
        res.extend(b'\x00' * pad_end)
        return bytes(res)


class PartySkillHelper:
    """Helper for reading and writing PartySkillData .bin structures safely."""
    
    @staticmethod
    def read_party_skill(bin_data):
        p0 = struct.unpack('<Q', bin_data[8:16])[0]
        p1 = struct.unpack('<Q', bin_data[16:24])[0]
        p2 = struct.unpack('<Q', bin_data[24:32])[0]
        name = bin_data[p0:bin_data.find(b'\x00', p0)].decode('latin-1')
        s1 = bin_data[p1:bin_data.find(b'\x00', p1)].decode('latin-1')
        s2 = bin_data[p2:bin_data.find(b'\x00', p2)].decode('latin-1')
        req = s1.split('\n')[0]
        effect = s1.split('\n')[1] if '\n' in s1 else ""
        return {'name': name, 'req': req, 'effect': effect, 's1': s1, 's2': s2}

    @staticmethod
    def write_party_skill(bin_data, new_effect):
        p0 = struct.unpack('<Q', bin_data[8:16])[0]
        p1 = struct.unpack('<Q', bin_data[16:24])[0]
        p2 = struct.unpack('<Q', bin_data[24:32])[0]
        fixed_hdr = bytearray(bin_data[:p0])
        name_str = bin_data[p0:bin_data.find(b'\x00', p0)].decode('latin-1')
        s1 = bin_data[p1:bin_data.find(b'\x00', p1)].decode('latin-1')
        req_str = s1.split('\n')[0]
        
        new_s1 = f"{req_str}\n{new_effect}"
        new_s2 = f"{req_str}\n  {new_effect}"
        
        name_bytes = name_str.encode('latin-1') + b'\x00'
        s1_bytes = new_s1.encode('latin-1') + b'\x00'
        s2_bytes = new_s2.encode('latin-1') + b'\x00'
        
        new_p0 = p0
        pad0 = (8 - (len(name_bytes) % 8)) % 8
        name_bytes += b'\x00' * pad0
        
        new_p1 = new_p0 + len(name_bytes)
        pad1 = (8 - (len(s1_bytes) % 8)) % 8
        s1_bytes += b'\x00' * pad1
        
        new_p2 = new_p1 + len(s1_bytes)
        pad2 = (8 - (len(s2_bytes) % 8)) % 8
        s2_bytes += b'\x00' * pad2
        
        struct.pack_into('<Q', fixed_hdr, 8, new_p0)
        struct.pack_into('<Q', fixed_hdr, 16, new_p1)
        struct.pack_into('<Q', fixed_hdr, 24, new_p2)
        
        res = bytearray(fixed_hdr)
        res.extend(name_bytes)
        res.extend(s1_bytes)
        res.extend(s2_bytes)
        
        pad_end = (16 - (len(res) % 16)) % 16
        res.extend(b'\x00' * pad_end)
        return bytes(res)


class FoodMenuHelper:
    """Helper for reading and writing FoodMenuData .bin structures safely."""
    
    @staticmethod
    def read_food_menu(bin_data):
        p0 = struct.unpack('<Q', bin_data[8:16])[0]
        p1 = struct.unpack('<Q', bin_data[16:24])[0]
        name = bin_data[p0:bin_data.find(b'\x00', p0)].decode('latin-1')
        desc = bin_data[p1:bin_data.find(b'\x00', p1)].decode('latin-1')
        lines = desc.split('\n')
        flavor = lines[0]
        effect = lines[1] if len(lines) > 1 else ""
        return {'name': name, 'flavor': flavor, 'effect': effect, 'desc': desc}

    @staticmethod
    def write_food_menu(bin_data, new_effect):
        p0 = struct.unpack('<Q', bin_data[8:16])[0]
        p1 = struct.unpack('<Q', bin_data[16:24])[0]
        fixed_hdr = bytearray(bin_data[:p0])
        name_str = bin_data[p0:bin_data.find(b'\x00', p0)].decode('latin-1')
        orig_desc = bin_data[p1:bin_data.find(b'\x00', p1)].decode('latin-1')
        flavor = orig_desc.split('\n')[0]
        new_desc = f"{flavor}\n{new_effect}"
        
        name_bytes = name_str.encode('latin-1') + b'\x00'
        desc_bytes = new_desc.encode('latin-1') + b'\x00'
        
        new_p0 = p0
        pad0 = (8 - (len(name_bytes) % 8)) % 8
        name_bytes += b'\x00' * pad0
        
        new_p1 = new_p0 + len(name_bytes)
        pad1 = (8 - (len(desc_bytes) % 8)) % 8
        desc_bytes += b'\x00' * pad1
        
        struct.pack_into('<Q', fixed_hdr, 8, new_p0)
        struct.pack_into('<Q', fixed_hdr, 16, new_p1)
        
        res = bytearray(fixed_hdr)
        res.extend(name_bytes)
        res.extend(desc_bytes)
        
        pad_end = (16 - (len(res) % 16)) % 16
        res.extend(b'\x00' * pad_end)
        return bytes(res)


class EnemyAttackHelper:
    """Helper for reading and writing EnemyAttackData .bin structures safely."""
    
    @staticmethod
    def read_enemy_attack(bin_data):
        p0 = struct.unpack('<Q', bin_data[8:16])[0]
        p1 = struct.unpack('<Q', bin_data[16:24])[0]
        p2 = struct.unpack('<Q', bin_data[24:32])[0]
        p3 = struct.unpack('<Q', bin_data[32:40])[0]
        name = bin_data[p0:bin_data.find(b'\x00', p0)].decode('latin-1', 'replace')
        desc = bin_data[p3:bin_data.find(b'\x00', p3)].decode('latin-1', 'replace')
        return {'name': name, 'desc': desc, 'p0': p0, 'p1': p1, 'p2': p2, 'p3': p3}

    @staticmethod
    def write_enemy_attack(bin_data, new_desc):
        p0 = struct.unpack('<Q', bin_data[8:16])[0]
        p1 = struct.unpack('<Q', bin_data[16:24])[0]
        p2 = struct.unpack('<Q', bin_data[24:32])[0]
        p3 = struct.unpack('<Q', bin_data[32:40])[0]
        
        fixed_hdr = bytearray(bin_data[:p0])
        name_bytes = bytearray(bin_data[p0:bin_data.find(b'\x00', p0) + 1])
        jp_bytes = bytearray(bin_data[p1:bin_data.find(b'\x00', p1) + 1])
        s2_bytes = bytearray(bin_data[p2:bin_data.find(b'\x00', p2) + 1])
        new_desc_bytes = bytearray(new_desc.encode('latin-1') + b'\x00')
        
        new_p0 = p0
        pad0 = (8 - (len(name_bytes) % 8)) % 8
        name_bytes += b'\x00' * pad0
        
        new_p1 = new_p0 + len(name_bytes)
        pad1 = (8 - (len(jp_bytes) % 8)) % 8
        jp_bytes += b'\x00' * pad1
        
        new_p2 = new_p1 + len(jp_bytes)
        pad2 = (8 - (len(s2_bytes) % 8)) % 8
        s2_bytes += b'\x00' * pad2
        
        new_p3 = new_p2 + len(s2_bytes)
        
        struct.pack_into('<Q', fixed_hdr, 8, new_p0)
        struct.pack_into('<Q', fixed_hdr, 16, new_p1)
        struct.pack_into('<Q', fixed_hdr, 24, new_p2)
        struct.pack_into('<Q', fixed_hdr, 32, new_p3)
        
        res = bytearray(fixed_hdr)
        res.extend(name_bytes)
        res.extend(jp_bytes)
        res.extend(s2_bytes)
        res.extend(new_desc_bytes)
        
        pad_end = (16 - (len(res) % 16)) % 16
        res.extend(b'\x00' * pad_end)
        return bytes(res)

