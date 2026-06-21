# Privacy and Security Policy

## Prohibited repository content

The repository must not contain:

- student or government identification numbers;
- personal email addresses, phone numbers, addresses, or account screenshots;
- passwords, access tokens, API keys, private keys, or populated `.env` files;
- personal submission documents or source course PDFs;
- arbitrary desktop captures that could expose unrelated applications;
- model/data files whose origin or redistribution permission is unclear.

Generic PDF and office-document patterns are ignored. Only reviewed application-generated images under `assets/evidence/` are committed as visual evidence.

## Configuration posture

- The project requires no secret or external service credential.
- `.env` is ignored; `.env-example` states that no environment variables are required.
- Runtime and development dependencies are declared in `pyproject.toml` and locked in `uv.lock`.
- Simulator and training choices use versioned JSON configuration rather than machine-specific absolute paths.
- The GitHub Actions workflow has read-only repository contents permission.

## Release check

Before pushing, run a tracked-text scan for credential markers, email addresses, personal identifiers, and long numeric ID candidates. Review every committed image visually. If sensitive data was ever committed, deleting it in a later commit is insufficient; repository history and any exposed credential must be remediated separately.
