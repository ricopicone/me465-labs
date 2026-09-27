# Sim 1: Forward kinematics, with the simulator as referee

**In class Wednesday 9/30. Due Friday 10/2 at noon**, submitted once on the
course site (no correction round).

In class your group works through `sim1.ipynb`. That gets you most of the way;
what you submit finishes it. Submit **one PDF per person**. Work together as
much as you like, but write your own explanations. The PDF has the parts
below, with your code and its output. In JupyterLab, **File → Save and Export
Notebook As → HTML**, then print the HTML to PDF.

## What to submit

1. **Your own forward kinematics.** Write `my_fk_space(M, S, theta)`
   yourself, as the product of exponentials in the notes: use `sc.exp6` and
   `sc.vec_to_se3` (MR's `MatrixExp6` and `VecTose3`), but not `sc.fk_space`.
   Show that it agrees with `sc.fk_space` for three configurations of your
   choosing; `screws.testing.check(my_fk_space, sc.fk_space, cases)`, with each
   case a tuple `(M, S, theta)`, does the
   comparison for you.

2. **The scene's model of the UR5.** Your `S_scene` and `M_scene`, read from
   the simulator. For each screw axis, say in a sentence why it does or does
   not equal the corresponding column of MR's $\mathcal{S}$.

3. **The two home configurations.** The joint offsets that put the simulated
   arm in MR's home pose, and how you found them. Then the position error that
   remains: its size, its direction, and where it comes from.

4. **A table for three configurations:** your group's card and two others of
   your choosing, not the zero pose. For each, give:

   | | your prediction (in words) | FK, scene model | FK, MR's model through the offset | simulator | errors (mm, deg) |
   |---|---|---|---|---|---|

5. **The last half-millimetre.** With the scene's own model, forward kinematics
   and the simulator still disagree by a fraction of a millimetre. Is the
   model wrong, the angles, or something else? Give one test that tells those
   possibilities apart, and its result.

**MME 565 also:** read the body-frame screw axes $\mathcal{B}_i$ directly off
the simulator (express each joint's frame in the tool frame at home), and show
numerically that $\mathcal{B}_i = [\mathrm{Ad}_{M^{-1}}]\,\mathcal{S}_i$. Then
explain why one of the six offsets changes nothing about where the tool *is*,
only how its frame is turned.
