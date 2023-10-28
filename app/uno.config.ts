import { defineConfig } from 'unocss'
import { presetWebFonts, presetWind } from 'unocss'

export default defineConfig({
  presets: [
    presetWind(),
    presetWebFonts({
        provider: "none",
        fonts: {
            primary: [
                {
                    name: "Inter",
                    provider: "google"
                },
                {
                  name: '"Noto Sans"',
                  provider: "none"
                },
                {
                    name: '"Helvetica Neue"',
                    provider: "none"
                },
                {
                    name: "Helvetica",
                    provider: "none"
                },
                {
                    name: "Arial",
                    provider: "none"
                },
                {
                    name: "sans-serif",
                    provider: "none"
                }
            ]
        }
    }),
  ],
  rules: [
    [/^bgi-\[([\w\W]+)\]$/, ([, d]) => {
      return { 'background-image': `url('${d}')` }
    }]
  ],
  theme: {
    colors: {
        'quite-blue': '#121315',
        'unrailed': '#7364FF',
        'blackbird': '#9da1a4',
        'quite-more-blue': '#181C22',
        'some-blue': '#101317',
        'some-gray': '#686768'
    },
  },
})