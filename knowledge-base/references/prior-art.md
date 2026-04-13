# Prior art

Historical and academic work the Agent Colony pattern draws on or distinguishes itself from. Where the pattern is genuinely derivative, this document states so plainly — the honest version of the intellectual heritage.

## Concessions the reviewer extracted and the author accepted

### MAPE-K (Monitor-Analyse-Plan-Execute over Knowledge)

**Origin:** IBM Autonomic Computing (2003). Kephart and Chess, *The Vision of Autonomic Computing*.

**What it contributes:** A control-loop architecture for self-managing systems. Four functions (Monitor, Analyse, Plan, Execute) share a Knowledge base. Originally defined for autonomic computing but has been widely adopted for self-adaptive software.

**Relationship to Agent Colony:** The Equilibrium Agent and the Immune System agents are MAPE-K loops in everything but name. The Equilibrium Agent monitors overlap and vitality (M), analyses against thresholds (A), plans merger proposals (P), and executes or escalates (E), all over the Agent Mirror registry as knowledge (K). The Sentinel + Response Coordinator + Patch Agent triad maps identically.

**What the pattern adds over MAPE-K:** The contribution is not the loops themselves — those are explicitly MAPE-K. The contribution is (a) the **Agent Mirror** as the shared knowledge schema across multiple MAPE-K loops in the same colony, (b) the **Constitutional Memory** layer that turns recurring lessons from one loop into rules that govern all loops, and (c) the **Coexistence Boundary** as a first-class interface rather than an external actor. These three additions are what the reviewer summarised as *"synthesis + OASF extension fields + Constitutional Memory"*.

**Honest framing:** Any specification of the Agent Colony that presents the Equilibrium Agent or Immune System as novel is overstating the claim. They are MAPE-K. The pattern's novelty is how they compose, not that they exist.

**Status:** Conceded in the thesis §2.8. To be fleshed out with a fuller section in v2.0 once a reference implementation exists.

### FIPA (Foundation for Intelligent Physical Agents)

**Origin:** 1996 standards body, now an IEEE committee (FIPA is dormant as an active standard-setting body but the specifications remain).

**What it contributes:**
- **Agent Management System (AMS)** — manages agent lifecycle with formal states: Initiated, Active, Suspended, Waiting, Transit, Unknown.
- **Directory Facilitator (DF)** — yellow-pages service for agent capability registry and discovery.
- **Agent Communication Language (ACL)** — speech-act-based messages (inform, request, query, propose).

**Relationship to Agent Colony:** FIPA AMS is the closest historical precedent for the Colony's Lifecycle Agent. FIPA DF is the closest historical precedent for the Registry Agent. These are not coincidences — they are the same architectural solutions to the same problems, restated for the LLM era.

**What has changed since FIPA:** FIPA pre-dates LLM-based agents by two decades. It has no concept of:
- Self-evolution (agents that modify their own behaviour within bounds)
- Behaviour versioning (SemVer for agent behaviour, not just API)
- Epistemic discipline (evidence grades, mandatory dissent, bias detection)
- The Coexistence Boundary as a mutual border rather than a permission system
- Security posture as a first-class field of agent identity

**Honest framing:** Any specification that positions the Agent Colony as a novel approach to agent lifecycle management without acknowledging FIPA is misrepresenting its history. The Lifecycle Agent is a descendant of the FIPA AMS, not a fresh invention.

**Status:** Conceded as prior art in the thesis §3.3.1. Could be expanded in v1.3 with a footnote on where FIPA's influence ends and the Agent Colony's additions begin.

### KQML (Knowledge Query and Manipulation Language)

**Origin:** DARPA Knowledge Sharing Effort, early 1990s. Finin, Fritzson, McKay, McEntire.

**What it contributes:** An earlier speech-act-based agent communication language, a direct ancestor of FIPA ACL. Defined performatives (ask, tell, achieve, subscribe) and a wrapping structure for messages.

**Relationship to Agent Colony:** Historical context. The Agent Mirror's `contracts` and `protocols` fields do the same job KQML did — defining a structured communication surface — but at the level of modern API schemas rather than speech acts.

**Status:** Mentioned for completeness. Not directly cited in the thesis.

### MOISE+ / OperA / Jason — organisational multi-agent systems

**Origin:**
- **MOISE+** — Hübner, Sichman, Boissier (2002). An organisational model for multi-agent systems with structural, functional, and deontic dimensions.
- **OperA** — Dignum (2003). An organisational model separating organisation, social, and interaction concerns.
- **Jason** — Bordini, Hübner, Wooldridge (2007). A Java-based platform for BDI (Belief-Desire-Intention) agents.

**What they contribute:** Formal models for the *organisational* layer of multi-agent systems — roles, norms, obligations, group structures, deontic constraints. Directly prefigure the Colony's governance and epistemic discipline concerns.

**Relationship to Agent Colony:** These literatures are the single biggest gap in the thesis' literature review. The Agent Colony's Gaps 3 (Collective Memory), 4 (Equilibrium and Population Governance), and arguably 5 (Epistemic Framework) have direct precursors in organisational MAS research.

