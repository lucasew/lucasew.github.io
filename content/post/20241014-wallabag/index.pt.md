---
date: 2024-10-14T00:00:00
title: 'Wallabag no NixOS'
summary: 'A saga para configurar o Wallabag como um módulo integrado com HTTPS no NixOS'
math: false
showToc: true
alsoAvailable:
  - https://blog-do-lucao.vercel.app/post/20241014-wallabag/
---

Eae pessoal!!! Quanto tempo!

Depois de muito tempo, decidi desempoeirar o blog com o side project do momento.

Ultimanente to com um interesse em autocustodiar algumas coisas. Uma delas é o
Pocket. Não pelo Pocket ser ruim ou ter melhorado tanto que piorou mas porque eu
queria tentar algo diferente.

Tempo atrás achei esse tal de [Wallabag](https://wallabag.org/), que é
basicamente um Pocket/Instapaper selfhosted feito em Symphony/PHP.

Fim de semana tava meio de saco cheio e não tinha nada programado pra sair então
resolvi meter o louco e tirar um pouco a ferrugem da minha config NixOS.

A config do NixOS nem tava ruim, só que eu cheguei num ponto que eu não tava
precisando mais mexer. Tava usando branch stable então basicamente não tinha
nenhum ajuste que precisava fazer entre bumps então tava bem mó paz mesmo, não
tinha porque mexer.

Basicamente esse projeto aconteceu nas seguintes fases:

- Fazer o wallabag funcionar como módulo NixOS
- Criar o vhost
- Importar os artigos do Pocket de do Instapaper
- Configurar os clientes (principalmente o app Android)

# Fazendo funcionar

Porque faz todo sentido preguiçoso, eu não comecei do zero, ~~roubei código~~
tomei inspiração no trabalho de
[outra pessoa](https://cce.whatthefuck.computer/updates#20231106T181545.910122)
e tive que fazer uns ajustes pra minha situação, também fazendo umas adaptações
para ficar no padrão de módulos do nixpkgs.

Meu requisito era que funcionasse numa rede interna Tailscale, não tenho
intenção de expor pra Internet, o que simplifica muito as coisas, até certo
ponto.

Depois de vários ajustes o código do módulo ficou
[assim](https://github.com/lucasew/nixcfg/blob/854cda49af1800a3e481f617fcdad7d29d6499c3/nix/nodes/common/services/wallabag.nix#L1).

Uma coisa que eu gostei bastante do resultado, além de funcionar, é claro, é que
eu fiz o `console` do Wallabag (basicamente um php-artisan da vida) já entrar no
usuário do serviço certo então o script em sí já sobe no usuário certo.

Uma coisa que trouxe dificuldade é que o Wallabag reclama se falta alguma config
no parameters.yaml então tem que especificar todas as chaves nem que seja com
null.

# Criar o vhost

De início eu usei o nginx pra criar um vhost HTTP como eu já fazia em
basicamente todos os serviços mas o Wallabag é muito xarope com HTTPS então eu
tinha que achar um jeito.

O app oficial se nega a funcionar sobre HTTP mesmo que eu já tenha a
criptografia do wireguard já segurando as pontas. É HTTPS ou GTFO. Eu podia usar
SSL autoassinado mas fiquei com preguiça de fazer tudo na mão. Ou eu automatizo
o processo ou deixo quieto.

Nessa me dei conta que o Tailscale consegue criar certificados TLS mesmo que não
esteja usando Tailscale Funnel. É um tanto imperativo usando o daemon do sistema
mas eu já tinha uma carta na manga que era só adaptar pra funcionar nesse caso.

O [ts-proxy](https://github.com/lucasew/ts-proxy) é basicamente um proxy reverso
que expõe uma porta HTTP como um serviço ou nó em uma rede Tailscale. Com
MagicDNS já ganho DNS de graça e com aquela manha do TLS eu já consigo fazer
HTTPS na rede local.

Depois de uns ajustes isso foi entregue na versão 0.5.0. Como eu fiz cagada na
release lancei a 0.5.1 arrumando. Não tem novidade nenhuma, só correção da minha
cagada pra fazer release.

Agora com um módulo simples consigo subir um ts-proxy para cada serviço que eu
quero expor, TLS fica atrás de um enable, ou flag se chamar o ts-proxy direto,
token pra autorizar o nó é provisionado com sops-nix. Na primeira vez tem que
autorizar o serviço no dashboard do Tailscale e depois tudo funciona sem ter que
expor pra Internet e com certificado let's encrypt depois de um warmup de uns
10s se o TLS tiver ativado.

Com esse ajuste do HTTPS o aplicativo oficial, que eu tentei patchear sem
sucesso pra aceitar HTTP, funcionou sem problemas e começou finalmente a
sincronizar.

# Importar artigos do Pocket e do Instapaper

É nessa parte que filho chora e mãe não vê, porque eu sou usuário Pocket desde
2015 e nessa conta tem uma quantidade imoral de artigos. Quanto imoral? Imoral
assim:

![tenho tanto artigo na minha conta do pocket que pra exportar os dados tive que apelar](power_guido.png)

Eu tinha começado a importar os artigos antes de configurar HTTPS então o fluxo
OAuth pra importar do Pocket não funcionava e o importador do Instapaper
funciona com um arquivo que o serviço exporta. Por causa da quantidade de
artigos o import travava o Wallabag inteiro e dava em Gateway Time Out.

Fiz na mão. Basicamente usei uma lib de cliente do Wallabag em Python e
respectivamente um parser de CSV do Instapaper e um export pra JSON continuável
do Pocket.

Primeiro dumpei o Pocket com esse script:

```python
# cria um app oauth lá
consumer_key = "CHANGEME"
access_token = "CHANGEME"

from pocket import Pocket
from pathlib import Path
import json

pocket = Pocket(consumer_key, access_token)

output_dir = Path('.').parent / "pocket_fetched"


def index_gen():
    offset = 0
    batch_size = 30
    while True:
        yield offset
        offset += batch_size
for offset in index_gen():
    file_name = output_dir / f"fetch_{offset:04}.json"
    if file_name.exists():
        continue
    print(f"fetch offset={offset}")
    res, _headers = pocket.get(
        images=1,
        videos=1,
        tags=1,
        rediscovery=1,
        annotations=1,
        authors=1,
        itemOptics=1,
        meta=1,
        posts=1,
        total=1,
        forceaccount=1,
        offset=offset,
        count=30,  # max count per request according to api docs
        state='all',
        sort='newest',
        detailType='complete',
    )
    if res.get('list') is not None and len(res['list']) == 0:
        break
    file_name.write_text(json.dumps(res))
```

E pra aplicar:

```python
from wallabag.api.add_entry import AddEntry, Params as AddEntryParams
from wallabag.entry import Entry
from wallabag.config import Configs
from pathlib import Path
import json
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import random
import sys
import contextlib
import io

pocket_fetched = Path('.').parent / "pocket_fetched"
config_file = Path.home() / ".config/wallabag-cli/config.ini"

config = Configs(config_file)

def find_urls():
    for bundle in pocket_fetched.glob('*.json'):
        data = json.loads(bundle.read_text())
        if data.get('error') is not None:
            bundle.unlink()
            continue
        for post in data['list'].values():
            print(post)
            url = post.get('resolved_url', post.get('given_url'))
            if url is None:
                continue
            yield AddEntry(config, url, {
                AddEntryParams.READ: post['status'] == 1,
                AddEntryParams.TITLE: post['resolved_title'],
                AddEntryParams.STARRED: post['favorite'] == 1
            })

data = find_urls()
data  = list(data)
# print(data[:4])
# exit(0)
random.shuffle(data)
with tqdm(total=len(data), desc="Ingerindo artigos", miniters=1, file=sys.stdout) as ops:
    def ingest_once(item):
        try:
            ops.update()
            ops.refresh(nolock=True)
            sys.stdout.flush()
            entry = item.request().response
            entry = Entry(entry)
            return entry
        except Exception as e:
            # pass
            print(e, file=sys.stdout)

    with ThreadPoolExecutor(max_workers=16) as tp:
        for item in tp.map(ingest_once, data):
            pass
            # if item is not None:
            #     ops.set_description(f"Ingerido {item.url}")
    print(folders)
```

E para fazer ingestão do Instapaper

```python
from wallabag.api.add_entry import AddEntry, Params as AddEntryParams
from wallabag.entry import Entry
from wallabag.config import Configs
from pathlib import Path
import csv
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import random
import sys
import contextlib
import io

config_file = Path.home() / ".config/wallabag-cli/config.ini"

config = Configs(config_file)

url = "https://google.com"
starred = False
read = False
# print(entry)

folders = set()

with open("instapaper-export.csv", 'r') as f:
    data = csv.DictReader(f)
    data  = list(data)
    random.shuffle(data)
    with tqdm(total=len(data), desc="Ingerindo artigos", miniters=1, file=sys.stdout) as ops:
        def ingest_once(item):
            try:
                # print('item', item)
                folder = item['Folder']
                title = item['Title']
                url = item['URL']
                ops.update()
                ops.refresh(nolock=True)
                sys.stdout.flush()
                entry = Entry(AddEntry(config, url, {
                    AddEntryParams.READ: folder == 'Archive',
                    AddEntryParams.TITLE: title
                #     AddEntryParams.STARRED: starred
                }).request().response)
                return entry
            except Exception as e:
                # pass
                print(e, file=sys.stdout)

        with ThreadPoolExecutor(max_workers=16) as tp:
            for item in tp.map(ingest_once, data):
                pass
                # if item is not None:
                #     ops.set_description(f"Ingerido {item.url}")
        print(folders)
```

No total isso deu em 14449 artigos depois de rodar o comando de deduplicação de
artigos da instância.

Tinha uma quantidade significativa de ids sem links no Pocket, provavelmente
soft-deletes.
