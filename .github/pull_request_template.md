<!--
Thanks for contributing to pibooth! Keep the change focused: one feature or
one fix per pull request (see docs/sources/dev/rules.rst).
-->

## What and why

<!--
What does this change do, and what problem does it solve?
Link the issue if there is one: "Fixes #123".
-->

## How it was tested

<!--
The CI runs the test suite headless: it exercises no camera, no printer and
no GPIO. Say what you ran yourself, and on what.
-->

- [ ] The test suite passes locally (see docs/sources/dev/tests.rst)
- [ ] Tested on real hardware: <!-- Raspberry Pi model, OS, camera (Pi camera / DSLR model / webcam), printer -->
- [ ] Not tested on real hardware

## Checklist

- [ ] New or changed behaviour is covered by a test, or the reason it cannot be is stated above
- [ ] `docs/sources/config/default.cfg` is regenerated if a configuration option changed
- [ ] Every language in `pibooth/language.py` defines the new key, if a text was added
- [ ] The documentation under `docs/` is updated if the user-facing behaviour changed
