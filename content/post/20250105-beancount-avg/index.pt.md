---
date: 2025-01-05T00:00:00
title: Média de posição no Beancount
summary: A saga para fazer o Beancount funcionar direito com as regras Brasileiras do mercado de ações
---

Eae pessoal. Primeiro post do ano!

Esse ano, ali por Junho, depois de muito estudo para entender como a banda toca,
pelo menos na teoria, eu resolvi começar a praticar um pouco essa coisa de
investir dinheiro.

Por inércia eu tinha todo o meu capital acumulado em poupança. Eu fui criado
desde cedo a guardar dinheiro e tava já ciente que poupança tem uma relação
risco/rentabilidade bem meh, mas por outro lado é um negócio com zero
manutenção.

Outros meios já podem ter a questão do leão, de ter que declarar imposto de
renda, e confesso que eu tava com um tanto de cagaço dessa parte então eu tinha
que entrar já sabendo decentemente como o jogo funciona.

Tecnicamente já tinha alguma experiência com corretoras porque eu já ganhei
cripto de airdrop e eu cheguei a dar uma brincada com o que eu ganhei no airdrop
do Keybase (Stellar), além de algumas migalhas de faucet. Quando eu descobri que
eu fui elegível no airdrop do Starknet, pela minha atividade no nixpkgs, eu já
sabia que tinha que vender para uma cripto de verdade, como o BTC, o quanto
antes. Sepa ainda faço um post a parte sobre essa saga. Eu já tenho todos os
dados das transações reunidos na ferramenta que eu vou falar sobre nesse post.

## O que caraglios ser Beancount?

