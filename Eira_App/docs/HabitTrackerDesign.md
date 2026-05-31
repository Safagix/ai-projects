# Eira Habit Tracker: Design Document

## Part 1: Market Research and Critical Analysis

### The Current State of Habit Tracking

The habit tracker market is saturated with applications that share a common set of features: daily checkboxes, streak counters, and basic gamification elements. Despite sophisticated interfaces and millions of downloads, the underlying problem remains unsolved.

Research shows that approximately 80% of users abandon habit tracking apps within the first three days. By day 60, that number rises to 92%. The question is not whether these apps are well-designed in a technical sense, but whether they understand human behavior at a fundamental level.

Most do not.

### What Existing Trackers Get Right

The best applications on the market have identified certain principles that work:

- Visual progress tracking increases user engagement. Seeing a grid fill up or a progress bar advance provides immediate feedback that activates the brain's reward system.

- Simplicity in interface reduces friction. Apps like Streaks and Loop succeed because they do not overwhelm users with features during the critical first week.

- Reminders, when properly timed and personalized, help users remember to perform their habits. The key word here is "personalized" because generic push notifications quickly become noise.

- Community features can provide social accountability. Knowing others are on the same journey creates a sense of shared purpose.

- The habit loop of cue, routine, and reward is well-understood. Successful apps implement this loop by serving as the cue (notification), making the routine easy (one-tap logging), and providing a reward (visual confirmation).

### What Existing Trackers Get Wrong

Despite these successes, the failures are more instructive.

The streak mechanic is the most common and most problematic feature. While streaks can initially motivate, they create several dangerous patterns:

- They promote perfectionism. A streak demands unbroken consistency, which is not how real life works.

- They create anxiety. Users report feeling judged by their apps and stressed about maintaining their numbers.

- They punish bad days. When a streak breaks, the app treats it as a complete failure, even if the user has maintained consistency for months.

- They shift motivation from intrinsic to extrinsic. Users stop caring about the benefit of the habit and start caring about defending the number.

Beyond streaks, many trackers fail because they are fundamentally designed for people who already have discipline. They are downloaded by people who need to build discipline, creating a mismatch between the product and its actual users.

Other structural weaknesses include:

- Lack of context awareness. Life is unpredictable. Illness, travel, emergencies, and simply difficult days are normal. Most trackers treat every day the same.

- Binary success-failure logic. Either you did the habit or you did not. There is no room for partial completion, reduced effort on hard days, or celebrating the attempt.

- No emotional connection. Apps focus on what users should do, not why they do it or how they feel. There is no space for reflection or meaning-making.

- Overwhelming complexity. Some apps offer so many features that users spend more time configuring than actually building habits.

- Fragility of progress. All effort is tied to a single daily action. Miss one day and the psychological perception is that everything is lost.

### The Deeper Problem

The fundamental issue is that most habit trackers are built around the wrong model of human behavior. They assume that people fail to build habits because of a lack of tracking or a lack of reminders. The truth is more complex.

Habits are not just about repetition. They are about identity. A person who identifies as a reader will read. A person who identifies as healthy will exercise. The behavior flows from the self-concept, not from external pressure.

Most habit trackers apply external pressure and expect it to create internal change. This rarely works. What users need is a system that helps them see themselves differently, not a system that punishes them for imperfection.

## Part 2: The Eira Habit Tracker Philosophy

### Core Principles

The Eira Habit Tracker is built on a different foundation. It rejects the assumption that users need to be pressured into consistency. Instead, it operates on the following principles:

- Habits are connected to identity, not streaks. The goal is not to maintain a number but to become a certain kind of person.

- Progress is measured in patterns, not perfection. A user who completes a habit 80% of the time over three months has built something real, regardless of broken streaks.

- Bad days are expected and accommodated. The system does not punish missed days. It treats them as data points in a larger picture.

- Reflection is part of the process. Users are encouraged to think about why they want to build a habit, how they feel about their progress, and what obstacles they face.

- The tracker integrates with the rest of life. Habits connect to notes, calendar events, and Eira's conversational interface. They are not isolated checkboxes.

### What This Tracker Is

The Eira Habit Tracker is a system for self-awareness and gentle accountability. It helps users:

- Define who they want to become.
- Track behaviors that align with that identity.
- Reflect on their journey without judgment.
- See patterns over time rather than obsessing over daily performance.
- Receive encouragement that adapts to their current state.

### What This Tracker Is Not

It is not a punitive system. There are no broken streaks, no reset counters, no shame mechanics. Missing a day does not erase progress.

It is not pure gamification. While visual elements provide feedback, the system does not rely on dopamine-driven mechanics that create dependency.

It is not a checkbox list. While habits can be marked as complete, the interface encourages context and reflection rather than mindless tapping.

## Part 3: Core Features

### Identity Anchors

When creating a habit, users are asked to articulate the identity behind it. Instead of "Exercise 30 minutes" the user defines "I am becoming someone who prioritizes physical health."

This identity anchor appears throughout the interface, reminding users why they are doing what they are doing. The habit is not just an action; it is evidence of who they are becoming.

### Flexible Completion States

Rather than binary complete-or-not states, habits can be marked as:

- Completed as intended
- Partially completed (with optional note)
- Acknowledged but not completed (user was aware of the habit and made a conscious choice)
- Automatically excused (user has marked the day as a recovery day, travel day, or similar)

This flexibility removes the all-or-nothing pressure and creates space for real life.

### Pattern View Instead of Streak View

The primary visual is not a streak counter but a pattern view. This view shows the last 30, 60, or 90 days as a grid where:

- Completed days are shown in a solid, vibrant color
- Partial days are shown in a lighter shade
- Acknowledged days are shown with a subtle indicator
- Missed days are shown in a neutral tone, not red or alarming

