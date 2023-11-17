# AssignmentGenerator

A tool for generating assignments comprising several smaller tasks.

## Requirements

pandoc

## Usage

To use, run the program with parameters for the task directory and (optionally) title.

To build an assignment, select one or more tags you want to include, and click the + button when you have selected some tasks to include. Multiple tasks can be selected either one at a time, or many at once. When the "Generate" button is pressed, `assignment.pdf` and `assignment-solved.pdf` files are generated, which include the tasks, and tasks with solutions where applicable, respectively.

## Task format

Each task comprises two files, and an optional solution.

The first file is a json description of the task, e.g.:

```json
{
    "title": "A sum function",
    "difficulty": 1,
    "tags": ["function", "argument", "return"],
    "text": "oppgave1.md",
    "solution": "oppgave1.c"
}
```

The following fields are required:
title - the name of the task, this is inserted into the assignment text
difficulty - the perceived difficulty of the task, used to balance the composition of tasks in a given assignment
tags - some tags that somehow communicate the skills used/required in the task, to ensure the learning outcomes are achieved
text - the filename of the actual task description, in markdown or latex format
solution - (optional) an example solution to the task, which is added to the "assignment-solved.pdf" file

NOTE: The footer and header tags are special, and should only be used for introduction and appendix files.
