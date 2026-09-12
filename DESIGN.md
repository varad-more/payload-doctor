---
name: Payload Doctor
description: A dark diagnostic code-review workbench for JSON and AWS event payloads.
colors:
  canvas: "#0c1012"
  panel: "#111719"
  panel-raised: "#161d20"
  panel-quiet: "#0f1416"
  line: "#2a3336"
  line-strong: "#3b474a"
  ink: "#eef2ee"
  muted: "#9ba9a5"
  faint: "#84938e"
  diagnostic-green: "#79d49a"
  diagnostic-green-hover: "#99e2b2"
  diagnostic-green-dark: "#183828"
  warning-amber: "#e6b85c"
  warning-amber-dark: "#3b2d13"
  error-coral: "#ff8e78"
  error-coral-dark: "#40231f"
  focus-mint: "#b7e8c8"
  accent-ink: "#07120b"
  code-ink: "#e2e8e4"
  error-ink: "#ffd3cb"
  shadow-ambient: "rgba(0, 0, 0, 0.3)"
  shadow-contact: "rgba(0, 0, 0, 0.22)"
typography:
  display:
    fontFamily: "Archivo Variable, Segoe UI, sans-serif"
    fontSize: "clamp(2.45rem, 5.4vw, 5rem)"
    fontWeight: 600
    lineHeight: 0.98
    letterSpacing: "-0.04em"
  headline:
    fontFamily: "Archivo Variable, Segoe UI, sans-serif"
    fontSize: "clamp(1.7rem, 3vw, 2.6rem)"
    fontWeight: 590
    letterSpacing: "-0.035em"
  body:
    fontFamily: "Archivo Variable, Segoe UI, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.7
  label:
    fontFamily: "SFMono-Regular, Consolas, Liberation Mono, Menlo, monospace"
    fontSize: "0.68rem"
    fontWeight: 700
    letterSpacing: "0.055em"
  code:
    fontFamily: "SFMono-Regular, Consolas, Liberation Mono, Menlo, monospace"
    fontSize: "0.84rem"
    fontWeight: 400
    lineHeight: 1.66
  path:
    fontFamily: "SFMono-Regular, Consolas, Liberation Mono, Menlo, monospace"
    fontSize: "0.73rem"
    fontWeight: 400
  badge:
    fontFamily: "SFMono-Regular, Consolas, Liberation Mono, Menlo, monospace"
    fontSize: "0.58rem"
    fontWeight: 750
    letterSpacing: "0.06em"
rounded:
  badge: "3px"
  index: "4px"
  compact: "5px"
  control: "6px"
  disclosure: "8px"
  workbench: "11px"
components:
  button-primary:
    backgroundColor: "{colors.diagnostic-green}"
    textColor: "{colors.accent-ink}"
    typography: "{typography.label}"
    rounded: "{rounded.control}"
    padding: "0 16px"
    height: "42px"
  button-primary-hover:
    backgroundColor: "#99e2b2"
    textColor: "{colors.accent-ink}"
    rounded: "{rounded.control}"
  button-secondary:
    backgroundColor: "{colors.panel-raised}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "0 15px"
    height: "42px"
  button-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.muted}"
    rounded: "{rounded.control}"
    padding: "0 15px"
    height: "42px"
  workbench:
    backgroundColor: "{colors.panel}"
    rounded: "{rounded.workbench}"
  text-field:
    backgroundColor: "#0e1315"
    textColor: "#dfe9e2"
    typography: "{typography.code}"
    rounded: "0"
    padding: "18px 20px 18px 19px"
---

# Design System: Payload Doctor

## Overview

**Creative North Star: "The Diagnostic Review Sheet"**

Payload Doctor treats payload analysis as a focused code review: an ownable charcoal work surface, precise ruled divisions, and compact diagnostic annotations. The interface is dense but calm, with the input and verdict held in equal visual authority instead of broken into a generic dashboard of cards.

The visual language is factual and instrument-like. Paper-white type and quiet blue-charcoal layers carry most of the screen; green, amber, and coral appear only when an action or finding needs a clear verdict. Archivo Variable gives the shell a contemporary editorial voice, while the system monospace stack makes payloads, measurements, paths, and labels read like review notation.

**Key Characteristics:**

- Equal split input and diagnosis panes on desktop, collapsing into one review flow on narrow screens.
- Thin ruled borders, restrained tonal layering, and a single elevated workbench.
- Diagnostic color reserved for actions, status, findings, focus, and selection.
- Compact uppercase labels paired with readable mixed-case explanations and monospaced payload data.
- Direct state transitions: ready, examining, service error, findings, repairs, and copyable output.

