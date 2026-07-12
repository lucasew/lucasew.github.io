{ pkgs ? import <nixpkgs> {}}:

pkgs.mkShell {
  packages = with pkgs; [
    dprint
    ltex-ls
    nodejs
  ];
}
