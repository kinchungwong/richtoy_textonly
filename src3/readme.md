# src3 (2024-07-14)

Prototype of game map initialization.

This prototype initializes a 2D grid of cells, each of which can be "painted"
to be anything, such as object types.

The grid-painting approach is just one of the many approaches that belong to
the family of "spatially based" or "physics based" game map initialization algorithms.

The first things to be painted are streets. This prototype allows two kinds of streets:
horizontal (latitudinal) and vertical (longitudinal).

(Horizontal and vertical refers to the directions of their appearance on the computer screen.)

Street intersections (crossroads in the code base) can then be picked out merely
by checking the street direction flags.

By using this grid-painting approach, the earlier, graph-based algorithm appears
to have been greatly simplified. That said, the approach imposes some constraints
on the game map design.
