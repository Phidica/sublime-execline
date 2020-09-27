execline
========

A Sublime Text 3 package for [execline](https://skarnet.org/software/execline/). execline is a command-line scripting language, but not an interactive shell. It presents a unique syntax to access all of the power of a shell, which is logical and predictable while free of potential security issues.

This project is under active development and is not yet feature-complete.

Planned features
----------------

- [x] Complete syntax coverage of the execline builtins.
- [x] Snippets (~~keywords~~).
- [ ] \(If possible) Custom specification of signatures for user-defined functions.
- [ ] Distribution via Package Control.

File extension
--------------

Technically this package is not for "execline" scripts, but rather `execlineb` scripts. The `execlineb` launcher is the only part of execline which understands *b*races (`{ }`) to delimit blocks, which it converts into the system of prepended spaces delimiting blocks which execline binaries understand.

The only official way to exclusively indicate that a file is an `execlineb` script is to include a shebang that references `execlineb`. Some scripts distributed with execline use the `.txt` extension, but it would be inconvenient to override this extension to be recognised as execline in general.

`.el` is already closely associated with Emacs Lisp. Therefore, `.elb` was chosen to serve as an unofficial file extension, which is tested as an alternative if a shebang referencing `execlineb` is not found.
