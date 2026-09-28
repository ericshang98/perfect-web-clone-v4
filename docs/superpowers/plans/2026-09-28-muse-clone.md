# Meta Muse Page Clone Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a responsive local React/Vite clone of Meta Muse's full landing page with matching visual language and interactive states.

**Architecture:** Create an isolated Vite app in `showcase/products/muse`. Keep page composition and UI state in `src/App.jsx`; keep all visual styling, responsive layout, and animation in `src/index.css`; use CSS-generated media placeholders instead of remote video assets.

**Tech Stack:** React 18, Vite 5, plain CSS.

---

### Task 1: Scaffold the Muse app

**Files:**
- Create: `showcase/products/muse/package.json`
- Create: `showcase/products/muse/index.html`
- Create: `showcase/products/muse/src/main.jsx`
- Create: `showcase/products/muse/src/App.jsx`
- Create: `showcase/products/muse/src/index.css`

- [ ] **Step 1:** Copy the base Vite package metadata and set the app title to Meta Muse Clone.
- [ ] **Step 2:** Add `main.jsx` to mount `<App />` and import global CSS.
- [ ] **Step 3:** Build the page markup in `App.jsx` with semantic sections, nav anchors, tab/card state, carousel state, FAQ state, and media controls.
- [ ] **Step 4:** Add CSS tokens, typography, section grids, responsive breakpoints, gradient media surfaces, and keyframe animations in `index.css`.
- [ ] **Step 5:** Run `npm install` and `npm run build` from the Muse app directory.
- [ ] **Step 6:** Commit the scaffold and page implementation with `git add showcase/products/muse && git commit -m "feat: add Meta Muse landing page clone"`.

### Task 2: Verify desktop and mobile behavior

**Files:**
- Modify: `showcase/products/muse/src/App.jsx` if interaction defects are found.
- Modify: `showcase/products/muse/src/index.css` if layout defects are found.

- [ ] **Step 1:** Start Vite on a local port and open the page in the browser at a desktop viewport.
- [ ] **Step 2:** Confirm hero, feature tabs, creator carousel, FAQ accordion, links, and media controls visibly change state.
- [ ] **Step 3:** Capture the page at desktop and mobile widths and adjust overflow, type scale, and card stacking.
- [ ] **Step 4:** Run `npm run build` again and confirm no console or compile errors.
- [ ] **Step 5:** Commit visual fixes with `git add showcase/products/muse && git commit -m "fix: tune Muse clone responsive behavior"`.
