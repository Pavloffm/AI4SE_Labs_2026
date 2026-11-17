# Task 7 Assignment

Alternatively to skills, tools are another way to provide new capabilities to your coding assistant. A commonly used protocol for tools in LLM context is MCP. An MCP server is a catalogue of MCP tools. You can find entire MCP servers online, or you can create or collect existing MCP tools, and create your own MCP servers.

Some say that MCP is the USB-C for tools. That may be far-fetched, but for entire systems, MCP servers are being created as a wrapper for LLM communication. When a legacy system is to be used with a new GUI, a new thin client is created and the legacy system acts as server. Nowadays, when an existing/legacy system is to be used by LLM, an MCP server acts as an interface between the system and LLM.

Note that when you use an MCP server, the catalogue of available MCP tools is usually appended to the context you share with LLM. Therefore, too many MCP tools seriously degrade performance.

Create a simple local MCP server with one simple MCP tool. Submit the files you create to enable this. Make your coding assistant use the tool once to prove it's working.

If your coding assistant does not support this feature, submit instead a super short text about which coding assistant you use and why do you think it does not support this feature, and what alternatives similar to this feature it supports.

## POINTS AWARDED FOR SUCCESSFUL COMPLETION: 0.5b

## OUTPUT:
Files required for your MCP server+tool OR short report why that is not possible and what alternatives your coding assistant has