The pattern view emphasizes overall consistency rather than unbroken chains. A user can see at a glance that they have been 75% consistent over the past month, which is a meaningful achievement regardless of whether there were consecutive missed days.

### Momentum Score

Instead of streak counts, users have a Momentum Score. This score is calculated based on:

- Recent activity (last 7 days weighted more heavily)
- Overall consistency (percentage of days completed over time)
- Recovery rate (how quickly the user returns after a missed day)

The Momentum Score can increase even after a missed day if the user returns quickly and maintains overall consistency. It measures the trend, not the perfection.

### Weekly Reflection Prompt

Once per week, the tracker prompts users with a short reflection. This is not a mandatory feature, but it is encouraged. The reflection asks:

- How do you feel about your progress this week?
- What made it easier or harder to maintain your habits?
- Is there anything you want to adjust?

Responses are stored as notes and can be reviewed later. Over time, users build a journal of their habit journey that provides insight into patterns and growth.

### Contextual Awareness

Users can mark days with context tags such as:

- Travel
- Illness
- High stress
- Rest day
- Special occasion

When a day is tagged, the system adjusts its expectations. A missed habit on a travel day does not affect the Momentum Score the same way as a missed habit on a normal day.

### Adaptive Encouragement

Eira, the conversational AI at the center of the app, provides encouragement that adapts to the user's state:

- When the user is on a strong run, Eira acknowledges the progress without excessive celebration.
- When the user has missed several days, Eira does not shame but instead offers a gentle prompt to return.
- When the user completes difficult habits, Eira recognizes the effort.
- When the user reflects, Eira may summarize patterns or ask follow-up questions.

This is not generic motivational text. Eira responds based on actual user data and adjusts tone accordingly.

## Part 4: User Experience Flow

### Creating a Habit

The user opens the Habits module and selects "New Habit."

They are first asked: "What kind of person do you want to become?" This is the identity anchor and is required.

Then they define the specific behavior, the frequency (daily, multiple times per week, or custom), and optionally set a reminder.

The habit is created and appears in the main habit list.

### Daily Interaction

Each day, the user sees their active habits. For each one, they can:

- Tap once to mark as complete
- Long-press to access flexible completion options
- Swipe to view notes or reflections related to that habit

The interface is minimal and fast. Most interactions take less than two seconds.

### Weekly Review

At the end of the week, a subtle prompt appears encouraging reflection. Users can write freely or respond to guided questions. This reflection is linked to the habits of that week.

### Monthly Pattern Analysis

Each month, the user can view a summary that shows:

- Overall consistency across all habits
- Momentum trends over the month
- Common context tags (e.g., user missed more habits during high-stress weeks)
- Any notes or reflections from the period

This is not a judgment. It is information that helps users understand themselves.

## Part 5: Integration with Eira Ecosystem

### Notes Connection

Any reflection or note attached to a habit is stored in the Notes module. Users can search their notes and find entries related to specific habits.

Habits can also reference notes. For example, a habit called "Write 500 words" could link to a note where the user tracks their writing project.

### Calendar Connection

Habits with scheduled reminders appear on the Calendar. Users can see at a glance which days have habit reminders and which do not.

Context tags (travel, illness, etc.) can also be marked from the Calendar, which then flows into the Habit module automatically.

### Conversational Integration

Eira can be asked about habits:

- "How am I doing with my exercise habit?"
- "What's my momentum score?"
- "Show me my reflections from last month."
- "I'm traveling this week, pause my habits."

This allows habits to be managed through natural language, not just through the dedicated interface.

## Part 6: How It Evolves with the User

The system is designed to grow alongside the user.

In the first weeks, the focus is on building awareness. Users are not pressured to achieve perfection; they are encouraged to simply notice their behavior and reflect.

As patterns emerge, the tracker provides more insight. Users can see which days of the week are harder, which context tags correlate with missed habits, and how their momentum has trended over months.

For users who achieve high consistency, the system subtly fades into the background. Habits that have become truly automatic no longer need active tracking. Users can archive habits that are now part of their identity without ceremony or loss.

For users who struggle, the system offers compassion. It does not escalate reminders or add pressure. Instead, it asks reflective questions and offers to adjust expectations. The goal is never to make the user feel bad but to help them understand what is happening and what might help.

## Part 7: Why This Design Is Different

Most habit trackers are built on the assumption that users need external pressure. Eira's Habit Tracker is built on the assumption that users need self-understanding.

Most trackers punish imperfection. This tracker expects it.

Most trackers measure streaks. This tracker measures patterns.

Most trackers are isolated tools. This tracker is integrated into a larger system of notes, calendar, and conversational AI.

Most trackers create anxiety. This tracker aims to create awareness.

The result is a system that users do not fear. They do not dread opening the app after a missed day. They do not feel judged. They feel seen and supported in a realistic, long-term journey of becoming the person they want to be.

This is what makes the Eira Habit Tracker fundamentally different.

## Part 8: Technical Implementation Notes

### Data Model

Each habit contains:

- Unique identifier
- Identity anchor (text)
- Behavior description
- Frequency configuration
- Reminder settings (optional)
- Creation date
- Archive status

Each habit log entry contains:

- Date
- Completion state (completed, partial, acknowledged, excused)
- Optional note
- Context tag (optional)

### Momentum Score Calculation

The algorithm weights recent days more heavily, considers consistency over weekly windows, and includes a recovery component that rewards quick returns after missed days.

### Storage

All data is stored locally using the existing Tauri filesystem plugin. The schema follows the pattern established in the Backend Document.

### Future Considerations

Cloud sync could be added later for users who want access across devices, but the local-first principle must be maintained.
