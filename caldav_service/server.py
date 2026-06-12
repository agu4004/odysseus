"""
Minimal CalDAV server — Odysseus personal use.

RFC 4791 subset: principal discovery, calendar-home-set, PROPFIND (depth 0/1),
REPORT (calendar-query time-filter + calendar-multiget), MKCALENDAR,
GET, HEAD, PUT, DELETE, OPTIONS.

Storage : flat .ics files under  CALDAV_DATA_DIR/{user}/{cal}/{uid}.ics
Auth    : HTTP Basic — env CALDAV_USER / CALDAV_PASSWORD
Port    : 5232 (default CalDAV)
"""

import base64
import hashlib
import logging
import os
import re
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)

# ── namespaces ───────────────────────────────────────────────────────────────
D = "DAV:"
C = "urn:ietf:params:xml:ns:caldav"
ET.register_namespace("D", D)
ET.register_namespace("C", C)

# ── config ───────────────────────────────────────────────────────────────────
DATA   = Path(os.environ.get("CALDAV_DATA_DIR", "/data/calendars"))
USER   = os.environ.get("CALDAV_USER", "admin")
PASSWD = os.environ.get("CALDAV_PASSWORD", "admin")

# ── XML helpers ──────────────────────────────────────────────────────────────

def d(local: str) -> str:
    return f"{{{D}}}{local}"

def c(local: str) -> str:
    return f"{{{C}}}{local}"

def xml_doc(root: ET.Element, status: int = 207) -> Response:
    body = '<?xml version="1.0" encoding="utf-8"?>' + ET.tostring(root, encoding="unicode")
    return Response(body, status_code=status, media_type="application/xml; charset=utf-8")

def ms() -> ET.Element:
    return ET.Element(d("multistatus"), {"xmlns:D": D, "xmlns:C": C})

def resp_with_prop(href: str) -> tuple[ET.Element, ET.Element]:
    """Return (response_el, prop_el) with a pre-wired 200 propstat."""
    r = ET.Element(d("response"))
    ET.SubElement(r, d("href")).text = href
    ps = ET.SubElement(r, d("propstat"))
    prop = ET.SubElement(ps, d("prop"))
    ET.SubElement(ps, d("status")).text = "HTTP/1.1 200 OK"
    return r, prop

def rtype(*tags: str) -> ET.Element:
    rt = ET.Element(d("resourcetype"))
    for t in tags:
        ET.SubElement(rt, t)
    return rt

# ── auth ─────────────────────────────────────────────────────────────────────

def auth_ok(req: Request) -> bool:
    h = req.headers.get("authorization", "")
    if not h.lower().startswith("basic "):
        return False
    try:
        u, p = base64.b64decode(h[6:]).decode("utf-8", "replace").split(":", 1)
        return u == USER and p == PASSWD
    except Exception:
        return False

def unauth() -> Response:
    return Response(status_code=401, headers={"WWW-Authenticate": 'Basic realm="caldav"'})

# ── storage ──────────────────────────────────────────────────────────────────

def cal_dir(user: str, cal: str) -> Path:
    return DATA / user / cal

def ev_file(user: str, cal: str, name: str) -> Path:
    return cal_dir(user, cal) / name

def ensure_cal(user: str, cal: str = "default") -> None:
    cal_dir(user, cal).mkdir(parents=True, exist_ok=True)

def list_cals(user: str) -> list[str]:
    base = DATA / user
    if not base.exists():
        return []
    return [p.name for p in base.iterdir() if p.is_dir() and not p.name.startswith(".")]

def list_events(user: str, cal: str) -> list[Path]:
    d_ = cal_dir(user, cal)
    if not d_.exists():
        return []
    return [p for p in d_.iterdir() if p.suffix == ".ics"]

def etag(data: bytes) -> str:
    return '"' + hashlib.md5(data).hexdigest() + '"'

def cal_display(user: str, cal: str) -> str:
    meta = cal_dir(user, cal) / ".meta"
    if meta.exists():
        for line in meta.read_text().splitlines():
            if line.startswith("displayname="):
                return line.split("=", 1)[1].strip()
    return cal

# ── iCal helpers ─────────────────────────────────────────────────────────────

_DT_RES = [
    (re.compile(r"(\d{8}T\d{6}Z)$"),  "%Y%m%dT%H%M%SZ"),
    (re.compile(r"(\d{8}T\d{6})$"),   "%Y%m%dT%H%M%S"),
    (re.compile(r"(\d{8})$"),          "%Y%m%d"),
]

def _parse_ical_dt(raw: str) -> datetime:
    raw = raw.strip()
    for pat, fmt in _DT_RES:
        if pat.match(raw):
            dt = datetime.strptime(raw, fmt)
            return dt.replace(tzinfo=timezone.utc) if raw.endswith("Z") else dt
    raise ValueError(f"unrecognised dt: {raw!r}")

