---
name: design-rounds
description: Ask the design questions of a brainstorming session in rounds, each question numbered and with a recommended answer, when the work is a technical design whose facts can be measured or read from the project. Use inside a brainstorming session for a change to existing code, an analyzer rule, a data format, or an interface, and when the user asks to be grilled or interviewed about a design. Not for a new product or feature with no facts to find yet, where one open question per message works better, and not for a task that is clear from the request.
---

# Design Rounds

## Purpose

Settle the decisions of a technical design in few turns. The decisions form a tree: each one opens the decisions that depend on it. Ask every question that is ready in one round, with a recommended answer, so that the user can accept most of them with one word and spend their attention on the rest.

This skill sets the question format only. The brainstorming skill, when it is in use, still sets the opt-out line, the sizing of the work, the written design, and the rule that nothing is built before the user approves the description.

## When to Use

Use this skill when:

- A brainstorming session is about a technical design, and the project, its data, or its tools can answer the factual questions.
- The user asks to be grilled or interviewed about a design.

Do not use it when no facts exist yet to find, as with a new product or a feature nobody has described. Ask one open question per message there, as the brainstorming skill does.

## Procedure

### 1. Ask one open question first

Before any round, ask one open question with no recommendation and no list of answers, such as what the user wants to be true when the work is done. Wait for the answer. The words of the user carry intent that a recommendation cannot.

### 2. Find the facts

Finding facts is your job, never the user's. Do not ask the user for anything that the filesystem, the tools, or a measurement can answer.

- Find a fact in the session when one command, one script, or one read answers it. This is the usual case, and it keeps the context that the fact needs.
- Send a sub-agent only for a broad search of code you do not know. A search that is still running is an unsettled prerequisite: hold only the questions that depend on it and ask the others now.
- Measure before you state a consequence. A claim taken from reading the code alone can be wrong.

### 3. Ask a round

The frontier is every decision whose prerequisites are settled. Ask the whole frontier in one round.

- State the new facts above the questions, with their numbers, so that each recommendation has its basis in view.
- Number the questions across the session, so that `Q7` names one question from start to end.
- A question whose answer depends on another question of the same round belongs to a later round.
- Give a technical decision with a measured basis a recommended answer, and word the question so that "yes" accepts it.
- Ask a question of priority, taste, or risk open, with no recommendation. Say what each answer costs and let the user choose.
- End the round with one open line that asks what the round did not ask.

Format a round as follows:

```markdown
**Facts**

- <a fact found since the last round, with its number or source>

**Round N**

❓ **Q1** - **<title>**: <the decision, and the choices where there are several>

➡️ <the recommended answer, and its reason in one sentence>

---

❓ **Q2** - **<title>**: <a question of priority, asked open>

➡️ No recommendation. <what each answer costs>

---

What did this round not ask?
```

### 4. Wait, then compute the next round

Wait for the answers. Each answer moves the frontier: a settled decision opens the questions that depended on it.

- An answer that is a question is the most useful turn of the session. Answer it with facts, measure if needed, and ask the open questions of the round again afterward.
- An unanswered question stays open. Ask it again in the next message. Do not take silence as a yes.
- A decision the user makes outside the recommendation changes the tree. Compute the frontier again and drop the questions that no longer apply.

### 5. Play the design back

The frontier is empty when every branch of the tree is visited and nothing is assumed in silence. Then write the full description of what will be built:

- What each part does, in the order it will be built.
- How each part is proved.
- What is out of scope, and where that work is recorded.
- The calls that you made and the user did not, marked as yours.

State the size of the work in plain words and ask whether the description is what the user wants built. Do not act until the user says yes.

## Example

- **Use this skill:** "Start the brainstorming session for how the analyzer should treat member access."
- **Use this skill:** "Grill me on this cache design before we write the plan."
- **Do not use this skill:** "I want to build something that helps writers keep track of characters."
- **Do not use this skill:** "Rename this function and update its callers."
