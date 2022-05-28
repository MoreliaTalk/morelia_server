# How to contribute to MoreliaServer #

## Support questions ##

Please don't use the issue tracker for this. The issue tracker is a tool
to address bugs and feature requests in Morelia server itself. Use one of the
following resources for questions about using Morelia server or issues with your
own code:

- The ``#general`` channel on our [Slack](https://moreliatalk.slack.com) chat.
- Ask on our [GitHub Discussions](https://github.com/MoreliaTalk/morelia_server/discussions).
- Ask for support in our telegram chatroom:
[Project MoreliaTalk](https://t.me/+xfohB6gWiOU5YTUy).


## Reporting issues ##

Include the following information in your post:

- Describe what you expected to happen.
- If possible, include a
[minimal reproducible example](https://stackoverflow.com/help/minimal-reproducible-example) to help us
    identify the issue. This also helps check that the issue is not with
    your own code.
- Describe what actually happened. Include the full traceback if there
    was an exception.
- List your Python and MoreliaServer versions. If possible, check if this
    issue is already fixed in the latest releases or the latest code in
    the repository.


## Submitting patches ##

If there is not an open issue for what you want to submit, prefer
opening one for discussion before working on a PR. You can work on any
issue that doesn't have an open PR linked to it or a maintainer assigned
to it. These show up in the sidebar. No need to ask if you can work on
an issue that interests you.

Include the following in your patch:

- all patches are created in separate branches. 
For example new branch name ``develop-#xxx``. Where xxx in name is the issue number. 
- Use [Flake8](https://github.com/PyCQA/flake8) to format your code.
- Check types in your code using [mypy](https://github.com/python/mypy)
- Include tests if your patch adds or changes code. Make sure the test
    not fails.
- Update any relevant docs pages and docstrings. Doc pages and
    docstrings should be wrapped at 120 characters.
- Add an entry in ``CHANGES.md``. Use the same style as other
    entries. Also include ``.. versionchanged::`` inline changelogs in
    relevant docstrings.

After you checking all steps for create patch you can create Pull Request (aka PR). Before that, read the
[rules](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request).


## Main code rules ##

### Conventional Commits ###

Commit messages should be of the following structure:
`<type>(optional scope): <description> [optional body] [optional footer]`:

`<type>` - for example `fix`, `feat`, `refactor`, `add`, `BREAKING CHANGE`, `docs`, `perf`, `test`.

`(optional scope)` - context MUST BE a noun enclosed in parentheses, describing the part of the code base affected by
the commit, for example `fix(parser)`

`<description>` - a brief description of changes to the code

`[optional body]` - additional description of changes to the code

`[optional footer]` - meta-information about commit. For example, related pull-requests, discussions, issues, people, etc.

Read more at [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)

### Code style ###

- If not specified below, the entire code is executed according to the [PEP8](https://www.python.org/dev/peps/pep-0008/)
standard.
- Length of string is limited to 79 characters.
- For name constant declaration MUST BE used UPPERCASE.
- Each import MUST BE on a separate line.
- Import templates (from import *) SHOULD NOT be used.
- `lower_case_with_underscores` style MUST BE used for function.
- `CapitalizedWords` style MUST BE used for classes.
- `lowercase` or `lower_case` stype MUST BE used for simple object (variable)
- Each function parameter MUST BE on a separate line.
- All transfers MUST BE vertically aligned
- For docstring MUST BE uses [Google style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
of comment and docstring.
- Project uses automatic generation of documentation using [Sphinx](https://www.sphinx-doc.org/en/stable/),
for which use the following keywords in the docstrings:
`Args (alias of Parameters)`, `Arguments (alias of Parameters)`, `Attention`, `Attributes`, `Caution`, `Danger`, `Error`
, `Example`, `Examples`, `Hint`, `Important`, `Keyword Args (alias of Keyword Arguments)`, `Keyword Arguments`, `Methods`
`Note`, `Notes`, `Other Parameters`, `Parameters`, `Return (alias of Returns)`, `Returns`, `Raise (alias of Raises)`,
`Raises`, `References`, `See Also`, `Tip`, `Todo`, `Warning`, `Warnings (alias of Warning)`, `Warn (alias of Warns)`,
`Warns`, `Yield (alias of Yields)`, `Yields`.
- All new class (also class methods) and function MUST BE contained a docstring
- All code MUST BE documenting in sphinx-format *.rst files which contains in ./docs
