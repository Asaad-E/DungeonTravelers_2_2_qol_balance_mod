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

        # Original archives end with the data section padded to 16 bytes
        # (relative to data_start) followed by 8 zero bytes.
        pad_end = (16 - (len(data_section) % 16)) % 16
        res.extend(b'\x00' * (pad_end + 8))
        return bytes(res)


class SkillHelper:
    """Helper for reading and writing skill .bin structures."""
    
    @staticmethod
    def read_skill(bin_data, category):
        p0, p1 = struct.unpack('<2Q', bin_data[8:24])
        name = bin_data[p0:bin_data.find(b'\x00', p0)].decode('latin-1')
        desc = bin_data[p1:bin_data.find(b'\x00', p1)].decode('latin-1')
        
        lvup = ""
        msg = ""
        if category in ['Technique', 'Magic', 'Passive']:
            p2 = struct.unpack('<Q', bin_data[24:32])[0]
            if p2 < len(bin_data):
                lvup = bin_data[p2:bin_data.find(b'\x00', p2)].decode('latin-1')
            # 4th string: battle message shown when the skill triggers ("%name danced the %skill!")
            p3 = struct.unpack('<Q', bin_data[32:40])[0]
            if p3 < len(bin_data):
                msg = bin_data[p3:bin_data.find(b'\x00', p3)].decode('latin-1')

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
            'msg': msg,
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

            # Keep the battle message the 4th pointer refers to (empty for most skills)
            old_p3 = struct.unpack('<Q', fixed_hdr[32:40])[0]
            if old_p3 < len(bin_data):
                msg_bytes = bytes(bin_data[old_p3:bin_data.find(b'\x00', old_p3)+1])
            else:
                msg_bytes = b'\x00'
            pad4 = (8 - ((new_p3 + len(msg_bytes)) % 8)) % 8
            msg_bytes += b'\x00' * pad4

            struct.pack_into('<Q', new_bin, 24, new_p2)
            struct.pack_into('<Q', new_bin, 32, new_p3)

            new_bin.extend(name_bytes)
            new_bin.extend(desc_bytes)
            new_bin.extend(lvup_bytes)
            new_bin.extend(msg_bytes)
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
        # Each string is padded to 8 bytes; the entry itself is not padded further.
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
        
        pad_end = (8 - (len(res) % 8)) % 8   # every string is padded to 8 bytes, the last one too
        res.extend(b'\x00' * pad_end)
        return bytes(res)


class ClassDataHelper:
    """Helper for reading and writing ClassData .bin structures safely."""
    
    @staticmethod
    def read_class(bin_data):
        p_code = struct.unpack('<I', bin_data[0x08:0x0c])[0]
        p_name = struct.unpack('<I', bin_data[0x10:0x14])[0]
        p_desc = struct.unpack('<I', bin_data[0x18:0x1c])[0]
        code = bin_data[p_code:bin_data.find(b'\x00', p_code)].decode('latin-1', 'replace')
        name = bin_data[p_name:bin_data.find(b'\x00', p_name)].decode('latin-1', 'replace')
        desc = bin_data[p_desc:bin_data.find(b'\x00', p_desc)].decode('latin-1', 'replace')
        return {'code': code, 'name': name, 'desc': desc}

    @staticmethod
    def write_class(bin_data, new_desc):
        p_code = struct.unpack('<I', bin_data[0x08:0x0c])[0]
        p_name = struct.unpack('<I', bin_data[0x10:0x14])[0]
        
        code = bin_data[p_code:bin_data.find(b'\x00', p_code)].decode('latin-1', 'replace')
        name = bin_data[p_name:bin_data.find(b'\x00', p_name)].decode('latin-1', 'replace')
        
        hdr = bytearray(bin_data[:0x28])
        b_code = code.encode('latin-1') + b'\x00'
        pad_code = (8 - (len(b_code) % 8)) % 8
        b_code += b'\x00' * pad_code
        
        b_name = name.encode('latin-1') + b'\x00'
        pad_name = (8 - (len(b_name) % 8)) % 8
        b_name += b'\x00' * pad_name
        
        b_desc = new_desc.encode('latin-1') + b'\x00'
        pad_desc = (8 - (len(b_desc) % 8)) % 8
        b_desc += b'\x00' * pad_desc
        
        new_p_code = 0x28
        new_p_name = new_p_code + len(b_code)
        new_p_desc = new_p_name + len(b_name)
        
        struct.pack_into('<I', hdr, 0x08, new_p_code)
        struct.pack_into('<I', hdr, 0x10, new_p_name)
        struct.pack_into('<I', hdr, 0x18, new_p_desc)
        
        return bytes(hdr + b_code + b_name + b_desc)


