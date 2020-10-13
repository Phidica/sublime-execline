execline
========

A Sublime Text 3 package for [execline](https://skarnet.org/software/execline/). execline is a command-line scripting language, but not an interactive shell. It presents a unique syntax to access all of the power of a shell, which is logical and predictable while free of potential security issues.

The package currently supports up to execline version: **2.6.1**

Features
--------

- Snippets for all builtins that use blocks.
- Completions for all builtins.
- Precise syntax highlighting that works regardless of whether chainloading commands are separated by newlines or not (see *Figure 3* below).
	- Easy definition of custom chainloading commands to ensure they are highlighted correctly.
	- Preloaded with definitions of all chainloading commands from [s6](https://skarnet.org/software/s6/) and friends.
- Syntax selection via shebang or file extension (see *File extension* below)

Installation
------------

<!--
### Via Package Control

Install [Package Control](https://packagecontrol.io), then go to Command Palette (Ctrl+Shift+P) > Package Control: Install Package > execline.
-->

### Manual

Install [PyYAML](https://github.com/packagecontrol/pyyaml) and [jsonschema](https://github.com/kylebebak/sublime-jsonschema).

Clone the repository to your [Packages directory](https://www.sublimetext.com/docs/3/packages.html) and rename it to `execline`.

    cd /path/to/sublime/packages/directory
    git clone https://github.com/Phidica/sublime-execline.git
    mv sublime-execline execline

Open an execline script and verify the selected syntax is "Execline".

File extension
--------------

Technically this package is not for "execline" scripts, but rather `execlineb` scripts. The `execlineb` launcher is the only part of execline which understands *b*races (`{ }`) to delimit blocks, which it converts into the system of prepended spaces delimiting blocks which execline binaries understand.

The only official way to exclusively indicate that a file is an `execlineb` script is to include a shebang that references `execlineb`. Some scripts distributed with execline use the `.txt` extension, but it would be inconvenient to override this extension to be recognised as execline in general.

`.el` is already closely associated with Emacs Lisp. Therefore, `.elb` was chosen to serve as an unofficial file extension, which is tested as an alternative if a shebang referencing `execlineb` is not found.

Screenshots
-----------

As of release 1.0.0, an execline script (for example, `execline/examples/etc/execline-shell`) will look something like:

![Screenshot of text in Monokai](https://imgur.com/fvWW7PB.png)

Figure 1: Default Monokai colour scheme

![Screenshot of text in custom Monokai](https://imgur.com/0uYj7Cp.png)

Figure 2: Example custom Monokai colour scheme formatting additional scopes

![Screenshot of text which has had all meaningful line breaks removed](https://imgur.com/cfPCcBX.png)

Figure 3: Example custom Monokai colour scheme formatting additional scopes, with all meaningful line breaks removed as an extreme example of the versatility of the highlighter to distinguish the end of one command and the start of the next.

Exposed scopes
--------------

| execline construct           | Scope name
| :----------------:           | :----------
| Unquoted string              | `meta.string.unquoted`
| Command name                 | `meta.function-call.name`
| Parameter                    | `meta.function-call.parameter.` { `option` , `argument` }
| Block                        | `meta.function-call.block` and `punctuation.section.braces`
| Variable expansion           | `variable.other` and `punctuation.definition.variable`
| Globbing (with `elglob`)     | `meta.function-call.parameter.argument.glob` and `keyword.operator.glob.` { `asterisk` , `question-mark` , `bracketexp` }
| Signal names (with `trap`)   | `constant.language.sigcode`
