---

date: 2025-09-10T00:00:00

title: "Socket activation com systemd e podman"
summary: "Murros em pontas de faca e macetes aprendidos no processo"
---

Aoba, aqui é o Lucão. Primeiro post depois do alinhamento do olho, que eu fiz a
exatamente um mês atrás.

Vez ou outra eu me enfezo de fazer algumas limpezas e ajustes. Nos ultimos dias,
comecei a configurar o [Mise](https://mise.jdx.dev/)[^mise] em alguns projetos
meus simplesmente porque Nix não me deixa pinar uma versão específica de um
programa específico.

[^mise]: [Post do Mise](../20250911-mise)

Também aproveitei um tempo mais de várzea de fim de projeto para dar uma mexida
no tal do [Bun](https://bun.com/) e nessa migrei alguns projetos para usar ele,
pelo menos como gerenciador de pacotes.

Eu tenho um projeto em Svelte, chamado
[cf-torrent](https://github.com/lucasew/cf-torrent) que basicamente é um cliente
glorificado para alguns mecanismos de busca e que busca links magnéticos. Criei
por preguiça, hoje é basicamente um laboratório para testar macetes de devops.

Um deles é que eu to removendo a parte Nix das coisas, até porque para alguns
projetos ele tá ficando no caminho. Como eu disse, Nix não tem um jeito simples
de pinar alguma coisa e eu tenho preguiça de escrever e manter overlays. O que
eu puder delegar para o Renovate atualizar e me mandar PR sugerindo atualização
eu to delegando.

Nessa pensei, uso o cf-torrent como serviço socket ativável localmente e já que
eu to removendo a parte Nix eu ia a princípio perder essa possibilidade. Teria
que achar outro jeito, e eu achei: Podman!

O NixOS tem um conjunto de options, basicamente um tipo de API para configurar
módulos, que permite de forma declarativa configurar containers como serviços.
Tipo docker compose? Tipo docker compose! Só que usando o systemd, o que eu acho
mais apropriado no NixOS. Juntar vários gerenciadores de serviços é algo que eu
evito. Acho sujeira. Ser declarativo é certamente um plus!

O macete é o seguinte: Para fazer socket activation primeiro é necessário ter
uma unit do tipo _socket_, que dispara uma unit do tipo _service_. No NixOS isso
fica abstraído.

# O módulo

Para referências, o módulo completo que eu fiz está aqui:
https://github.com/lucasew/nixcfg/blob/0a9d66c6ff9e4b43c8e951a64f028a7b781484d1/nix/nodes/common/services/cf-torrent.nix

O começo é bem padrão (linhas 1 a 16): imports e organização de escopo para
ajudar a análise estática e o autocomplete me ajudar.

A parte de definição das options (linhas 19 a 37): Bem intuitivo, ali defino que
opções eu passo para frente para poder usar na configuração das minhas máquinas.

E agora a parte interessante

- 39: Invoco o meu alocator de porta que não foi aceito no nixpkgs. Basicamente
  ele usa o nome do serviço para decidir um número de porta dado um critério.
  Criei para não ter que pensar em número de porta, conflito e tal. E não
  importa, porque essa porta vai ser proxiada. Estando chumbado igual nas duas
  pontas tá massa.

- 41: Uso a porta calculada do alocator como porta padrão do serviço.
- 43-49: Invocação das options do ts-proxy, meu proxy reverso que expõe o
  serviço dentro da minha rede do Tailscale, com HTTPS válido e sem ter que
  expor para a Internet.
- 51-62: Define a unit do tipo _socket_ que dispara o serviço. Systemd padrão
  basicamente, com algumas pequenas magias _NixOSisticas_
- 64-72: Utilização das options do oci-containers para definir o serviço do
  container. Esse `IDLE_TIMEOUT` define quanto tempo de inatividade faz o Svelte
  derrubar o servidor. Como o socket segue ativo, uma nova requisição
  simplesmente acorda o serviço. O container também sempre vai ficar atualizado
  pois eu mando checar toda vez que sobe e eu coloquei para o container não
  subir com o sistema. Só sobe se for usado, como se fosse uma lambda!
- 74: Gambiarra para o systemd não ficar tentando reiniciar o container quando
  ele desliga sozinho por inatividade. O `mkForce` é porque o valor tá definido
  no módulo do oci-containers ao invés de usar `mkDefault` então é necessário
  fazer esse valor ter uma prioridade maior que uma definição normal.

E é isso ai. O ts-proxy ainda precisa rodar o tempo inteiro porque alguém tem
que negociar os endpoints com o Tailscale. A qualquer momento consigo acessar
esse e qualquer outro serviço que eu esteja usando um sistema parecido de
qualquer dispositivo da minha rede do Tailscale. Homelab inteligente sem ter que
manter configuração de proxy reverso e DNS! E a aplicação só roda quando
necessário.

# Um outro macete

É possível testar socket activation sem ter que fazer a maracutaia das units
necessariamente.

O systemd possui o comando `systemd-socket-activate` que replica o mesmo sistema
fora do systemd e eu usei para debugar um bug que eu achei no Bun.

O SvelteKit, pelo adapter-node, tem suporte oficial a socket activation sem ter
que configurar nada. Até aquele `IDLE_TIMEOUT` é opcional, só que sem ele a
aplicação não para nunca. A mesma aplicação no Node responde normalmente ao
socket activation como esperado. No Bun nada acontece. O systemd percebe que tem
que subir a aplicação, sobe corretamente mas o Bun não consegue receber o file
descriptor do socket, ou pelo menos não sabe o que fazer com ele e não passa
para as primitivas que o SvelteKit tem para operar esse socket activation.
Basicamente a conexão cai em um limbo e fica travada. O
[bug já foi reportado](https://github.com/oven-sh/bun/issues/22559).
