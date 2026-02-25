# Steps to Run Chatbot with Function Calling and Take Screenshots

## Prerequisites
- You should have the venv activated
- Python 3.13 and all dependencies installed (from requirements.txt)

## Step 1: Generate the Sample Database

In the activated venv, run:
```powershell
python data/create_sample_db.py
```

Expected output:
```
✓ Sample database created at data/sample.db
  - 10 customers
  - 17 orders

Schema:
  customers: id, name, email, country, signup_date
  orders: id, customer_id, amount, order_date, status
```

## Step 2: Run the Demo/Validation Script (Optional)

To validate everything works:
```powershell
python scripts/demo.py
```

This will test the database module, security checks, and mock chatbot.

## Step 3: Run the Interactive Chatbot in Mock Mode (No Key Needed)

```powershell
python -m src.chatbot.cli --mock
```

Type some queries:
- `How many customers do we have?`
- `Which customers are from Germany?`

Expected: Mock echo responses (no DB access yet).

## Step 4: Run the Interactive Chatbot in Real Mode (Requires API Key)

Make sure you have `.env` set up with your real DIAL key (see instructions in the main README if needed).

```powershell
python -m src.chatbot.cli
```

### Example queries to take screenshots of:

**Screenshot 1: Count Query**
```
User: How many customers do we have?
```
Expected LLM response:
```
Assistant: You have 10 customers in total.
```

**Screenshot 2: Filtered Query**
```
User: Which customers are from the UK?
```
Expected LLM response:
```
Assistant: The customers from the UK are:
- Bob Smith (bob@example.com)
- Grace Lee (grace@example.com)
```

**Screenshot 3: Aggregate Query**
```
User: What is the total revenue from all orders?
```
Expected LLM response:
```
Assistant: The total revenue from all orders is $5,885.25.
```

**Screenshot 4: Join Query**
```
User: Which customers have pending orders?
```
Expected LLM response:
```
Assistant: The following customers have pending orders:
- Alice Johnson
- Bob Smith
- Henry Davis
- Jack Norton
```

**Screenshot 5: Verbose Mode (Shows Function Calls)**
```powershell
python -m src.chatbot.cli -v
```

```
User: How much revenue did we make from customers in Germany?
[Sending to LLM...]
Assistant: Based on the database query, the revenue from customers in Germany is $650.25.
```

## Demonstrating Requirements

Each screenshot should show:

1. **Function Calling** — The LLM internally:
   - Recognizes it needs to query the DB
   - Calls `execute_sql_query(sql)` with a generated SQL statement
   - Receives the result
   - Generates a natural language response

2. **Database Access** — The chatbot:
   - Queries the customers and orders tables
   - Filters, aggregates, and joins data
   - Returns accurate results

3. **Safety** — The function calling module:
   - Only allows SELECT queries
   - Rejects INSERT, UPDATE, DELETE, DROP operations

4. **Natural Language + Database** — The conversation:
   - Users ask questions in English
   - LLM translates to SQL
   - Results are presented in natural language

## Note on Function Calling Visibility

The function calling happens internally and isn't explicitly shown in the assistant's response, but you can observe:
- The chatbot uses real data (not mock)
- The results are specific to your sample DB
- Multiple DB calls may happen for complex questions
- The verbose flag (`-v`) can help show that processing is happening

## Troubleshooting

If the chatbot doesn't work:
1. Check that `.env` exists and has valid credentials (real mode).
2. Check that `data/sample.db` was created (run Step 1 again).
3. Run the demo script to validate all modules (Step 2).
4. Check for error messages in the terminal.

