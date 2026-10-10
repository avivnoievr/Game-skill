# Development and publication

- Development repository: [avivnoievr/Game-skill](https://github.com/avivnoievr/Game-skill).
- Publication repository: [avivnoievr/game-studio-3d](https://github.com/avivnoievr/game-studio-3d).

All edits, including publication templates and issue forms, originate in the development
repository. The publication repository receives snapshots of specific commits. Feedback can
be collected here; implementation remains in the development repository.

Initialize the publication repository with its own history. Copy the prepared files into
that repository; do not push, fork or mirror the development repository's commit history.
Keep the source SHA link, licenses and attribution in the prepared snapshot. This preserves
provenance without copying private-session links from old commit messages into the new history.

## Promotion sequence

1. Finish the change and the checks appropriate to it in the development repository.
2. Choose one committed source SHA and a unique version. Prepare a candidate with
   `tools/prepare_distribution.py` from that SHA.
3. The owner tries that candidate on the intended task. Record the source SHA, checks,
   observed result and remaining limitations. Continue development if the result needs work.
4. After the owner explicitly approves that exact SHA, prepare an approved snapshot with
   the approval record. Changing the source SHA invalidates that approval.
5. Verify the generated file hashes and installability. Publish the snapshot on `main`
   and create the matching `v<version>` tag. Keep a source link and release notes.

The preparation script only creates local files. It cannot create a repository, push,
publish a GitHub release, or obtain approval. No push-triggered sync or release automation
is configured. Candidate install links that name a future release tag become usable only
after that tag exists in the publication repository.

## Preservation and rollback

Keep development tests and previous release tags. Compare against a fixed prior commit,
not a moving branch. Never force-push publication history or move an existing version tag.
If a release fails, document it and publish a corrected version from the development
repository. Reverting to a prior tagged version remains possible.

Human approval, structural correctness and visual quality are separate facts. Publish the
observed validation limits with the version; do not describe historical tests as freshly run.
