# Sub-domain view model

One JSON file per sub-domain view, `models/<sub-domain>.json`. Every fact in it has a source (code,
infrastructure, a relations catalogue); a missing fact goes to `open_questions`, never into a guessed
field. The complete example is `../examples/ordering.json`; its shape:

```json
{
  "system": "Online shop",
  "focus": "Ordering",
  "date": "",
  "containers": [
    {"id": "orderingapi", "name": "ordering-api", "tech": "Container, REST API",
     "desc": "Places, cancels and returns orders", "kind": "container"},
    {"id": "ordersdb", "name": "Orders DB", "tech": "PostgreSQL",
     "desc": "Orders, order lines, status history", "kind": "store"}
  ],
  "externals": [{"id": "apigateway", "name": "API gateway", "desc": "Exposes the shop APIs to the web and mobile apps"}],
  "subdomains": [{"id": "payment", "name": "Payment", "purpose": "Charges and refunds"}],
  "public_bus": {"id": "publicbus", "name": "Enterprise event bus", "tech": "Apache Kafka", "techno": "KAFKA",
                 "desc": "Topics shared with the other systems"},
  "private_buses": [{"id": "privatebus", "name": "Domain event bus", "tech": "AWS SNS to SQS",
                     "desc": "Events and commands between the sub-domains"}],
  "messages": [
    {"from": "orderingapi", "to": "privatebus", "groups": [{"kind": "event", "names": ["order_submitted"]}]},
    {"from": "privatebus", "to": "payment", "groups": [{"kind": "command", "names": ["charge_order"]}]}
  ],
  "links": [{"from": "orderingapi", "to": "ordersdb", "label": "Insert orders, read order history", "protocol": "SQL"}],
  "notes": ["…"],
  "open_questions": ["…"]
}
```

| Field | Rule |
|---|---|
| `system` | the software system the sub-domain belongs to; it names the system boundary and the title |
| `focus` | the sub-domain name, as on its band |
| `date` | optional: the date the facts were collected, shown in the lead of the draw.io and the Mermaid title |
| `containers[].kind` | `container`, `store` (database, drawn below the band, one link band → store), `datasink` (job exporting one store to a data platform, drawn below that store) or `unexplored` (source not explored, drawn grey) |
| `externals` | systems outside the system in scope; on top when they only talk through the public bus, in the right column when they have a direct link |
| `subdomains` | the other sub-domains, one entry each; the generator draws one on top when it uses the public bus, at the bottom when it uses a private bus or a direct link, both when both |
| `public_bus` | the bus shared with the other systems, or `null` when the sub-domain does not use one |
| `private_buses` | the private bus and, when used, a Redis pub/sub; drawn side by side |
| `…bus.techno` | optional: the technology shown in the lane headers (`SNS`, `REDIS`, `KAFKA`…); read from `tech` when absent (`SNS` in it gives SNS, `Redis` gives REDIS, else `tech` itself) |
| `messages` | one entry per producer → bus or bus → consumer; an end is a bus, the other an element. `kind`: `event`, `command`, `Redis pub/sub`. A Redis key is not a message: it is a link to the distributed cache store (`protocol` `Redis`). Entries of the same element, bus and direction merge into one lane |
| `messages[].groups[].names` | one bullet each; an exact message name, or a compressed list kept as one bullet until the exact names are known |
| `links` | direct links (HTTP, SQL, NoSQL, Redis, file export…): `label` is the verb phrase, `protocol` the `[…]` |
| `notes`, `open_questions` | written into a new Mermaid view; an existing view keeps its own sections |
