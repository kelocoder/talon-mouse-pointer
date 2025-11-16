# Overview

mouse-pointer is a Talon Voice module which supports relative mouse pointer
movements.

Currently these include movements in radial directions relative to the
current mouse pointer position.

No screen artifacts are produced to guide movement.

# Usage

Example voice commands:
- `roam up`
  - Note: Default movement distance is 100 pixels.
- `roam 8 o'clock 25`
- `roam northeast 70 pixels`
  - Note: Saying "pixels" is optional.
- `nudge left`
- Note: Nudge distance depends on screen size.
  - Note: `step`, `hop`, `skip`, and `jump`, are commands like
    `nudge`. They move varying distances and are dependent on screen size.

For more example voice commands, see [mouse_pointer.talon](mouse_pointer.talon)

# Objective

This module is intended to enable use of just a single short voice command
to move the mouse pointer to a small or large area of interest (with
limitations).

It is limited in that in order for it to work using a single command, the
direction and distance from the current mouse position to the target area
must be roughly and visually estimatable by the user. Scenarios where it
would work well include: nudging the mouse pointer over a few pixels or
jumping the pointer on your browser on to a sizeable on the page.

It is not intended for movement to precise locations on a full screen
(unless they are only handful of pixels away from the current mouse pointer
position).  Although it is possible to use it to hone in on a precise
position on a full screen, it probably would end up being very inefficient
to do so.

# Installation

cd <your Talon user directory>
git clone https://github.com/talon-mouse-pointer mouse_pointer

