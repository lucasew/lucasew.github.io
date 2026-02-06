---
date: 2025-05-15T00:00:00
title: 'Como configurar o Renovate'
summary: 'Como manter as dependências dos seus projetos abertos atualizadas sem precisar gastar muito tempo'
---

Aqui é o Lucão e finalmente arrumei um erro de configuração no meu GitHub.

Não sei se já vem assim ou foi uma cagada que meu eu do passado fez mas se
alguém aleatório mandasse um PR em um repositório meu eu nem ia ficar sabendo
porque eu não era avisado.

Acontece que na
[configuração de notificações](https://github.com/settings/notifications) do
GitHub, watching estava só para notificar no GitHub. Selecionei para notificar
no e-mail e resolveu. Agora se eu receber algum PR em algum projeto que eu
esteja de olho eu fico sabendo.

Se eu não quiser mais saber de cada coisa que acontece em tal repositório é só
eu mudar o watch dele para só menções e resolvido. Foi o meu caso no nixpkgs.

Porque esse começo importa? Porque a principal fonte de PRs é o dependabot,
basicamente ele manda PRs atualizando dependências. Quebra um galho mas não é lá
tão exaustivo, e como você vai perceber, não é tão automático.

Um bot um tanto melhor nisso é o Mend Renovate, que basicamente funciona de
forma completa de graça.

Ataques de supply chain e vulnerabilidades estão acontecendo cada vez mais e
alguns dos PRs do Renovate inclusive incluem provas de conceito das
vulnerabilidades sendo corrigidas na atualização. Alguns PRs tem um release
notes completo das versões no intervalo. É realmente caprichado.

# O Renovate

O Renovate é um add-on, que pode ser
[auto-hospedado](https://github.com/renovatebot/renovate) e é usado para manter
dependências atualizadas de forma Jidoka (automação com toque humano). Ele
sugere alterações em lockfiles e manifestos que atualizam dependências
específicas e submete pull-requests que podem ser revisados ou configurados para
serem mesclados automaticamente se o CI passar, por exemplo.

É uma ferramenta extremamente flexível, prática, com configuração baseada em um
arquivo: o renovate.json.

# O Fluxo

A configuração do renovate é feita através da ativação de um
[app do GitHub](https://github.com/marketplace/renovate). Você autoriza o app e
de repente surge um PR
[assim em todos os projetos que você autorizou](https://github.com/lucasew/bumpkin/pull/2).
Eu Autorizei em toda a minha conta e na org do LEWTEC.

Em condições normais de temperatura e pressão, se você quer ativar o renovate é
só mergear o PR, senão pode fechar ou deixar lá.

Assim que você mergear o PR as análises entram na fila e qualquer novidade vai
chegar no e-mail. Dá para decidir essas atualizações diretamente pelo celular no
4G se quiser. É bem conveniente.

E é isso ai. Qualquer novidade ele vai mandar PR, você vai ser avisado no e-mail
e ai você analisa caso a caso e decide se mergeia ou não.

# Dicas

Se o PR tiver conflito de merge, tem uma checkbox que quando marcada adiciona um
rebase na fila do bot então ele mesmo já consegue ajustar o PR.