## Colors

The palette is a charcoal review surface with paper-white text and three semantic diagnostic signals.

### Primary

- **Diagnostic Green:** The principal action, passing verdict, caret, brand mark, disclosure marker, repair line, and text-selection signal.

### Secondary

- **Warning Amber:** Warnings and caution badges only; its dark companion provides the contained warning field.

### Tertiary

- **Error Coral:** Failed verdicts, payload limits, invalid syntax, and service errors; its dark companion provides the error field.

### Neutral

- **Canvas Charcoal:** The page ground and deepest persistent surface.
- **Review Charcoal:** The workbench base beneath ruled panes.
- **Raised Charcoal:** Buttons, keycaps, and compact interactive surfaces.
- **Quiet Charcoal:** Tool strips, disclosure panels, and subdued operation messages.
- **Paper Ink:** Primary headings and high-confidence copy.
- **Muted Ink:** Supporting prose and secondary controls.
- **Faint Ink:** Metadata, limits, shortcuts, and inactive states.
- **Ruled Line / Strong Ruled Line:** Ordinary section divisions and structural pane boundaries.
- **Focus Mint:** The visible keyboard focus outline and editor focus inset.

### Named Rules

**The Verdict Color Rule.** Green, amber, and coral communicate action or diagnostic meaning; they are not decorative accents.

**The Charcoal Ladder Rule.** Separate regions with the four established charcoal surfaces and ruled borders before introducing another surface color.

## Typography

**Display Font:** Archivo Variable (with Segoe UI and sans-serif fallbacks)
**Body Font:** Archivo Variable (with Segoe UI and sans-serif fallbacks)
**Label/Mono Font:** SFMono-Regular (with Consolas, Liberation Mono, Menlo, and monospace fallbacks)

**Character:** Archivo is compact and editorial without becoming ornamental. Monospace is reserved for machine-facing material: code, paths, metrics, counts, status labels, pane indexes, and keyboard commands.

### Hierarchy

- **Display** (600, `clamp(2.45rem, 5.4vw, 5rem)`, 0.98): Product title only; tightly tracked and balanced.
- **Headline** (590, `clamp(1.7rem, 3vw, 2.6rem)`): Supporting section title such as the AWS architecture note.
- **Title** (700-750, `0.76rem-0.79rem`): Pane and report headings; uppercase with deliberate tracking.
- **Body** (400, `0.9rem-1rem`, 1.7-1.75): Explanations and supporting copy, held to roughly 68-70 characters.
- **Label** (700, `0.64rem-0.75rem`, tracked): Controls, statuses, metadata, limits, and compact actions; uppercase where the implementation establishes it.
- **Code** (400, `0.75rem-0.84rem`, 1.6-1.66): Payload input, excerpts, output, and paths.

### Named Rules

**The Machine Voice Rule.** Use monospace only when the text is a value, location, measurement, state, or direct command.

## Layout

The shell is centered and capped at 1480px with 28px horizontal gutters. A compact 76px masthead leads into an editorial introduction; the real Diagnose action remains reachable before the editor. The workbench is a two-column, equal-width review sheet whose toolbar sits above both panes and whose operation bar closes the sheet below them. Input uses a fixed line-number gutter and the result pane preserves its own vertical scroll region.

Spacing is compact inside the tool: 8-20px gaps and padding dominate controls, pane headers, report sections, and action groups. Larger 46-90px intervals are reserved for page-level separation around the introduction, workbench, architecture note, and footer.

At 980px the introduction and health summary become single-column, and the action-bar shortcut disappears. At 780px the workbench panes stack, the toolbar wraps, the payload selector becomes full-width, the editor shortens from 555px to 430px, and the result uses a flexible 430-650px region. At 480px the Diagnose call-to-action and toolbar actions become full-width, pane/report headings stack, schema controls stack, and the disabled GitHub item is hidden. The layout supports a 320px minimum viewport.

**The Review Order Rule.** Responsive layouts preserve input before diagnosis and operations after both; the workflow order never changes.

## Elevation & Depth

The system is flat by default. Tonal charcoal steps and one-pixel ruled borders establish hierarchy inside the page. Only the workbench receives persistent elevation, using a broad low-opacity shadow paired with a tighter contact shadow; controls rely on border and background shifts rather than lift.

### Shadow Vocabulary

