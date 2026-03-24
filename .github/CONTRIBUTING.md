# Chessai Contributing Guide

Thanks for wanting to contribute!

All code and resources contributed to a project become owned by the project under the respective license upon submission.

## Code of Conduct

Make sure to familiarize yourself with our [Code of Conduct](./CODE_OF_CONDUCT.md).

## Reporting Issues

To allow for flexibility when it comes to issue types and submission contexts,
we do not have a strict template for reporting issues.
Try to follow this general guidance when submitting (or dealing with) issues:

 - Be sure to clearly state your issue.
   Be descriptive and concise.
   The required information changes depending on the specific needs,
   but some information generally required for bugs is:
    - Steps to reproduce the issue.
    - Expected vs actual behavior.
    - Your environment (OS, language version, etc.) if applicable.

 - Note that issues are not meant for arbitrary communication,
   see [the Discussion section](#discussion) for guidance on that.

 - Remember that the aims of the project may differ from your personal needs.
   So, a contributor may not agree with the priority or need for an issue.

 - Remember that this is open source and we have limited resources,
   so we may not address an issue as fast as you would like.
   In cases like this, submitting a PR yourself could help out.

 - We don't call "dibs" or reserve issues.
   A PR is the best way to show others your interest in an issue.
   Conversely, if you clearly see someone working on an issue, don't try to "scoop" them.
   If it looks like an effort was abandoned, feel free to politely ask them or an admin if they are going forward with it.

## Submitting a PR

Thanks for wanting to contribute to our projects!
Healthy open source ecosystems depend on contributors like you.
Pull/Merge requests (and code reviews) are a fundamental part of Software Engineering.
They can be very intimidating (especially to a new developer),
but they are the type of thing that gets easier the more you do them.

### General Guidance on PRs

 - Contributors should strive to make things as easy as possible on the reviewer.
   You are using their time, so make sure to respect it.

 - Ensure that the description is sufficient, but concise.
   Overly long PR descriptions waste the reviewer's time.

 - Keep in mind that PR comments are generally terse, but constructive.
   Try to read them with a positive outlook.
   Receiving criticism on code can be tough at first, it gets easier over time.

 - You are responsible for ensuring that you have the legal right to submit all code/resources you present.

 - When you are ready for a new pass/re-review, make sure to explicitly let the reviewer know you are ready.
   Often the PR system (like GitHub) may send out messages for every commit, so it can be hard for a reviewer to tell when the code is ready.
   There will usually be a "Re-request Review" button you can use to indicate that you are ready for another pass.

 - Ensure that all comments are addressed before requesting another pass by a reviewer.
   If a comment has been fully addressed, resolve it (via the resolve button) without further comments.
   If a comment requires further discussion, then comment on it.
   Keep in mind what things will look like for the reviewer.
   When they re-review a PR, they should only see things that need action on their part.

    - Note that this also applies when a reviewer asks a question in a comment,
      and you agree with the premise of the question and make changes accordingly.
      For example, if a review says: "Shouldn't this be 1?",
      then you can just resolve if you agree that it should be 1 and you make that change.
      Only comment if further discussion is required.

 - Take your time.
   Quality is strongly preferred over quantity.

 - Do not submit an AI code review to your own PR (e.g., having CoPilot do a pass on a PR).
   A reviewer may choose to use an AI tool to assist them with a review,
   but a contributor should not submit reviews to their own code.

 - Review your own PR before asking for a (re)review.

### Extra Advice for New Contributors

For contributors that are new to PRs,
here is a general procedure you can follow:
 1. Fork the target repo.
 2. Make a branch in your fork for the new changes (here we will call it `change-branch`).
 3. Implement your code, tests, and documentation in `change-branch`. Make sure your code passes testing and CI.
 4. Review your code.
 5. Create a new branch for your PR based on `change-branch` (here we will call it `pr-branch`).
 6. Create a PR using `pr-branch`.
 7. Wait patiently for comments.
 8. Address comments first in `change-branch`.
 9. Do a self review. Make sure to check style, tests, and CI.
 10. Once your changes are looking good, merge them into `pr-branch`.
 11. Re-request a review (there is usually a button for this).
 12. If changes are requested, GOTO 7.
 13. Done! Update your fork.

Note that the use of multiple branches is to avoid excess emails that can happen when you push changes to a branch with an open PR.
It also gives more advanced users the opportunity to squash changes before the next PR pass.

For new contributors, we have some additional rules:
 - At most 1 open PR at a time.
 - Try to stick to "Easy" issues.
   It is expected that contributors tackling "Medium/Hard" issues are experienced with this repository and/or open source development.
   We will provide limited or no support for new contributor tackling harder issues.

## General Coding Style

The coding style we use will differ based on the language and project.
Follow the rules of the specific project/repo you are in.

In general, follow these principles:

 - Be consistent with existing code.
 - Strive to write maintainable code that is:
   - easy to read,
   - self documenting,
   - and not surprising.

## AI Tools

We do not outright ban the use of AI coding tools.
However, it is important to remember that all code you submit is considered yours.
You are responsible for all your code.
You are expected to fully understand, explain, and justify all your code.
If we find that you are not acting responsibly with your code, we may ban you.

AI tools can make it very easy to do things like submit PRs,
but can waste a reviewer's time if the code is of low-quality.
Not respecting a review's time is against our [Code of Conduct](./CODE_OF_CONDUCT.md#foster-collaboration) and can result in being banned.

If you are using a coding tool and someone asks you about it,
you should be honest and willing to disclose the tool, version, and how you used it.
If you are not comfortable disclosing this information, then avoid using AI coding tools.

Also be wary when using AI tools for text/conversations (e.g., emails, PR descriptions, issues, etc).
AI will often generate text that is much longer and more verbose than necessary.
Unnecessarily long conversations are generally against our [Code of Conduct](./CODE_OF_CONDUCT.md#try-to-be-concise).

We always encourage learning.
If you use AI tools, use them in a way that helps you learn, instead of taking away your learning opportunities.

## Discussion

For discussion outside of GitHub, you can use our [Discord](https://discord.gg/xRxdbWqtWS).
