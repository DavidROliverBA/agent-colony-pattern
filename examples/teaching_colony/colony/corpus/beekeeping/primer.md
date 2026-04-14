# Beekeeping — a plain-English primer

This primer exists so that the Teaching Colony has something concrete to
teach. Beekeeping is the running example Teacher uses to explain the
Agent Colony pattern to a newcomer. The metaphor is the point.

## What a beehive actually is

A modern beehive is a stack of wooden boxes. The bottom box — the hive
body or brood chamber — is where the queen lays eggs and where the
youngest bees develop. Above it sit one or more shallower boxes called
supers, where the worker bees store honey. Inside each box hangs a set
of removable frames. Each frame holds a sheet of wax comb, and each cell
in the comb is either a nursery for a growing bee, a pantry for pollen,
or a jar for honey.

The hive is not a single organism, and it is also not a crowd. It is a
colony: thousands of individual bees whose collective behaviour produces
something none of them could produce alone. Take any one bee out of the
hive and she dies within days. Leave the colony intact and it can
outlive a dozen generations of its own members.

## The three types of bee

A healthy colony has one queen. She is the only reproductive female in
the hive, and her single job is to lay eggs — up to fifteen hundred a
day in peak season. Workers feed her, clean her, and decide when she
should be replaced. She does not rule; she is a resource the colony
protects and, when necessary, retires.

Workers are sterile females and make up almost the entire colony. Their
role changes with age: a newly emerged worker cleans cells, then
progresses to nursing larvae, building comb, guarding the entrance, and
finally foraging for nectar and pollen in the final weeks of her life.
No supervisor assigns these roles; a worker takes on whatever the
colony currently needs, guided by hormones and the chemical signals
drifting through the hive.

Drones are the males. They exist for one purpose — to mate with queens
from other colonies — and they do nothing else useful. When autumn
comes and resources tighten, the workers evict every drone. It is the
colony's cruellest routine maintenance operation, and nobody decides to
do it. The colony simply reaches a state in which drones are no longer
affordable.

## How the colony makes decisions

Beehives make real decisions without anyone being in charge. When a
colony grows too large, a portion of the workers and the old queen
leave together in a swarm. The swarm clusters on a nearby branch while
scout bees fly out, inspect candidate nest sites, and report back using
the waggle dance — a geometric code that communicates both the
direction and the quality of each site. Scouts visit each other's
preferred sites, dance more for better ones, and within hours the
swarm converges on a single choice. No bee voted. No bee decided. The
collective converged.

Queen replacement works the same way. When a queen's pheromone output
drops below a threshold, workers quietly build emergency queen cells
and raise a successor. The old queen is superseded without a fight,
often without even being removed — the colony simply stops treating
her as queen.

## How a beekeeper keeps a hive

A beekeeper's job is not to run the colony. It is to notice when the
colony is struggling and act only when necessary. A typical inspection
takes twenty minutes: open the hive, lift each frame, look for eggs
and larvae in a healthy pattern, check honey reserves, look for
disease, look for the queen if you can find her (you usually cannot),
close the hive. You intervene to add supers when the bees run out of
storage space, to treat for parasites, and to replace a failing queen.
You do not intervene to tell them how to forage, which flowers to
visit, or how to organise their brood. They know.

## Why this maps to a software colony

A software agent colony is structured like a beehive on purpose. Each
agent is a single bee — narrow, specialised, replaceable. The colony
as a whole is what matters. Decisions emerge from local signals and
pre-registered review regimes rather than from a central controller.
The human role is the beekeeper's: notice, inspect, intervene only
when the colony cannot correct itself. The Comprehension Contract is
the equivalent of the beekeeper knowing which frames she must never
skip during an inspection and which interventions require the whole
apiary club to sign off on. The agents do the work; the governance
decides which work requires a second pair of eyes.

Beekeeping and software colonies share the same uncomfortable truth:
the system is stronger than any single member, and anyone who tries to
run it top-down tends to kill it.
