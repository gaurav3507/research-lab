# research-lab

A long-lived home for new research ideas. Each idea lives in its own folder and is
complete in itself — you can work on one without touching any other.

## Structure

```
research-lab/
  ideas/
    <idea-name>/   # one folder per idea, self-contained
    <idea-name>/
```

Every idea is a single folder under `ideas/<name>/`. Put whatever that idea needs
inside its own folder — code, configs, notes, requirements. An idea imports only
from within its own folder: no shared code and no imports across ideas, so any idea
can be moved, copied, or deleted on its own without breaking the others.

## Where things run

- **This machine (Windows) is where ideas run.** New ideas are written and executed
  here. This is the default place for everything.
- **The Mac / A100 are optional next steps.** If an idea gets far enough to write up
  for a paper, or needs a GPU (A100) for a heavier run, carry that idea's folder over
  by pulling this repo there. Nothing has to move until an idea earns it.

## Working across machines

The repo is on GitHub, so this machine, the Mac, and the A100 all stay in sync
through it:

- **Before working:** `git pull`
- **After changes:** `git add -A && git commit -m "..." && git push`

## Start a new idea

Make a folder and start building:

```powershell
mkdir ideas\<newname>
```

That's it — no required files or layout. Give the folder whatever structure the idea
needs.