class StringDataHelper:
    """Helper for reading and writing StringData .bin structures safely."""
    
    @staticmethod
    def read_string(bin_data):
        p = struct.unpack('<I', bin_data[8:12])[0]
        text = bin_data[p:bin_data.find(b'\x00', p)].decode('latin-1', 'replace')
        return text

    @staticmethod
    def write_string(bin_data, new_text):
        hdr = bytearray(bin_data[:16])
        b_str = new_text.encode('latin-1') + b'\x00'
        pad = (8 - (len(b_str) % 8)) % 8
        b_str += b'\x00' * pad
        return bytes(hdr + b_str)


class EquipmentHelper:
    """Helper for reading and writing EquipmentData .bin structures safely."""
    
    @staticmethod
    def read_equipment(bin_data):
        p0 = struct.unpack('<I', bin_data[8:12])[0]
        p1 = struct.unpack('<I', bin_data[16:20])[0]
        p2 = struct.unpack('<I', bin_data[24:28])[0]
        p70 = struct.unpack('<I', bin_data[0x70:0x74])[0] if len(bin_data) > 0x74 else 0
        name = bin_data[p0:bin_data.find(b'\x00', p0)].decode('latin-1', 'replace')
        desc = bin_data[p1:bin_data.find(b'\x00', p1)].decode('latin-1', 'replace')
        s2 = bin_data[p2:bin_data.find(b'\x00', p2)].decode('latin-1', 'replace') if p2 < len(bin_data) else ""
        s70 = bin_data[p70:bin_data.find(b'\x00', p70)].decode('latin-1', 'replace') if p70 < len(bin_data) else name
        return {'name': name, 'desc': desc, 's2': s2, 's70': s70}

    @staticmethod
    def write_equipment(bin_data, new_desc):
        fixed_hdr = bytearray(bin_data[:0x80])
        p0 = struct.unpack('<I', bin_data[8:12])[0]
        p2 = struct.unpack('<I', bin_data[24:28])[0]
        p70 = struct.unpack('<I', bin_data[0x70:0x74])[0]
        
        name_str = bin_data[p0:bin_data.find(b'\x00', p0)].decode('latin-1')
        s2_str = bin_data[p2:bin_data.find(b'\x00', p2)].decode('latin-1')
        s70_str = bin_data[p70:bin_data.find(b'\x00', p70)].decode('latin-1') if p70 < len(bin_data) else name_str

        name_bytes = name_str.encode('latin-1') + b'\x00'
        desc_bytes = new_desc.encode('latin-1') + b'\x00'
        s2_bytes = s2_str.encode('latin-1') + b'\x00'
        s70_bytes = s70_str.encode('latin-1') + b'\x00'

        new_p0 = 0x80
        pad0 = (8 - (len(name_bytes) % 8)) % 8
        name_bytes += b'\x00' * pad0

        new_p1 = new_p0 + len(name_bytes)
        pad1 = (8 - (len(desc_bytes) % 8)) % 8
        desc_bytes += b'\x00' * pad1

        new_p2 = new_p1 + len(desc_bytes)
        pad2 = (8 - (len(s2_bytes) % 8)) % 8
        s2_bytes += b'\x00' * pad2

        new_p70 = new_p2 + len(s2_bytes)
        pad70 = (8 - (len(s70_bytes) % 8)) % 8
        s70_bytes += b'\x00' * pad70

        struct.pack_into('<I', fixed_hdr, 8, new_p0)
        struct.pack_into('<I', fixed_hdr, 16, new_p1)
        struct.pack_into('<I', fixed_hdr, 24, new_p2)
        struct.pack_into('<I', fixed_hdr, 0x70, new_p70)

        res = bytearray(fixed_hdr)
        res.extend(name_bytes)
        res.extend(desc_bytes)
        res.extend(s2_bytes)
        res.extend(s70_bytes)

        pad_end = (8 - (len(res) % 8)) % 8
        res.extend(b'\x00' * pad_end)
        return bytes(res)


