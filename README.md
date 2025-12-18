# Akshar

Akshar is a desktop application for creating fonts by drawing glyphs directly.
It is built with Python and PyQt6 and is designed to support both Latin and
complex scripts such as Devanagari.

The application emphasizes a visual, structured workflow where each character
is treated as an intentional drawing rather than abstract font data.

---

## Current scope

This repository documents **version 1** of Akshar.

Version 1 focuses on:
- Manual glyph creation
- Clear Unicode-based structure
- A predictable, distraction-free workflow
- Reliable export of usable font files

Advanced typography features are intentionally deferred.

---

## Application flow

Akshar follows a linear, layered flow. Each screen has a single responsibility.

### 1. Start screen

The start screen is the entry point to the application.

From here, the user can:
- Enter the application
- Access usage guidance
- Open global settings

No font data is shown at this stage.

---

### 2. Home screen

The home screen displays all existing fonts as a grid.

Each font is represented visually, allowing users to recognize projects without
opening them. The grid adapts to window size and never scrolls horizontally.

From the home screen, users can:
- Create a new font
- Open an existing font
- Continue working on recent projects

---

### 3. Font editor

The font editor represents a single font project.

All characters belonging to the selected script or Unicode range are shown in a
grid. Each cell corresponds to one Unicode codepoint.

The grid shows:
- The character
- Its Unicode value
- Whether the glyph is empty or drawn

From this screen, users manage the font as a collection of glyphs.

---

### 4. Glyph editor

The glyph editor is a focused drawing workspace for a single character.

Only one glyph is edited at a time.

#### Canvas
- Square, centered drawing area
- Vector-based drawing
- Infinite zoom and pan
- Visual guides such as baseline and reference lines

#### Tools
- Freehand brush
- Precise pen tool
- Eraser
- Selection and movement
- Importing raster or vector images for tracing

Guides and overlays are visible while editing but are not part of the exported
glyph.

Changes are saved automatically to prevent accidental loss of work.

---

## What you can create with Akshar v1.0.0

With the current feature set, users can create:

- Fully usable custom fonts
- Handwritten fonts
- Display fonts and logos
- Decorative scripts
- Experimental glyph sets
- Script-specific alphabets (Latin, Devanagari, symbols)

Fonts created in Akshar v1 can be installed and used in other applications after
export in .ttf and .otf.

---

## Technical foundation

- Language: Python
- UI framework: PyQt6
- Drawing model: vector-based glyphs
- Target platforms: Windows, Linux, macOS

The architecture is intentionally simple to support future expansion.

---

## Version 2 onwards

I have planned the following features for a future version:

- Kerning and spacing editor
- Advanced font metrics controls
- Ligatures and contextual alternates
- Script shaping support
- Glyph components and reuse
- Stroke and pressure data
- Batch glyph import
- OpenType feature support
- Validation and font diagnostics
- Plugin or extension system

These will be introduced incrementally after the v1 workflow is stable.

---

## Status

Akshar is under active development.

The goal of version 1 is to establish a solid, understandable foundation for
font creation before moving into advanced typography features.
