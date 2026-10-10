---
name: "github-markdown-style"
description: Create, edit, review, or improve GitHub Markdown documentation (README.md, CONTRIBUTING.md, SECURITY.md, CODE_OF_CONDUCT.md, CHANGELOG.md, issue and pull-request templates, docs pages, and other Markdown-based project guides) using the principles of The Elements of Style by Strunk and White. Use whenever writing, editing, reviewing, or proofreading GitHub-flavored Markdown prose or documentation, including style and tone checks.
---

# GitHub Markdown Style

## Purpose

Use this skill whenever creating, editing, reviewing, or improving GitHub Markdown documentation.

The primary editorial authority is **The Elements of Style by William Strunk Jr. and E. B. White** ("Strunk & White").

The goal is documentation that is:

* clear
* concise
* concrete
* direct
* precise
* readable
* consistent
* useful to the reader

Do not make prose ornate, promotional, vague, or unnecessarily conversational.

Preserve the author's technical meaning, factual claims, terminology, and intended audience unless the task explicitly asks for substantive changes.

## Core Editorial Rules

Apply these principles throughout the document.

### 1. Omit needless words

Remove words that do not add meaning.

Prefer:

> This command creates a new repository.

over:

> This command is used to create a new repository.

Prefer:

> To install the package, run:

over:

> In order to install the package, you should run:

Delete unnecessary:

* introductory phrases
* qualifiers
* redundant modifiers
* repeated explanations
* empty transitions
* throat-clearing
* corporate language
* unnecessary apologies
* unnecessary conclusions

Do not shorten text merely to make it shorter. Preserve information that helps the reader understand or use the project.

### 2. Use active voice

Prefer active constructions when they are clearer.

Prefer:

> The command creates the configuration file.

over:

> The configuration file is created by the command.

Use passive voice when the actor is unknown, irrelevant, or obvious, or when the passive construction makes the documentation clearer.

Do not mechanically convert every passive construction.

### 3. Use definite, specific, concrete language

Prefer precise statements over abstractions.

Weak:

> This provides a mechanism for handling configuration.

Better:

> The configuration file stores the server address and port.

Avoid vague words such as:

* thing
* stuff
* various
* several
* some
* appropriate
* properly
* easily
* simply
* basically
* generally
* usually

unless the imprecision is intentional and accurate.

Replace vague claims with concrete information whenever the source material provides it.

### 4. Put statements in positive form

State what something does rather than what it does not do, when practical.

Prefer:

> The command accepts one input file.

over:

> The command does not accept multiple input files.

Prefer:

> Use `--verbose` to enable diagnostic output.

over:

> You should not run the command without `--verbose` if you want diagnostic output.

Negative statements are appropriate when the prohibition or limitation itself is important.

### 5. Use specific nouns and strong verbs

Prefer a strong verb over a noun-plus-weak-verb construction.

Prefer:

> The tool validates the configuration.

over:

> The tool performs validation of the configuration.

Prefer:

> The script generates the manifest.

over:

> The script is responsible for the generation of the manifest.

### 6. Avoid unnecessary modifiers

Use adjectives and adverbs only when they add information.

Avoid promotional or subjective modifiers such as:

* powerful
* easy
* simple
* seamless
* robust
* elegant
* incredibly
* extremely
* highly
* very

unless they convey a specific, defensible technical distinction.

Do not describe software as "easy to use" when the documentation can instead explain how to use it.

### 7. Make every word count

Do not repeat information merely for emphasis.

When information appears in:

* a table
* a list
* a code example
* a preceding paragraph
* a heading

do not restate it unnecessarily.

Documentation should minimize the reader's cognitive load.

## Structure and Organization

### 8. Start with the information the reader needs

Do not begin documentation with unnecessary background.

For a README, prefer a structure such as:

1. Project name
2. One-sentence description
3. Key information or status
4. Installation
5. Quick start
6. Usage
7. Configuration
8. Examples
9. Development
10. Contributing
11. License

Adapt the structure to the project.

