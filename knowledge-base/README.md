# Knowledge Base

> The Agent Colony pattern is a living document. This folder is where its evolution is recorded — the feedback that shaped it, the lessons extracted from that feedback, the prior art it draws on, and the design memos that point at where it might go next.

The pattern's own specification requires colonies to maintain Event Memory, Lesson Memory, and Constitutional Memory. This knowledge base applies that principle to the pattern's own development. Feedback arrives, lessons are extracted, recurring lessons graduate into specification rules. The process that the pattern prescribes for colonies is the process that built the pattern itself.

## Structure

```
knowledge-base/
├── README.md                    # this file
├── feedback/                    # peer review, critique, reader reactions
├── lessons/                     # insights extracted from feedback and development
├── references/                  # external prior art, related standards, academic work
└── writings/                    # things written about the pattern (articles, talks)
```

- **[feedback/](feedback/)** — peer review captured as it arrives. Every round is dated and preserved. Negative feedback is as welcome as positive — it is the kind that changes things.
- **[lessons/](lessons/)** — insights distilled from the feedback and from building. Each lesson carries an evidence grade and a note on whether it has graduated into a specification rule.
- **[references/](references/)** — external work the pattern engages with: prior art, related standards, academic papers. The literature review in the thesis is the formal statement; these files are the working notes behind it.
- **[writings/](writings/)** — articles, blog posts, and talks about the pattern. Each entry is preserved verbatim with a link to the canonical published version. Outgoing communication, complementing the incoming feedback.

Forward-looking design memos about what to build next live in [`../examples/`](../examples/) alongside worked examples. Start with [`../examples/demonstration-options.md`](../examples/demonstration-options.md) for the most recent.

## How to contribute

1. **Feedback** — open an issue using the Challenge or Refinement template. If the feedback is substantial enough to capture verbatim, open a PR adding a file to `feedback/` with date and reviewer attribution (or "anonymous peer review" if they prefer).
2. **Lessons** — if you notice a recurring pattern across multiple feedback threads, propose a new file in `lessons/` with the evidence backing it. Lessons are not opinions; they carry grades.
3. **References** — if the pattern engages with an external work not currently in the references, add it. Keep entries short and link to the primary source.

## How the knowledge base is used

- **Feedback** informs the next revision of the manifesto, thesis, and specification. Every substantive revision cites the feedback that prompted it.
- **Lessons** that recur in 3+ places graduate into specification rules. This mirrors how the pattern itself promotes lessons to constitutional memory.
- **References** are the raw material for the literature review. When a new reference is added, the thesis gap analysis is checked against it.

## Why this folder exists

An earlier reviewer observed that the pattern repeatedly asserts "this is v1, interrogate it" but had no visible mechanism for capturing that interrogation. The manifesto asked for peer review; the repo did not make it easy to see what peer review had already happened or what it had changed.

This folder closes that loop. Every critique captured here is visible to future readers. Every lesson is traceable back to the feedback that produced it. Every rule in the specification can be queried for its origin. The pattern's intellectual honesty is now a property of the repository, not just of the prose.

This is also a hedge against a specific failure mode: **the pattern becoming dogma**. Dogma is what happens when rules are preserved but the reasoning that produced them is lost. Keeping the feedback verbatim alongside the lessons and rules means future contributors can always ask "why does this rule exist?" and get a real answer — the conversation that produced it, in the words of the people who had it.
