with open("src/layouts/SlideLayout.astro", "r") as f:
    content = f.read()

content = content.replace("      // @ts-ignore\n      import RevealMath from 'reveal.js/dist/plugin/math.js'", "      import RevealMath from 'reveal.js/plugin/math'")
content = content.replace("      // @ts-ignore\n      import RevealZoom from 'reveal.js/dist/plugin/zoom.js'", "      import RevealZoom from 'reveal.js/plugin/zoom'")

with open("src/layouts/SlideLayout.astro", "w") as f:
    f.write(content)
