---
name: frontend-scrolling-conventions
description: Enforces locked viewport with internal scrolling using view container classes. Use when creating views, fixing overflow issues, or ensuring proper scroll behavior.
---

# Frontend Scrolling Conventions

This skill defines scrolling conventions where the global container is non-scrollable and all scrolling happens internally.

## When to Use

- When creating any new view
- When content extends beyond viewport height
- When fixing content overflow issues
- When implementing scrollable components
- When debugging scroll behavior

## Instructions

### Core Principle

**The global container (`html`, `body`, `#app`, `.app-main`) is ALWAYS non-scrollable. The viewport is locked to prevent body scroll.**

If any view or component needs to display content taller than the screen, it MUST use internal scrolling.

### Why This Matters

A locked viewport provides:
- Consistent layout (no shifting when content changes)
- Predictable positioning (fixed/absolute elements stay in place)
- Better mobile experience (no overscroll bounce on body)
- Cleaner animations
- Full control over scrolling behavior

### View Container Options

Every view **must** use one of these container classes:

**1. `.view-fullscreen` (Non-Scrollable)**

For views that fit entirely within the viewport (auth pages, simple forms).

```vue
<template>
  <div class="view-fullscreen">
    <div class="auth-card">
      <h1>Login</h1>
      <form>...</form>
    </div>
  </div>
</template>
```

**When to use:**
- Content will always fit on screen
- Login/signup pages
- Loading screens
- Empty states
- Error pages

**2. `.view-scrollable` (Scrollable)**

For views with content that may exceed viewport height (dashboards, lists, long forms).

```vue
<template>
  <div class="view-scrollable">
    <div class="view-content">
      <h1>Dashboard</h1>
      <div v-for="item in longList" :key="item.id">
        {{ item }}
      </div>
    </div>
  </div>
</template>
```

**When to use:**
- Content may exceed screen height
- Lists, feeds, dashboards
- Long forms or content
- Settings pages

### Decision Tree

```
Will content ALWAYS fit on screen?
├─ YES → .view-fullscreen
└─ NO or MAYBE → .view-scrollable (safer default)
```

**Default to `.view-scrollable`** when uncertain.

### Component-Level Scrolling

Components can have internal scrolling when needed:

**Scrollable Modal:**
```vue
<template>
  <div class="modal-overlay">
    <div class="modal-container">
      <div class="modal-header">Header (fixed)</div>
      <div class="modal-body overflow-y-auto">
        <!-- Scrollable content -->
      </div>
      <div class="modal-footer">Footer (fixed)</div>
    </div>
  </div>
</template>

<style scoped>
.modal-container {
  display: flex;
  flex-direction: column;
  max-height: 90vh;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
}
</style>
```

### Common Patterns

**Pattern 1: Fixed Header + Scrollable Content**
```vue
<template>
  <div class="view-scrollable">
    <header class="page-header sticky top-0 bg-white">
      <h1>Page Title</h1>
    </header>
    <div class="view-content">
      <!-- Long content -->
    </div>
  </div>
</template>
```

**Pattern 2: Split View (Both Sides Scroll)**
```vue
<template>
  <div class="flex h-full">
    <div class="flex-1 overflow-y-auto">
      <!-- Left panel (scrollable) -->
    </div>
    <div class="flex-1 overflow-y-auto">
      <!-- Right panel (scrollable) -->
    </div>
  </div>
</template>
```

### Debugging Issues

**Issue: Content is cut off, no scroll**
- **Cause**: Using `.view-fullscreen` but content is too tall
- **Fix**: Change to `.view-scrollable`

**Issue: Whole page scrolls (body scroll)**
- **Cause**: View container missing or incorrect
- **Fix**: Ensure view uses proper container class

**Issue: Component overflow not working**
- **Cause**: Missing explicit height or flex constraints
- **Fix**: Add height constraint to component

### CSS Utilities

Use these utility classes:
```css
.overflow-hidden     /* No scrolling */
.overflow-auto       /* Auto scrolling (both axes) */
.overflow-y-auto     /* Vertical scrolling only */
.overflow-x-auto     /* Horizontal scrolling only */
.scrollbar-hidden    /* Invisible scrollbar */
```

### Checklist for New Views

- [ ] View has a container class (`.view-fullscreen` or `.view-scrollable`)
- [ ] If using `.view-scrollable`, wrapped content in `.view-content`
- [ ] No custom `overflow` styles on view container
- [ ] Tested on mobile viewport
- [ ] Tested with content taller than screen
- [ ] No body/html scroll occurs

### Golden Rules

1. **Every view** must use `.view-fullscreen` or `.view-scrollable`
2. **Never modify** overflow on `html`, `body`, `#app`, or `.app-main`
3. **Default to `.view-scrollable`** when content height is uncertain
4. **Components can scroll** internally when needed
5. **Test with tall content** to ensure scrolling works
