# Feedback and contributions

Use this repository's issue forms for reproducible bugs and visual/design feedback. Report
the distributed version and source commit from `RELEASE.json`, the task you asked Claude to
perform, relevant tool versions, the result and the expected behavior.

For a visual issue, include an image or clip and the reference used to judge it. Identify the
camera, scale and lighting where relevant. Distinguish a functional failure from a stylistic
preference. Neither more polygons nor a passing metric alone establishes design quality.

## Where code and skill edits go

Development happens in [{{SOURCE_REPOSITORY}}](https://github.com/{{SOURCE_REPOSITORY}}).
Open implementation pull requests there, against its current default branch. The tests,
source content and public README/issue templates are maintained there as well.

This repository is the publication channel. A fix described here is implemented and tested
in the development repository, reviewed by the owner, and then included in a selected release.
Do not maintain a second independent copy of the skill here.

## Reviewing a candidate

The owner tests the prepared candidate on the intended Claude task and records the exact
source SHA, what was tried, what worked and any remaining limitation. Approval applies only
to that source SHA. A subsequent development commit needs a new release review before promotion.
Automated checks do not replace the owner's approval or prove professional visual taste.
