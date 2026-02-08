import struct
import os

def extract_simple(pak_path):
    with open(pak_path, 'rb') as f:
        header = f.read(12)
        magic, offset, length = struct.unpack('<4sII', header)
        if magic != b'PACK': 
            print("Inte en PACK-fil")
            return
        
        f.seek(offset)
        num_files = length // 64
        for _ in range(num_files):
            entry = f.read(64)
            # Vi läser 56 bytes för namnet, 4 för offset, 4 för storlek
            name_raw, file_offset, file_size = struct.unpack('<56sII', entry)
            
            # ÄNDRING: Använd latin-1 istället för ascii för att undvika krasch
            filename = name_raw.decode('latin-1').strip('\x00').replace('\x00', '')
            
            # Skapa mappar (viktigt för t.ex. progs/ eller maps/)
            os.makedirs(os.path.dirname(filename) or '.', exist_ok=True)
            
            # Spara filens nuvarande position i indexet
            current_pos = f.tell()
            
            # Gå till filens data och läs den
            f.seek(file_offset)
            data = f.read(file_size)
            
            with open(filename, 'wb') as out:
                out.write(data)
                
            # Gå tillbaka till nästa fil i indexet
            f.seek(current_pos)
            print(f"Extraherade: {filename}")

extract_simple("pak1.pak")
