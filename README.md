# ntlmclient

Minimaler NTLM-over-HTTP-Client.

## Installation

```bash
uv tool install git+https://github.com/Q2Flc2FySec/ntlmclient.git
```

Einmalig ausführen, ohne dauerhaft zu installieren:

```bash
uvx --from git+https://github.com/Q2Flc2FySec/ntlmclient.git ntlmclient -u $USER -p $PASSWORD -d $DOMAIN
```

## Verwendung

```bash
ntlmclient -u $USER -p $PASSWORD -d $DOMAIN
```

