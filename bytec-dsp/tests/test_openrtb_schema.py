"""Tests for OpenRTB 2.5 Pydantic schema."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from shared.openrtb.schema import (
    BidRequest,
    BidResponse,
    BidResponseBid,
    BidResponseSeatBid,
    NoBidReasonCode,
    Imp,
    Banner,
    App,
    Device,
    Geo,
)


def _make_bid_request(request_id: str = "req-001") -> BidRequest:
    return BidRequest(
        id=request_id,
        imp=[
            Imp(
                id="imp-001",
                bidfloor=0.5,
                bidfloorcur="USD",
                banner=Banner(w=320, h=50),
            )
        ],
        app=App(
            id="app-001",
            bundle="com.example.game",
            cat=["IAB9"],
        ),
        device=Device(
            devicetype=4,
            os="Android",
            geo=Geo(country="US"),
        ),
    )


class TestBidRequestSchema:
    def test_basic_parse(self):
        req = _make_bid_request()
        assert req.id == "req-001"
        assert len(req.imp) == 1
        assert req.imp[0].bidfloor == 0.5

    def test_defaults(self):
        req = _make_bid_request()
        assert req.at == 2        # second-price auction default
        assert req.test == 0      # not test mode

    def test_app_fields(self):
        req = _make_bid_request()
        assert req.app.bundle == "com.example.game"
        assert "IAB9" in req.app.cat

    def test_device_geo(self):
        req = _make_bid_request()
        assert req.device.geo.country == "US"
        assert req.device.os == "Android"

    def test_serialise_roundtrip(self):
        req = _make_bid_request()
        data = req.model_dump()
        req2 = BidRequest.model_validate(data)
        assert req2.id == req.id
        assert req2.imp[0].id == req.imp[0].id

    def test_optional_fields_none(self):
        req = _make_bid_request()
        assert req.site is None
        assert req.user is None
        assert req.tmax is None


class TestBidResponseSchema:
    def test_no_bid(self):
        resp = BidResponse.no_bid("req-001", NoBidReasonCode.UNMATCHED_USER)
        assert resp.id == "req-001"
        assert resp.seatbid is None
        assert resp.nbr == NoBidReasonCode.UNMATCHED_USER.value

    def test_valid_bid_response(self):
        resp = BidResponse(
            id="req-001",
            cur="USD",
            seatbid=[
                BidResponseSeatBid(
                    seat="bytec",
                    bid=[
                        BidResponseBid(
                            id="bid-001",
                            impid="imp-001",
                            price=40.0,
                            cid="campaign-001",
                            crid="creative-001",
                        )
                    ],
                )
            ],
        )
        assert resp.seatbid[0].bid[0].price == 40.0
        assert resp.seatbid[0].seat == "bytec"

    def test_no_bid_technical_error(self):
        resp = BidResponse.no_bid("req-002", NoBidReasonCode.TECHNICAL_ERROR)
        assert resp.nbr == 1
