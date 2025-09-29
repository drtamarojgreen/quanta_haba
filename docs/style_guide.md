# Editor UI/UX Style Guide

This document outlines the visual and interaction design standards for the editor application. Adhering to this guide ensures a consistent, intuitive, and high-quality user experience.

## 1. Guiding Principles

- **Clarity:** The interface should be clean and easy to understand. Users should be able to find what they need without confusion.
- **Consistency:** UI elements and interaction patterns should be consistent throughout the application.
- **Efficiency:** The design should empower users to accomplish tasks quickly and with minimal effort.
- **Feedback:** The application should provide clear and immediate feedback for user actions.

## 2. Color Palette

### Primary Colors
- **`#2A2A2A` (Charcoal):** Primary background, text.
- **`#FFFFFF` (White):** Primary text color on dark backgrounds.
- **`#007ACC` (Blue):** Interactive elements, links, and focus indicators.

### Secondary Colors
- **`#333333` (Dark Gray):** Borders, inactive tabs, secondary UI elements.
- **`#4F4F4F` (Medium Gray):** Disabled elements, placeholder text.
- **`#F0F0F0` (Light Gray):** Hover states for dark elements.

### Semantic Colors
- **`#5CB85C` (Green):** Success messages, confirmations.
- **`#D9534F` (Red):** Error messages, destructive actions.
- **`#F0AD4E` (Yellow):** Warnings, notifications.

## 3. Typography

- **Font Family:** `Roboto Mono`, `Menlo`, `monospace` (fallback)
- **Base Font Size:** `14px`
- **Line Height:** `1.5`

| Element       | Font Size | Font Weight |
|---------------|-----------|-------------|
| Headings (H1) | `24px`    | `Bold`      |
| Headings (H2) | `20px`    | `Bold`      |
| Body Text     | `14px`    | `Regular`   |
| Code Text     | `14px`    | `Regular`   |
| Labels        | `12px`    | `Bold`      |

## 4. Component Styling

### Buttons
- **Default:** White text on Blue (`#007ACC`) background.
- **Hover:** Light Gray (`#F0F0F0`) text on Blue (`#007ACC`) background.
- **Disabled:** Medium Gray (`#4F4F4F`) text on Dark Gray (`#333333`) background.
- **Padding:** `8px 16px`
- **Border Radius:** `4px`

### Input Fields
- **Background:** Charcoal (`#2A2A2A`).
- **Border:** `1px solid` Dark Gray (`#333333`).
- **Focus Border:** `1px solid` Blue (`#007ACC`).
- **Text Color:** White (`#FFFFFF`).
- **Placeholder Text:** Medium Gray (`#4F4F4F`).
- **Padding:** `8px`
- **Border Radius:** `4px`

## 5. Layout and Spacing

- **Base Unit:** `8px`
- **General Padding:** `16px` (`2 * base unit`)
- **Gutter Width:** `24px` (`3 * base unit`)

Use multiples of the base unit for all margins, padding, and positioning to maintain a consistent rhythm.

## 6. Interaction Patterns

- **Tooltips:** Should appear on hover after a `500ms` delay for all icon-only buttons or truncated text.
- **Focus States:** All interactive elements must have a clear focus state, using the primary Blue (`#007ACC`) color for outlines or borders.
- **Loading Indicators:** Use subtle, non-blocking spinners for asynchronous operations that take less than 2 seconds. For longer operations, use a more prominent loading bar or message.