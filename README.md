# ME 465 / MME 565 simulation labs

The code and the simulator scene for the course's lab days. Your Python program
drives a UR5 arm in [CoppeliaSim](https://www.coppeliarobotics.com/) through its
remote API: the simulator runs the physics, and your code decides what the
robot does, one time step at a time.

## Setting up (do this before the first lab)

You need two things: CoppeliaSim, and this folder with its Python environment.
Budget 30 minutes. When `uv run check` passes, paste its output into the setup
checkpoint on the course site.

### 1. Install CoppeliaSim (the Edu edition, version 4.10)

Download from <https://www.coppeliarobotics.com/> (Download, then the **Edu**
edition).

- **Windows:** run the installer.
- **macOS, Apple Silicon (M1–M4) on macOS 15 or newer:** the `macOS15_arm64` zip.
  **Intel Mac, or macOS 13–14:** the `macOS13_x86_64` zip. Unzip it and drag
  `coppeliaSim.app` into Applications. The first time, right-click it and choose
  **Open**, because macOS blocks apps from outside the App Store on a plain double-click.
- **Linux:** the Ubuntu 22.04 or 24.04 archive. Extract it and run `./coppeliaSim.sh`.
  If your system's locale uses a comma for decimals, start it with
  `LC_NUMERIC=en_US.UTF-8 ./coppeliaSim.sh`.

Open it once to make sure it starts.

**Register it.** The Edu edition is free, but it asks you to register. When the
registration window appears, fill it in with your university email: the
license key arrives by email, and the window then tells you where to paste it.
Until the key arrives, the window comes back now and then; clicking **Cancel**
closes it and CoppeliaSim keeps working. Do register, so it stops.

**Two things you can ignore:**
- CoppeliaSim's console may print a Python error ending in
  `No module named 'zmq'`. That is its own built-in Python scripting, which this
  course does not use.
- On Windows, if the firewall asks whether CoppeliaSim may use the network, allow it
  on private networks. Your code talks to it over `localhost`.

### 2. Open a terminal, and go somewhere sensible

Everything below is typed into a terminal: on macOS the **Terminal** app
(Applications → Utilities, or search for it), on Windows **PowerShell** (search
the Start menu for it; plain Command Prompt works too).

A terminal is always "in" some folder, and commands act on that folder. On
Windows it often opens in a system folder you have no business writing to, so
the first thing to type, every time, is a move to a folder of your own. Put
the course in your Documents:

- **macOS / Linux:**

```
cd ~/Documents
```

- **Windows:**

```
cd ~\Documents
```

(`cd` is "change directory"; `~` is your home folder. `pwd` prints where you are.)

### 3. Install git and uv

[git](https://git-scm.com/) is how you get this folder and keep it up to date
as the course changes. [uv](https://docs.astral.sh/uv/) installs the right
Python and every package this course needs, identically on every machine. You
do not need Anaconda or an existing Python.

- **macOS:** git comes with Apple's command-line tools. Type `git --version`;
  if a window offers to install the tools, accept. Then install uv:

```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

- **Windows:** install [Git for Windows](https://git-scm.com/download/win) with
  its default options, then in PowerShell:

```
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

- **Linux:** `sudo apt install git`, then the macOS uv command.

Then close and reopen the terminal so it can find both, and `cd` back to
your Documents (step 2).

### 4. Get this folder: clone it

From your Documents folder:

```
git clone https://github.com/ricopicone/me465-labs.git
cd me465-labs
```

That makes a folder `me465-labs` and moves you into it. **Clone; do not
"Download ZIP" and do not "Fork."** The course updates this folder during the
term, and `uv run update` (below) fetches those updates only for a clone of
this repository. A ZIP has no connection to it, and a fork is a separate copy
that falls behind. If you already did one of those, delete it and clone;
anything you wrote in a `work/` folder can be moved into the new clone.

### 5. Run the check

Open CoppeliaSim and leave it running. In the terminal, inside the folder
(`cd me465-labs` if you are not already there) run:

```
uv run check
```

The first run takes a minute while uv installs Python and the packages. You
should end with:

```
me465 check PASSED — CoppeliaSim 4.10.0, ...
```

If a step fails, the line under it says what to do. If you are stuck, bring
the output to office hours or post it. Do not wait until the lab.

## On a lab day

Open CoppeliaSim. Open a terminal and go into the folder (`cd ~/Documents/me465-labs`
on macOS, `cd ~\Documents\me465-labs` on Windows). Get the latest version of the
labs, then open the day's notebook:

```
uv run update
uv run lab sim1
```

`update` pulls the course's changes and syncs the packages. `lab` copies the lab's
notebook from `labs/` to `work/`, which is yours, and opens JupyterLab on it;
next time it opens your copy. When the course has changed a lab's notebook
since you copied it, both commands say so; `uv run lab sim1 --fresh` then sets
your copy aside as `work/sim1-previous.ipynb` and starts from the new version.
Never edit anything under `labs/`: the course updates those files, and
`update` refuses to overwrite edited ones. Each lab's folder also has a
`README.md` saying what to submit.

Before you run anything, **write down what you expect it to do**. The simulator
is the referee, and a run without a prediction teaches you nothing about your
model.

## What is in here

- The robotics and the simulator bridge come from the
  [`screws`](https://pypi.org/project/screws/) package: Modern Robotics'
  functions under snake_case names (MR's own names work too), plus
  `screws.coppelia` for driving CoppeliaSim.
- `src/me465/__init__.py`: `open_lab`, `settle` and `close`, the three
  helpers a lab day needs, and `joint_sliders`, six sliders that drive the arm.
- `src/me465/scenes/ur5.ttt`: the course scene, built by
  `src/me465/build_scene.py` from CoppeliaSim's own UR5 model.
- `labs/`: one folder per lab.
