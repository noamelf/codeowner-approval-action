# Codeowners Multi-Approval Action

This GitHub Action extends the functionality of GitHub's `CODEOWNERS` feature by requiring **all codeowners** listed for a file or directory to approve a pull request before it can be merged. This ensures stricter review policies, particularly for critical or shared code areas.

## Why Use This Action?

By default, GitHub only requires **one** codeowner's approval, even if multiple codeowners are listed. This action enforces that **every codeowner must approve**, providing better safeguards for code quality and accountability.

For example, given the following line in a `CODEOWNERS` file:

```plaintext
* @noamelf @otherdev
```

Both `@noamelf` and `@otherdev` must approve any pull request affecting files in the repository. Without this action, only one of these approvals would be required.

---

## How It Works

The action is triggered by the `pull_request_review` event when a review is submitted. It scans the `CODEOWNERS` file for the pull request's files and verifies that all listed codeowners, including individuals and teams, have approved the changes.

---

## Setup Instructions

1. **Create a Workflow File:**  \
   Add a new workflow in the `.github/workflows` directory. For example, create `.github/workflows/codeowners-approval.yml` with the following content:

   ```yaml
   name: "Codeowners Approval Workflow"

   on:
     pull_request_review:
       types: [submitted]

   jobs:
     codeowners-approval:
       runs-on: ubuntu-latest
       steps:
         - name: Check Codeowners Approval
           uses: noamelf/codeowner-approval-action@main
           with:
             pr-number: ${{ github.event.pull_request.number }}
             repo-name: ${{ github.repository }}
             github-token: ${{ secrets.MY_GITHUB_TOKEN }}
   ```

2. **Provide a GitHub Token:**  \
   This action requires a token with enhanced permissions to read organization teams. The next section explains how to set this up.

---

## Token Permissions

To handle teams in the `CODEOWNERS` file, the action requires a GitHub token with the following permissions:

- `repo`
- `read:org`

### Options to Provide the Token

1. **Personal Access Token (Simpler Setup):**  \
   Create a personal access token with the required permissions and add it as a repository secret (e.g., `MY_GITHUB_TOKEN`).

2. **GitHub App Token (Recommended for Organizations):**  \
   Use a GitHub App for token generation. This is more secure and scalable for larger organizations.

---

### Using a GitHub App Token

Here’s an example workflow using a GitHub App token:

```yaml
name: "Codeowners Approval Workflow"

on:
  pull_request_review:
    types: [submitted]

jobs:
  codeowners-approval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/create-github-app-token@v1
        id: app-token
        with:
          app-id: ${{ vars.app-id }}
          private-key: ${{ secrets.app-private-key }}
          owner: ${{ github.repository_owner }}

      - name: Check Codeowners Approval
        uses: noamelf/codeowner-approval-action@main
        with:
          pr-number: ${{ github.event.pull_request.number }}
          repo-name: ${{ github.repository }}
          github-token: ${{ steps.app-token.outputs.token }}
```

- **`app-id`**: The ID of your GitHub App.
- **`app-private-key`**: The private key for your GitHub App.
- **`owner`**: The organization name.

This workflow generates a token via the `actions/create-github-app-token@v1` action and passes it to the `codeowner-approval-action`.

---

By following these steps, you can enforce stricter code review policies for your repository, ensuring that all stakeholders approve critical changes before they are merged.
