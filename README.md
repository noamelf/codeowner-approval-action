# Codeowners Approval Action

This action ensures that all codeowners, defined in the `CODEOWNERS` file, have approved a pull request before it can be merged. The action provides enhanced functionality by supporting multiple codeowners per line in the `CODEOWNERS` file, ensuring that **every codeowner listed for a file is required to approve the pull request**.

## Key Features

- **Multiple Codeowners Per File**: GitHub’s default behavior only requires **one** codeowner from a list to approve a pull request. This action enforces that **all codeowners listed for a file or directory must approve** the pull request before it can be merged. This ensures stronger review policies, particularly for critical or shared code areas.

## Usage

To use this action, create a new workflow file in your repository under the `.github/workflows` directory. For example, create `.github/workflows/codeowners-approval.yml`.

```yaml
name: "Code Owner Approval Workflow"

on:
  pull_request_review:
    types: [submitted]

jobs:
  codeowners-approval:
    runs-on: ubuntu-latest
    steps:
      - name: Codeowners Approval Check
        uses: noamelf/codeowner-approval-action/.github/workflows/codeowner-approval-template.yaml@master
        with:
          pr-number: ${{ github.event.pull_request.number }}
          repo-name: ${{ github.repository }}
        env:
          BV_CI_GH_APP_PRIVATE_KEY: ${{ secrets.BV_CI_GH_APP_PRIVATE_KEY }}
```

### Multiple Codeowners Per Line

In the `CODEOWNERS` file, you can define multiple codeowners for a specific file or directory by listing multiple GitHub handles or teams per line. This action ensures that **all codeowners listed on the same line must approve the pull request**.

For example:

```plaintext
* @noamelf @otherdev
```

With this action, both the core and devops teams must approve the pull request for any changes to files in the repo, unlike GitHub’s default behavior where only one approval would be required.

## Setting Up Branch Protection Rules

To make this check mandatory for merging, you can add it to your branch protection rules by going to your repository’s `Settings > Branches` and adding this workflow to the required status checks.

## Conclusion

The `Codeowners Approval Action` ensures that all relevant codeowners must approve changes before they can be merged, offering stricter control than GitHub's default behavior, which only requires one codeowner’s approval. This is especially useful for teams managing critical or shared code areas.
