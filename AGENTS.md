# Agent development guidelines

## Git workflow
- Do not commit directly to `main`.
- Create a task-specific `feature/` or `fix/` branch from `main`.
- Commit changes to that branch and open a pull request targeting `main`.
- Do not merge pull requests without explicit user approval.

## Language and reporting
- **Write pull request titles, descriptions, review summaries, test reports, and user-facing progress/completion reports in Japanese.**
- Keep programming language identifiers and technical terms in English when clearer.
- In PR descriptions, include: 変更概要、設計判断、テスト方法と実行結果、既知の制約.
- Clearly distinguish tests actually executed from tests only added or proposed; never claim unexecuted tests passed.

## Engineering priorities
- Prefer minimal, understandable implementations over abstraction for its own sake.
- Keep production code focused; comprehensive test code is welcome.
- Introduce concurrency and performance optimizations in separate, reviewable PRs.
- Explain why changes are needed and preserve the sequential TCP server as a baseline.
