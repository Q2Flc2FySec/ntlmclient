# ntlmclient

Minimal NTLM-over-HTTP client.

## Installation

```bash
uv tool install git+https://github.com/Q2Flc2FySec/ntlmclient.git
```

Run once without installing permanently:

```bash
uvx --from git+https://github.com/Q2Flc2FySec/ntlmclient.git ntlmclient -u $USER -p $PASSWORD -d $DOMAIN
```

## Usage

```bash
ntlmclient -u $USER -p $PASSWORD -d $DOMAIN
```

