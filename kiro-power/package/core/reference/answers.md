# Answers and rounds

Summary in MANUAL §5.

**Answer mode** (`_status.md` → *Preferences*; if `ask`, ask once and save the choice):
- **walkthrough** — *Questions per message* (Preferences, default 5) at a time, most important first, each with
  options and your ★ recommendation, from the round fixed up front (`ba answers new <slug> --chat`). Open with the
  size ("Round 2: 24 questions, 5 at a time"); head each message with progress ("Questions 6–10 of 24"). The BA may
  answer, skip, or say "★ for the rest".
- **file** — `ba answers new <slug> [--who "<name>"] [--ids …]` writes `answers/round-NN.md`; the BA (or the
  stakeholder) ticks options or writes answers, saves, and says **"done"**; then `ba answers read <slug>` prints the
  answers and files the form as a new `SRC-`. Best when answers come from other people or a meeting.
- Either way, record each answer as a `D-` (or an `A-` status) with who answered.

**A round is complete before the first question is asked.** Finish the whole sweep (foundations, all gap lenses,
the profiles' questions) and **build in the follow-ups**: when an option would raise a further question, put it in
that option ("(b) escalate — to whom, after how many days?"). Questions that answers raise mid-round: Blocking and
Decision-critical ones join the next message (the total goes up and the progress line says so); the rest wait for
the next round. Nice to know is parked. Rounds are counted (*Elicitation round*), not turns.
