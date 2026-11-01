# Sim 2: Tracking a trajectory under feedback, with velocity inputs

**In class Wednesday 11/18. Due Friday 11/20 at noon**, submitted once on the
course site (no correction round).

In class your group works through `sim2.ipynb` (open it with `uv run lab sim2`,
which puts your copy in `work/`; run `uv run update` first). It drives the
capstone cell's UR5 in velocity mode: MR 11.3, the controller your capstone
will use. What you submit finishes it. Submit **one PDF per person**. Work
together as much as you like, but write your own explanations. The PDF has the
parts below, with your code and its output. In JupyterLab, **File → Save and
Export Notebook As → HTML**, then print the HTML to PDF.

## What to submit

1. **One joint, predicted and measured.** A table for the five runs of A2
   (feedforward only; P only with $K_p = 2$ and $5$; feedforward + P with
   $K_p = 2$ and $5$): your prediction of the final error and the 2% settling
   time from MR 11.3.1, and what the simulator did. Show where each prediction
   comes from. Where a prediction and a measurement differ by more than a step
   (0.05 s), say why.

2. **The sampled controller.** Derive $\theta_e[k+1] = (1 - K_p\Delta t)\,\theta_e[k]$
   for feedforward + P when the commanded rate is held for a whole step, and say
   what it predicts for $K_p\Delta t$ below 1, equal to 1, between 1 and 2, and
   above 2. Use it to predict the 2% settling time for $K_p = 5$, and compare
   with the continuous-time $4/K_p$. Then give your group's card result and two
   others from screens up. For each, say whether the robot did what the factor
   predicts, and where it did not, explain the gap. (The largest commanded rate
   is your clue.)

3. **Your task-space controller.** Your `task_rates` (MR eq. 11.16 and 6.3), and
   the error plots of B1. Explain each run: why feedforward alone never reaches
   the line, how long feedforward + P takes, and the size of the P-only lag. For
   the lag, compute the cup's peak speed along the reference and compare it with
   MR 11.3.1's lag behind a moving reference.

4. **Your group's B2 experiment**, in full: what you predicted, what happened,
   and why. Add one sentence each on the other two, from the exit check-in.

5. **For your capstone.** In a short paragraph: the gain you will use and why,
   whether you will limit joint rates and to what, and what you will feed back
   as $X$. Say what each choice costs.

**MME 565 also:** implement MR's other task-space law, eq. 11.18, which
controls $(\omega_b, \dot p)$ separately. To turn its output into joint rates,
note that $\mathcal{V}_b = (\omega_b, R^{\mathsf T}\dot p)$. Drive the cup from
the offset start of Part B to $X_A$ as a setpoint ($\mathcal{V}_d = 0$,
$K_i = 0$, $K_p = 2$) with each law. Plot both paths of the cup's origin, and
give for each the largest distance of its path from the straight line between
start and goal. Explain the difference, with reference to MR Figure 11.10.
