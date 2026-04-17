with open("src/layouts/SlideLayout.astro", "r") as f:
    content = f.read()

content = content.replace("      // @ts-ignore\n      import RevealMath from 'reveal.js/plugin/math/math.js'", "      // @ts-ignore\n      import RevealMath from 'reveal.js/plugin/math/math.esm.js'")
content = content.replace("      // @ts-ignore\n      import RevealZoom from 'reveal.js/plugin/zoom/zoom.js'", "      // @ts-ignore\n      import RevealZoom from 'reveal.js/plugin/zoom/zoom.esm.js'")

with open("src/layouts/SlideLayout.astro", "w") as f:
    f.write(content)
