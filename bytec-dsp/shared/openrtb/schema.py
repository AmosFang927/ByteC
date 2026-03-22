"""
OpenRTB 2.5 Pydantic schema definitions.
Covers the subset used by ByteC DSP (bid request/response cycle).
Spec reference: https://www.iab.com/wp-content/uploads/2016/03/OpenRTB-API-Specification-Version-2-5-FINAL.pdf
"""

from __future__ import annotations

from enum import IntEnum
from typing import Any, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class BannerAdType(IntEnum):
    XHTML_TEXT = 1
    XHTML_BANNER = 2
    JAVASCRIPT = 3
    IFRAME = 4


class APIFramework(IntEnum):
    VPAID_1 = 1
    VPAID_2 = 2
    MRAID_1 = 3
    ORMMA = 4
    MRAID_2 = 5


class DeviceType(IntEnum):
    MOBILE_TABLET = 1
    PERSONAL_COMPUTER = 2
    CONNECTED_TV = 3
    PHONE = 4
    TABLET = 5
    CONNECTED_DEVICE = 6
    SET_TOP_BOX = 7


class NoBidReasonCode(IntEnum):
    UNKNOWN_ERROR = 0
    TECHNICAL_ERROR = 1
    INVALID_REQUEST = 2
    KNOWN_WEB_SPIDER = 3
    SUSPECTED_NON_HUMAN_TRAFFIC = 4
    CLOUD_OR_DATA_CENTER = 5
    UNSUPPORTED_DEVICE = 6
    BLOCKED_PUBLISHER = 7
    UNMATCHED_USER = 8


# ---------------------------------------------------------------------------
# Nested request objects
# ---------------------------------------------------------------------------

class Format(BaseModel):
    w: Optional[int] = None
    h: Optional[int] = None


class Banner(BaseModel):
    format: Optional[list[Format]] = None
    w: Optional[int] = None
    h: Optional[int] = None
    btype: Optional[list[int]] = None      # blocked creative types
    battr: Optional[list[int]] = None      # blocked creative attributes
    pos: Optional[int] = None             # ad position (1=above fold)
    api: Optional[list[int]] = None
    ext: Optional[dict[str, Any]] = None


class Video(BaseModel):
    mimes: list[str]
    minduration: Optional[int] = None
    maxduration: Optional[int] = None
    protocols: Optional[list[int]] = None
    w: Optional[int] = None
    h: Optional[int] = None
    linearity: Optional[int] = None
    battr: Optional[list[int]] = None
    ext: Optional[dict[str, Any]] = None


class Imp(BaseModel):
    """A single ad impression opportunity."""
    id: str
    banner: Optional[Banner] = None
    video: Optional[Video] = None
    displaymanager: Optional[str] = None
    displaymanagerver: Optional[str] = None
    instl: int = 0                          # interstitial flag
    tagid: Optional[str] = None
    bidfloor: float = 0.0                   # minimum CPM bid
    bidfloorcur: str = "USD"
    secure: Optional[int] = None
    ext: Optional[dict[str, Any]] = None


class Publisher(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    cat: Optional[list[str]] = None
    domain: Optional[str] = None
    ext: Optional[dict[str, Any]] = None


class App(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    bundle: Optional[str] = None           # e.g. "com.example.app"
    domain: Optional[str] = None
    storeurl: Optional[str] = None
    cat: Optional[list[str]] = None        # IAB content categories
    ver: Optional[str] = None
    paid: Optional[int] = None
    publisher: Optional[Publisher] = None
    ext: Optional[dict[str, Any]] = None


class Site(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    domain: Optional[str] = None
    cat: Optional[list[str]] = None
    publisher: Optional[Publisher] = None
    ext: Optional[dict[str, Any]] = None


class Geo(BaseModel):
    lat: Optional[float] = None
    lon: Optional[float] = None
    type: Optional[int] = None
    country: Optional[str] = None          # ISO 3166-1 alpha-3
    region: Optional[str] = None
    city: Optional[str] = None
    zip: Optional[str] = None
    ext: Optional[dict[str, Any]] = None


class Device(BaseModel):
    ua: Optional[str] = None               # user agent string
    geo: Optional[Geo] = None
    ip: Optional[str] = None
    devicetype: Optional[int] = None       # see DeviceType enum
    make: Optional[str] = None
    model: Optional[str] = None
    os: Optional[str] = None
    osv: Optional[str] = None
    language: Optional[str] = None
    carrier: Optional[str] = None
    connectiontype: Optional[int] = None
    ifa: Optional[str] = None              # IDFA / GAID
    ext: Optional[dict[str, Any]] = None


class User(BaseModel):
    id: Optional[str] = None
    buyeruid: Optional[str] = None
    yob: Optional[int] = None
    gender: Optional[str] = None
    keywords: Optional[str] = None
    ext: Optional[dict[str, Any]] = None


class BidRequest(BaseModel):
    """OpenRTB 2.5 BidRequest — top-level object sent by SSP to DSP."""
    id: str
    imp: list[Imp]
    site: Optional[Site] = None
    app: Optional[App] = None
    device: Optional[Device] = None
    user: Optional[User] = None
    test: int = 0                          # 1 = test mode (no billing)
    at: int = 2                            # auction type: 1=first price, 2=second price
    tmax: Optional[int] = None             # max time for DSP to respond (ms)
    wseat: Optional[list[str]] = None      # whitelisted buyer seats
    bcat: Optional[list[str]] = None       # blocked IAB categories
    badv: Optional[list[str]] = None       # blocked advertiser domains
    ext: Optional[dict[str, Any]] = None


# ---------------------------------------------------------------------------
# Bid response objects
# ---------------------------------------------------------------------------

class BidResponseBid(BaseModel):
    """A single bid for one impression."""
    id: str                                # bidder-generated bid ID
    impid: str                             # matches Imp.id from request
    price: float                           # CPM bid in bidfloorcur
    adid: Optional[str] = None            # creative ID
    nurl: Optional[str] = None            # win notice URL
    lurl: Optional[str] = None            # loss notice URL
    adm: Optional[str] = None             # ad markup
    adomain: Optional[list[str]] = None   # advertiser domains
    bundle: Optional[str] = None          # app bundle
    iurl: Optional[str] = None            # image URL for creative preview
    cid: Optional[str] = None             # campaign ID
    crid: Optional[str] = None            # creative ID (DSP-side)
    cat: Optional[list[str]] = None
    w: Optional[int] = None
    h: Optional[int] = None
    ext: Optional[dict[str, Any]] = None


class BidResponseSeatBid(BaseModel):
    bid: list[BidResponseBid]
    seat: Optional[str] = None
    group: int = 0
    ext: Optional[dict[str, Any]] = None


class BidResponse(BaseModel):
    """OpenRTB 2.5 BidResponse — returned by DSP to SSP."""
    id: str                                # mirrors BidRequest.id
    seatbid: Optional[list[BidResponseSeatBid]] = None
    bidid: Optional[str] = None           # optional bidder-generated ID
    cur: str = "USD"
    customdata: Optional[str] = None
    nbr: Optional[int] = None             # no-bid reason code
    ext: Optional[dict[str, Any]] = None

    @classmethod
    def no_bid(cls, request_id: str, reason: NoBidReasonCode = NoBidReasonCode.UNMATCHED_USER) -> "BidResponse":
        """Return an empty (no-bid) response."""
        return cls(id=request_id, nbr=reason.value)