[Beancount](https://github.com/beancount/beancount) é basicamente uma ferramenta
de contabilidade em texto puro. Basicamente você escreve as transações entre
contas em arquivos de texto usando a linguagem da ferramenta, que é bem simples,
e ela valida se as transações estão certas, se as asserções de balanço batem e
se não batem, qual o tamanho do rombo. Seria o tipo de ferramenta ideal para
estruturar dados do portal da transparência se não fosse tão lento para o tanto
de dado que tem lá.

É uma ferramenta em Python que possui a funcionalidade de plugins, que podem ser
escritos em Python e linkados nos seus beancounts. Além de controlar dinheiro
ela também funciona para controlar ativos, como ações e fundos imobiliários.

As contas seguem um padrão hierárquico e tem no nome os seguintes prefixos
obrigatórios:

- `Assets`: O que você tem
- `Liabilities`: O que você deve
- `Expenses`: No que você gastou
- `Income`: O que você ganhou
- `Equity`: Basicamente é usado para começar a usar

Para começar primeiro você precisa inicializar o saldo. Como não dá pra sempre
ser retroativo e pegar transações desde o começo você provavelmente vai querer
inicializar com um saldo inicial.

O jeito é você pegar o saldo inicial de `Equity:Opening-Balances`. Você pode
depois ir fazendo as transações de forma retroativa conforme for tendo tempo ou
interesse. Não é obrigatório preencher transação desde o início dos tempos.

Exemplo:

```beancount
2025-01-01 pad Assets:Banco:ContaCorrente Equity:Opening-Balances
2025-01-01 balance Assets:Banco:ContaCorrente 420.69BRL
```

Você poderia usar uma transação normal? Poderia. Mas com `pad` fica mais fácil,
não precisa pensar nisso e funciona.

Um detalhe extremamente importante que vai te evitar dor de cabeça é que o
**beancount só conta a transação no balanço no próximo dia**. Se você colocou
uma transação no dia 1 e já botou ela num `balance` o `balance` não vai passar.
Isso pode dar uns problemas menores usando importers.

## O projeto

Para definir a compra de uma ação, por exemplo, você precisa passar a posição de
compra. Basicamente o preço que você pagou por ela. O Beancount então faz o
"câmbio" e coloca o valor cambiado no balanço.

Exemplo:

```beancount
2025-01-01 * "Compra de ações 1"
  Assets:Banco:Acao 1 B3_MXRF11 {9.20BRL} ;; Não é indicação de investimento
  Expenses:Banco:Taxa 0.10 BRL
  Assets:Banco:ContaCorrente

2025-01-01 * "Compra de ações 2"
  Assets:Banco:Acao 1 B3_MXRF11 {9.10BRL}
  Expenses:Banco:Taxa 0.10 BRL
  Assets:Banco:ContaCorrente
```

Até ai tudo certo. No Fava, infelizmente, na seção Patrimônio o B3_MXRF11 vai
aparecer duas vezes, o que não é bem desejável. No Brasil Ibovespa, pelo menos,
nós queremos saber o preço médio da posição, que no caso é `9.15BRL`, só que o
Beancount não suporta esse caso. Nessa eu tentei algumas soluções.

### A primeira solução: Plugin

Plugins são basicamente funções Python que recebem a base parseada e um
dicionário de opções e entregam a base parseada mais transações adicionais e uma
lista de erros durante o processo.

Porém, algum problema no Beancount faz ele validar as transações antes e depois
da execução dos plugins, logo, o plugin não roda direito porque as transações
dão erro antes de rodar o plugin. E esse erro só acontece depois de registrar
uma venda nas posições. Tentei bastante tentar passar por cima disso mas sem
alterar o código em sí pra não checar os erros antes de passar para os plugins
não rola. E eu to usando o Beancount 2.x, que eventualmente vai ser depreciado.
E o Beancount 3.x tem umas breaking changes que eu to com preguiça de arrumar,
principalmente na parte dos extratores.

Depois de um tempo empurrando com a barriga movi para outro aproach.

### A segunda solução: Codegen

Além de poder escrever plugins em Python, o Beancount pode ser usado como uma
biblioteca. Isso permite você escrever geradores de código e lógicas custom que
consomem as primitivas do Beancount. E foi o que eu fiz. Cada transação e
posting pode ter um dicionário de valores que você pode definir e no plugin
procurar por esses valores para passar alguma configuração para esse plugin. Eu
basicamente buscava uma opção na diretiva `open`, que cria a conta, para checar
se essa solução vai trabalhar com essa conta e ai quando ele detectava uma
compra ou venda de uma ação na conta ele atualizava o preço médio com uma
transação semelhante a essa:

```beancount
2024-09-25 * "BEANCOUNT" "Equilíbrio de preço médio"
  doc_name: "corretagem.pdf"
  Assets:BR:BB:Acao  -20 B3_MXRF11 {10.00 BRL, 2024-08-07}
  Assets:BR:BB:Acao  -10 B3_MXRF11 {9.99 BRL, 2024-09-25}
  Assets:BR:BB:Acao   30 B3_MXRF11 {9.996666666666666666666666667 BRL, 2024-09-25}
```

Para deixar idempotente, todas as transações geradas vinham com Payee igual a
BEANCOUNT, ai eu poderia pular elas na iteração e ai ele gerava o que precisava
alterar.

Essa propriedade doc_name é outro plugin. Basicamente eu salvo minhas notas de
corretagem na pasta docs do meu repositório e basicamente sigo o padrão
`YYYYMMDD-$nome` sendo nome o valor de doc_name e a data obtida da data de
transação. É mais copypaste friendly. Recomendo essa abordagem. Daria para
automatizar ainda mais BTW.

## Como eu uso

Agora tenho um negócio basicamente automatizado. Eu só chamo um script e ele
arruma a bagunça. Chamo outro e ele atualiza os preços. Chamo um terceiro pelo
rofi e ele sincroniza o repositório Git. No celular, rodo o script de backup e
já tenho o backup 3 2 1.

A cada dia 2 eu gero os extratos de todas as contas, enquanto isso pego o saldo
de cada uma e crio os `balance` no `balances.beancount`. Baixo os extratos. PDF
para o Mercado Pago, CSV para o Banco do Brasil. Chamo um script que faz
ingestão. Dou nome aos bois nas transações geradas, removo duplicatas. Baixo
todas as notas de corretagem e preencho os dados no `b3.beancount`. Rodo o
script para equalizar os preços médios, debugo eventuais rombos e é isso ai.
Todo mês tem um Pix para um nome estranho, mas que no final das contas é um
estabelecimento conhecido.

Com dinheiro físico é mais difícil porque não tem rastro, ai eu que lute pra
descobrir o porque o saldo final esperado tá 155 reais maior que o que tem.

E o mais legal de tudo isso é que é uma ferramenta 100% local, sem política de
privacidade, sem servidor tendo que rodar 24/7, sem lock-in, usando como base
tecnologias que já funcionavam bem sepa desde antes de eu existir.

## Os scripts

### Script para preço médio

Ele espera que esteja em uma pasta dentro do repositório, que o beancount
principal seja o `main.beancount` e que salva os resultados no
`fixes.beancount`.

```python
#!/usr/bin/env python3
from beancount import loader
from beancount.core import data
from beancount.parser import printer
from pathlib import Path
import sys

FIXES_FILE = Path(__file__).parent.parent / "fixes.beancount"
MAIN_FILE = Path(__file__).parent.parent / "main.beancount"

fixers = {}
def fixer(func):
    fixers[func.__name__] = func
    return func


def counter(initial=0):
    i = initial
    while True:
        yield i
        i += 1


@fixer
def b3(entries):
    from collections import defaultdict
    import datetime
    from decimal import Decimal

    initial_date = datetime.date(1970, 1, 1)

    class Price():
        def __init__(self, amount, price, date):
            self.amount = amount
            if not isinstance(self.amount, Decimal):
                self.amount = Decimal(self.amount)
            self.price = price
            if not isinstance(self.price, Decimal):
                self.price = Decimal(self.price)
            assert isinstance(date, datetime.date)
            self.date = date

        def value(self, amount):
            if not isinstance(amount, Decimal):
                amount = Decimal(amount)
            return self.price * amount

        def __repr__(self):
            return f"Price(amount={self.amount}, price={self.price} day={self.date})"

    class AccountState():
        def __init__(self, currency):
            self.currency = currency
            self.price = defaultdict(lambda: Price(0, 0, initial_date))

        def handle_posting(self, entry, account, amount, price, share_currency):
            if self.price[share_currency].date == initial_date:
                self.price[share_currency].date = entry.date
                self.price[share_currency].amount = amount
                self.price[share_currency].price = price
                print(self.price[share_currency], account, amount, price, share_currency, file=sys.stderr)
                return None
            if amount == 0:
                return None
            default_args = dict(
                narration="Equilíbrio de preço médio",
                date=entry.date,
                meta=entry.meta,
                flag='*',
                tags=set(),
                links=set(),
            )
            if amount < 0:
                self.price[share_currency].amount += amount # - ia somar
                print(self.price[share_currency], account, amount, price, share_currency, file=sys.stderr)
                return
            final_cost = (self.price[share_currency].amount * self.price[share_currency].price) + (amount * price)
            final_amount = (self.price[share_currency].amount + amount)
            final_avgcost = final_cost / final_amount
            ret = dict(
                **default_args,
                postings=[
                    dict(
                        account=account,
                        units=data.Amount(-self.price[share_currency].amount, share_currency),
                        cost=data.Cost(self.price[share_currency].price, self.currency, self.price[share_currency].date, None),
                    ),
                    dict(
                        account=account,
                        units=data.Amount(-amount, share_currency),
                        cost=data.Cost(price, self.currency, entry.date, None),
                    ),
                    dict(
                        account=account,
                        units=data.Amount(final_amount, share_currency),
                        cost=data.Cost(final_avgcost, self.currency, entry.date, None),
                    )
                ]
            )
            ret['postings'] = [posting for posting in ret['postings'] if posting['units'].number != 0]
            self.price[share_currency].date = entry.date
            self.price[share_currency].amount = final_amount
            self.price[share_currency].price = final_avgcost
            print(self.price[share_currency], account, amount, price, share_currency, file=sys.stderr)
            return ret
    errors = []
    extra_entries = []
    accounts = []
    currencies = {}
    line_counter = counter(initial=1)
    price = {}

    yield dict(
        narration="Teste",
        date=datetime.date.today(),
        postings=[]
    )

    for entry in entries:
        if isinstance(entry, data.Open):
            if entry.meta.get('b3_automations') == "TRUE":
                price[entry.account] = AccountState(
                    currency = entry.meta.get('b3_currency', 'BRL')
                )
            continue
        # print(entry)
        if isinstance(entry, data.Transaction):
            date = entry.date
            for posting in entry.postings:
                amount = posting.units.number
                currency = posting.units.currency
                if posting.cost is None:
                    continue
                cost = posting.cost.number
                cost_currency = posting.cost.currency
                account = posting.account
                # print(list(price.keys()))
                if account not in list(price.keys()):
                    continue

                if cost_currency != price[account].currency:
                    errors.append(f"in {entry.meta.filename}:{entry.meta.fileno}: invalid currency: expected: {cost_currency} got: {price[entry.account].currency}")
                    continue
                new_entry = price[account].handle_posting(
                    entry=entry,
                    account=account,
                    amount=amount,
                    price=cost,
                    share_currency=currency,
                )
                if new_entry is None:
                    continue
                yield new_entry


if __name__ == '__main__':
    default_transaction = dict(
        meta=None,
        flag="*",
        payee="BEANCOUNT",
        narration="",
        tags=set(),
        links=set(),
        postings=[]
    )
    default_posting = dict(
        price=None,
        flag=None,
        meta=None,
    )
    entries, _, _ = loader.load_file(Path(__file__).parent.parent / "main.beancount")
    entries = [entry for entry in entries if not (isinstance(entry, data.Transaction) and entry.payee == "BEANCOUNT")]
    with FIXES_FILE.open('w') as f:
        print(';; Generated using scripts/codegen_fixes.py. Do not edit.', file=f)
        print(file=f)
        for fixer_name, fixer in fixers.items():
            for item in fixer(entries):
                processed_item = data.Transaction(**{
                    **default_transaction,
                    **item,
                    'postings': [data.Posting(**{**default_posting, **posting}) for posting in item.get('postings', [])]
                })
                printer.print_entry(processed_item, file=f)
```

### Plugin de documentos

Ele espera que esteja em uma pasta no repositório e que o repositório tenha a
pasta docs

Use a diretiva `plugin` para usar.

```python
from beancount.core import data
from datetime import date
from pathlib import Path
import sys

__plugins__ = ["autodocs"]

DOCS_FOLDER=Path(__file__).parent.parent / "docs"

def autodocs(entries, options_map):
    extra_entries = []
    for entry in entries:
        if not isinstance(entry, data.Transaction):
            continue
        # print(entry)
        doc_name = entry.meta.get('doc_name')
        if doc_name is None:
            continue
        doc_account = entry.meta.get('doc_account')
        if doc_account is None:
            if len(entry.postings) > 0:
                doc_account=entry.postings[0].account
        if doc_account is None:
            continue
        tx_date = entry.date
        to_append = data.Document(
            meta=data.new_metadata(entry.meta['filename'], entry.meta['lineno']),
            account=doc_account,
            filename=str(DOCS_FOLDER / f"{tx_date.year}{tx_date.month:02}{tx_date.day:02}-{doc_name}"),
            date=tx_date,
            tags=set(),
            links=set(),
        )
        # print(entry, file=sys.stderr)
        # print(to_append, file=sys.stderr)
        extra_entries.append(to_append)
    return [*entries, *extra_entries], []
```
