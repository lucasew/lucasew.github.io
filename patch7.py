with open("src/layouts/SlideLayout.astro", "r") as f:
    content = f.read()

content = content.replace("      import RevealMath from 'reveal.js/dist/plugin/math.js'", "      // @ts-ignore\n      import RevealMath from 'reveal.js/dist/plugin/math.js'")
content = content.replace("      import RevealZoom from 'reveal.js/dist/plugin/zoom.js'", "      // @ts-ignore\n      import RevealZoom from 'reveal.js/dist/plugin/zoom.js'")

with open("src/layouts/SlideLayout.astro", "w") as f:
    f.write(content)