**Honest framing:** The reviewer was right that *"engagement with organisational MAS (MOISE+, Jason, OperA) is a one-liner where it needs a section"*. The pattern does not currently engage with this literature in the depth it deserves. This is a known weakness.

**Status:** Explicit gap in the thesis. To be addressed in v1.3 or v2.0 with a dedicated subsection. The engagement should be honest — in many cases the Colony's additions over MOISE+ are the LLM-specific concerns (self-evolution, behaviour drift, security posture) rather than structural novelty.

### Constitutional AI

**Origin:** Anthropic, Bai et al., 2022. *Constitutional AI: Harmlessness from AI Feedback*.

**What it contributes:** A method for training AI systems using a set of written principles ("a constitution") that the model uses to evaluate and revise its own outputs. The constitution is human-authored but applied by the model.

**Relationship to Agent Colony:** The Colony's **Constitutional Memory** shares a name and a family resemblance, but the mechanism is different. Anthropic's Constitutional AI has a fixed constitution authored by humans and applied at inference time. The Colony's Constitutional Memory is **grown from the colony's own experience** — lessons recur in Event Memory, extract into Lesson Memory, graduate into Constitutional rules only after accumulating evidence. The constitution is the *output* of the colony's learning, not the *input* to it.

**What the pattern adds:** The Promotion step — the explicit mechanism by which a lesson graduates from provisional to constitutional based on evidence grade and recurrence count. Anthropic's version does not have this because the constitution is given, not earned.

**Honest framing:** The reviewer noted this as *"a differentiator from Anthropic-style constitutional AI"*. The differentiator is the direction of authorship: Anthropic's runs top-down, the Colony's runs bottom-up. Both are legitimate uses of the word "constitutional", but they solve different problems.

**Status:** Noted in the thesis §5.3. Could be expanded with a direct comparison paragraph.

### Stigmergy / swarm intelligence

**Origin:** Grassé (1959) for the biological concept in termite colonies. Widely adopted in swarm robotics and ant colony optimisation.

**What it contributes:** A model of coordination through environmental traces — agents modify the environment, other agents respond to those modifications, coordination emerges without direct communication.

**Relationship to Agent Colony:** The name "Agent Colony" *invites* the stigmergy comparison. The thesis dismisses it in a single sentence — which the reviewer flagged as too thin.

**Honest framing:** Stigmergy is a real family of coordination mechanisms that overlap partially with what the Colony's shared memory structures do. The difference is that stigmergy is typically decentralised and implicit — ants dropping pheromones, not agents writing to Chronicler. The Colony's memory is explicit, inspected, and used as input to reasoning rather than as a coordination substrate. But the pattern would be stronger if it acknowledged where stigmergy's ideas could apply (e.g., lightweight indirect coordination between peer agents in the mesh) rather than dismissing the comparison.

**Status:** To be addressed in v1.3 with a proper footnote stating when stigmergy applies and when the Colony's explicit memory applies.

### Holonics

**Origin:** Arthur Koestler, *The Ghost in the Machine* (1967). Adopted into manufacturing and multi-agent systems research as holonic manufacturing.

**What it contributes:** A model where each entity is simultaneously a whole and a part of a larger whole — a "holon". Useful for modelling hierarchies where components retain autonomy while contributing to collective behaviour.

**Relationship to Agent Colony:** The four-layer architecture has a holonic flavour — each layer is complete in itself (it has its own agents, its own responsibilities) while being part of the larger colony. A Registry Agent in L1 is a holon: a complete MAPE-K loop internally, and a participant in the wider governance layer.

**Status:** Interesting background, not currently cited in the thesis. Could be a footnote in v1.3 if the holonic framing clarifies the four-layer model for academic readers.

### Agentic Hives (arXiv 2603.00130, March 2026)

**Origin:** The closest academic work to the Equilibrium System. Formally models self-organising multi-agent systems with variable population through birth, duplication, specialisation, and death. Proves equilibrium existence via Brouwer's fixed-point theorem.

**What it contributes:** A mathematical treatment of what the Colony calls equilibrium — existence proofs, stability conditions, conditions for endogenous demographic cycles.

**Relationship to Agent Colony:** The Colony's Equilibrium System is not the first work to consider multi-agent populations as dynamic. The Agentic Hives paper proves existence of equilibrium states formally. The Colony's contribution is the *engineering* of equilibrium — the Equilibrium Agent, the three indices, the anti-monopoly threshold, the phased handover from human-governed to self-governed. The theoretical existence result is compatible with the Colony's engineering approach; the engineering approach is not required by the theoretical result.

**Honest framing:** The earlier claim that "equilibrium management is absent from the literature" was softened in v1.1.1 after the reviewer pointed out Agentic Hives. The corrected claim is that *engineering frameworks and standards* for equilibrium management are absent — the theoretical work now exists.

**Status:** Cited in the thesis §3.3.6 and §4.7 (What Doesn't Exist Yet).
