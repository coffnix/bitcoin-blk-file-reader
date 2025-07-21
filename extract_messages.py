import binascii
import struct
import sys

def log(string):
    print(string)

def readShortLittleEndian(blockFile):
    return struct.pack(">H", struct.unpack("<H", blockFile.read(2))[0])

def readLongLittleEndian(blockFile):
    return struct.pack(">Q", struct.unpack("<Q", blockFile.read(8))[0])

def readIntLittleEndian(blockFile):
    return struct.pack(">I", struct.unpack("<I", blockFile.read(4))[0])

def hexToInt(value):
    return int(binascii.hexlify(value), 16)

def hexToStr(value):
    return binascii.hexlify(value).decode('utf-8')

def readVarInt(blockFile):
    varInt = blockFile.read(1)[0]
    returnInt = 0
    if varInt < 0xfd:
        return varInt
    if varInt == 0xfd:
        returnInt = readShortLittleEndian(blockFile)
    if varInt == 0xfe:
        returnInt = readIntLittleEndian(blockFile)
    if varInt == 0xff:
        returnInt = readLongLittleEndian(blockFile)
    return int(binascii.hexlify(returnInt), 16)

def readInput(blockFile):
    previousHash = binascii.hexlify(blockFile.read(32)[::-1]).decode('utf-8')
    outId = binascii.hexlify(readIntLittleEndian(blockFile)).decode('utf-8')
    scriptLength = readVarInt(blockFile)
    scriptSignatureRaw = hexToStr(blockFile.read(scriptLength))
    seqNo = binascii.hexlify(readIntLittleEndian(blockFile)).decode('utf-8')

    # Extrair mensagens apenas se for input coinbase
    if previousHash == '0000000000000000000000000000000000000000000000000000000000000000' and outId == 'ffffffff':
        script_hex = scriptSignatureRaw.lower()
        position = 0
        script_len = len(script_hex) // 2
        while position < script_len:
            op_hex = script_hex[position*2:(position+1)*2]
            position += 1
            op = int(op_hex, 16)
            if op == 0:
                continue
            elif op <= 75:
                data_length = op
            elif op == 76:  # OP_PUSHDATA1
                data_length_hex = script_hex[position*2:(position+1)*2]
                data_length = int(data_length_hex, 16)
                position += 1
            elif op == 77:  # OP_PUSHDATA2
                data_length_hex = script_hex[position*2:(position+2)*2]
                data_length = int(data_length_hex, 16)
                position += 2
            elif op == 78:  # OP_PUSHDATA4
                data_length_hex = script_hex[position*2:(position+4)*2]
                data_length = int(data_length_hex, 16)
                position += 4
            else:
                break  # Não é push, parar
            data_hex = script_hex[position*2:(position + data_length)*2]
            position += data_length
            if len(data_hex) // 2 != data_length:
                break  # Dados incompletos
            data_bytes = binascii.unhexlify(data_hex)
            # Verificar se todo o data é ASCII imprimível
            if all(32 <= b <= 126 for b in data_bytes) and len(data_bytes) > 3:
                message = data_bytes.decode('ascii')
                log(message)
        return True # is_coinbase
    
def readOutput(blockFile):
    value = hexToInt(readLongLittleEndian(blockFile)) / 100000000.0
    scriptLength = readVarInt(blockFile)
    blockFile.read(scriptLength)  # Ignorar scriptPubKey, não usado para mensagens

def readTransaction(blockFile):
    extendedFormat = False
    beginByte = blockFile.tell()
    version = hexToInt(readIntLittleEndian(blockFile))
    inputCount = readVarInt(blockFile)

    found_coinbase = False  # Flag para rastrear se encontrou coinbase

    if inputCount == 0:
        extendedFormat = True
        flags = blockFile.read(1)[0]
        if flags != 0:
            inputCount = readVarInt(blockFile)
    for inputIndex in range(0, inputCount):
        if readInput(blockFile):  # readInput agora retorna True se for coinbase
            found_coinbase = True
    outputCount = readVarInt(blockFile)
    for outputIndex in range(0, outputCount):
        readOutput(blockFile)

    if extendedFormat:
        if flags & 1:
            for inputIndex in range(0, inputCount):
                countOfStackItems = readVarInt(blockFile)
                for stackItemIndex in range(0, countOfStackItems):
                    stackLength = readVarInt(blockFile)
                    blockFile.read(stackLength)  # Ignorar witness

    lockTime = hexToInt(readIntLittleEndian(blockFile))

    endByte = blockFile.tell()
    blockFile.seek(beginByte)
    lengthToRead = endByte - beginByte
    blockFile.read(lengthToRead)  # Avançar, preservar leitura

    return found_coinbase  # Retorna se encontrou coinbase

def readBlock(blockFile):
    blockFile.read(4)  # Magic Number, ignorar
    blockFile.read(4)  # Blocksize, ignorar
    blockFile.read(4)  # Version, ignorar
    blockFile.read(32)  # Previous Hash, ignorar
    blockFile.read(32)  # Merkle Hash, ignorar
    blockFile.read(4)  # Time, ignorar
    blockFile.read(4)  # Bits, ignorar
    blockFile.read(4)  # Nonce, ignorar
    countOfTransactions = readVarInt(blockFile)
    for transactionIndex in range(0, countOfTransactions):
        found_coinbase = readTransaction(blockFile)
        if found_coinbase:
            # Pular as transações restantes do bloco
            for remaining in range(transactionIndex + 1, countOfTransactions):
                skipTransaction(blockFile)
            break

def skipTransaction(blockFile):
    """Pula uma transação inteira sem processar"""
    extendedFormat = False
    version = hexToInt(readIntLittleEndian(blockFile))
    inputCount = readVarInt(blockFile)

    if inputCount == 0:
        extendedFormat = True
        flags = blockFile.read(1)[0]
        if flags != 0:
            inputCount = readVarInt(blockFile)
    
    # Pular todos os inputs
    for _ in range(inputCount):
        blockFile.read(32)  # previousHash
        blockFile.read(4)   # outId
        scriptLength = readVarInt(blockFile)
        blockFile.read(scriptLength)  # script
        blockFile.read(4)   # seqNo
    
    # Pular todos os outputs
    outputCount = readVarInt(blockFile)
    for _ in range(outputCount):
        blockFile.read(8)  # value
        scriptLength = readVarInt(blockFile)
        blockFile.read(scriptLength)  # scriptPubKey

    # Pular witness se existir
    if extendedFormat and (flags & 1):
        for _ in range(inputCount):
            countOfStackItems = readVarInt(blockFile)
            for _ in range(countOfStackItems):
                stackLength = readVarInt(blockFile)
                blockFile.read(stackLength)

    blockFile.read(4)  # lockTime

def main():
    blockFilename = sys.argv[1]
    with open(blockFilename, "rb") as blockFile:
        try:
            while True:
                readBlock(blockFile)
        except Exception as e:
            pass  # Parar no fim do arquivo sem erro

if __name__ == "__main__":
    main()