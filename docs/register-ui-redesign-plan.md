# Register UI Redesign Plan

## Objective

Upgrade the current `Warm Signup Sketch` from a concept-driven visual into a product-ready signup screen that preserves the warm mascot direction while making registration the clear primary goal.

## Core Decisions

1. Reduce left-side illustration dominance so the form becomes the first actionable focal point.
2. Remove explanation-heavy decorative content that does not help the user register.
3. Rebuild the form area as a real component system with clear states and stronger CTA emphasis.
4. Improve conversion clarity with better supporting copy, lower-friction trust cues, and a cleaner action path.

## Layout Strategy

### Left Brand Panel

- Keep the mascot illustration.
- Keep one short emotional headline.
- Keep one concise support line.
- Remove the four expression/state cards from the first screen.
- Reduce decorative background blobs and visual noise.
- Shrink the mascot/stage presence by roughly 15% to 20%.

### Right Signup Panel

- Increase the panel's visual weight and perceived importance.
- Use a cleaner internal spacing rhythm.
- Keep this content order:
  - welcome badge
  - page title
  - supporting copy
  - username field
  - email field
  - password field
  - confirm password field
  - terms checkbox row
  - trust/supporting note
  - primary CTA
  - login switch link

## Component Rules

### Input Fields

- Height: 52px to 56px
- Clear outline and white input surface
- Consistent icon treatment using real vector-style symbols
- Visible default, focus, and error states
- Password fields should support a visibility affordance

### CTA

- Full-width primary button
- Stronger contrast than surrounding warm tones
- Action-first copy: `创建账号`
- Designed for default / hover / press / loading / disabled behavior

### Terms and Trust

- Replace passive legal helper copy with an explicit checkbox row
- Make `服务条款` and `隐私政策` visually clickable
- Add one low-friction trust line, for example:
  - `你的邮箱仅用于账号验证，不会公开展示`

## Visual System Changes

- Background remains warm cream.
- Form card stays near-white for separation.
- Inputs stay pure white with warmer border tones.
- CTA shifts to a stronger warm orange for contrast.
- Text hierarchy should clearly separate:
  - headline
  - support copy
  - field labels
  - helper text
  - legal text

## Copy Direction

### Left Panel

- Headline: `把你的 AI 灵感入口，安顿下来`
- Support line: `创建账号后即可开始定制资讯节奏、收藏重点内容，并持续追踪你的兴趣主题。`

### Right Panel

- Eyebrow: `欢迎加入`
- Title: `创建你的账号`
- Support line: `30 秒完成设置，开始建立属于你的 AI 资讯流。`
- CTA: `创建账号`
- Login switch: `已有账号？立即登录`

## Implementation Priorities

1. Remove the four state cards.
2. Rebalance the left and right visual weight.
3. Increase form clarity and CTA prominence.
4. Replace symbolic text icons with proper icon-like marks.
5. Add checkbox-based terms confirmation and trust messaging.

## Success Criteria

The redesign succeeds if:

1. The page reads as a signup page before it reads as an illustration page.
2. The user can identify the action path within 3 seconds.
3. The form feels like a real interactive UI, not a presentation mockup.
