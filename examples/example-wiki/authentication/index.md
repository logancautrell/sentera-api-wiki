---
url: https://admin.sentera.com/api/docs/authentication/index.html
kind: page
title: Authentication
description: In order to use FieldAgent's GraphQL API, a client application must first
  authenticate with FieldAgent to obtain an access token that should be sent in theAuthorizationheader
  of GraphQL API HTTP requests. This is done using theOAuth2 authorization code grant
  flow.
parent: null
children: []
tags: ['authentication', 'core', 'howto']
last_fetched: '2026-05-31T14:18:04Z'
---

# Authentication

**Description:** In order to use FieldAgent's GraphQL API, a client application must first authenticate with FieldAgent to obtain an access token that should be sent in theAuthorizationheader of GraphQL API HTTP requests. This is done using theOAuth2 authorization code grant flow.

## Authentication

In order to use FieldAgent's GraphQL API, a client application must first authenticate with FieldAgent to obtain an access token that should be sent in the Authorization header of GraphQL API HTTP requests. This is done using the OAuth2 authorization code grant flow .

But before a client can authenticate with FieldAgent via OAuth2, it must be registered with Sentera. When you register your client application, Sentera will provide you with a client ID and a client secret, which you'll use during the authentication process. To register your client, send an email to api-support@sentera.com requesting assistance. We will work with you to get your client application set up within FieldAgent, so it can authenticate with FieldAgent and use its GraphQL API to access user data.


### OAuth2 Authorization Code Grant Flow

The sequence diagram below illustrates the OAuth2 authorization code grant flow:

```
sequenceDiagram
    autonumber
    actor Browser
    Browser->>+Client App:Click Login with FieldAgent button
    Client App-->>-Browser:Redirect...
    Browser->>+FieldAgent Authentication:...to FieldAgent Login
    FieldAgent Authentication-->>-Browser:Returns FieldAgent Login form
    Browser->>+FieldAgent Authentication:Submit FieldAgent credentials
    Note right of FieldAgent Authentication:authenticate user
    FieldAgent Authentication-->>-Browser:Returns approve/deny access form
    Browser->>+FieldAgent Authentication:Submit approval
    FieldAgent Authentication-->>-Browser:Redirect...
    Browser->>+Client App:...with code
    Client App->>+FieldAgent Authentication:Request access token
    Note right of Client App:request includes:grant type='authorization_code', client id, client secret,code & redirect URI
    Note right of FieldAgent Authentication:validate:client id, client secret & code
    FieldAgent Authentication-->>Client App:Returns access token & refresh token
    Client App->>+FieldAgent GraphQL API:Request user's fields
    Note right of Client App:request includes:access token
    Note left of FieldAgent GraphQL API:validate:access token
    FieldAgent GraphQL API-->>-Client App:Returns user's fields
    Client App-->>-Browser:Returns user's fields
```

If you prefer to just dive into some code and get going, there is a working code example that demonstrates this flow available at GitHub .


### Requesting the Grant

The flow above starts by making a request to the /oauth/authorize endpoint in FieldAgent and providing required information as query string parameters.

To try this yourself, open a browser window and enter the following URL, replacing the stand-in values with actual values: https://api.sentera.com/oauth/authorize?client_id=XXXX&response_type=code&redirect_uri=YYYY&scope=ZZZZ

- `XXXX`is the client ID you received when you registered your client application with Sentera.
- `YYYY`is the callback URI you provided when you registered your client application with Sentera. The value you provide here must match the value you registered exactly or your request will be rejected.
- `ZZZZ`is the scope you provided when you registered your client application with Sentera.

The values you supply in your URL must match the values you provided when you registered exactly, or your request will be rejected.

Once you log into FieldAgent and grant access to your application, the callback URI will be triggered and will provide the authorization code in the code query string parameter. Grab that value, you'll use it in the next step.


### Getting an Access Token

Use the /oauth/token endpoint in FieldAgent to exchange the authorization code for an access token.

