# Preserved W1 failures

- Initial preparation: the no-host-driver audit rejected `four_stage.cpp` because
  a second initialization line assigned `memory_idle=1` and
  `compact_fixed_idle=1`. No simulator was run. The generator originally removed
  only zero assignments. It now removes both initialization values and repeats
  the audit across all copied C++ files. Exact exception:
  `AssertionError: (.../onchip/four_stage.cpp, 'memory_idle')`.

# Reading/preflight gaps

The root `plan.md` requested by AGENTS.md is absent (`cat: plan.md: No such file
or directory`). The current user W1 brief and the retained 13 October proposal
were read. The W1 brief explicitly authorizes this bounded execution; broader
automations remain paused. No agents or cloud resources are used.
