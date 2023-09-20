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
        'quite-blue': '#0A1628'
    }
  }
})