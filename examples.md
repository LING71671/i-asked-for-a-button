# Usage examples

[中文](examples_zh.md)

## 1. Deliver the requested text

Request: “The export problem is fixed. Write the release note without the cause, and reply with only the note.”

> The export problem is fixed.

Follow-up: “Add that the fix takes effect after restarting the app.”

> The export problem is fixed. Restart the app to apply the fix.

## 2. Write for the reader

Request: “Write an update for the colleague who organizes meeting notes. PDF export works; automatic email is unfinished. I'll send it over on Friday. The implementation uses a queue and SQLite.”

> Meeting notes can now be exported as PDFs. Automatic email is still unfinished. I'll send you the tool to try on Friday.

An engineering handoff would include the queue and storage details needed to maintain it.

## 3. Complete a software change

Request: “Add a filter that shows only unfinished tasks in this to-do app.”

Add the filter to the existing list controls and preserve saved tasks. Check lists with unfinished tasks, all tasks completed, and no tasks. Deliver the working change with the relevant check results.

## 4. Place interface information

Request: “Make an equipment-loan form with equipment, borrower, and return-date fields. There are also detailed borrowing rules.”

Label the fields “Equipment,” “Borrower,” and “Return date.” Enable Save when required values are valid, and place errors beside the affected field. Add a “Borrowing rules” link that opens the full rules without losing the form entries.

## 5. Arrange layout and color

Request: “Place the loan form beside its records on desktop and adapt it for phones. Use a calm palette.”

On desktop, use a shared grid to align the form and records table. On phones, stack the form above the records. Check the page with no records and with long equipment and borrower names; open the status menu to check that its options fit.

Use a neutral background and a restrained accent for actions. Show “On loan” and “Returned” as labels as well as colors. Check text, buttons, focus outlines, selected rows, and the open status menu against their backgrounds. Inspect the desktop and phone layouts for cramped text or large bright areas. See the [color guidance](skills/i-asked-for-a-button/references/color.md) for specific color checks.
