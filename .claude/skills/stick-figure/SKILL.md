---
name: stick-figure
description: Draw a stick figure as a clean SVG (static or animated) for the Tolo Travel project — for example a traveller walking with a suitcase. Use when the user runs /stick-figure or asks for a stick figure / آدمک.
---

# Stick figure

Create a stick figure drawing as a self-contained SVG file.

## What to make

1. Read any arguments the user passed after `/stick-figure` (pose, action, colors, size,
   animated or static). If nothing was given, make the default: **a traveller walking
   with a suitcase**, animated.
2. Reply to the user in the language they wrote in (Persian if they wrote in Persian).

## How to draw it

- Pure SVG, no external libraries or images. `viewBox="0 0 200 200"` by default.
- Head: a circle. Body, arms and legs: `<line>` or `<path>` with `stroke-linecap="round"`,
  `stroke-width` about 4, no fill.
- Use `currentColor` for strokes so the figure follows the page's text color
  (works in light and dark mode).
- Travel props when they fit: suitcase (rounded `<rect>` with a handle), backpack,
  map, camera, passport.
- Group limbs in `<g>` elements with a clear `transform-origin` at the joint
  (shoulder, hip) so they can be animated.

## Animation (when animated)

- Use CSS `@keyframes` inside a `<style>` tag in the SVG: swing arms and legs
  opposite each other, a small up-down bob for the body, loop forever.
- Keep it smooth and short (about 1s per step cycle).
- Respect `@media (prefers-reduced-motion: reduce)` by stopping the animation.

## Output

- Save the file to `assets/stick-figures/<short-name>.svg` (create the folder if needed).
- Also show the user how to use it in a page, for example:
  `<img src="assets/stick-figures/traveller.svg" alt="Traveller" width="200">`
- Briefly say what was drawn and where the file is.