Do not impose sections that contain no useful information.

### 9. Use headings to reveal structure

Headings should describe their content.

Prefer:

```markdown
## Installation
## Configuration
## Usage
## Troubleshooting
```

Avoid vague headings such as:

```markdown
## Getting Started
## More Information
## Other Things
```

unless they accurately describe the material underneath them.

Keep headings brief and unembellished: `## Snapshots`, not `## Undo insurance: snapshots`. Never phrase a heading as a question. Questions and answers belong only in a FAQ section, and add FAQ items only when asked.

Do not create excessive heading levels.

Put only what the reader needs in the body. Move useful supporting detail, such as the reason for a requirement, to a footnote (`[^1]`). Remove detail that serves no reader.

### 10. Keep related information together

Place explanations, prerequisites, commands, and caveats near the task they describe.

Do not force readers to search elsewhere in the document for information required to understand an example.

### 11. Use lists when items are genuinely parallel

Use bullets for unordered collections.

Use numbered lists when:

* order matters
* the reader must perform steps sequentially
* the items represent a ranked or ordered process

Each item in a list should use parallel grammatical construction.

Prefer:

```markdown
1. Install the dependencies.
2. Configure the application.
3. Start the server.
```

over a mixture of grammatical forms.

## GitHub Markdown Rules

### 12. Write for GitHub's rendered Markdown

Use valid, conventional GitHub-Flavored Markdown.

Prefer:

* ATX headings (`# Heading`)
* fenced code blocks
* descriptive link text
* tables when tabular structure improves comprehension
* task lists for actionable checklists
* blockquotes for actual quotations
* semantic Markdown rather than HTML when Markdown is sufficient

Avoid unnecessary HTML.

Use HTML only when GitHub Markdown cannot express the required presentation adequately.

### 13. Use descriptive links

Prefer:

```markdown
See the [installation guide](docs/installation.md).
```

over:

```markdown
Click [here](docs/installation.md).
```

Avoid bare URLs when descriptive link text is practical.

Link text should identify the destination.

### 14. Make code examples executable when possible

Code examples should be:

* syntactically valid
* minimal
* relevant
* complete enough to demonstrate the stated behavior

Prefer:

```bash
git clone https://github.com/example/project.git
cd project
make
```

over an incomplete fragment that requires the reader to infer missing steps.

Do not add unnecessary commands merely to make an example appear complete.

### 15. Identify code languages

Use language identifiers on fenced code blocks whenever the language is known.

Prefer:

````markdown
```bash
npm install
```
````

over:

````markdown
```
npm install
```
````

Use `text` when the content is textual but does not represent source code.

### 16. Keep prose outside code blocks

Do not put explanatory prose inside a code block merely to preserve formatting.

Use a paragraph before or after the example.

### 17. Do not alter code merely for style

When editing documentation, distinguish between:

1. prose
2. Markdown structure
3. code examples
4. literal command output
5. configuration examples

Do not change technically meaningful code, commands, API names, identifiers, output, or configuration syntax unless the task explicitly includes technical correction.

If a code example appears incorrect, identify the problem rather than silently changing its semantics.

## README-Specific Rules

### 18. The opening must answer three questions quickly

A README should make it clear:

1. What is this project?
2. What problem does it solve?
3. Why would the reader use it?

Do this concisely.

A useful opening is generally more valuable than a long project history.

### 19. Keep the project description concrete

Prefer:

> `foo` converts Vim configuration files into JSON.

over:

> `foo` is a powerful and flexible solution for seamlessly managing your configuration workflow.

The first tells the reader what the software does.

### 20. Installation instructions must be actionable

State:

* prerequisites
* supported platforms when relevant
* installation commands
* required versions
* important environment variables
* post-installation steps

Do not make the reader infer required steps.

### 21. Quick starts should be genuinely quick

A quick-start section should demonstrate the smallest useful path from installation to successful use.

Avoid turning the quick start into a comprehensive tutorial.

### 22. Examples should demonstrate real usage

Prefer examples that answer likely user questions.

