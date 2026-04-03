---
title: Markdown test
summary: Markdown test
type: post
---

Teste

# Basic template eval

{{% eval %}} {{ .Title }} {{ 2 }} {{% /eval %}}

# Details direto

<details>
<summary>Teste</summary>
<h1>Teste</h1>
</details>

# Details

{{% details "Test" %}}

Test

{{% /details %}}

# Template eval with details

{{% eval %}} {{% details "{{.Title}}" %}} Teste {{% /details %}} {{% /eval %}}

# Unsafe console.log

<script>
console.log("aoba")
</script>
