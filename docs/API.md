# API reference

The running FastAPI app is the authoritative source for request/response schemas: open `/docs` or `/openapi.json`. API routes are mounted under `/api/v1`; health is at `/health`.

Most routes require a bearer access token obtained from authentication. Successful JSON responses generally use `{ "success": true, "data": ... }`; paginated routes also include `meta`. Error responses use a structured `error` object. Endpoints returning `204` have no response body.

## Route groups

| Prefix | Implemented operations |
| --- | --- |
| `/auth` | Register, login, refresh, logout, forgot/reset/change password, verify email |
| `/users` | Read/deactivate own account; administrator user listing |
| `/profile` | Read/update profile, replace allergies and conditions |
| `/scans` | Upload label, list/history stats, read/status, edit notes, soft delete, restore, cancel; admin cleanup/orphan routes |
| `/ocr` | Process OCR, read processing status and result |
| `/parser` | Parse ingredient text |
| `/kg` | Import dataset; search ingredients, products, allergens, and additives |
| `/medical` | Read rule-relevant profile, evaluate supplied product information, evaluation history |
| `/recommendation` | Generate recommendations and read recommendation history |

## Example

```http
GET /api/v1/profile/me HTTP/1.1
Host: localhost:8000
Authorization: Bearer <access-token>
```

For multipart scan upload, use the schema shown for `POST /api/v1/scans/upload` in Swagger UI. Upload constraints and accepted image formats are configured in backend settings. Do not use real personal health data in public examples.

## Notes

- Routes and schemas may evolve; prefer the live OpenAPI document over copied request examples.
- The product evaluation is rule-based and depends on the available dataset and profile data; it is not medical diagnosis.
- Some administrative routes require an administrator account.
