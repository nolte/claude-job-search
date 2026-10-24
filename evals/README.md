# Evals

Model-in-the-loop evals of this plugin (`claude plugin eval`). They cost money and use your credentials.

Read [docs/en/evals.md](../docs/en/evals.md) (German: [docs/de/evals.md](../docs/de/evals.md)) first: prerequisites, how to
run, what the cases mean, what the first exploratory run found.

```bash
export ANTHROPIC_API_KEY=...
evals/run.sh trigger      # one natural request per skill and the reviewer
evals/run.sh behavior     # behavioural cases; the preconditions behavior-bash-works and behavior-python-works run first;
                          # cases tagged bash-denied run in a second invocation without Bash
task eval -- behavior     # the same through the Taskfile
```

The data is fictional (`tests/fixtures/szenarien/`). Never put a real application here. Results go to `evals/results/`
(git-ignored).
