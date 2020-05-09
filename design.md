# Design

This application has 3 components

+ The service that manages the API key and a light frontend (keypress)
+ A custom expiration time extension mapper ([exp-mapper](https://github.com/ackerleytng/exp-mapper)).
+ A kong plugin, and a database that is part of kong

![design.svg](./design.svg)

## Service that manages API key

+ Users must log in to Keypress as they would with any other SSO-protected site
  + Keypress is an OAuth client on its own

### `exp-mapper` setup

The extension of expiration time is clearly weakening security, and hence we
need to be very careful with those access tokens with extended validity.

Here are the considerations for the security of the long-lived access tokens.

+ The long-lived access tokens are never released to a public client or User Agent
  + They will only live within Kong (server side), the keypress database and Keycloak
  + All communications between these three parties are protected by TLS

We also want to reduce the chance that other applications can request an
extension on validity, and hence we have the following setup.

1. Create a special client scope called `exp-extension`. This client scope will
   contain the exp-mapper mapper as the only mapper, for easy composition with
   other client scopes.
2. Configure `exp-mapper` to only permit keypress as the client. This way, even
   if other applications request the `exp-extension` scope, the `exp` extension
   will not be granted. (The original token will be returned for other clients)
3. Disable "Full Scope Allowed" for your clients.
4. Configure `exp-extension` as an "Assigned Optional Client Scope" only for
   the client you want to allow `exp-extension` to be used. We *don't* use
   "Assigned Default Client Scopes" because we don't want `exp-extension` to be
   applied by default. (Even if it were applied by default, only keypress would
   get the extension, since that was configured in the mapper itself)
5. Configure Token Exchange for your client to permit keypress to exchange
   tokens. (This allows keypress to exchange *any* token, not just keypress's
   tokens, for the target client, but I can't seem to make keycloak permit only
   a certain role guaranteed only to be available in a keypress token.)

### Getting a long-lived access token

+ Keypress will exchange the its own access token (keypress's token) for an access token with an extended expiration time
+ Keypress will then issue a randomly generated API key, and set the access token at the kong plugin

### Listing access tokens

+ Keypress should be able to list access tokens, grouped by application that it is protecting

### Revoking access tokens

+ Keypress will call the revoke access token endpoint of the Kong plugin, and remove the API key from its own database

## Kong plugin

### Set access tokens

This is an API endpoint that will receive an (API key, access token) pair, and write it to a table in the Kong database

### Revoke access tokens

This is an API endpoint that will receive an API key remove it from the table in the Kong database

### Proxy

This will read the API Key from the `X-API-KEY` header, and look it up in the Kong database.

If it exists, allow routing to continue using the matching long-lived access token.

If it does not exist, reject the user with a HTTP error code

> We don't need to check that the access token matches the requested path,
>   because the resource server will validate that it is the intended audience
>   of the access token
