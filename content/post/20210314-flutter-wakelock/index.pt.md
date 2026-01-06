---
title: "Como manter a tela ligada durante o desenvolvimento de um app Flutter"
date: 2021-03-14T10:53:51-03:00
summary: "Configurando um wakelock se o aplicativo estiver sendo executado em modo dev"
alsoAvailable:
- https://blog-do-lucao.vercel.app/post/flutter_wakelock
---

# Overview

Esses dias descobri um esquema no ADB que permite uso dele via rede mesmo em
celulares usando o sistema stock (o que vem junto). Se o post não saiu vai sair.
O problema dessa manha é que pelo menos no meu caso com o meu **Redmi Note 5
(whyred)** rodando **MIUI Global 12.0.2** a conexão do ADB caia se a tela
desligasse. Foi uma pedra no meu caminho que eu consegui passar por cima e que
vou mostrar para vocês como.

O projeto que eu usei para lidar com isso foi o [Limpazap](../limpazap).

# A estratégia

Uma funcionalidade que eu já tinha percebido no
[Termux](https://f-droid.org/pt_BR/packages/com.termux/) é que ele tem a opção
de ativar um wakelock.

![image-20210314112501608](image-20210314112501608.png)

Infelizmente esta funcionalidade não funcionou para esse caso, mesmo assim a
conexão do `flutter run` caia e a tela desligava normalmente. O problema parece
ser apenas resolvível se o próprio app flutter pegar um wakelock.

Felizmente eu achei um
[pacote perfeito para esse caso](https://pub.dev/packages/wakelock), o problema
agora é que eu só quero criar um wakelock quando eu for desenvolver o app, não
quero isso na aplicação final.

Nisso descobri que tem uma constante presente em
`package:flutter/foundation.dart` chamada `kReleaseMode` que é um boolean. Se o
app for compilado em modo release essa constante é `true`, logo dá para resolver
isso simplesmente invertendo. Se o app estiver rodando em modo não release ele
pega esse wakelock. Sobre questão de otimização o flutter lida bem com isso
simplesmente removendo o código inacessível, processo conhecido como
`tree shaking`.

Todo esse processo de adição de um wakelock para desenvolvimento para não deixar
a tela apagar enquanto está acontecendo o `flutter run` foi feito em um commit,
que está [logo abaixo](#TLDR).

# TL;DR {#TLDR}

https://github.com/lucasew/limpazap/commit/2596a8b1bb1ff2e6b8205bab273d21fc65f8e73b
