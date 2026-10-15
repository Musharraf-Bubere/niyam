# Niyam interview notes: process concepts

How to use this file: read the plain meaning, look at the Niyam example, then practise saying the interview answer out loud in your own words. New sections are added as the project grows.

---

## 1. Small, labelled commits

**Plain meaning:** Each commit does one thing, and its label says what kind of change it is. The common labels are `feat` (new feature), `fix` (bug fix), `docs`, `test`, `refactor` and `chore` (upkeep). This style is called Conventional Commits.

**Niyam example:** `feat: add structured logging configuration` and `test: cover logging level filtering and JSON output` are two separate commits. A message like `update stuff` tells nobody anything.

**Why it matters:** Small commits are easy to review, easy to undo, and make the history readable. If something breaks, you can find the commit that caused it.

**Likely questions**

- *Why commit often?* Because each commit is a safe checkpoint. If a change goes wrong I can go back one step instead of losing a day of work.
- *Why labels in commit messages?* They make history scannable, and tools can generate release notes from them.

---

## 2. Reproducible environments

**Plain meaning:** Everyone who runs the project gets exactly the same library versions. The file `uv.lock` records the exact version of every library, like a recipe that names exact brands.

**Niyam example:** The same lockfile is used on my laptop, in GitHub Actions and later in Docker, so the code behaves the same in all three.

**Why it matters:** Without a lockfile, a library can update overnight and break the app on one machine only. That is the "it works on my machine" problem.

**Likely questions**

- *What is a lockfile?* A file that pins the exact versions of all dependencies, including indirect ones.
- *Why separate dev dependencies?* Tools like ruff, mypy and pytest are needed to develop but not to run the app. Keeping them out of production makes the image smaller and reduces the attack surface.

---

## 3. Quality gates

**Plain meaning:** Every change must pass a fixed series of checks before it is accepted. Think of airport security: several stages, each catching a different kind of problem.

**Niyam example:** Three gates, in order: `ruff` (style and common mistakes), `mypy` (types), `pytest` (behaviour). Later, GitHub Actions runs the same three on every push, plus evaluations.

**Why it matters:** Humans forget. Automatic gates do not. The same checks run locally and in CI, so there are no surprises.

**Likely questions**

- *What does your CI check?* Formatting and lint, strict type checking, unit tests, and later the retrieval and answer-quality evaluations.
- *What is a quality gate?* A check that must pass before code can move forward. If it fails, the change is blocked.

---

## 4. Shift-left

**Plain meaning:** Find problems as early as possible. "Left" means earlier in the timeline of write, test, deploy, run.

**Niyam example:** mypy flagged a problem with `_env_file` in a test within seconds, before running anything. A wrong type found at the desk costs a minute. The same bug found by a user in production costs far more.

**Why it matters:** The cost of fixing a bug rises the later it is found.

**Likely question**

- *Why strict type checking?* It turns a class of runtime errors into errors I see while writing the code.

---

## 5. Test isolation

**Plain meaning:** A test must not depend on other tests, on the order they run in, or on the machine. Each test sets up its own world and cleans up after itself.

**Niyam example:** The settings tests run inside an empty temporary folder and clear all `NIYAM_` environment variables first. That way, my personal `.env` file cannot change a result. The logging tests reset structlog's global configuration after every test.

**Why it matters:** Tests that sometimes pass and sometimes fail (flaky tests) make people stop trusting the test suite.

**Likely questions**

- *What causes flaky tests?* Shared state, such as global configuration, files, environment variables, time or the network, and tests that depend on running order.
- *What is a fixture?* Reusable setup and cleanup code that pytest hands to a test. Code before `yield` is setup, and code after it is cleanup.

---

## 6. Twelve-factor configuration

**Plain meaning:** Settings live outside the code, in environment variables. The same build runs in every environment, and only the settings change.

**Niyam example:** `NIYAM_ENVIRONMENT=production` and `NIYAM_LOG_LEVEL=WARNING` change behaviour without touching a file. The `.env` file is ignored by git, and a `.env.example` with fake values documents what is needed.

**Why it matters:** Secrets such as API keys never enter the repository. One container image can be promoted from test to production unchanged.

**Likely questions**

- *Where do you keep API keys?* In environment variables or a secret manager, never in code or git.
- *How do you switch the LLM?* By configuration only, through environment variables read by one settings object and one factory function.

---

## 7. Fail fast

**Plain meaning:** If something is wrong, stop immediately and say clearly what is wrong, instead of limping on and failing somewhere confusing later.

**Niyam example:** Setting `NIYAM_LOG_LEVEL=LOUD` makes the app refuse to start with a message listing the allowed values. Without that, the problem might only show up hours later.

**Why it matters:** A crash at startup is cheap and obvious. A silent wrong behaviour in production is expensive and hard to find.

**Likely question**