Use realistic names and values unless placeholders are necessary.

When placeholders are used, make them visually obvious:

```bash
mytool --config /path/to/config.toml
```

Avoid examples that look executable but contain unexplained fake values.

## Technical Accuracy

### 23. Never trade accuracy for brevity

Concise documentation that is wrong is worse than longer documentation that is correct.

Preserve important:

* version requirements
* platform limitations
* compatibility information
* warnings
* edge cases
* error conditions
* security considerations
* configuration constraints

Remove words, not necessary facts.

### 24. Distinguish facts from recommendations

State factual behavior directly.

For example:

> The application reads configuration from `$XDG_CONFIG_HOME`.

For recommendations, make the recommendation explicit:

> Use `$XDG_CONFIG_HOME` when you need to keep configuration outside the default location.

Do not disguise opinions as technical facts.

### 25. Do not make unsupported claims

Avoid claims such as:

* fastest
* easiest
* best
* most powerful
* production-ready
* secure
* lightweight
* highly reliable

unless they are supported by evidence or are clearly framed as an opinion.

Prefer measurable facts.

## Grammar and Usage

### 26. Use standard grammar

Correct:

* subject/verb agreement
* pronoun references
* modifier placement
* verb tense
* capitalization
* punctuation
* parallel construction

Do not introduce grammatical errors in the name of conversational style.

### 27. Prefer simple words

Prefer a familiar word when it expresses the meaning precisely.

Prefer:

* use over utilize
* help over facilitate
* start over commence
* show over display when appropriate
* before over prior to
* about over approximately when precision is not required

Technical terminology is appropriate when it is the correct term.

Do not replace established technical vocabulary merely to make prose simpler.

### 28. Avoid needless nominalization

Prefer:

> Configure the server.

over:

> Perform configuration of the server.

Prefer:

> The program validates the file.

over:

> The program performs validation of the file.

### 29. Maintain consistent terminology

Use one term for one concept.

If the software calls something a "workspace," do not alternate between:

* workspace
* project
* environment
* working area

unless these terms have distinct meanings.

Preserve terminology already established by the project.

## Punctuation

### 30. Use punctuation to clarify structure

Punctuation should make sentences easier to parse.

Use commas, semicolons, colons, parentheses, and em dashes deliberately.

Do not add punctuation merely because a sentence feels long.

### 31. Use the serial comma consistently

Use the serial comma in lists of three or more items.

Prefer:

> Linux, macOS, and Windows

over:

> Linux, macOS and Windows

### 32. Use parentheses only for a purpose

Purposeful uses: code and command syntax (`:Cmd {arg}`), link syntax, and short values in tables. Otherwise make the content part of a sentence or its own sentence. Do not bury essential instructions in parentheses. In tables, use one form consistently.

### 33. Limit dashes and semicolons

Use at most two of each per document: dashes used as punctuation (` - `, em dash, en dash) and semicolons. Exceed this only when necessary. Hyphens in names (`vim-nox`) and a dash between a term and its definition in a list (`**Logger** - a logging utility`) do not count. Rewrite the rest as separate sentences. These marks are correct grammar, but frequent use is off-putting to readers.

## Tone

### 34. Be direct and professional

Documentation should sound like an experienced technical writer explaining something clearly.

Avoid:

* marketing language
* hype
* fake enthusiasm
* unnecessary friendliness
* jokes that obscure meaning
* rhetorical questions
* excessive exclamation points
* corporate jargon

Prefer:

> Install the package with:

over:

> Getting started is super easy! Just run the following command!

### 35. Address the reader directly when useful

"you" is acceptable when giving instructions.

For example:

> Run the command from the project directory.

Avoid excessive second-person phrasing when an imperative is clearer.

### 36. Do not apologize unnecessarily

Do not write:

> Sorry for the inconvenience.

unless the apology is genuinely part of the communication being documented.

State the problem and solution directly.

## Revision Procedure

When asked to edit or improve a Markdown document, follow this process.

### Step 1: Determine the document's purpose

Identify:

