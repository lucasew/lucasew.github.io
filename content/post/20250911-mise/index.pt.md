---

date: 2025-09-11T00:00:00

title: "Configuração de ferramentas com o Mise"
summary: "Onde se destaca, quanto longe dá pra chegar"
---

Esses dias, surfando pelas internets, me deparei com algo interessante.

Provavelmente vocês já ouviram falar de ferramentas como o Brew ou o ASDF para
instalar ferramentas de projeto. Arquivos .tool-versions.

Então, o Mise é basicamente como se fosse para essas ferramentas o que o UV é
para o pip, por exemplo. Algo rápido, completo, integra outras ferramentas
dentro dele.

O Mise basicamente funciona como um sistema de plugins, e oficialmente um
arquivo mise.toml no projeto que diz qual versão de tal ferramenta foi
instalada. Ele não mistura as ferramentas, separa por nome e versão então cada
projeto vai ter a PATH ajustada para as ferramentas apropriadas e se dois
projetos usam as exatas mesmas ferramentas ele não duplica. Mais ou menos como é
o sistema de store de cache do UV. Se dois projetos Python usam a mesma versão
de certo pacote o UV simplesmente reusa, só que o Mise não cria um .venv com
hardlinks para essa store, e nem precisa.

O Mise funciona com um sistema de plugins, basicamente se você usa ASDF pode
simplesmente trocar pelo Mise porque o Mise suporta ASDF.

Outra funcionalidade muito útil é que você pode usar, por exemplo
`mise use github:lucasew/ts-proxyd`, ele vai campear as releases e procurar
pelos assets pré compilados e vai puxar o apropriado para sua máquina. Nesse
caso, como eu mandei os binários sem Zip nas releases ele ainda tem a
inteligência de cortar fora o nome do target botando o binário ts-proxyd no
radar. Maravilha. 100% automático. Se quiser pinar, chama o use com `--pin` e
ele salva a versão junto no toml ao invés de latest.

Eu também tentei usar o módulo de npm para em um projeto puxar o `vercel-cli`.
Nesse caso não deu certo. Simplesmente usei npx/bunx e ai foi.

Se chamar só `mise use` você pode pesquisar pelas ferramentas que ele já
consegue baixar já de cara. O resto você pode procurar se tem pré compilado nas
releases do git e partir para o abraço.

Outra utilidade interessante é que eles tem um preset de
[action pronto para o GitHub Actions](https://github.com/jdx/mise-action).
Aposentei os setup-go e setup-node. Migrar para outro CI ficaria bem mais fácil
se necessário.

Mise também tem um sistema de tasks embutido. Um ponto em comum. Compilar PDF de
projeto LaTeX ou APK de projeto Flutter com `mise build`.

Houve casos onde eu tive que fazer setup adicional, como instalação de
biblotecas LaTeX [^tinylatex-deps] porque o tinylatex que ele dá suporte vem
pelado. No caso do Flutter, ele instala o framework e o sdkmanager, mas os SDKs
em sí tu tem que chamar o gerenciador para rodar depois,
[ai eu já deixei
os comandos engatilhados](https://github.com/lucasew/limpazap/blob/master/mise.toml).

[^tinylatex-deps]: Comando: `tlmgr install scheme-full`

Eu poderia dizer que algo assim seria útil no Android mas ai seria mancada com o
pessoal do [Obtaininum](https://obtainium.imranr.dev/).
