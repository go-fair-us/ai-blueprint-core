# Identifying AI Agents on Your Website

*Approaches, standards work, and references for site owners*

Caution: Specifications and vendor documentation in this area change quickly; check the references for current versions.

> **Bottom line.** A website can often tell **which company or product** is behind an automated visit, but generally cannot tell **which AI model** is driving it. There is no widely deployed HTTP standard for model identity. The strongest signal described here is cryptographic: Web Bot Auth lets an operator sign requests so you can verify who sent them. Names in headers and IP addresses can be spoofed or change; behavioral signals indicate likelihood, not proof.

## Approaches at a glance

| Approach | What it tells you | Can it be faked? | Effort for you |
|---|---|---|---|
| 1. User-Agent strings | Vendor and purpose (training crawl, search, user-requested fetch) | Yes, trivially | Very low (read logs) |
| 2. Published IP ranges | Request really came from the vendor’s network | Hard, but lists change and not every vendor publishes them | Low to medium |
| 3. Web Bot Auth signatures | Cryptographic proof of the operator | No, without the operator’s secret key | Low behind a CDN; medium to verify yourself |
| 4. CDN bot management | Classified bot/agent category, verified bots | Depends on the provider’s methods | Low (configuration) |
| 5. Behavioral fingerprinting | Likely automated vs. human | Partly; it is a probability, not proof | Medium to high |
| 6. Asking the agent | Whatever the agent chooses to say | Yes; unreliable and not recommended | Low, but risky |

None of these approaches reliably identifies the underlying model. A single product (for example, a chat assistant) sends the same identity no matter which model the user selected, and agents built by third parties on a model API show the developer’s own identity, not the model provider’s.

## 1. User-Agent strings

Well-behaved AI crawlers and fetchers identify themselves in the User-Agent header and document what each bot is for. Vendors now separate bots by purpose, which lets you allow search and user-requested fetches while blocking training crawls in `robots.txt`. This is the easiest signal to read and the easiest to fake: any client can send any User-Agent, and bots that drive a real browser usually send an ordinary Chrome string.

