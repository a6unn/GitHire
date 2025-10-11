# UI Components

This directory contains reusable, foundational UI components for the GitHire application.

## Components

- **Button** - Enhanced button with variants (primary, secondary, ghost, danger), sizes, loading states
- **Card** - Reusable card component with variants (default, elevated, bordered, interactive)
- **Input** - Modern input component with icon support and floating labels
- **Badge** - Badge component for tags, status indicators, and skill pills
- **Avatar** - Avatar component for user profiles and GitHub avatars
- **Skeleton** - Skeleton loader for loading states
- **Modal** - Modal/dialog component using Headless UI
- **Dropdown** - Dropdown menu component for user menus

## Usage

Import components from this directory:

```tsx
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
```

## Design Principles

- Accessible by default (WCAG 2.1 AA)
- Consistent styling with design tokens
- Support for keyboard navigation
- Reduced motion support
- TypeScript typed props
