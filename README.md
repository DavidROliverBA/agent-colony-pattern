# Airbus A350-1000 — 3D Assembly Schematic

An interactive, fully procedural 3D schematic of the Airbus A350-1000 in
British Airways' Chatham Dockyard livery, built with
[Three.js](https://threejs.org/). The aircraft assembles itself inside-out in
17 stages: first the structure (keel beam, floor grid, fuselage frames, wing
spars) and the contents (flight deck, 369-seat cabin), then the fuselage skin
wraps around them as upper/lower clamshells, followed by the lofted wings with
blended winglets, tail, Trent XWB-97 engines, the type's signature 6-wheel
main bogies and finally the livery details. Then you can fly through it with a
free camera.

Everything is generated in code at true scale (metres): no model files,
no build step, a single `index.html`.

## Running it

Three.js is loaded from a CDN, so any static server works:

```bash
cd a350-1000-schematic
python3 -m http.server 8350
# open http://localhost:8350
```

(Opening `index.html` directly from disk also works in most browsers.)

## Controls

| Input | Action |
| --- | --- |
| **Click** | Enter fly mode (pointer lock) |
| **W / A / S / D** | Move forward / left / back / right |
| **Space / C** | Climb / descend |
| **Shift** | Boost (4×) |
| **Scroll** | Adjust fly speed (or zoom while orbiting) |
| **X** | X-ray mode — see the structure through the skin |
| **Esc** | Release the mouse, return to orbit view |
| **Drag** | Manual orbit while not flying |

Buttons (top right): **Skip assembly**, **Replay**, **X-ray**.

Fly through an open door, down the cabin aisle, into the cockpit, or hold a
station inside an engine inlet while the fan spins. The assembly can also be
watched from inside — click to fly at any time.

## How it's built

- **Fuselage** — five lathe-generated barrel sections, each split at the
  livery seam into a white upper shell and a navy lower shell (so the skin
  visibly closes around the interior during assembly), sharing one
  radius-vs-station function, with nose droop and tail upsweep applied as a
  vertex-level shear. Frames, crown stringer, keel beam and floor grid carry
  the schematic look.
- **Wings, fin, tailplane** — a small lofting routine sweeps a NACA-style
  airfoil through stations (position, chord, thickness, bank). The last wing
  stations bank progressively to ~75° to form the blended winglet.
- **Engines** — lathe-profiled fan cowl with inlet lip, 22-blade fan
  (animated), spinner, core and exhaust cone.
- **Interior** — instanced economy seats (3-3-3) and business pods, overhead
  bins, emissive ceiling light strips, galleys, lavatories, and a flight deck
  with displays, pedestal and pilot seats.
- **Details** — instanced cabin windows, four door pairs per side, canvas-drawn
  BRITISH AIRWAYS titles with the red speedmarque, G-XWBA registration, Union
  Flag ribbon tailfin, pulsing beacons, wingtip navigation lights and a
  double-flash tail strobe.

Key dimensions match the real aircraft: length 73.79 m, wingspan 64.75 m,
fuselage diameter 5.96 m, tail height ≈ 17.1 m.

### Scripting hook

`window.__a350` exposes `lookFrom(px,py,pz, tx,ty,tz)`, `freeCam()`, `skip()`,
`replay()` and `xray()` for automated screenshots or camera work.