def event_in_range(ics: str, start: datetime | None, end: datetime | None) -> bool:
    if start is None and end is None:
        return True
    m = re.search(r"^DTSTART[^:]*:(.+)$", ics, re.MULTILINE)
    if not m:
        return True
    try:
        dt = _parse_ical_dt(m.group(1))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        # generous ±1 day window for all-day / floating times
        if start and dt < start - timedelta(days=1):
            return False
        if end and dt > end + timedelta(days=1):
            return False
        return True
    except Exception:
        return True

# ── REPORT body parsing ──────────────────────────────────────────────────────

def parse_time_range(body: bytes) -> tuple[datetime | None, datetime | None]:
    try:
        root = ET.fromstring(body)
        for el in root.iter(c("time-range")):
            s, e = el.get("start"), el.get("end")
            fmt = "%Y%m%dT%H%M%SZ"
            return (
                datetime.strptime(s, fmt).replace(tzinfo=timezone.utc) if s else None,
                datetime.strptime(e, fmt).replace(tzinfo=timezone.utc) if e else None,
            )
    except Exception:
        pass
    return None, None

def is_multiget(body: bytes) -> bool:
    try:
        return ET.fromstring(body).tag == c("calendar-multiget")
    except Exception:
        return False

def multiget_hrefs(body: bytes) -> list[str]:
    try:
        return [el.text for el in ET.fromstring(body).findall(d("href")) if el.text]
    except Exception:
        return []

# ── handlers ─────────────────────────────────────────────────────────────────

def handle_options(_req: Request) -> Response:
    return Response(status_code=200, headers={
        "Allow": "OPTIONS, GET, HEAD, PUT, DELETE, PROPFIND, MKCALENDAR, REPORT",
        "DAV": "1, 2, 3, calendar-access",
    })


async def handle_propfind(req: Request, parts: list[str]) -> Response:
    depth = req.headers.get("depth", "0")
    root = ms()

    # ── / → current-user-principal ────────────────────────────────────────
    if not parts or parts == [".well-known", "caldav"]:
        r, prop = resp_with_prop("/")
        cup = ET.SubElement(prop, d("current-user-principal"))
        ET.SubElement(cup, d("href")).text = f"/principals/{USER}/"
        root.append(r)
        return xml_doc(root)

    # ── /principals/{user}/ ────────────────────────────────────────────────
    if parts[0] == "principals":
        user = parts[1] if len(parts) > 1 else USER
        href = f"/principals/{user}/"
        r, prop = resp_with_prop(href)
        prop.append(rtype(d("collection"), d("principal")))
        ET.SubElement(prop, d("displayname")).text = user
        chs = ET.SubElement(prop, c("calendar-home-set"))
        ET.SubElement(chs, d("href")).text = f"/calendars/{user}/"
        cup = ET.SubElement(prop, d("current-user-principal"))
        ET.SubElement(cup, d("href")).text = href
        root.append(r)
        return xml_doc(root)

    # ── /calendars/… ──────────────────────────────────────────────────────
    if parts[0] == "calendars":
        user = parts[1] if len(parts) > 1 else USER
        cal  = parts[2] if len(parts) > 2 else None
        name = parts[3] if len(parts) > 3 else None

        # event resource
        if name:
            ep = ev_file(user, cal, name)
            if not ep.exists():
                return Response(status_code=404)
            data = ep.read_bytes()
            r, prop = resp_with_prop(f"/calendars/{user}/{cal}/{name}")
            ET.SubElement(prop, d("getetag")).text = etag(data)
            ET.SubElement(prop, d("getcontenttype")).text = "text/calendar; charset=utf-8"
            prop.append(rtype())
            root.append(r)
            return xml_doc(root)

        # calendar collection
        if cal:
            href = f"/calendars/{user}/{cal}/"
            r, prop = resp_with_prop(href)
            prop.append(rtype(d("collection"), c("calendar")))
            ET.SubElement(prop, d("displayname")).text = cal_display(user, cal)
            sccs = ET.SubElement(prop, c("supported-calendar-component-set"))
            ET.SubElement(sccs, c("comp"), {"name": "VEVENT"})
            root.append(r)
            if depth == "1":
                for ep in list_events(user, cal):
                    data = ep.read_bytes()
                    er, ep_prop = resp_with_prop(f"/calendars/{user}/{cal}/{ep.name}")
                    ET.SubElement(ep_prop, d("getetag")).text = etag(data)
                    ET.SubElement(ep_prop, d("getcontenttype")).text = "text/calendar; charset=utf-8"
                    ep_prop.append(rtype())
                    root.append(er)
            return xml_doc(root)

        # calendar home
        ensure_cal(user)   # seed default calendar on first visit
        href = f"/calendars/{user}/"
        r, prop = resp_with_prop(href)
        prop.append(rtype(d("collection")))
        ET.SubElement(prop, d("displayname")).text = user
        chs = ET.SubElement(prop, c("calendar-home-set"))
        ET.SubElement(chs, d("href")).text = href
        root.append(r)
        if depth == "1":
            for cal_name in list_cals(user):
                cr, cprop = resp_with_prop(f"/calendars/{user}/{cal_name}/")
                cprop.append(rtype(d("collection"), c("calendar")))
                ET.SubElement(cprop, d("displayname")).text = cal_display(user, cal_name)
                sccs = ET.SubElement(cprop, c("supported-calendar-component-set"))
                ET.SubElement(sccs, c("comp"), {"name": "VEVENT"})
                root.append(cr)
        return xml_doc(root)

    return Response(status_code=404)