class WeaponRankHelper:
    """WeaponRankData entry: int index, -1, u64 name pointer, float delay multiplier at 0x10, -1, name at 0x18."""
    HEADER = 0x18

    @staticmethod
    def read_rank(bin_data):
        p_name = struct.unpack_from('<Q', bin_data, 8)[0]
        return {
            'index': struct.unpack_from('<i', bin_data, 0)[0],
            'delay': struct.unpack_from('<f', bin_data, 0x10)[0],
            'name': bin_data[p_name:bin_data.find(b'\x00', p_name)].decode('latin-1'),
        }

    @staticmethod
    def write_rank(bin_data, new_name):
        hdr = bytearray(bin_data[:WeaponRankHelper.HEADER])
        struct.pack_into('<Q', hdr, 8, WeaponRankHelper.HEADER)
        b_name = new_name.encode('latin-1') + b'\x00'
        b_name += b'\x00' * ((8 - (len(b_name) % 8)) % 8)
        return bytes(hdr + b_name)


class TrapHelper:
    """Helper for reading and writing TrapData .bin structures safely."""
    
    @staticmethod
    def read_trap(bin_data):
        p_name = struct.unpack('<I', bin_data[8:12])[0]
        name = bin_data[p_name:bin_data.find(b'\x00', p_name)].decode('latin-1', 'replace')
        return name

    @staticmethod
    def write_trap(bin_data, new_name):
        hdr = bytearray(bin_data[:0x20])
        struct.pack_into('<I', hdr, 0x08, 0x20)
        b_name = new_name.encode('latin-1') + b'\x00'
        pad = (8 - ((0x20 + len(b_name)) % 8)) % 8
        b_name += b'\x00' * pad
        return bytes(hdr + b_name)


class TrophyHelper:
    """Helper for reading and writing TrophyData .bin structures safely."""
    
    @staticmethod
    def read_trophy(bin_data):
        p_title = struct.unpack('<I', bin_data[8:12])[0]
        p_desc = struct.unpack('<I', bin_data[16:20])[0]
        title = bin_data[p_title:bin_data.find(b'\x00', p_title)].decode('latin-1', 'replace')
        desc = bin_data[p_desc:bin_data.find(b'\x00', p_desc)].decode('latin-1', 'replace')
        return {'title': title, 'desc': desc}

    @staticmethod
    def write_trophy(bin_data, new_desc, new_title=None):
        p_title = struct.unpack('<I', bin_data[8:12])[0]
        orig_title = bin_data[p_title:bin_data.find(b'\x00', p_title)].decode('latin-1')
        title_str = new_title if new_title is not None else orig_title
        
        hdr = bytearray(bin_data[:24])
        b_title = title_str.encode('latin-1') + b'\x00'
        pad_title = (8 - (len(b_title) % 8)) % 8
        b_title += b'\x00' * pad_title
        
        new_p_desc = 24 + len(b_title)
        struct.pack_into('<I', hdr, 16, new_p_desc)
        
        b_desc = new_desc.encode('latin-1') + b'\x00'
        pad_desc = (8 - (len(b_desc) % 8)) % 8
        b_desc += b'\x00' * pad_desc
        
        return bytes(hdr + b_title + b_desc)





