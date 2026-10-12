import struct

def inspect_bin(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()
    print(f"=== {filepath} (len={len(data)}) ===")
    p_code = struct.unpack('<I', data[0x08:0x0c])[0]
    p_name = struct.unpack('<I', data[0x10:0x14])[0]
    p_desc = struct.unpack('<I', data[0x18:0x1c])[0]
    print(f"Pointers: code={hex(p_code)}, name={hex(p_name)}, desc={hex(p_desc)}")
    # Header is 0x28 (40 bytes)
    # Let's inspect ints/shorts in header:
    ints = struct.unpack('<10I', data[:0x28])
    print(f"Header uint32s: {ints}")
    # After desc, is there anything?
    print(f"Data from 0x20 to 0x28: {data[0x20:0x28].hex()}")

inspect_bin('mod_project/backups/ClassData.pck')