async def handle_report(req: Request, parts: list[str]) -> Response:
    if len(parts) < 3 or parts[0] != "calendars":
        return Response(status_code=400)
    user, cal = parts[1], parts[2]
    body = await req.body()
    root = ms()

    if is_multiget(body):
        for href in multiget_hrefs(body):
            name = href.rstrip("/").split("/")[-1]
            ep   = ev_file(user, cal, name)
            if ep.exists():
                data = ep.read_bytes()
                r, prop = resp_with_prop(href)
                ET.SubElement(prop, d("getetag")).text = etag(data)
                ET.SubElement(prop, c("calendar-data")).text = data.decode("utf-8", "replace")
                root.append(r)
    else:
        start, end = parse_time_range(body)
        for ep in list_events(user, cal):
            text = ep.read_bytes()
            if event_in_range(text.decode("utf-8", "replace"), start, end):
                href = f"/calendars/{user}/{cal}/{ep.name}"
                r, prop = resp_with_prop(href)
                ET.SubElement(prop, d("getetag")).text = etag(text)
                ET.SubElement(prop, c("calendar-data")).text = text.decode("utf-8", "replace")
                root.append(r)

    return xml_doc(root)


def handle_mkcalendar(_req: Request, parts: list[str]) -> Response:
    if len(parts) < 3:
        return Response(status_code=400)
    ensure_cal(parts[1], parts[2])
    log.info("MKCALENDAR /calendars/%s/%s/", parts[1], parts[2])
    return Response(status_code=201)


def handle_get(req: Request, parts: list[str]) -> Response:
    if len(parts) < 4 or parts[0] != "calendars":
        return Response(status_code=404)
    ep = ev_file(parts[1], parts[2], parts[3])
    if not ep.exists():
        return Response(status_code=404)
    data = ep.read_bytes()
    headers = {"ETag": etag(data), "Content-Type": "text/calendar; charset=utf-8"}
    if req.method == "HEAD":
        return Response(status_code=200, headers=headers)
    return Response(content=data, status_code=200, headers=headers)


async def handle_put(req: Request, parts: list[str]) -> Response:
    if len(parts) < 4 or parts[0] != "calendars":
        return Response(status_code=400)
    ensure_cal(parts[1], parts[2])
    body = await req.body()
    ep = ev_file(parts[1], parts[2], parts[3])
    existed = ep.exists()
    ep.write_bytes(body)
    log.info("PUT /calendars/%s/%s/%s (%d bytes)", parts[1], parts[2], parts[3], len(body))
    return Response(status_code=204 if existed else 201, headers={"ETag": etag(body)})


def handle_delete(_req: Request, parts: list[str]) -> Response:
    if len(parts) < 4 or parts[0] != "calendars":
        return Response(status_code=400)
    ep = ev_file(parts[1], parts[2], parts[3])
    if not ep.exists():
        return Response(status_code=404)
    ep.unlink()
    log.info("DELETE /calendars/%s/%s/%s", parts[1], parts[2], parts[3])
    return Response(status_code=204)


# ── main dispatcher ──────────────────────────────────────────────────────────

ALL_METHODS = ["GET", "HEAD", "POST", "PUT", "DELETE",
               "OPTIONS", "PROPFIND", "REPORT", "MKCALENDAR"]


async def dispatch(req: Request) -> Response:
    if not auth_ok(req):
        return unauth()

    method = req.method
    parts  = [p for p in req.url.path.strip("/").split("/") if p]

    log.info("%s /%s  depth=%s", method, "/".join(parts), req.headers.get("depth", "-"))

    if method == "OPTIONS":
        return handle_options(req)
    if method == "PROPFIND":
        return await handle_propfind(req, parts)
    if method == "REPORT":
        return await handle_report(req, parts)
    if method == "MKCALENDAR":
        return handle_mkcalendar(req, parts)
    if method in ("GET", "HEAD"):
        return handle_get(req, parts)
    if method == "PUT":
        return await handle_put(req, parts)
    if method == "DELETE":
        return handle_delete(req, parts)
    return Response(status_code=405)


app = Starlette(routes=[
    Route("/",           dispatch, methods=ALL_METHODS),
    Route("/{path:path}", dispatch, methods=ALL_METHODS),
])
