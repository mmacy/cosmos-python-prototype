# Documenting your SDK

Documentation is important. Often cited by customers as one of their top criterion when evaluating an SDK, complete and current documentation can enable a successful customer that builds a product using your service and espouses the merits of your SDK to colleagues and others.

Or, if your documentation is incomplete or out of date, it can hinder their progress, prevent adoption of your SDK and service, and result in negative public reviews.

Avoid the latter by following a few guiding principles.

## Doc deliverables

There are three types of documentation for an Azure SDK. Two are the responsibility of the product teams, the other is

| Type | Description | Author | Example |
| -- | -- | -- | -- |
| README | `README.md` file in the root of the SDK repository. Ingested by docs.microsoft.com and displayed as the SDK's "landing page."  | SDK author (product team)| [Cosmos DB Python SDK README](../README.md) |
| Reference | API reference documentation for the SDK's types and their members. Auto-generated from the comments in the SDK source code. | SDK author (product team) | |
| Conceptual | | Content developer (docs team) | |

## README

The `README.md` is typically the entry point for your SDK. It's the welcome mat and front door, and should provide the quickest, easiest path for getting up and running with your SDK. It should be as brief as possible but as complete as necessary, enabling SDK users to perform the most common operations with the least amount of friction.

Include these sections in your README:

| Section | Description |
| ------- | ----------- |
| Introduction | |
| Prerequisites | |
| Installation | |
| Authentication | |
| Examples | |
| Troubleshooting | |
| Next steps | |

For a more detailed discussion of each, see the [Azure SDK README template](doc_readme_template.md).

> TIP: See the Cosmos DB Python SDK [README.md](../README.md) for an example of a README that follows this guidance.

## Reference

Reference documentation is generated from the documentation of the types and their members in your code. For example, docstrings in Python and triple-slash (`///`) comments in C#. It enables the generation of the [API reference][docs_api_ref_python] that appears on docs.microsoft.com, and IntelliSense-like hover help in IDEs.

Your in-code documentation...

## Conceptual

"Conceptual documentation" is that which is written by content developers, PMs, and others that describe an Azure service and its features.

<!-- LINKS -->

[docs_api_ref_python]: https://docs.microsoft.com/python/api/overview/azure/?view=azure-python