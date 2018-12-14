# README.md

SDK READMEs can vary in content, coverage, and length, but should include these sections:

* [Introduction](#introduction)
* [Prerequisites](#prerequisites)
* [Installation](#installation)
* [Authentication](#authentication)
* [Usage](#usage)
* [Examples](#examples)
* [Troubleshooting](#troubleshooting)
* [Next steps](#next-steps)

Use the following general guidelines for each section to ensure consistency and readability.

## Introduction

The introduction appears directly under the title (H1) of your README. Do not use an "Introduction" or "Overview" heading (H2).

* Begin the first sentence with the standard phrase "The `<SDK name>` SDK..."
* Use an active verb after the standard phrase, such as "The Azure Batch SDK contains..." or "The Azure Batch SDK provides..."
* Use the first sentence to describe the functionality of the SDK.
* Use subsequent sentences to provide additional information. Provide enough information so that users of your SDK know whether they can complete their task using the SDK:
  * Include a list of tasks supported by the SDK.
  * Include a link, preferably near the top of the topic, to conceptual content that explains the use of the SDK in more detail.
  * Do not repeat content found in the conceptual topics.

## Prerequisites

Specify all requirements a customer must satisfy in order to use the examples in the README or otherwise use your SDK effectively:

* Azure subscription
* Azure service account
* Framework, interpreter, language version
* External modules, packages, or assemblies

## Installation

Provide step-by-step instructions for obtaining and installing the SDK. Whether it's NuGet, pip, npm, or cloning a GitHub repository, include any information specific to setting an environment for working with the SDK. Customers should be able to [authenticate](#authentication) and test all of the snippets in the [Examples](#examples) section after following the steps or referring to the links in this section.

## Authentication

If your SDK requires authentication for use, such as for Azure services, include instructions and example code needed for initializing and authenticating.

## Usage

The *Usage* section should describe the functionality of the main classes. It should point out the most important and useful classes in the SDK and explain how those classes work together. You can use bulleted lists, tables, code blocks, diagrams (images), and other formatting to organize the information. Provide enough information so that users of your SDK know whether they can complete their task using that SDK.

## Examples

Include code snippets and their descriptions for those operations that most customers will use. Include examples for operations that are complex or otherwise tricky to use. If possible, use the same snippets that your in-code documentation uses. For example, use the same snippets included in an `examples.py` file that Sphinx uses to ingest snippets via its [literalinclude](https://www.sphinx-doc.org/en/1.5/markup/code.html?highlight=code%20examples#includes) directive. These snippets should reside alongside your SDK code, and should be tested in an automated fashion.

## Troubleshooting

Describe common errors and exceptions, how to "unpack" them (if necessary), and include guidance for graceful handling and recovery.

## Next steps

If appropriate, point users to other SDKs that might be useful. Also, if you think there is a good chance that users might stumble across your SDK in error (because they are searching for specific functionality and mistakenly think the SDK provides that functionality), point them to other SDKs they might be looking for.