- **Workbench Lift** (`0 22px 60px rgba(0, 0, 0, 0.3), 0 3px 12px rgba(0, 0, 0, 0.22)`): Applied only to the complete input-and-diagnosis workbench.
- **Editor Focus Inset** (`inset 0 0 0 1px var(--focus)`): Keeps text-area focus visible without moving the ruled editor geometry.

### Named Rules

**The One Lift Rule.** The workbench is the only persistently shadowed surface; all internal sections remain ruled and flat.

## Shapes

Forms are restrained and technical. The workbench has the softest outer corner (11px), optional disclosure panels use 8px, controls use 6px, keycaps and error excerpts use 5px, pane indexes use 4px, and finding badges use 3px. The editor itself stays square so its gutter and textarea read as one continuous code sheet. Status dots and the loading spinner are the only circles.

**The Nested Radius Rule.** Corners tighten as components move inside the workbench; do not give inner reports card-sized rounding.

## Components

### Buttons

- **Shape:** Compact controls use gently rounded corners (6px) and a minimum 42px touch target; the masthead Diagnose action is 52px high.
- **Primary:** Diagnostic green with near-black text, a matching border, compact horizontal padding, bold uppercase labels in workbench contexts, and an arrow glyph in the masthead action.
- **Hover / Focus / Active:** Hover shifts to a lighter mint green; keyboard focus uses a 2px Focus Mint outline with 3px offset; active state moves down 1px. Disabled buttons become low-contrast charcoal and never retain an action color.
- **Secondary:** Raised charcoal, paper ink, and a strong ruled border; adjacent example buttons share their inner seam.
- **Ghost:** Transparent background with muted text for low-priority actions such as clearing or reusing input.

### Chips

- **Style:** Finding badges are tiny square-edged labels (3px) in the semantic error or warning dark field with a lighter matching foreground.
- **State:** They identify severity, not selection; use uppercase monospace and pair them with the exact payload path.

### Cards / Containers

- **Corner Style:** The outer workbench uses 11px corners; the optional schema disclosure uses 8px.
- **Background:** Review Charcoal for the workbench, Quiet Charcoal for control strips, and the deeper editor charcoal for payload regions.
- **Shadow Strategy:** Only the whole workbench uses Workbench Lift.
- **Border:** One-pixel ruled lines define every pane, report section, metric cell, and list row.
- **Internal Padding:** Tool and action strips use 12-17px; diagnosis sections use 22-24px.

### Inputs / Fields

- **Style:** Selects and schema fields use a strong ruled border, dark charcoal fill, and 6px corners. The payload editor is borderless and square inside its ruled shell, with a 54px desktop line gutter.
- **Focus:** Global interactive focus is a 2px Focus Mint outline; the payload editor uses the focus color as a 1px inset so the sheet does not shift.
- **Error / Disabled:** Oversize counts switch to Error Coral and gain a dark coral alert strip. Disabled controls use subdued text, line, and fill values while retaining their dimensions.

### Navigation

The masthead keeps navigation sparse: brand at left and two text links at right. Archivo labels use muted ink, shifting to paper ink on hover; an unavailable repository link remains visibly subdued and disappears below 480px.

### Payload Review Sheet

The signature component combines a toolbar, A/B pane indexes, ruled pane headings, line-numbered payload editor, scrollable result report, and closing operation bar. Status rows pair human-readable checks with compact colored verdicts. Findings order errors before warnings and combine severity, JSON path, explanation, expected/received values, and an optional hint without turning each issue into a separate card.

### Result States

The result pane has four explicit visual states: ready uses three ruled scan lines and a keyboard hint; examining uses a green-tipped circular activity mark; service failure shifts the heading to coral; completed analysis uses structured health, metrics, findings, changes, and output sections. Motion is limited to the 700ms linear activity rotation and 140ms control transitions, with both effectively removed under reduced-motion preference.

## Do's and Don'ts

### Do:

- **Do** keep the editor and diagnosis equally prominent on desktop and in one logical sequence on mobile.
- **Do** use ruled lines and charcoal tonal steps to organize dense diagnostic information.
- **Do** reserve semantic green, amber, and coral for actions and verdicts.
- **Do** preserve visible focus, 42px minimum controls, semantic status regions, and reduced-motion behavior.
- **Do** keep paths, metrics, byte limits, statuses, and code in the monospace voice.

### Don't:

- **Don't** convert the review sheet into a dashboard of floating cards.
- **Don't** use diagnostic colors as general decoration or mix their semantic roles.
- **Don't** add persistent shadows to inner sections, findings, metrics, or controls.
- **Don't** round the code editor or individual report rows into pills or tiles.
- **Don't** hide the primary Diagnose action below the editor in the first viewport.
