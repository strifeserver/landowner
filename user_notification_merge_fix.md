I spotted the issue! It was "forgetting" the previous order number between syncs, so the first item of a new batch always showed the total.

I've updated the system to **check the last row of your Google Sheet** first. Now, if the new item belongs to the same order as the last one on the sheet, it will correctly leave the cell blank.

Give it one more sync! 🔄
