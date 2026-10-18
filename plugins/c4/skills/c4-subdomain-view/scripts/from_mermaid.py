"""Model of a sub-domain view (JSON) read from an existing Mermaid view.

    python from_mermaid.py <view.md> > model.json

Reads the ```mermaid block written by subdomain_view.py (or by hand in the same layout): the focus
band, its containers, the externals, the other sub-domains (a `_pub` alias is the top copy of the
same sub-domain), the buses, the messages (a Rel touching a bus) and the direct links, plus the
Notes and Open questions sections. A message group is split into one name per bullet only when
every item is a complete message name; a compressed list ("provider_meeting, race, … _changed")
stays one bullet, so no name is ever invented.
"""
import json, re, sys

KINDS = r"event|command|Redis pub/sub|Redis key"
NAME = re.compile(r"^[a-z][a-z0-9_*:{},.-]*_[a-z0-9_*:{}.-]*$")


def args_of(line):
    return re.findall(r'"([^"]*)"', line)


def names_of(text):
    """Bullets of one message group."""
    out = []
    for part in [p.strip() for p in text.split(";") if p.strip()]:
        items = [i.strip() for i in part.split(",")]
        if all(NAME.match(i) for i in items):
            out += items
        else:
            out.append(part)
    return out


def groups_of(label, tech):
    kinds = [k.strip() for k in tech.split(",")]
    if len(kinds) == 1:
        return [dict(kind=kinds[0], names=names_of(label))]
    groups, pending = [], []
    for part in [p.strip() for p in label.split(";")]:
        m = re.search(rf"\s*\(({KINDS})\)$", part)
        if m:
            pending.append(part[:m.start()])
            groups.append(dict(kind=m.group(1), names=names_of("; ".join(pending))))
            pending = []
        else:
            pending.append(part)
    if pending:
        raise SystemExit(f"message without kind: {label}")
    return groups


def main(path):
    md = open(path, encoding="utf-8").read()
    code = re.search(r"```mermaid\n(.*?)```", md, re.S).group(1)
    model = dict(system=None, focus=None, date="", containers=[], externals=[], subdomains=[], public_bus=None,
                 private_buses=[], messages=[], links=[], notes=[], open_questions=[])
    m = re.search(r"title .*?(\d{4}-\d{2}-\d{2})", code)
    if m:
        model["date"] = m.group(1)
    buses, sds, stack, alias = {}, {}, [], {}
    for line in code.splitlines():
        s = line.strip()
        b = re.match(r"(System_Boundary|Boundary)\((\w+),", s)
        if b:
            a = args_of(s)
            stack.append((b.group(2), a[1] if len(a) > 1 else ""))
            if b.group(1) == "System_Boundary" and not model["system"]:
                model["system"] = a[0]
            if len(a) > 1 and a[1] == "Sub-domain":
                model["focus"] = a[0]
            continue
        if s == "}":
            stack.pop()
            continue
        e = re.match(r"(System_Ext|ContainerQueue_Ext|ContainerQueue|ContainerDb|Container_Ext|Container)\((\w+),", s)
        if not e:
            continue
        macro, ident = e.groups()
        a = args_of(s)
        in_focus = bool(stack) and stack[-1][1] == "Sub-domain"
        if macro == "System_Ext":
            model["externals"].append(dict(id=ident, name=a[0], desc=a[1] if len(a) > 1 else ""))
        elif macro == "ContainerQueue_Ext":
            model["public_bus"] = dict(id=ident, name=a[0], tech=a[1], desc=a[2])
            buses[ident] = "public"
        elif macro == "ContainerQueue":
            model["private_buses"].append(dict(id=ident, name=a[0], tech=a[1], desc=a[2]))
            buses[ident] = "private"
        elif len(a) > 1 and a[1] == "Sub-domain" and not in_focus:
            sd = ident[:-4] if ident.endswith("_pub") else ident
            alias[ident] = sd
            if sd not in sds:
                sds[sd] = dict(id=sd, name=a[0], purpose=a[2] if len(a) > 2 else "")
        elif in_focus:
            kind = {"ContainerDb": "store", "Container_Ext": "unexplored"}.get(macro, "container")
            model["containers"].append(dict(id=ident, name=a[0], tech=a[1], desc=a[2], kind=kind))
    model["subdomains"] = list(sds.values())
    cache = None
    for r in re.finditer(r'^\s*Rel\((\w+),\s*(\w+),\s*"([^"]*)",\s*"([^"]*)"\)', code, re.M):
        a, b, label, tech = r.groups()
        a, b = alias.get(a, a), alias.get(b, b)
        if a in buses or b in buses:
            groups = groups_of(label, tech)
            # a Redis key is a distributed cache access, not a message: it becomes a link to the cache store
            for g in [g for g in groups if g["kind"] == "Redis key"]:
                if cache is None:
                    cache = dict(id="distcache", name="Distributed cache", tech="Azure Cache for Redis",
                                 desc="Cache keys shared by the sub-domains", kind="store")
                    model["containers"].append(cache)
                elem, verb = (a, "Write") if b in buses else (b, "Read")
                for n in g["names"]:
                    model["links"].append({"from": elem, "to": "distcache", "label": f"{verb} {n}", "protocol": "Redis"})
            groups = [g for g in groups if g["kind"] != "Redis key"]
            if groups:
                model["messages"].append(dict(**{"from": a, "to": b}, groups=groups))
        else:
            model["links"].append(dict(**{"from": a, "to": b}, label=label, protocol=tech))
    notes = re.search(r"## Notes\n(.*?)(?=\n## |\Z)", md, re.S)
    if notes:
        model["notes"] = [n.strip()[2:].replace("\n  ", " ") for n in re.split(r"\n(?=- )", notes.group(1).strip()) if n.strip().startswith("- ")]
    qs = re.search(r"## Open questions[^\n]*\n(.*?)(?=\n## |\Z)", md, re.S)
    if qs:
        model["open_questions"] = [re.sub(r"\s+", " ", q.split(". ", 1)[1]) for q in re.split(r"\n(?=\d+\. )", qs.group(1).strip()) if re.match(r"\d+\. ", q)]
    json.dump(model, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main(sys.argv[1])