- *How do you validate configuration?* With Pydantic Settings. Types and allowed values are declared once, and invalid values are rejected at startup.

---

## 8. Structured logging

**Plain meaning:** Logs are written as data with named fields, not as sentences. Compare `user 42 logged in` with `{"event": "login", "user_id": 42}`. The second can be searched, filtered and counted by a tool.

**Niyam example:** In production, each log line is a JSON object with `event`, `level` and a UTC `timestamp`. Locally the same events print as readable coloured text. Later we attach a request ID to every line of one request.

**Why it matters:** When something breaks, you can ask the logs precise questions, for example "show all errors for request abc123".

**Likely questions**

- *What is structured logging?* Logging events as key-value data, usually JSON, so machines can parse them.
- *Why UTC timestamps?* They stay consistent across servers and time zones.
- *What is a request ID for?* It ties all log lines from one request together, so you can follow it end to end.

---

## 9. Decision records

**Plain meaning:** A written log of important choices: what we chose, what else we considered, why, and what it costs us.

**Niyam example:** `docs/decision-log.md` explains why we use Postgres with pgvector instead of a separate vector database, why the model is chosen by configuration, and why LangSmith replaced Langfuse. Old decisions are marked superseded, never deleted.

**Why it matters:** In six months nobody, including me, remembers why something was chosen. It also shows that decisions were deliberate.

**Likely questions**

- *Tell me about a decision you changed.* I started with Langfuse for tracing, then switched to LangSmith because it integrates natively with LangChain and LangGraph. I recorded the change and kept the old entry marked as superseded.
- *How do you make technical decisions?* I list the options, name the trade-offs, choose one for stated reasons, and write it down so it can be revisited.

---

## 10. Writing the problem before the solution

**Plain meaning:** Before building, write down who the users are, what the problem is, what is out of scope, and how success will be measured.

**Niyam example:** `docs/01-problem-and-solution.md` lists non-goals and success targets. The targets are labelled "initial" and are revised after the baseline evaluation, so they are not presented as results.

**Why it matters:** It stops scope creep, and it gives every later decision something to be checked against.

**Likely question**

- *How did you decide what "good" means for your system?* I set measurable targets first, built an evaluation set, measured a baseline, and then reported real numbers.

---

## 11. Secrets management

**Plain meaning:** Passwords and API keys are kept out of the code and out of git. They live in a place only the running app can read.

**Niyam example:** The real Gemini key sits in a local `.env` file that git ignores. A committed `.env.example` shows which variables exist but holds fake values. In code the key is a `SecretStr`, so printing the settings shows `**********` instead of the key. To read it you must deliberately call `.get_secret_value()`.

**Why it matters:** Keys pushed to a public repository get found by automated scanners, often within minutes. Deleting the file later does not help, because the key stays in git history. A leaked key must be revoked and replaced.

**Likely questions**

- *Where do you keep API keys?* In environment variables loaded from an ignored `.env` locally, and from a secret manager in production. Never in code or git.
- *What if a key is committed by mistake?* Revoke it immediately and create a new one. Then remove it from history if needed. Treat it as compromised either way.
- *How do you stop secrets leaking into logs?* Secrets are wrapped in `SecretStr`, which hides their value when printed or logged.

---

## 12. Verify before you trust

**Plain meaning:** Check that a safety measure works before relying on it, and check facts against the source instead of from memory.

**Niyam example:** Before putting a real key into `.env`, I ran `git check-ignore -v .env` to prove git would ignore it. For model names, I read Google's current model page, because LangChain's own docs example used a model name that was not on Google's list.

**Why it matters:** Safety rules that were never tested are only assumptions. Documentation, tutorials and AI assistants can all be out of date.

**Likely questions**

- *How do you keep up with fast-changing LLM APIs?* I keep model names in configuration, read the provider's official model page, and confirm with a real call.
- *How do you know your safeguards work?* I test them directly, for example by checking that the ignore rule matches before the secret exists.

---

## 13. Configuration over code (model independence)

**Plain meaning:** Anything likely to change, such as which model to use, lives in settings and not in the source code. Changing it means editing one line in `.env`, not editing and redeploying code.

**Niyam example:** `NIYAM_LLM_MODEL` and `NIYAM_EMBEDDING_MODEL` choose the models. No model name appears anywhere in the Python code. When Google retires a model, the fix is one environment variable.

**Why it matters:** Models are retired, renamed and repriced often. Google has already shut down older Gemini models. Hard-coded names turn each of those events into a code change and a release.

**Likely questions**

- *How would you switch from Gemini to another provider?* Change the provider and model settings and install that provider's LangChain package. Then run the evaluation suite to confirm quality did not regress.
- *What is the catch?* Embedding models are special. A new embedding model produces vectors that are incompatible with the old ones, so the index must be rebuilt, and the app checks the stored model name against the configured one.
- *Why not set a default model in code?* A default is a hidden model name. Leaving it empty forces an explicit choice, and the model factory fails with a clear message if it is missing.

