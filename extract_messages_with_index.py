import sys
import struct
import re
import subprocess

# CONFIGURAÇÕES
bitcoin_cli_path = "/usr/bin/bitcoin-cli"
rpc_user = "coffnix"
rpc_password = "a1b2c3d4e5f6"

if len(sys.argv) < 2:
    print("Usage: python mensagens_blk.py /path/to/blkXXXXX.dat [optional_filter]")
    sys.exit(1)

filename = sys.argv[1]
filtro = sys.argv[2] if len(sys.argv) > 2 else None

magic = b'\xf9\xbe\xb4\xd9'
header_size = 80

def get_block_hash_from_header(header_bytes):
    sha256_1 = subprocess.Popen(["openssl", "dgst", "-sha256", "-binary"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    sha256_2 = subprocess.Popen(["openssl", "dgst", "-sha256", "-binary"], stdin=sha256_1.stdout, stdout=subprocess.PIPE)
    sha256_1.stdin.write(header_bytes)
    sha256_1.stdin.close()
    final_hash = subprocess.check_output(["xxd", "-p", "-c", "64"], stdin=sha256_2.stdout)
    hexes = final_hash.decode().strip()
    hash_bytes = [hexes[i:i+2] for i in range(0, len(hexes), 2)]
    return ''.join(reversed(hash_bytes))

def get_block_height(block_hash):
    try:
        output = subprocess.check_output([
            bitcoin_cli_path,
            "-rpcuser=" + rpc_user,
            "-rpcpassword=" + rpc_password,
            "getblockheader", block_hash, "true"
        ]).decode()
        for line in output.splitlines():
            if '"height"' in line:
                return int(line.strip().split(":")[1].strip().strip(","))
    except:
        return None

with open(filename, "rb") as f:
    data = f.read()

offset = 0
index = 0

while True:
    idx = data.find(magic, offset)
    if idx == -1:
        break

    try:
        block_len = struct.unpack("<I", data[idx + 4:idx + 8])[0]
        full_block = data[idx + 8 : idx + 8 + block_len]
        header = full_block[:header_size]

        block_hash = get_block_hash_from_header(header)
        height = get_block_height(block_hash)

        matches = re.findall(rb'[ -~]{20,}', full_block)
        mensagens_encontradas = []

        for m in matches:
            msg = m.decode("utf8", errors="ignore").strip()
            if not filtro or filtro in msg:
                mensagens_encontradas.append(msg)

        if mensagens_encontradas:
            altura = height if height is not None else "unknown"
            print(f"Index #{index} (height: {altura}) @ offset {idx}")
            for msg in mensagens_encontradas:
                print(msg)
            print("-" * 60)

    except Exception:
        pass

    offset = idx + 8 + block_len
    index += 1
