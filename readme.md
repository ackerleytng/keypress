# Keypress

The API key management system built to work with Keycloak and a special mapper to extend the expiration time (exp) of an access
tokens.

See [Ackerley's plugin](https://github.com/ackerleytng/exp-mapper).

This project is part of a pair of components, as documented in [design](./design.md).

## Tips

To [decode a jwt on the command line](https://gist.github.com/angelo-v/e0208a18d455e2e6ea3c40ad637aac53), do

```
echo "$JWT" | jq -R 'split(".") | .[1] | @base64d | fromjson'
```