---

## 14. Security regression tests

**Plain meaning:** A test that locks in a safety property, so a later change cannot quietly break it.

**Niyam example:** One test sets a fake API key and checks the secret never appears in `repr` or `str` of the settings object. If someone changes the key's type to a plain string, that test fails immediately.

**Why it matters:** Security properties break silently. Nothing crashes when a secret starts appearing in logs, so only a test will notice.

**Likely questions**
- *How do you make sure secrets don't leak into logs?* The key is a `SecretStr`, and a test checks that the value does not appear when settings are printed.
- *What is a regression test?* A test added to make sure a past or possible mistake does not come back.

---

## 15. Commit hygiene: inspect before you commit

**Plain meaning:** Look at exactly what is staged before committing, and make sure the message describes it.

**Niyam example:** I ran `git status` and `git diff --staged` before committing. Once a commit message was re-used by accident and described the wrong change. Since it was already pushed, I left it alone and corrected the habit instead of rewriting shared history.

**Why it matters:** A clear history is only useful if each message is true. Staging only what you intend also keeps secrets, such as a `.env` file, out of commits.

**Likely questions**
- *How do you avoid committing secrets?* A `.gitignore` rule, an explicit `git add` of named files, and checking `git status` and `git diff --staged` before each commit.
- *When would you rewrite git history?* Only on my own unpushed or private branches. Rewriting shared history with a force-push can break other people's work.

---

## 18. Architecture documentation: views and diagrams as code

**Plain meaning:** Describe the system from several angles instead of one big picture: the whole system and its neighbours, the deployable pieces, the code structure, and the flow of one important request. The diagrams are written as text (Mermaid) inside the repository, so they are versioned and reviewed like code.

**Niyam example:** `docs/02-architecture.md` has a system diagram, a question-answering sequence, the orchestration graph, an ingestion flow and a data model, plus a status table showing what is built and what is only planned.

**Why it matters:** A diagram stored as an image gets out of date. Text diagrams live next to the code and are updated in the same change.

**Likely questions**
- *How do you document architecture?* A short document with context, container, flow and data views, kept in the repository and updated each phase.
- *How do you keep it from going stale?* It has a status table, and changes to the design update the document in the same pull request.

---

## 19. Layering and dependency direction

**Plain meaning:** Code is arranged in layers, and a layer may only use the layers below it. The API can use the orchestrator, but the database layer can never reach back up into the API.

**Niyam example:** `api -> agents -> retrieval, llm, guardrails -> db -> core`. Only `llm`, `retrieval` and `agents` import LangChain, and only `db` talks to Postgres.

**Why it matters:** Without a direction, every module ends up depending on every other one, and a small change breaks things far away. Layers make the code easier to test, to replace and to explain.

**Likely questions**
- *How do you keep boundaries from eroding?* By writing the rules down, then enforcing them automatically with a check in CI.
- *Why not microservices?* One team and one deployable do not need network boundaries. A modular monolith has clear module boundaries without the operational cost, and can be split later.

---

## 20. Designing for failure

**Plain meaning:** For each dependency, decide ahead of time what the system does when it breaks, instead of finding out in production.

**Niyam example:** Section 11 of the architecture lists each failure and its behaviour. When Gemini rate-limits us we retry, then fall back to a second model, then return a clear error. When evidence is weak we refuse, and never guess.

**Why it matters:** Every external service fails sometimes. A system with planned fallbacks degrades gracefully, and one without them simply breaks.

**Likely questions**
- *What happens if the LLM provider is down?* Retries with backoff, then a configured fallback model, then a clear error. Health checks show the state.
- *What is graceful degradation?* Continuing to do the most important part of the job when a secondary part fails, for example skipping the cache when Redis is down.

---

## 21. Model factory (step 1.14)

**Q: How would you swap LLM providers?**
A: A single factory builds the chat model from configuration (provider and model name). The rest of the app depends only on LangChain's `BaseChatModel` interface. Swapping is an environment change and no code change.

**Q: How do you test LLM code?**
A: Unit tests use a fake model, so they're fast, free and need no key. A small separate set of real-API smoke tests proves the integration.

**Q: How do you keep a strictly typed codebase when a library is untyped?**
A: Annotate the value at the boundary (`model: BaseChatModel = init_chat_model(...)`), so type-checking applies everywhere past that point.

**Q: What makes a good commit?**
A: One logical change, a clear message, and it passes the quality gates by itself. Unrelated fixes get their own commit.

**Q: What did your wrong-model experiment show?**
A: The error appears at call time, not build time. So production needs a startup check, which makes config mistakes fail at boot.

---

## Coming next (to be added as we build)

Continuous integration, pre-commit hooks, containerisation, database migrations, background jobs, evaluation-driven development, security and guardrails, observability, and deployment.
