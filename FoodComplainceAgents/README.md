# Food Additive Compliance Agent

## Description

This project is an agent-based solution designed to evaluate the compliance of food additives in products sold in the European Union. It uses a multi-agent approach to parse user queries, evaluate them against a local database of food additives, and provide a clear, formatted output.

## How it Works

The solution is composed of four distinct agents that work together to process a user's query:

1.  **Orchestrator Agent (`orchestrator.py`):** This is the main entry point of the application. It receives the user's query and coordinates the workflow between the other agents.
2.  **Evaluator Agent (`evaluator_agent.py`):** This agent is responsible for the core logic of the evaluation. It takes the structured query from the orchestrator and compares it against a local JSON database (`food_additives_data.json`) of food additive regulations. It uses fuzzy matching to find the relevant ingredient and food category.
3.  **Judge Agent (`judge_agent.py`):** This agent receives the evaluation from the Evaluator Agent and performs a "judgment" on the compliance.
4.  **Output Agent (`output_agent.py`):** This agent takes the final judgment and formats it into a user-friendly table.

## Installation

1.  Clone the repository.
2.  Install the required Python libraries:
    ```bash
    pip install thefuzz
    ```

## Usage

To use the Food Additive Compliance Agent, run the `orchestrator.py` script from the command line with your query as an argument. The query should be in the following format:

```
"Can I use [Ingredient] in [Food Product] at [Concentration] [Unit]?"
```

## Example of a working test

Here is a step-by-step example of how to test the agent with a query that works:

1.  **Open your terminal.**
2.  **Navigate to the project directory:**
    ```bash
    cd /home/student_01_ab8595ac0887/hackathon_project
    ```
3.  **Run the orchestrator with a sample query:**
    ```bash
    python3 orchestrator.py "Can I use E220 in dried apricots at 1500 mg/kg?"
    ```
4.  **Expected Output:**
    The agent will process the query and return a table with the compliance evaluation. Since 1500 mg/kg is within the 2000 mg/kg limit for E220 in dried fruits, the output will be:

    ```
    | Ingredient | Status | Reason | Regulation_Reference |
    |---|---|---|---|
    | E220 (Sulphur dioxide) | ✅ Compliant | Requested concentration 1500 mg/kg is within the maximum limit of 2000 mg/kg for food category 'Dried fruits'. | Reg. (EC) No 1333/2008, Annex II, Category 4.2.2 |
    ```

## Example of a failing test (exceeding the limit)

To see an example of a query that is conditionally allowed because it exceeds the maximum limit, you can run:

```bash
python3 orchestrator.py "Can I use E220 in dried apricots at 2500 mg/kg?"
```

**Expected Output:**

```
| Ingredient | Status | Reason | Regulation_Reference |
|---|---|---|---|
| E220 (Sulphur dioxide) | ⚠️ Conditionally allowed | Requested concentration 2500 mg/kg exceeds the maximum limit of 2000 mg/kg for food category 'Dried fruits'. | Reg. (EC) No 1333/2008, Annex II, Category 4.2.2 |
```