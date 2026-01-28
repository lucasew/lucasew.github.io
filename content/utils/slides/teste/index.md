---
title: RevealJS test
summary: Slides as Hugo site
---

# Demonstração dos testes usando Reveal e Hugo

---

## Funciona a logo da Internet

- A logo é importada como asset então é redistribuida com o site gerado
- Tem que ser num formato mais padrão tipo PNG ou JPG senão o hugo reclama que
  não sabe lidar

---

%auto-animate%

## Funciona código

```java
public class Main {
    public static void main(String args[]) {
        System.out.println("aha");
    }
}
// Parece bem funcional pra mim
```

---

%auto-animate%

## Funciona código

```nix
# Svelte reclamava bastante desse trecho
{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
    buildInputs = with pkgs; [ hugo ];
}
```

---

## Funciona matemática

- $x^2$
- $\frac{-b \pm \sqrt{b^2 -4ac}}{2a}$

---

## Funciona HTML arbitrário

- HTML arbitrário agora é desativado por segurança. O código abaixo será
  escapado.

<button onclick="alert('vai dizer que não')">Testar</button>

---

## Funciona embed

{{< youtube dQw4w9WgXcQ >}}

---

%auto-animate%

## Animações

<p>AAAA</p>

---

%auto-animate%

## Animações

<p color="red">AAAA</p>

---

<!-- Unsafe style removed -->

%auto-animate%

# Animações

<!-- Unsafe img removed -->

Imagem vermelha (HTML removido)

---

%auto-animate%

# Animações

<!-- Unsafe img removed -->

Imagem azul (HTML removido)
