# Commerce pressure corpus

Canonical thread: seller **Northstar**, staff member **Alice**, buyer **Bob**, Order 17, SKU `lamp-blue`, an external payment provider, and a refund policy. Reuse this thread unless it cannot expose the distinction under test.

Required cases: seller-like isolation without a tenant primitive; exactly one seller; at least one item; oversell and cancellation races; scoped reads and field disclosure; uncertain payment outcome; refund approval; coupon once per buyer; temporary delegation; corrected webhook; exact money; human-readable semantic diff.

