# bitcoin-blk-file-reader
Reads the blkXXXXX.dat files from bitcoind (Bitcoin-Core).  
The implementation is in Python e inclui suporte ao formato de transação com witness (SegWit), cálculo correto do hash da transação (txid) e agora também a extração de mensagens de transações coinbase.

## Usage
Normalmente seu cliente bitcoind armazena os arquivos blk em:

```
/storage2/bitcoin/blocks/
```

Para ler o arquivo de bloco específico, como o `blk00040.dat`:

```shell
python analyze.py /storage2/bitcoin/blocks/blk00040.dat
```

Ou para extrair mensagens ocultas em transações coinbase:

```shell
python extract_messages.py /storage2/bitcoin/blocks/blk00040.dat
```

Esse último script localiza automaticamente os blocos via magic bytes, identifica transações coinbase e tenta decodificar mensagens ASCII legíveis no scriptSig.

## Novas funcionalidades do extract_messages.py

- Busca por blocos reais com magic bytes `f9beb4d9`
- Extração e decodificação de coinbase scriptSig
- Suporte a múltiplas mensagens por bloco
- Filtragem por mensagens ASCII legíveis
- Caminho de entrada `.dat` via argumento obrigatório

## Exemplo de saída

```
Bloco encontrado na posição: 0x00000000
Mensagem extraída:
hi from poolserverj
```

## Aviso

Alguns endereços multisig ainda não são calculados corretamente, pois o suporte ainda não foi adicionado.  
O código foi escrito como protótipo inicial e pode conter melhorias pendentes.  
Sinta-se à vontade para modificar ou entrar em contato para discutir melhorias.
