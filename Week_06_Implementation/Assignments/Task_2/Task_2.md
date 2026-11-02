# Task 2 Assignment

You are once again going to build a simple agent (much like you did with agentic network a few labs back). But this time, it will just be one agent; we do not need LangChain. Rather, you will focus on building a simple retrieval-augmented-generation (RAG) tool.

Usually, you use RAG when the context you are going to to work with is too large to fit into context window (or your budget). In such cases, you assume that some parts of the context will be enough to complete the task where you'd ideally have access to entire context (e.g. a repository of code).

Your context in this case is the repository you cloned in Task 1. Your agent will be solving coding tasks in that repository. You will want the RAG to provide relevant parts of the repository for the coding tasks.

First, you need split the large context (i.e. the repository) into chunks. Choose chunk size, and implement a method to perform the chunking. Store the chunks in some simple data structure for further processing. Create a short report justifying your chunk size and splitting method.

POINTS AWARDED FOR SUCCESSFUL COMPLETION: 1b

OUTPUT:
A data structure (file?) with chunks of the repository
A python script for chunking the repository
A short report on your desing decisions