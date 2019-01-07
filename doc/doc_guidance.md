# Document your SDK

Documentation is critical. Often cited by developers as one of their top criterion when evaluating an SDK, complete and current documentation can enable a successful customer that builds a product using your service and espouses the merits of your SDK to colleagues and others.

Or, if your documentation is incomplete or out of date, it can hinder their progress, prevent adoption of your SDK and service, and result in negative public reviews.

Provide clear, complete, and up-to-date documentation for your SDK to make your customers happy and drive adoption.

## Documentation deliverables

There are three primary types of documentation for an Azure SDK as shown in the following table.

| Type | Description | Owner(s) | Example |
| -- | -- | -- | -- |
| [README](#readme) | `README.md` in the root of the SDK repository. This file is used for:<ul><li>SDK README (GitHub)</li><li>Quickstart (docs.microsoft.com)</li><li>Landing page - SDK reference (docs.microsoft.com)</li><li>Landing page - package distro page (NuGet, PyPi, etc.)</li></ul> | Content developer, product PM | [Cosmos DB Python SDK README](../README.md) |
| [Reference](#reference) | API reference documentation for the SDK's types and their members. Auto-generated from the comments in the SDK source code. | Product team, Azure SDK team | [Cosmos DB Python SDK reference][docs_api_ref_cosmosdb] |
| [Conceptual](#conceptual) | Long-form technical documentation for the service. Concepts, quickstarts, tutorials, and how-tos. | Content developer, product PM, public | [Cosmos DB documentation][azure_docs_cosmos] |

> NOTE: The "Owner(s)" column identifies *typical* ownership for each type--we build the experience and ensure its quality **as one team**.

Here's an overview of how these types of documentation relate to each other for a Python SDK; arrows indicate automatic content ingestion:

![Developer documentation types diagram][doc_diagram]

## README

The `README.md` is the entry point to your SDK. It's the welcome mat and front door, and should provide the quickest, easiest path for getting up and running with your SDK. It should be as brief as possible but as complete as necessary, enabling SDK users to perform the most common operations with the least amount of friction.

Include these sections in your README. For a more detailed discussion of each, see the [Azure SDK README template](doc_readme_template.md).

| Section | Description |
| ------- | ----------- |
| Introduction | Appears directly under the title (H1) of your README. **Do not** use an "Introduction" or "Overview" heading (H2) for this section. |
| Prerequisites | Specify all requirements a customer must satisfy in order to use your SDK effectively. Subscriptions, accounts, packages, versions, etc. |
| Installation | Step-by-step instructions for obtaining and installing the SDK. |
| Authentication | Instructions and example code needed for initializing and authenticating the SDK client with Azure. |
| Usage | Point out the most important and useful classes in the SDK, and briefly explain how those classes work together. |
| Examples | Code snippets and their descriptions for those operations that most customers will use. Include examples for operations that are complex or otherwise tricky to use. |
| Troubleshooting | Describe common errors and exceptions, how to "unpack" them (if necessary), and include guidance for graceful handling and recovery. |
| Next steps | Provide pointers to related SDKs, documentation, or otherwise helpful content in other locations. |

> TIP: See the Cosmos DB Python SDK [README.md](../README.md) for an example of a README that follows this guidance.

## Reference

Reference documentation is generated from the documentation in your code. For example, docstrings in Python and triple-slash (`///`) comments in C#. It enables the generation of the [API reference][docs_api_ref_python] that appears on docs.microsoft.com, and IntelliSense-like hover help in IDEs.

Follow the documentation best practices for the language in which your SDK is written. At a minimum, include the following:

* **All types, their members, and parameters are documented**. Provide typical usage instruction and include pointers to related members or help content.
* **Code snippets** are included for every major and "tricky" operation. The code for these snippets should be:
  * As short and simple as possible, yet as long as necessary to make it easy to use and follow. *Everyone* will copy+paste your snippets into their code.
  * Located alongside your SDK code (in the same repo).
  * Tested in an automated fashion.
  * Ingested into your code automatically via includes. For example, Python's Sphinx supports the [`literalinclude`][sphinx_literalinclude] directive.
* **Return types** are fully documented. Not just its type, but how to use or interact with the returned thing.
* **Exceptions and errors** are fully documented. Your docs should answer questions like:
  * "What errors/exceptions are commonly encountered when using this method?"
  * "How do I gracefully handle and recover from this exception? Best ways for preventing it from occurring in the first place?"
* **Crosslink** between your reference docs, the README, and conceptual docs.
  * Provide links to types/members in the reference documentation from the README and conceptual docs, and vice-versa.
* Code documentation **validation tools** are available for most languages to help validate your in-code documentation--use them! For example, Python docstrings can be validated with [flake8-docstrings][tool_flake8docstrings], [pydocstyle][tool_pydocstyle], and [docformatter][tool_docformatter].

> TIP: See the Cosmos DB Python SDK [API reference][docs_api_ref_cosmosdb] for an example of SDK reference documentation that follows this guidance.

## Conceptual

[Conceptual documentation][azure_docs] is that which is written by content developers, PMs, and others that describe an Azure service and its features. This is the long-form technical content appearing as articles on docs.microsoft.com, and resides in [azure-docs-pr][azure_docs_private] (or [azure-docs][azure_docs_public] for public contributions).

Conceptual docs for each Azure service typically includes these types of articles:

* Overview
* Quickstarts
* Tutorials
* How-tos
* Concepts

See the [Docs Contributor Guide][docs_contrib] for details on contributing conceptual content.

## Next steps

The Open Publishing System (OPS) [Onboarding & Admin Guide][ops_guide] contains extensive details about the docs.microsoft.com publishing pipeline. The following links contain information you might find valuable while you document your SDK.

* [Supported platforms][ops_platforms] - Publishing system toolchain information, including a matrix of the language-native documentation tools used in reference generation (Sphinx for Python, TypeDoc for TypeScript, etc.)
* Documenting code
  * .NET: [Preparing your .NET code for doc generation][ops_how_dotnet]
  * Java: [How to Document Java APIs][ops_how_java]
  * JavaScript/TypeScript: [Documenting JavaScript & TypeScript APIs][ops_how_javascript]
  * Python: [How to document a Python API][ops_how_python]

<!-- LINKS -->

[azure_docs_cosmos]: https://docs.microsoft.com/azure/cosmos-db/
[azure_docs_private]: https://github.com/MicrosoftDocs/azure-docs-pr
[azure_docs_public]: https://github.com/MicrosoftDocs/azure-docs
[azure_docs]: https://docs.microsoft.com/azure/index
[docs_api_ref_cosmosdb]: http://cosmosproto.westus.azurecontainer.io/
[docs_api_ref_python]: https://docs.microsoft.com/python/api/overview/azure/?view=azure-python
[docs_contrib]: https://review.docs.microsoft.com/help/contribute/index?branch=master
[ops_guide]: https://review.docs.microsoft.com/help/onboard/?branch=master
[ops_how_dotnet]: https://review.docs.microsoft.com/help/onboard/admin/reference/dotnet/documenting-api?branch=master
[ops_how_java]: https://review.docs.microsoft.com/help/onboard/admin/reference/java/documenting-api?branch=master
[ops_how_javascript]: https://review.docs.microsoft.com/help/onboard/admin/reference/js-ts/documenting-api?branch=master
[ops_how_python]: https://review.docs.microsoft.com/help/onboard/admin/reference/python/documenting-api?branch=master
[ops_platforms]: https://review.docs.microsoft.com/help/onboard/admin/reference/concepts/platforms?branch=master
[sphinx_literalinclude]: https://www.sphinx-doc.org/en/1.5/markup/code.html?highlight=code%20examples#includes
[tool_docformatter]: https://github.com/PyCQA/pydocstyle
[tool_flake8docstrings]: https://pypi.org/project/flake8-docstrings/
[tool_pydocstyle]: https://pypi.org/project/docformatter/

<!-- images -->
[doc_diagram]: ./media/docs-sdk-properties.png