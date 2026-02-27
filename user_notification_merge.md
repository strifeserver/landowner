I've updated the sync logic to handle the "merging" look! 🧩

**How it works:**
The system now checks if an item belongs to the same Order ID/Number as the previous row.
If it does, the **Downpayment** and **Remaining Balance** fields will be left **blank** for the subsequent items, so you only see the total amount **once per order** (on the first item).

This gives a much cleaner look, similar to a merged cell effect. Try syncing again to see the result!
