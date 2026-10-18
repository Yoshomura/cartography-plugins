"""Level 1 example: System Context of an online shop.

One box per software system: the shop in scope, the people who use it, and the systems it depends
on. Containers and sub-domains live in the Container diagram (examples/containers_level2.py).
The same diagram in Mermaid: examples/context_level1.mmd.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from c4lib import Doc

d = Doc("System Context diagram for Online shop", 1760, 1240)
CARDS, SEGS = [], []


def card(l, t, w, h, kind, name, typ, desc):
    d.card(l, t, w, h, kind, name, typ, desc); CARDS.append((name, l, t, w, h))


def route(pts, head=True, dashed=False):
    d.route(pts, head=head, dashed=dashed)
    SEGS.extend((x1, y1, x2, y2) for (x1, y1), (x2, y2) in zip(pts, pts[1:]))


L = d.label

d.title(64, 64, "C4 · Level 1 · System Context · Online shop", "System Context diagram for Online shop",
        "Who uses the online shop and which systems it depends on. One box per software system; containers and sub-domains live in the Container diagram.")

# ---------------- system in scope
card(704, 300, 320, 760, "system", "Online shop", "Software System", "Product catalog, shopping cart, ordering, payment and shipping follow-up")
# ---------------- left: the people
card(64, 400, 240, 130, "person", "Customer", "Person", "Browses the catalog, places and follows orders")
card(64, 820, 240, 130, "person", "Back-office operator", "Person", "Manages products, prices and refunds")
# ---------------- right: the systems it depends on
card(1424, 300, 240, 110, "external", "Identity provider", "Software System", "Customer sign-up and sign-in")
card(1424, 460, 240, 130, "external", "Payment service provider", "Software System", "Card payments and refunds")
card(1424, 640, 240, 110, "external", "Carrier API", "Software System", "Shipment booking and parcel tracking")
card(1424, 800, 240, 110, "external", "Email service", "Software System", "Transactional emails")
card(1424, 950, 240, 110, "external", "Data warehouse", "Software System", "Sales reporting")

# ---------------- people
route([(304, 465), (703, 465)]);    L(330, 420, 340, "Browses products, places and follows orders [HTTPS]")
route([(304, 885), (703, 885)]);    L(330, 840, 340, "Manages catalog, prices and refunds [HTTPS]")
# ---------------- systems it depends on
route([(1024, 355), (1423, 355)]);  L(1050, 318, 340, "Authenticates customers [OIDC]")
route([(1024, 505), (1423, 505)]);  L(1050, 468, 340, "Charges and refunds payments [HTTPS]")
route([(1424, 555), (1025, 555)], dashed=True); L(1050, 566, 340, "Notifies payment results [webhook]")
route([(1024, 695), (1423, 695)]);  L(1050, 658, 340, "Books shipments, tracks parcels [HTTPS]")
route([(1024, 855), (1423, 855)]);  L(1050, 818, 340, "Sends order and shipping emails [HTTPS]")
route([(1024, 1005), (1423, 1005)]); L(1050, 968, 340, "Exports orders and sales every night [file export]")

d.legend(64, 1120, [("person", "Person"), ("system", "Software system in scope"), ("external", "Other software system"),
                    ("sync", "Relationship [protocol]"), ("async", "Message [event / webhook]")])
d.footer("C4 · L1 · Online shop")
print(d.write("Context.html"))
print(d.write_drawio("Context.drawio"))

# ---------------- geometry check: no segment may run through a card
def through(s, c):
    x1, y1, x2, y2 = s; _, l, t, w, h = c
    xa, xb = sorted((x1, x2)); ya, yb = sorted((y1, y2))
    return xb > l + 1 and xa < l + w - 1 and yb > t + 1 and ya < t + h - 1


bad = [(s, c[0]) for s in SEGS for c in CARDS if through(s, c)]
print("cards", len(CARDS), "segments", len(SEGS), "card-crossings", len(bad))
for b in bad:
    print("  THROUGH", b)
