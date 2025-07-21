# bitcoin-blk-file-reader

Reads the blkXXXXX.dat files from bitcoind (Bitcoin Core).  
A implementação é em Python e inclui:

- suporte ao formato de transação com witness (SegWit)
- cálculo correto do hash da transação (txid)
- extração de mensagens ocultas da coinbase
- verificação cruzada com altura real do bloco usando bitcoin-cli

## Requisitos

Certifique-se de que o `bitcoind` esteja rodando e com o RPC habilitado.  
No `bitcoin.conf`, você deve ter:

```
rpcuser=coffnix
rpcpassword=a1b2c3d4e5f6
```

Essas credenciais são configuráveis no topo do script `extract_messages_with_index.py`.

## Caminho padrão dos arquivos

Normalmente os arquivos de bloco `.dat` ficam em:

```
/storage2/bitcoin/blocks/
```

## Uso

### Análise básica de blocos

```bash
python analyze.py /storage2/bitcoin/blocks/blk00040.dat
```

### Extração de mensagens da coinbase

```bash
python extract_messages.py /storage2/bitcoin/blocks/blk00040.dat
```

### Extração de mensagens com índice real e altura correta do bloco

```bash
python extract_messages_with_index.py /storage2/bitcoin/blocks/blk00040.dat
```

Você pode passar um segundo argumento para filtrar por string:

```bash
python extract_messages_with_index.py /storage2/bitcoin/blocks/blk00040.dat "Jesus"
```

A saída mostrará o índice sequencial, altura do bloco (real, via bitcoin-cli), offset e mensagens ASCII com 20 ou mais caracteres.

---