To try this yourself, use the following cURL command to POST a request to /oauth/token , replacing the stand-in values with actual values:

```
curl -i --request POST \
  --header 'Content-Type: application/json' \
  --data '{ "grant_type": "authorization_code", "client_id": "XXXX", "client_secret": "YYYY", "redirect_uri": "ZZZZ", "code": "CCCC" }' \
  https://api.sentera.com/oauth/token
```

- `XXXX`is the client ID you received when you registered your client application with Sentera.
- `YYYY`is the client secret you received when you registered your client application with Sentera.
- `ZZZZ`is the callback URI you provided when you registered your client application with Sentera. The value you provide here must match the value you registered exactly or your request will be rejected.
- `CCCC`is the authentication code you received in the previous step.

Example response

```
HTTP/1.1 200 OK
{
  "access_token": "AeLRx-np4pdGRJWezDp8mh-VyqQD-yopEkbfLqmqNwg",
  "token_type": "Bearer",
  "expires_in": 28800,
  "refresh_token": "68OCxLVGMGcIMoHBvbHh0avldx9VAOcFNbekQMtI8Vw",
  "scope": "read_fields",
  "created_at": 1691152104
}
```


### Refreshing an Access Token

Use the /oauth/token endpoint in FieldAgent to refresh your access token when it has expired.

To try this yourself, use the following cURL command to POST a request to /oauth/token , replacing the stand-in values with actual values:

```
curl -i --request POST \
  --header 'Content-Type: application/json' \
  --data '{ "grant_type": "refresh_token", "client_id": "XXXX", "client_secret": "YYYY", "redirect_uri": "ZZZZ", "refresh_token": "RRRR" }' \
  https://api.sentera.com/oauth/token
```

- `XXXX`is the client ID you received when you registered your client application with Sentera.
- `YYYY`is the client secret you received when you registered your client application with Sentera.
- `ZZZZ`is the callback URI you provided when you registered your client application with Sentera. The value you provide here must match the value you registered exactly or your request will be rejected.
- `RRRR`is the refresh token you received in the previous step.

Example response

```
HTTP/1.1 200 OK
{
  "access_token": "kQn3NV8sJK7rqLyqYIf_r9qncuEylSSPntiKlSkreR8",
  "token_type": "Bearer",
  "expires_in": 28800,
  "refresh_token": "9kBfBKwkWUp9E1yomVNCI13P05biEYfqwI43zcGlhgA",
  "scope": "read_fields",
  "created_at": 1691152582
}
```


### Revoking Access

Use the /oauth/revoke endpoint to revoke an access token or a refresh token.

To try this yourself, use the following cURL command to POST a request to /oauth/revoke , replacing stand-in values with actual values:

```
curl -i --request POST \
  --header 'Content-Type: application/json' \
  --data '{ "token_type_hint": "access_token", "client_id": "XXXX", "client_secret": "YYYY", "token": "AAAA" }' \
  https://api.sentera.com/oauth/revoke
```

- `XXXX`is the client ID you received when you registered your client application with Sentera.
- `YYYY`is the client secret you received when you registered your client application with Sentera.
- `AAAA`is the access token you want to revoke. This only revokes a single access token. It does not affect the refresh token.

Example response

```
HTTP/1.1 200 OK
{}
```

You can also revoke a refresh token. Once the refresh token has been revoked, it cannot be used to obtain more access tokens.

Try the following to revoke a refresh token:

```
curl -i --request POST \
  --header 'Content-Type: application/json' \
  --data '{ "token_type_hint": "refresh_token", "client_id": "XXXX", "client_secret": "YYYY", "token": "RRRR" }' \
  https://api.sentera.com/oauth/revoke
```

- `RRRR`is the refresh token you want to revoke.

Example response

```
HTTP/1.1 200 OK
{}
```


### Legacy Authentication

For details on using the legacy authentication endpoint, click here . Not to be used with new client applications.

---
*Generated by sentera-wiki-builder (structured extraction, no LLM)*
