import { defineConfig } from 'unocss'
import { presetWebFonts, presetWind } from 'unocss'

export default defineConfig({
  presets: [
    presetWind(),
    presetWebFonts({
        fonts: {
            primary: [
                {
                    name: "Montserrat",
                    weights: [
                        400,
                        600
                    ],
                    italic: true,
                    provider: "google"
                },
                {
                    name: "Noto Sans",
                    provider: "none"
                },
                {
                    name: "Helvetica Neue",
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
  theme: {
    colors: {
        'quite-blue': '#181a1f',
        'unrailed': '#7364FF',
        'blackbird': '#979CA7',
        'quite-more-blue': '#22252b',
    },
    backgroundImage: {
        'trains-away': "url('assets/trains-away.jpg')"
    }
  }
})