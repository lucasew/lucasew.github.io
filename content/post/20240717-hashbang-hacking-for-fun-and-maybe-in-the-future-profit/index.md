---
title: Hashbang hacking for fun and, maybe in the future, profit 
language: en
---

This is the story of how I created a thing to make self contained scripts. It's basically a Nix flakes based workaround, so the environment of a script can be automatically provisioned before the actual script starts without having to install stuff globally.

I am a Nix user, and as a Nix user, I tend to put Nix in everything. At least everything that I think it makes sense.

Hashbangs are the UNIX-like way to make a text file executable, so it becomes a program, and a pain point I have is that there is so much boilerplate to have something simple to start hacking on something. In a non-Nix distro one would have to install many packages and pray for them to not conflict with each other, build some kind of boilerplate like a package.json for a Node application, or a requirements.txt for a Python application, or a pom.xml, or Gradle, for a Java project. What if I do it a little different?

For the ones that don't know, Nix allows one to setup temporary environments in a way that you don't need to install stuff globally. Think of it like a Python virtualenv but using a content addressed storage, so, if you use the exact same packages in more than one project, these are only downloaded once. And if there is a native extension in the middle that requires compilation it can just be downloaded using Nix's substituters (aka binary caches) if available. And if stuff needs to be compiled you can setup remote builders to a beefier machine so the compilation happens somewhere else and you just get the chewed result from that machine.

Because stuff changes, this ephemeral shell thing changed too. Right now in Nix there is a old way (nix-shell, nix-env and stuff) and the new way (flakes, nix command, right now all behind a feature flag) and some stuff doesn't map exactly from the old world to the new world. An example is how development shell works. In nix-shell the environment is built using the `pkgs.mkShell` function, but in `nix develop` it either assumes that this `pkgs.mkShell` is already applied or just add the binaries to the `PATH` environment variable ignoring all the other details such as shell hooks.

Also, nix-shell allows it to be [used in hashbangs](https://nixos.wiki/wiki/Nix-shell_shebang) but the old way is very reliant on the `NIX_PATH` environment variable, that is basically system state, so there is a limbo in the middle. What if I could use the power of flakes and bring it to a nix-shell-esque style?

That's what I tried to do in [nix-flake-shell](https://github.com/lucasew/nix-flake-shell).

Basically one adds a hashbang running `nix run` to the repository and adds a bunch of directives using comments, that would be ignored by the language but interpreted using a Nix script. For it to be recognized the line must only have a `#!nix-flake-shell` somewhere.

This way one can declare fetchers in a way that the result path is available in an environment variable passed to the payload application, what is the interpreter, which flake inputs to use, which extra packages to bring with all it's bells and whistles and propagated stuff and Nix dark magic for stuff to be available.

The [`tests`](https://github.com/lucasew/nix-flake-shell/tree/main/tests) folder has examples of usage of the script. If you know some more exoteric languages and want to contribute with examples feel free to try and play with it, if you found some rough edges or suggestions please feel free to open an issue or a pull request.

BTW this is me exploring the potential of this workaround: ![](https://camo.githubusercontent.com/7a1c04e6ff90028a95f65e36c5eaf17af0cf39d9fcf1b7ddf469669401bd638e/68747470733a2f2f692e696d67666c69702e636f6d2f3370633665302e6a7067)
