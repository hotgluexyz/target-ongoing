# target-ongoing

`target-ongoing` is a Singer target for **Ongoing**, built with the [Hotglue Singer SDK](https://github.com/hotgluexyz/HotglueSingerSDK) (`TargetHotglue`, HTTP sinks, SDK authenticators).

This project was generated from the Hotglue target cookiecutter with:

| Option | Value |
|--------|--------|
| `auth_method` | `Basic Auth` |
| `sinks` | `Items | record, PurchaseOrders | record` |
| `base_url` | `https://api.ongoingsystems.se` |

## Project layout

| Path | Role |
|------|------|
| `target_ongoing/target.py` | `TargetOngoing` — config schema, `SINK_TYPES`, optional `default_sink_class` and `access_token_support` |
| `target_ongoing/client.py` | `OngoingSink` base class, `RecordSink` / `BatchSink` stubs, `authenticator` |
| `target_ongoing/sinks.py` | Per-stream sink classes (`FallbackSink` or named `*Sink` classes) |
| `target_ongoing/auth.py` | Present only when generated with **OAuth2** (removed by cookiecutter hook otherwise) |
| `.secrets/config.json` | Sample config matching your `auth_method` |

## Configuration

Settings are defined in `config_jsonschema` on `TargetOngoing` in `target_ongoing/target.py`.
For this project (**Basic Auth**), config includes `username`, `password`,
`warehouse_name`, `goods_owner_id`, and `warehouse_id`. `api_server` defaults to `api`.

Inspect the live schema:

```bash
target-ongoing --about
target-ongoing --about --format=markdown
```

Local secrets: edit `.secrets/config.json` (shape matches `auth_method` above).

## Authentication

| `auth_method` | Implementation |
|---------------|----------------|
| **OAuth2** | `OngoingAuthenticator` in `auth.py`; `TargetOngoing.access_token_support()` returns the authenticator class and token URL (replace the TODO endpoint in `target.py`). |
| **Bearer Token** | `BearerTokenAuthenticator` in `client.py` |
| **Basic Auth** | `BasicAuthenticator` with `username` / `password` |
| **API Key** | `ApiAuthenticator` with configurable header name/prefix |

HTTP calls use `base_url` on `OngoingSink` (`https://api.ongoingsystems.se` unless you change it in `client.py`).

## Sinks

Sinks are declared at scaffold time as `StreamName | record` or `StreamName | batch`, comma-separated.

Generated with: `Items | record, PurchaseOrders | record`

Both sinks use Ongoing's idempotent `PUT` endpoints. `Items` creates or updates
`/articles`; `PurchaseOrders` creates or updates `/purchaseOrders`. The target
maps QuickBooks `Name` to Ongoing `articleNumber`, because QuickBooks purchase
order line references point to the item name; optional QuickBooks SKU is retained
as Ongoing `productCode`.

Shared HTTP behavior lives in `client.py` (`OngoingRecordSink` / `OngoingBatchSink` as generated).

## Usage

```bash
target-ongoing --version
target-ongoing --help
tap-smoke-test | target-ongoing --config /path/to/config.json
```

## Developer setup

Prerequisites: Python 3.10+, [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run pytest
uv run target-ongoing --help
tox -e lint    # ruff check + format
```

For implementation notes and conventions, see `AGENTS.md` (or `CLAUDE.md` if that was selected at generation).

## References

- [Hotglue Singer SDK](https://github.com/hotgluexyz/HotglueSingerSDK)
