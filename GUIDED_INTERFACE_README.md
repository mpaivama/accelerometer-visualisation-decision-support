# Decision support for visualising accelerometer-derived movement behaviour data

This folder contains a lightweight local web interface for the decision tree
component of the toolkit.

The interface is deliberately small:

- It asks one plain-language question at a time.
- It hides questions that become irrelevant based on previous answers.
- It automatically fills non-applicable inputs, such as
  `comparison_structure="not_applicable"` when there is no comparison.
- It sends the completed answers to the existing tested Python decision engine
  in `decision_tree.py`.
- It does not generate plots and does not cover model-result visualisation.

## How to Run It

From this folder, run:

```bash
python3 guided_interface.py
```

Then open:

```text
http://127.0.0.1:8765
```

To stop the interface, return to the terminal and press `Control-C`.

## Files

- `guided_interface.py`: local web server, question flow, branch logic, and API.
- `guided_interface/index.html`: page structure.
- `guided_interface/styles.css`: visual styling.
- `guided_interface/app.js`: browser-side interaction.
- `test_guided_interface.py`: tests for branch logic and recommendation calls.

## Development Notes

The recommendation logic should remain in `decision_tree.py`. If the decision
tree later gains new input fields or changes which fields are conditional, edit
the question definitions and branch rules in `guided_interface.py`, then rerun:

```bash
python3 -m unittest test_guided_interface.py test_decision_tree.py test_decision_report.py -v
```
