# Editor UI/UX Style Guide (Live Site)

This document outlines the visual and interaction design standards for the editor application, based on the live site's CSS. Adhering to this guide ensures a consistent user experience.

## 1. Guiding Principles

- **Clarity:** The interface should be clean and easy to understand.
- **Consistency:** UI elements and interaction patterns should be consistent.
- **Organic & Welcoming:** The design uses a nature-inspired palette and soft gradients to create a welcoming feel.

## 2. Color Palette

### Primary Colors
- **`#357438` (Forest Green):** Primary text color for headings, titles, and important elements.
- **`#4caf50` / `#66bb6a` (Lush Green Gradient):** Used for primary headers and prominent UI elements.
- **`#FFFFFF` (White):** Background for content cards and text on dark backgrounds.

### Secondary Colors
- **`#e8f5e8` / `#f0faf4` (Mint Green Gradient):** Primary page background.
- **`#732751` (Plum):** Used for descriptive text and secondary content.
- **`#f8fdf9` (Off-White):** Background for interactive list items.
- **`#f0f9ff` (Light Sky Blue):** Background for treatment list items.

### Semantic Colors
- **Border/Hover:** Colors are derived from the primary palette (e.g., `#357438` for hover borders, `#e8f5e8` for default borders).

## 3. Typography

- **Primary Font Family:** `'Segoe UI', Tahoma, Geneva, Verdana, sans-serif`.
- **Base Line Height:** `1.6`

| Element                  | Font Size | Font Weight | Notes                     |
|--------------------------|-----------|-------------|---------------------------|
| Main Header (`h1`)       | `2.5em`   | `300`       | `letter-spacing: 2px`     |
| Section Titles           | `1.8em`   | `600`       | -                         |
| Body Text                | `1em`     | `Regular`   | Inherited                 |
| Condition Item Text      | `1em`     | `500`       | -                         |
| Treatment Item Strong    | `1em`     | `Bold`      | Color: `#357438`          |

## 4. Component Styling

### Cards (`.section-card`)
- **Background:** White (`#FFFFFF`).
- **Border Radius:** `20px`.
- **Box Shadow:** `0 15px 35px rgba(0,0,0,0.08)`.
- **Padding:** `40px`.
- **Top Border Accent:** A linear gradient of `(#4caf50, #66bb6a, #81c784)`.

### List Items (`.condition-item`)
- **Background:** Off-White (`#f8fdf9`).
- **Border:** `2px solid #e8f5e8`.
- **Border Radius:** `12px`.
- **Padding:** `15px 20px`.
- **Hover State:** Background changes to `#e8f5e8`, border to `#357438`.

### Headers (`.conditions-header`)
- **Background:** Lush Green Gradient (`#4caf50`, `#66bb6a`).
- **Border Radius:** `20px`.
- **Padding:** `30px 0`.
- **Text Color:** White (`#FFFFFF`).

## 5. Layout and Spacing

- **Container Padding:** `40px 20px` on desktop.
- **Grid Gap:** `40px` between major content sections.
- **Content Padding:** Spacing is generally generous, with `40px` padding inside cards and `20px` inside list items.