# Color for visual work

[中文](color_zh.md)

Use this reference when selecting or revising a palette. Match the audience, content, environment, and intended mood; reuse an existing design system when it fits. A small local change needs the affected color pairs and states checked, not an unrelated redesign.

## Harmony and hierarchy

Choose a relationship deliberately: monochromatic uses one hue with tonal variation; analogous uses neighboring hues; complementary uses opposing hues; split-complementary uses the neighbors of an opposing hue; triadic uses three evenly spaced hues. These are palette starting points. Tune lightness, chroma, and visual area so accents support the intended hierarchy. A vivid opposing accent can occupy a small area while neutral surfaces carry the work. Avoid making every region equally prominent or imposing a universal palette or percentage formula. [Adobe palette relationships](https://www.adobe.com/uk/creativecloud/design/discover/color-palette.html).

## Roles and states

Assign reusable roles for background/surface, text, necessary control outlines, actions, selection, focus, and status. Distinguish decorative separators from boundaries needed to recognize a control. Pair foregrounds with their actual backgrounds; keep meaning consistent across components, open menus, hover, pressed, selected, disabled, and error states. Design dark and local inverse surfaces with their own paired colors. [Material color roles](https://m3.material.io/styles/color/the-color-system), [Fluent color](https://fluent2.microsoft.design/color).

Alternating row backgrounds can aid tracking when needed; they still need readable content and distinct selection. An inverse surface, a complementary accent, and a pixel-inversion filter are different choices. Do not derive an entire dark theme by numerically inverting every color. [MDN inversion](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Values/filter-function/invert).

## Visibility and comfort

For WCAG AA, normal text needs at least 4.5:1 contrast with its background; large text needs 3:1. Required non-text control/state cues need 3:1 against adjacent colors. Inactive controls have exceptions. Not every decorative border or difference between hover and default requires 3:1. Check computed colors, including opacity and overlays, without rounding a failing ratio up to pass. Use a check, shape, label, or another visible distinction when color alone would carry meaning. [Text contrast](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html), [non-text contrast](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html), [use of color](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html).

Inspect the rendered work at intended sizes and themes: text size, weight, line length and spacing, content density, competing accents, large bright or saturated fields, and focus/selection visibility. Preserve readability when softening glare; faint important text is not a comfort solution. Respect available text-size, contrast, and theme preferences. WCAG's visual-presentation guidance includes further Level AAA provisions; apply them according to the actual requirement, not as automatic defaults for every layout. Assess visibility, aesthetic fit, and reading comfort through their relevant observations. Report the colors, states, sizes, and checks actually observed. [Visual presentation](https://www.w3.org/WAI/WCAG22/Understanding/visual-presentation.html).
