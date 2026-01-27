---
name: frontend-styling-conventions
description: Enforces CSS variables and utility classes design system. Use when styling components, creating layouts, or ensuring design consistency across the frontend.
---

# Frontend Styling Conventions

This skill defines styling conventions using a design token system with CSS variables and pre-built utility classes.

## When to Use

- When styling any component
- When creating layouts
- When adding colors, spacing, or typography
- When ensuring design consistency
- When implementing responsive design
- When reviewing component styles

## Instructions

### Core Principle

**This project uses a design token system with CSS variables and pre-built utility classes. Always use these variables instead of hard-coded values.**

### CSS Variables (Design Tokens)

All design tokens are defined in `styles/variables.css`.

**Colors:**
```css
.my-component {
  background: var(--surface-base);
  color: var(--text-primary);
  border: 1px solid var(--border-subtle);
}

/* ❌ DON'T hard-code colors */
.bad-component {
  background: #ffffff; /* Wrong! */
  color: #333333;      /* Wrong! */
}
```

**Spacing:**
```css
.my-component {
  padding: var(--space-4);
  gap: var(--space-3);
  margin-bottom: var(--space-6);
}

/* ❌ DON'T hard-code spacing */
.bad-component {
  padding: 16px; /* Wrong! */
}
```

**Typography:**
```css
.my-heading {
  font-size: var(--text-2xl);
  font-weight: var(--font-semibold);
  line-height: var(--leading-tight);
}
```

**Other Variables:**
- Border radius: `var(--radius-lg)`
- Shadows: `var(--shadow-sm)`
- Transitions: `var(--transition-fast)`

### Component Styling Approaches

**1. Scoped Styles (Preferred for Components)**

```vue
<template>
  <div class="user-card">
    <img :src="user.avatar" class="avatar" />
    <h3 class="name">{{ user.name }}</h3>
  </div>
</template>

<style scoped>
.user-card {
  padding: var(--space-4);
  background: var(--surface-elevated);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
}

.avatar {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-full);
}
</style>
```

**2. Utility Classes (Preferred for Layout)**

```vue
<template>
  <div class="flex flex-col gap-4 p-4">
    <div class="flex items-center justify-between">
      <h2 class="text-2xl font-semibold">Title</h2>
      <button class="btn btn-primary">Action</button>
    </div>
  </div>
</template>
```

**3. Pre-Built Component Classes**

```vue
<template>
  <!-- Buttons -->
  <button class="btn btn-primary">Primary</button>
  <button class="btn btn-secondary">Secondary</button>

  <!-- Inputs -->
  <input class="input" type="text" />
  <textarea class="textarea"></textarea>

  <!-- Cards -->
  <div class="card">
    <div class="card-header">Header</div>
    <div class="card-body">Content</div>
  </div>
</template>
```

### Common Utility Classes

**Layout:**
```html
<!-- Flexbox -->
<div class="flex flex-col items-center justify-between gap-4">
<!-- Grid -->
<div class="grid grid-cols-3 gap-4">
<!-- Spacing -->
<div class="p-4 m-2">
<!-- Size -->
<div class="w-full h-full">
<!-- Overflow -->
<div class="overflow-y-auto">
```

**Typography:**
```html
<!-- Headings -->
<h1 class="h1">Heading 1</h1>

<!-- Text sizes -->
<p class="text-sm">Small text</p>
<p class="text-base">Base text</p>
<p class="text-lg">Large text</p>

<!-- Font weight -->
<span class="font-semibold">Semibold</span>

<!-- Text color -->
<p class="text-primary">Primary color</p>
```

### Form Styling

```vue
<template>
  <form @submit.prevent="handleSubmit" class="form-stack">
    <div class="form-group">
      <label for="email" class="form-label">Email</label>
      <input
        id="email"
        v-model="email"
        type="email"
        class="input"
        required
      />
    </div>

    <button type="submit" class="btn btn-primary btn-block">
      Submit
    </button>
  </form>
</template>
```

### Responsive Design (Mobile-First)

```vue
<template>
  <!-- Stack on mobile, row on tablet+ -->
  <div class="stack-to-row">
    <div>Left</div>
    <div>Right</div>
  </div>
</template>
```

**Custom Media Queries:**
```css
.my-component {
  /* Mobile styles (default) */
  padding: var(--space-2);
}

@media (min-width: 768px) {
  .my-component {
    /* Tablet and up */
    padding: var(--space-4);
  }
}
```

### Animations

**Pre-defined Transitions:**
```vue
<template>
  <!-- Fade in/out -->
  <transition name="fade" mode="out-in">
    <component :is="currentView" />
  </transition>

  <!-- Slide down (notifications) -->
  <transition name="slide-down">
    <div v-if="showNotification">Notification</div>
  </transition>
</template>
```

**Custom Animations:**
```vue
<style scoped>
.my-element {
  transition: all var(--transition-base);
}

.my-element:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}
</style>
```

### Common Mistakes to Avoid

**❌ WRONG: Hard-coded values**
```css
.bad-component {
  padding: 16px;              /* Use var(--space-4) */
  color: #333333;             /* Use var(--text-primary) */
  font-size: 14px;            /* Use var(--text-sm) */
  transition: all 0.3s ease;  /* Use var(--transition-base) */
}
```

**✅ CORRECT: CSS variables**
```css
.good-component {
  padding: var(--space-4);
  color: var(--text-primary);
  font-size: var(--text-sm);
  transition: all var(--transition-base);
}
```

### Style Organization in Components

Order CSS properties as:
1. Layout & positioning
2. Box model (size, spacing)
3. Visual (colors, borders, shadows)
4. Typography
5. Transitions & animations
6. States (hover, focus, active)
7. Media queries

### Checklist

- [ ] Uses CSS variables instead of hard-coded values
- [ ] Scoped styles for component-specific CSS
- [ ] Utility classes for common layout patterns
- [ ] Pre-built component classes where available
- [ ] Mobile-first responsive design
- [ ] Consistent spacing using `--space-*` scale
- [ ] Transitions use `--transition-*` variables
- [ ] Colors use semantic variable names
- [ ] No !important flags (unless absolutely necessary)

### Golden Rules

1. **Always use CSS variables** from `variables.css`
2. **Prefer scoped styles** for component-specific CSS
3. **Use utility classes** for common layout patterns
4. **Mobile-first** responsive design
5. **Consistent spacing** with design token scale
6. **No hard-coded** colors, spacing, or timing values
