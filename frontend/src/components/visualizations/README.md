# Visualization Components

This directory contains data visualization components for displaying candidate scores, charts, and metrics.

## Components

- **ScoreRing** - Circular progress ring for displaying scores (0-100)
- **ScoreBar** - Horizontal bar chart for score breakdowns
- **ScoreBreakdown** - Complete score breakdown visualization
- **DistributionChart** - Bar chart showing candidate score distribution
- **SkillCoverage** - Visualization for skill match across candidates

## Usage

```tsx
import { ScoreRing } from '@/components/visualizations/ScoreRing';
import { ScoreBreakdown } from '@/components/visualizations/ScoreBreakdown';
```

## Technologies

- Recharts for chart rendering
- Framer Motion for animations
- Custom SVG for score rings
