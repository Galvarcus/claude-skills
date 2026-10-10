# Classes

A class forward-referenced only inside a function body works fine: a local variable's type annotation, or a call to `ClassName.new()`, resolves lazily and can name a class defined later in the same script.

A class used in another function's own signature (a parameter type or return type) is resolved eagerly, at that function's definition time. If the class is defined later in the file, this throws `E1010: Type not recognized` at the function's own `def` line, before the file finishes compiling.

```vim
# Breaks: Flatten's return type references Row before Row is defined.
export def Flatten(project: Pj.Project): list<Row>
  ...
enddef

export class Row
  ...
endclass
```

```vim
# Works: Row is defined first.
export class Row
  ...
endclass

export def Flatten(project: Pj.Project): list<Row>
  ...
enddef
```

This is a genuine functional dependency, not a style preference. When Script Structure would otherwise put bare functions before classes, and a class appears in another function's own parameter or return type, keep that class defined first instead and note why in a short comment above it (functionality depends on the order; this is not a rule violation to fix later).

The same eager-resolution rule applies to a class's own fields: if class `A` declares a field typed `B`, `B` must be defined before `A`, regardless of which one is exported.

A class field typed as a list of its own class is a special case of this - `A` can never be "defined before" itself, so reordering never fixes it:

```vim
export class BinderItem
  var children: list<BinderItem> = []  # folder-only
endclass
```

Whether this throws `E1010: Type not recognized` depends on the Vim version, not the code: older Vim9-class patch levels reject self-referencing field types outright, while a sufficiently current Vim (confirmed working: 9.2 with a full patch set) allows them. Ubuntu's packaged `vim-nox`, and `rhysd/action-setup-vim`'s `stable` option on Linux (which installs the same distro package), both lag far enough behind Vim9's actively-evolving class system to hit this - see `references/testing.md` for a CI fix that doesn't require compiling Vim from source on every run. Don't "fix" this by loosening the field to `list<any>` - a self-referencing tree structure (a binder item's own children, a linked list node's own next pointer) is a normal, correct pattern; the fix is a current-enough Vim, not different code.

## Interfaces that name their implementing class

An interface must be defined before a class that implements it, so its method signatures cannot name that class: `E1010: Type not recognized`. Type those parameters and returns as `any` in the interface, and keep the exact type in each class's methods. Vim 9.2 accepts the narrower class signature as an implementation, calls through the interface reach the class, and a wrong type is still rejected at run time (`E1013`) by the class method.

```vim
export interface ItemContainer
  def AddChild(child: any): void
  def ChildAt(idx: number): any
endinterface

export class BinderItem implements ItemContainer
  def AddChild(child: BinderItem): void
  ...
```

Pick the implementation with a ternary into a variable of the interface type: `var owner: ItemContainer = folder is null_object ? project : folder`.

A shared interface must not create circular imports: script A imports script B and B imports A, directly or through other scripts. If it does, move the interface to its own script, and have that script import none of the scripts that implement the interface. It then cannot name their classes, so type them `any`, as above. Do not rely on a cycle that happens to work: through `import autoload` a cycle can load, because loading is lazy, but the same cycle through plain `import` fails with `E1010`, and any cycle can break when an import or the load order changes.