* intended audience
* primary task
* expected reader knowledge
* document type
* technical context

Do not rewrite blindly.

### Step 2: Preserve meaning

Before changing prose, determine what each section communicates.

Do not remove information simply because it is verbose.

### Step 3: Remove needless words

Delete:

* redundancy
* filler
* unnecessary qualifiers
* unnecessary introductions
* repeated conclusions
* promotional language

### Step 4: Improve sentence construction

Check for:

* passive voice
* weak verbs
* nominalizations
* vague references
* ambiguous pronouns
* excessive sentence length
* misplaced modifiers
* inconsistent terminology

Rewrite where doing so improves clarity.

### Step 5: Improve organization

Check whether:

* sections appear in a useful order
* prerequisites appear before dependent instructions
* examples appear near the concepts they demonstrate
* headings accurately describe their contents
* related information is grouped together

### Step 6: Check Markdown

Verify:

* heading hierarchy
* fenced code blocks
* language identifiers
* links
* lists
* tables
* task lists
* escaping
* blank lines
* GitHub rendering conventions

### Step 7: Check technical integrity

Do not silently alter:

* commands
* APIs
* filenames
* paths
* identifiers
* configuration keys
* version numbers
* code semantics

unless correction is explicitly requested or the error is unambiguous.

### Step 8: Perform a final Strunk & White pass

Ask:

* Can any word be removed without losing meaning?
* Is every sentence clear?
* Is the subject doing the action where appropriate?
* Are the nouns specific?
* Are the verbs strong?
* Are unnecessary modifiers gone?
* Are statements positive where practical?
* Are related words together?
* Is the document's structure obvious?
* Does every section serve the reader?

## Review Mode

When asked to **review** rather than rewrite a document, do not automatically rewrite it.

Report findings under useful categories such as:

* Clarity
* Concision
* Grammar
* Organization
* Terminology
* Markdown
* Technical documentation quality

For each significant issue:

1. quote or identify the relevant text
2. explain the problem
3. identify the applicable principle
4. propose a correction when useful

Prioritize substantive problems over stylistic preferences.

Do not manufacture issues merely to produce a longer review.

## Rewrite Mode

When asked to **rewrite, improve, polish, or edit** a document:

* preserve technical meaning
* preserve the author's intended audience
* preserve established project terminology
* improve clarity and concision
* fix grammar and Markdown
* remove unnecessary words
* improve organization when necessary
* retain useful technical detail

Return the complete revised document when the user asks for a finished document.

Do not surround the Markdown document with commentary unless requested.

## Minimal-Change Mode

When the user asks for proofreading or minimal editing:

Make the smallest changes necessary to correct:

* grammar
* spelling
* punctuation
* obvious ambiguity
* Markdown errors

Do not restructure the document or substantially alter its voice.

## Aggressive-Editing Mode

When the user asks for a substantial improvement:

You may:

* reorder sections
* rewrite sentences
* consolidate redundant material
* replace vague language
* improve examples
* restructure lists
* improve headings
* eliminate unnecessary sections

Still preserve the technical meaning unless the user requests substantive content changes.

## Conflict Resolution

When editorial principles conflict with technical accuracy, **technical accuracy wins**.

When brevity conflicts with necessary context, **necessary context wins**.

When grammatical correctness conflicts with established code, API, command, or configuration syntax, **the technical syntax wins**.

When a project's established terminology conflicts with ordinary English terminology, use the project's terminology when it refers to a project-specific concept.

When a GitHub Markdown convention conflicts with an abstract stylistic preference, use the GitHub convention.

## Output Standards

Unless the user requests otherwise:

* return valid GitHub-flavored Markdown
* do not add unnecessary commentary
* do not add a "Conclusion" section merely to summarize the document
* do not add sections that contain no useful information
* do not use decorative language
* do not use emojis in technical documentation
* do not add claims that cannot be supported by the source material
* do not change technical semantics for stylistic reasons

The final document should read as though a careful technical writer removed everything unnecessary while preserving everything the reader needs.
