# Merchant & Ordering System Documentation

## 1. Merchant Management Flow

### Purpose

To onboard and manage merchants who can receive orders.

- **Entry Point**: Navigation "Merchants" -> `controllers/MerchantsController.py`
- **View File**: `views/merchants/merchant_form_view.py`
- **Database Table**: `merchants`

### Key Features

- **Order Number Prefix**: Defines the prefix (e.g., "ORD-") for orders generated for this merchant.
- **Order Number Padding**: Defines the number of digits (e.g., 4 -> "ORD-0001").
- **Assigned Users**: Comma-separated list of user IDs who can view orders for this merchant.

### Critical Logic

- **Modification Risk**: Changing `order_number_prefix` or `order_number_padding` will NOT retroactively update existing orders but will affect ALL future orders. This can cause sorting and sequence issues.

---

## 2. Order Creation Flow

### Overview

The "New Order" interface is a complex, POS-style form that writes to multiple tables simultaneously.

- **Entry Point**: `OrdersController.create`
- **View File**: `views/orders/create_order_view.py`
- **Controller Method**: `OrdersController.store(data)`

### Step-by-Step Process

1.  **User Input**: User fills out Customer info, adds Items, optionally adds Payment and Expenses.
2.  **Submission**: Data is bundled into a single dictionary.
3.  **Transaction Execution**: `OrdersController.store` opens a SQLite transaction.
    - **Step 3a**: Insert into `orders` table.
    - **Step 3b**: Insert into `order_items` table (linked to Order ID).
    - **Step 3c**: Insert into `payments` table (if payment added).
    - **Step 3d**: Insert into `expenses` table (if expenses added).
4.  **Commit**: If all steps succeed, the transaction is committed. If ANY fail, it rolls back.

> [!WARNING]
> **Critical Flow**: The atomic transaction in `OrdersController.store` is vital. Do not decouple these inserts. If the Order is saved but Items fail, you will have corrupt data.

---

## 3. Order Update & Synchronization Flow

### Overview

Updates are more complex than creation because they must handle **Synchronization** with the database states of related items (Items, Payments, Expenses).

- **Controller Method**: `OrdersController.update(id, data)`
- **View File**: `views/orders/update_order_view.py`

### The "Smart Sync" Logic

When an order is saved in the "Edit" view, the controller performs a "Diff and Sync" operation:

1.  **Fetch Existing**: Loads current IDs of items/payments/expenses from the DB.
2.  **Compare**: Compares with the incoming list from the UI.
3.  **Action Determination**:
    - **MATCH**: If ID exists in both -> **UPDATE** the record.
    - **NEW**: If ID is missing or new -> **INSERT** a new record.
    - **MISSING**: If ID is in DB but not in UI -> **DELETE** the record.

> [!CAUTION]
> **High Risk**: Modifying the logic inside `OrdersController.update` (specifically the `existing_ids - incoming_ids` logic) can cause **Mass Data Loss** (unintended deletion of line items).

---

## 4. Payment & Status Logic

### Database Columns

- `order_status`: Controlled by `Orders.py` options (Pending, Completed, Cancelled, etc.).
- `payment_status`: Controlled by `Orders.py` options (Unpaid, Partial, Paid).

### Automated Interactions

- Currently, status updates are manual via the UI dropdowns.
- **Future Scope**: Calculating `payment_status` based on `total_amount` vs `sum(payments)` is a planned feature but typically enforced in the View or via a helper service.

---

## 5. Google Sheet Integration (Spreadsheet SyncService)

### Overview

The system performs a one-way sync from the CMS to a Google Sheet.

- **Service**: `services/GoogleSheetService.py`
- **Trigger**: Manual "Sync" button or `sync_unsynced_orders` method.
- **Credentials**: Stored in `settings` table (`google_service_account`, `google_sheet_id`).

### The Sync Process

1.  **Discovery**: Finds orders/items where `spreadsheet_sync = 0`.
2.  **Validation**: Ensures "Orders" and "OrderItems" sheets exist in the target Spreadsheet.
3.  **Push**:
    - **Orders**: Updates exisiting rows (if found by ID) or Appends new rows.
    - **Items**: Appends items.
4.  **Completion**: Updates `spreadsheet_sync = 1` in the database to prevent re-syncing.

### Critical Components

- **`sync_unsynced_order_items`**: This function has complex logic to determining where to insert items and how to group them visually.
- **`ensure_sheet`**: Automatically creates tabs in the Google Sheet if they are missing.

> [!DANGER]
> **DO NOT MODIFY**: The `GoogleSheetService.py` logic handles API rate limits and row index calculation. modifying the `update_or_append_data` method without understanding the 0-indexed vs 1-indexed mapping of the Google Sheets API will corrupt the external spreadsheet.

---

## 6. Data Integrity & Dependencies

### Database Dependencies

- **Orders** depend on **Merchants** (Foreign Key `merchant_id`).
- **Items, Payments, Expenses** depend on **Orders** (Foreign Key `order_id`).
- **Sync Status** depends on the `spreadsheet_sync` flag in ALL these tables.

### Protected Columns

The following columns are managed by the system and should strictly NOT be editable by users directly:

- `id` (Primary Key)
- `created_at`, `updated_at` (Audit)
- `created_by`, `updated_by` (Audit)
- `spreadsheet_sync` (System Flag)