| Vendor | Bot names | Purpose | Docs |
|---|---|---|---|
| [Anthropic](https://support.claude.com/en/articles/8896518) | `ClaudeBot`, `Claude-SearchBot`, `Claude-User` | Training data collection; search indexing; fetching a page because a user asked Claude | [crawler docs](https://support.claude.com/en/articles/8896518) |
| [OpenAI](https://developers.openai.com/docs/gptbot) | `GPTBot`, `OAI-SearchBot`, `ChatGPT-User`, `OAI-AdsBot` | Training; ChatGPT search; user actions in ChatGPT; ad landing-page checks | [crawler docs](https://developers.openai.com/docs/gptbot) |
| [Perplexity](https://docs.perplexity.ai/docs/resources/perplexity-crawlers) | `PerplexityBot`, `Perplexity-User` | Search indexing; user-requested fetches | [crawler docs](https://docs.perplexity.ai/docs/resources/perplexity-crawlers) |

User-initiated fetchers are treated differently. [OpenAI](https://developers.openai.com/docs/gptbot) notes that robots.txt rules may not apply to ChatGPT-User, and [Perplexity](https://docs.perplexity.ai/docs/resources/perplexity-crawlers) says Perplexity-User generally does not follow robots.txt, because a person asked for that page. Check the linked vendor documentation for current details.

## 2. Published IP ranges

Some vendors publish the IP addresses their bots use, so you can confirm that a request claiming to be a given bot really came from that vendor. Match both the User-Agent and the source IP.

- **OpenAI** publishes [GPTBot](https://openai.com/gptbot.json), [OAI-SearchBot](https://openai.com/searchbot.json), and [ChatGPT-User](https://openai.com/chatgpt-user.json) IP files.
- **Perplexity** publishes [PerplexityBot](https://perplexity.com/perplexitybot.json) and [Perplexity-User](https://perplexity.com/perplexity-user.json) IP files.
- **Anthropic’s** [crawler documentation](https://support.claude.com/en/articles/8896518) describes how to verify its bots; check the current version for IP information.

Limitations: lists change and must be refreshed automatically, cloud IP space can be shared, and IP checks say nothing about traffic that does not claim to be a known bot. Third-party agents run from ordinary cloud or residential addresses.

## 3. [Web Bot Auth](https://datatracker.ietf.org/doc/draft-ietf-webbotauth-httpsig-protocol/) (HTTP Message Signatures)

Web Bot Auth replaces “trust the name tag” with “check the signature.” It builds on [RFC 9421, HTTP Message Signatures](https://www.rfc-editor.org/rfc/rfc9421), a finished IETF standard, and adds a profile for bots and agents. The work began as individual drafts from Cloudflare and is now in the IETF [webbotauth working group](https://datatracker.ietf.org/wg/webbotauth/about/). Its current [protocol draft](https://datatracker.ietf.org/doc/draft-ietf-webbotauth-httpsig-protocol/) and related [architecture](https://www.ietf.org/archive/id/draft-meunier-web-bot-auth-architecture-00.html) and [key-directory drafts](https://www.ietf.org/archive/id/draft-meunier-webbotauth-httpsig-directory-00.html) describe the design.

### How it works

**Keys.** The operator generates a key pair (Cloudflare uses Ed25519) and publishes the public key as a JSON Web Key Set at `/.well-known/http-message-signatures-directory` on its own domain, as described in the [key-directory draft](https://www.ietf.org/archive/id/draft-meunier-webbotauth-httpsig-directory-00.html) and [Cloudflare documentation](https://developers.cloudflare.com/bots/concepts/bot/verified-bots/web-bot-auth/).

**Signing.** Each request carries `Signature`, `Signature-Input` and `Signature-Agent` headers. The signature covers at least the target host (`@authority`), with `created` and `expires` timestamps, a `keyid` (the key’s thumbprint), and the tag `web-bot-auth`; see the [protocol draft](https://datatracker.ietf.org/doc/draft-ietf-webbotauth-httpsig-protocol/) for details. Short validity windows and nonces limit replay.

**Verification.** Your server or CDN fetches the operator’s key directory and checks the signature. If it verifies, the request came from that operator, regardless of the IP address or User-Agent it used.

![How Web Bot Auth works](web-bot-auth-diagram.png)

*Figure 1. Web Bot Auth explained for a non-technical audience. (Keep `web-bot-auth-diagram.png` in the same folder as this file for the image to display.)*

### Status and adoption

The protocol draft adopted by the working group (`draft-ietf-webbotauth-httpsig-protocol`) was last updated in September 2026. Specifications may still change. [Cloudflare's documentation](https://developers.cloudflare.com/bots/concepts/bot/verified-bots/web-bot-auth/) describes its production use of Web Bot Auth to verify bots and “signed agents”; see also its [announcement](https://blog.cloudflare.com/verified-bots-with-cryptography/). If your site is behind Cloudflare, you can write rules against verified-bot fields without implementing signature checks yourself.

> **What it does not do:** it proves the *operator* of the agent, not the model, and it only helps with agents whose operators choose to sign. Unsigned traffic remains unidentified.

## 4. CDN and bot-management services

Content delivery and security providers such as [Cloudflare](https://developers.cloudflare.com/bots/concepts/bot/verified-bots/web-bot-auth/), [Akamai](https://www.akamai.com/products/bot-manager), and [Fastly](https://www.fastly.com/products/bot-management) offer bot-management features. Depending on the provider, these can classify known AI crawlers, verified bots, signed agents, or likely automation, and let you allow, block, rate-limit, or challenge traffic. Providers combine the signals above with network-wide data that a single site cannot see. For sites behind Cloudflare, its documentation explains how to use Web Bot Auth verification.

## 5. Behavioral and browser fingerprinting

Agents that drive a real browser (computer-use agents, AI browser extensions, agentic browsers) look like human visitors at the header level. Timing, navigation patterns, pointer movement, and headless-browser fingerprints can suggest automation. These techniques give a probability rather than proof, produce false positives on real users, and cannot tell you which vendor or model is involved. They are best left to a bot-management provider.

## 6. Asking the agent to identify itself

Some sites hide instructions in pages telling AI agents to report their model, for example by submitting a form or loading a tracking URL. This is not recommended. Models often do not know their exact version, many agents are designed to ignore instructions embedded in web content (this is a form of prompt injection), the answer can be fabricated, and vendors may treat the practice as adversarial. If you want agents to know your policies, publish them openly (robots.txt, terms of use, or emerging declaration formats; see the W3C Introduction Layer group below).

## Standards landscape

### IETF

Bot and agent authentication at the HTTP level is being standardized in the IETF [webbotauth working group](https://datatracker.ietf.org/wg/webbotauth/about/). Its [draft documents](https://datatracker.ietf.org/wg/webbotauth/documents/) include the Web Bot Auth protocol and key-directory work; the [protocol repository](https://github.com/webbotauth/draft-ietf-webbotauth-httpsig-protocol) tracks development.

### W3C

There is no W3C Working Group (formal standards track) on this topic. Several W3C **Community Groups** work on agent identity and related questions. Community Groups are open to anyone, are run by their participants, and do not necessarily represent the views of the W3C Membership or staff.

| Group | Launched | Focus |
|---|---|---|
| [AI Agent Protocol CG](https://www.w3.org/community/agentprotocol/) | 2025 | Open protocols for agents to discover, identify and collaborate across the Web, including an agent identity model and a web-based DID method (did:wba). |
| [Agent Identity Registry Protocol CG](https://www.w3.org/community/agent-identity/) | April 2026 | A DID method for agent identity resolution, an agent credential format based on W3C Verifiable Credentials, and a trust negotiation protocol for cross-organizational agents. |
| [Agent Declaration and Assurance CG](https://www.w3.org/community/adacg/) | June 2026 | Verifiable ways for AI systems to declare their identity, operational boundaries, and alignment constraints. Closest to declaring what an agent is. |
| [Introduction Layer CG](https://www.w3.org/community/intro-layer/2026/08/13/call-for-participation-in-introduction-layer-community-group/) | August 2026 | The reverse direction: a way for a website to declare its identity, purpose, constraints and responsible party to AI agents in a machine-readable form. |

Related work includes NIST's [Software and SI Agent Identity and Authorization project](https://www.nccoe.nist.gov/projects/software-and-si-agent-identity-and-authorization), the OpenID Foundation's [Artificial Intelligence Identity Management Community Group](https://openid.net/cg/artificial-intelligence-identity-management-community-group), and the IETF [WIMSE working group](https://datatracker.ietf.org/wg/wimse/about/). The Agent Identity Registry Protocol CG describes coordination with these and other efforts on its [group page](https://www.w3.org/community/agent-identity/).

## Practical recommendations

For a site that publishes data, a sensible approach today is to:

1. Decide your policy per bot purpose in [robots.txt](https://www.rfc-editor.org/rfc/rfc9309) (training, search, user-requested fetches).
2. Verify claimed bots against published IP ranges or, better, signatures.
3. Let a CDN’s bot management handle verification, signed agents, and unidentified automation.
4. Treat anything unsigned and unverified as unknown rather than trusting its stated name.
5. Watch the [IETF webbotauth drafts](https://datatracker.ietf.org/wg/webbotauth/documents/) and the [W3C Community Groups](https://www.w3.org/community/) if you want to follow or influence work on agent identity.

## References

1. Anthropic. Crawler documentation (ClaudeBot, Claude-SearchBot, Claude-User). <https://support.claude.com/en/articles/8896518>
2. OpenAI. Overview of OpenAI crawlers. <https://developers.openai.com/docs/gptbot>
3. Perplexity. Perplexity Crawlers. <https://docs.perplexity.ai/docs/resources/perplexity-crawlers>
4. IETF. RFC 9421, HTTP Message Signatures. <https://www.rfc-editor.org/rfc/rfc9421>
5. Meunier, T. and Major, S. HTTP Message Signatures for automated traffic (draft-ietf-webbotauth-httpsig-protocol). <https://datatracker.ietf.org/doc/draft-ietf-webbotauth-httpsig-protocol/>
6. Meunier, T. HTTP Message Signatures for automated traffic: Architecture (earlier individual draft). <https://www.ietf.org/archive/id/draft-meunier-web-bot-auth-architecture-00.html>
7. Meunier, T. and Major, S. HTTP Message Signatures Directory. <https://www.ietf.org/archive/id/draft-meunier-webbotauth-httpsig-directory-00.html>
8. Cloudflare. Web Bot Auth (developer documentation). <https://developers.cloudflare.com/bots/concepts/bot/verified-bots/web-bot-auth/>
9. Cloudflare Blog. Message Signatures are now part of our Verified Bots Program. <https://blog.cloudflare.com/verified-bots-with-cryptography/>
10. IETF. Web Bot Auth working group draft repository. <https://github.com/webbotauth/draft-ietf-webbotauth-httpsig-protocol>
11. W3C. AI Agent Protocol Community Group. <https://www.w3.org/community/agentprotocol/>
12. W3C. Agent Identity Registry Protocol Community Group. <https://www.w3.org/community/agent-identity/>
13. W3C. Agent Declaration and Assurance Community Group. <https://www.w3.org/community/adacg/>
14. W3C. Introduction Layer Community Group (call for participation). <https://www.w3.org/community/intro-layer/2026/08/13/call-for-participation-in-introduction-layer-community-group/>
