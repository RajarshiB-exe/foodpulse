def test_contribution_math():
    subtotal=500; discount=50; commission=.20; delivery_fee=30; delivery_cost=35; payment=8
    platform_revenue=subtotal*commission
    contribution=platform_revenue+delivery_fee-delivery_cost-payment
    assert platform_revenue==100
    assert contribution==87
    assert subtotal-discount+delivery_fee==480
