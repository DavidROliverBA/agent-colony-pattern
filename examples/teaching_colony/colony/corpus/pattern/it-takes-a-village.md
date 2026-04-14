---
title: "It takes a village — the Agent Colony definition"
subtitle: "How we might one day let our AI Agents run their own world — and why we should think about it now"
author: David R Oliver
date_published: 2026-04-12
venue: Medium
url: https://medium.com/@davidroliver/it-takes-a-village-the-agent-colony-definition-32b9bd714bb8
audience: general
pattern_version_referenced: v1.1.x — the article is a lay-audience definition, not a citation of a specific spec version
length: ~16 min read
---

# It takes a village — the Agent Colony definition

> **How we might one day let our AI Agents run their own world — and why we should think about it now.**

*Originally published on Medium, 2026-04-12. [Read on Medium →](https://medium.com/@davidroliver/it-takes-a-village-the-agent-colony-definition-32b9bd714bb8)*

---

Imagine you walk into your kitchen one morning and ask the little speaker on the windowsill what the weather is doing. It tells you. You ask it to add milk to the shopping list. It does. You ask it to remind you to ring your sister at four o'clock. It will.

That little speaker is what people in my line of work call an AI agent. It's a computer program that can listen, think a bit, and do things on its own. Not a person. Not a robot with arms and legs. Just a small, helpful, invisible assistant.

There aren't many of them in your house yet. Maybe one or two. But in offices, factories, banks, and hospitals around the world, people are building thousands and thousands of them. Some answer the phone. Some read documents. Some watch for fraud. Some help doctors look at scans. They are everywhere, and there are more arriving every week.

And here's the thing nobody is really talking about: nobody has worked out how all these helpers are supposed to live together.

This is a piece about that question. I'm going to use a story about a village to explain it, because villages are something we all understand, and because the problem with the helpers turns out to be very much like the problem of running a village well.

## The village that grew too fast

Picture a village fifty years ago. One general shop. The shopkeeper knew everyone. If you wanted bread, milk, a stamp, or a pair of shoelaces, you went to the same place. Simple. Easy to understand. One person to thank, one person to complain to.

Then the village grew. The general shop wasn't enough any more. Someone opened a bakery. Someone else opened a butcher's. A greengrocer arrived. A post office. A chemist. Now there were lots of little shops, each one good at one thing. Better in many ways — fresher bread, proper meat, a real chemist who knew about medicines. But also more complicated. Where do you go? Who's in charge? What happens if two shops sell the same thing and one of them is rubbish?

This is more or less the story of every kind of organisation in the modern world. We start with one big thing that does everything. It gets too big to manage. We break it into smaller, specialised things. Then we have a different problem: how do you keep the smaller things working together properly?

Computers have been through exactly the same story. Big programs, then small specialised programs, then thousands of small specialised programs, all trying to talk to each other.

And now we are at the next step. The little programs are becoming agents — not just tools that do what they're told, but helpers that can think a bit, decide a bit, and act on their own. And the village they live in doesn't have any rules yet.

## What does it mean for a computer to think a bit?

Before we go further, let me explain what I mean by "an agent that can think a bit." I don't mean it dreams. I don't mean it has feelings. I mean, it can do something more interesting than just following orders.

A normal computer program is like a vending machine. You push button B4, and it gives you a packet of crisps. Always the same crisps. No surprises. If you push a button that doesn't exist, it just sits there.

An agent is more like a shop assistant. You can say, "I'm looking for something for my granddaughter's birthday, she's seven and likes horses." The shop assistant will think about it, suggest a few things, ask you a question or two, and try to help. They might even say, "We don't have anything quite right, but the toy shop next door might."

Most of the agents around today aren't quite as good as a real shop assistant yet. But they're getting closer. And the important difference is that they make small decisions on their own, instead of waiting for someone to push button B4.

Here's the bit that worries the people who think about these things for a living: an agent can also change itself. If a real shop assistant learned a new skill, you'd notice — they'd tell you, or you'd see them at a course. If an agent learns a new skill, you might not notice at all. It just starts doing something a bit differently than it did yesterday. Multiply that by ten thousand agents, and you have a problem.

## Six Principles

What I've been working on is a set of principles, like "look both ways before you cross the road" — that I think any village of agents will need if it's going to work for a long time without falling apart.

There are six of them.

### Rule 1: Good neighbours, not masters and servants

Most people who think about AI today imagine it as a tool. You're the boss. The AI does what it's told. End of story.

That's fine for a vending machine. It's not quite right for something that can think a bit. If you treat a thinking thing as nothing more than a tool, you end up with a strange relationship: you're constantly giving orders, it's constantly obeying, and nobody is responsible for what happens when the orders are wrong or the situation changes.

A better way is to think of agents and people as neighbours. Not equals — humans are still in charge of the things that matter — but neighbours sharing a fence. On one side of the fence is the human world, where humans decide things. On the other side is the agents' world, where they handle their own day-to-day business. Anything that crosses the fence — anything that affects the human side — needs a checkpoint. Like a gate you have to open.

The most important thing this fence protects against isn't an agent doing something rude in the human world. It's a human reaching into the agents' world on a bad day and breaking something, because they were tired, or angry, or didn't understand what they were touching.

Honest admission: this rule doesn't solve every problem. It just moves the question from "should there be a fence?" to "where should we put the fence, and what counts as crossing it?" Those are still hard questions. But at least we've named them.

### Rule 2: An agent is who it is, not what it's made of

Imagine your village had a wonderful baker. Mrs Thompson. She'd been baking for forty years. Then one day, she retired, and her daughter took over. Same shop, same bread, same kindness — but a different person. The shop kept its name and its character, even though the actual baker had changed.

Now imagine instead that the village rule was: when a baker retires, you have to knock down the bakery and build a brand new one from scratch, with no memory of what the old bakery was like or how the bread used to taste. Madness, isn't it?

That's exactly how we treat computer programs today. When the technology underneath them gets old, we throw the whole thing away and start again. All the experience, all the lessons, all the things that worked — gone.

The second rule says: an agent should be defined by who it is — its purpose, its history, what it's good at, what it promises to do, what it's allowed to change about itself — not by what bits of technology it happens to be made from this year. That way, when the technology changes, the agent can move to the new technology without losing itself. Like Mrs Thompson's daughter taking over the bakery.

### Rule 3: Keep the high street balanced

Remember the village high street with all those little shops? There are two ways it can go wrong.

One way: one shop gets really successful and starts taking over. First, it sells bread, then it adds milk, then it adds vegetables, then meat, then the post office moves inside it, and before long, the other shops have closed, and you've got one giant supermarket that you can't get rid of because the whole village depends on it. (This is also what happened in real life to a lot of high streets.)

The other way: every time someone wants something, they open a new shop instead of using one of the existing ones. Soon, you've got fifteen bakeries on the same street, none of them making any money, none of them quite as good as a single proper bakery would be.

Agent villages have exactly the same problem. Some agents try to do everything. Some agents are nearly identical to other agents nobody knows about. If you don't watch this carefully, the village either collapses into one giant agent that's impossible to manage, or it fills up with hundreds of nearly-identical agents that nobody understands.

So the third rule is: somebody — or rather, some agent whose job this is — has to keep an eye on the balance. Not by deciding everything, but by noticing when things are getting wonky and raising a flag.

### Rule 4: Built to last

The fourth rule is about time. A real village isn't built to last five years. It's built to last centuries. The buildings might be repaired, the people change, the shops come and go, but the village itself carries on.

Most computer systems are built like a marquee at a wedding. Lovely for the day, but you wouldn't want to live in it. The team that built it moves on. The technology gets old. Nobody remembers why anything is the way it is. After a few years, it falls down, and someone builds a new marquee.

If we want our agent village to be useful for our grandchildren as well as for us, we have to build it to outlive any one team, any one technology, and any one fashion. That means writing things down. Keeping records. Making sure no single piece of the village is irreplaceable. Treating the whole thing the way you'd treat a parish church, not a marquee.

### Rule 5: Trust has to be earned

This is my favourite of the rules.

Imagine giving a brand new shop assistant the key to the safe on their first day. Not a good idea. Not because they're a bad person, but because nobody knows yet whether they can be trusted with the key. Trust has to be earned, by doing small things well, then slightly bigger things well, then bigger things still, until eventually you give them the key — and even then, you check on them now and again.

Agents should be exactly the same. A new agent shouldn't be allowed to do anything important on day one. It should start by watching, then doing small, careful things under supervision, then doing slightly bigger things, and so on. Each step has to be earned by showing it can be trusted with the previous step.

And — this is the important bit — trust can be withdrawn. If an agent does something silly, hides a mistake, or can't roll back when it should, it gets demoted. Back down a step. It has to earn the trust back.

This isn't a new idea. It's how we already raise children, train apprentices, promote junior staff, and give teenagers later bedtimes. It's an old, reliable way of dealing with anything that has to grow into its responsibilities. There's no good reason not to use it for agents.

### Rule 6: Look after each other

The last rule is about defence. Computer systems get attacked. People try to break in, steal things, plant fakes, and cause mischief. This isn't going away.

The usual approach is to bolt on security from the outside. Like hiring a guard for the village. The agents do their thing, and somebody else worries about keeping them safe.

The problem with this is that the agents have no skin in the game. They don't care about security; that's the guard's job. And the guard doesn't really understand what the agents are doing, so there's a constant tug-of-war: the guard wants to lock things down, the agents want to get on with their work.

A better way is to make security part of every agent's own concern. Like a neighbourhood watch in a village — everyone keeps an eye out, everyone helps when something's wrong, and there's a small dedicated group whose job is to notice trouble fastest. If an agent spots a problem, it can fix it straight away, even without asking permission, because waiting for permission to fix a leak is silly.

That's the six rules. Coexistence, identity, balance, longevity, earned trust, and mutual defence. You could write all six on a postcard. But following them properly turns out to need quite a lot of thought.

## How the village remembers

Here's a small puzzle. Imagine the village had a problem in 1962 — let's say a flood. The villagers worked out how to handle it. They put sandbags here, dug a ditch there, and agreed to ring the church bell as a warning. It worked.

Now it's 2026. None of the people who lived through the 1962 flood are still around. Has anyone written down what they learned? If the village floods again next month, will anyone remember the trick with the church bell?

This is what they call institutional memory. Big organisations — hospitals, councils, the army — have it built into them. They keep records, write procedures, and train newcomers. Small organisations often don't, and they pay the price every few years when they rediscover something they already knew.

Agent villages have no memory at all unless you build one. By default, when an agent retires, everything it learned dies with it. The next agent makes the same mistakes, and this can go on repeatedly.

So one of the things the village needs is a way of remembering. Not just data — anyone can store data — but actual lessons. Things that worked, things that didn't, and the reasons why. And not just storing them, but reminding the village of them when they become useful again.

It works in three layers.

The first layer is just a diary. What happened, when, and who was involved. Plain facts.

The second layer is the lessons. When something interesting happens, somebody (well, some agent whose job this is) thinks about it and writes down: here's what happened, here's why we think it happened, here's what to do differently next time.

The third layer is what the village comes to believe. After a lesson keeps being useful, it gets promoted from "something we noticed once" to "a rule we live by." But — and this matters — these rules are not carved in stone. They have to be rechecked from time to time, because the world changes. A rule that made sense in 1962 might not make sense in 2026.

The whole point is that the village should be able to learn from its own life rather than starting fresh every time the people change.

## How to stop fooling yourself

There's a danger with any system that tries to learn lessons. The danger is that you start believing your own nonsense.

You remember the things that confirmed what you already thought, and forget the things that didn't. You give too much weight to the most recent thing that happened. You hold on to old beliefs because you're invested in them, even after the evidence has gone the other way. We all do this. It's human. It's also not ideal for a village that's supposed to last a hundred years.

So the village needs a few habits to keep itself honest.

The first habit is to call lessons hypotheses, not facts. A hypothesis is a guess that you think might be right, but you're going to keep checking.

The second habit is to grade the evidence. "I saw it once" is the weakest grade. "I saw it three times in different situations" is better. "I can prove it with maths" is best. Only the strong grades are allowed to become village rules.

The third habit is the most interesting one. For any big decision, somebody has to be appointed to argue against it. Not because they really disagree, but because somebody has to find the holes. If the decision survives the argument, it's a better decision. If it doesn't, you've saved yourself a mistake. This is exactly how courts work, by the way. There's a reason for it.

The fourth habit is letting old rules die when they've outlived their usefulness. Not pretending they were always wrong — just thanking them for their service and letting them go.

If you do all four of these things, you have a chance of building a village that actually gets wiser over time, instead of one that just gets more set in its ways.

## So what's actually wrong with how we're doing it now?

You might be wondering: if all this is so important, surely somebody is already doing it?

The answer is: bits of it, in lots of different places, by lots of different groups, with no agreement on how the bits fit together. As I write this in spring 2026, there are over a hundred thousand AI agents registered in more than fifteen different lists around the world, and they can barely talk to each other. Imagine if every village in Britain had its own kind of post office stamp and they didn't recognise each other's letters. That's where we are.

Some clever people are working on bits of it. There's a group called AGNTCY, run by the Linux Foundation, that's working on a way to describe what an agent is. There's a thing called A2A from Google, a thing called MCP from a company called Anthropic, both trying to make agents able to talk to tools and to each other. There's the American government starting to ask questions about how you'd even know which agent is which. Everyone is doing useful work.

But none of them, on their own, gives you a village. They give you bricks. The pattern of how the bricks fit together — that's still missing. That's what I've been trying to write down.

## Why does any of this matter to you

You might still be thinking: this all sounds very interesting, dear, but I have my crossword to finish. Why should I care?

Two reasons.

The first reason — is that these agents are already starting to make decisions that affect ordinary people. Whether you get a loan. Whether your insurance goes up. How long do you wait at a hospital? Whether your supermarket order arrives. Right now, most of those decisions are made by simple computer programs that follow rules a person wrote. But as the agents get cleverer, more and more of those decisions will be made by agents that nobody fully understands, including the people who built them. If we don't have rules for how those agents are supposed to behave, the rules will be made up after the fact, when something has already gone wrong.

The second reason — is that the way we set this up now — in the next few years, while the village is still small — will shape what it looks like for our grandchildren. The decisions we make now about how agents should be governed are like the decisions Victorian town planners made about where to put the streets, the sewers, and the parks. You can change them later, but it's much harder. Much, much harder.

I'm not trying to scare anyone. I genuinely think this is a hopeful story. We have a chance to build something really sensible — a way of letting useful little helpers do their work for us, with proper boundaries, proper records, proper checks, and proper kindness on both sides. We just have to choose to do it.

## What I'm not pretending to know

I want to end by being honest about what I don't know.

I don't know if all six rules are right. They feel right to me, and I've thought about them for a long time, but I haven't built a village to this design and watched it run for ten years. Nobody has. The whole thing is a proposal, not a finished thing.

I don't know exactly where the fence between humans and agents should sit. I think we'll have to keep moving it as the agents get cleverer and as we understand them better. That's not a cop-out — it's just the truth.

I don't know which of the technical bits will turn out to matter most. The thing called the Agent Mirror, where an agent describes who it is — I think that's the most important bit. But I might be wrong. Maybe the memory bit will turn out to matter more. Maybe the trust ledger. We'll find out by trying.

What I am sure of is this: somebody has to start writing down what a sensible agent village looks like, and the longer we wait, the harder it gets. The technology is moving very fast. The thinking about how to live with it is not moving nearly fast enough. That's the gap I'm trying to help close.

## A last thought

If you've got this far, thank you. I know this isn't the easiest topic. I tried to write it the way I'd explain it to someone in my own family who isn't a computer person — someone wise about life but not about my odd little world of brackets and code.

The funny thing is that almost everything I've described in this piece is something villages, families, schools, and parishes have always known how to do. How to share space. How to remember. How to earn trust. How to keep the peace. How to argue without falling out. How to look after each other.

We're not really inventing anything new. We're just trying to make sure the little thinking helpers we build know how to do it too, before there are too many of them to teach.

---

*Originally published on Medium on 2026-04-12. [Read on Medium →](https://medium.com/@davidroliver/it-takes-a-village-the-agent-colony-definition-32b9bd714bb8)*

*This is the canonical text as published. The Medium URL is the live version and may be edited; this in-repo copy reflects the article as published on 2026-04-12.*
