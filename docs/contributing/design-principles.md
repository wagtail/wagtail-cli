# Design principles

Here are key considerations for the design of the CLI. Follow this in day-to-day development and decision-making, as outlined in [the CLI roadmap](../ROADMAP.md).

## Principles

### Vision

- Design for simplicity and clarity for users, and also contributors and maintainers as much as possible.
- Consider defaults carefully. Favour safety, predictability, and ease of use.
- Focus on future needs, which likely encompass but go beyond current and past needs.
- In case of conflict, prioritize constituencies of users in this order: Wagtail website users, CLI users, contributors, maintainers. And last of all, theoretical purity.

### Maturity

- The CLI is alpha/pre-alpha prototype software. Avoid breaking compatibility for no reason, but do break it when necessary to improve the design or user experience.
- The CLI is provided as-is with no guarantees. We want to nonetheless prove it works with demos and examples.

### Developer Experience

- Follow idiomatic Click / Typer / Python CLI patterns. More predictable = better.
- Documentation is essential, for everyone. It does not have to be lengthy but it should exist.
- Support automation whenever possible. In CLI design, in tests, and in development workflows.

### Performance

- Optimize for speed and efficiency, but not at the expense of clarity or maintainability.
- Take advantage of caching where it is possible without compromising on clarity or maintainability.

### Security

- Follow best practices across cross-system compatibility, data handling, authentication, authorization / permissions.
- Design for security in our own implementation but also with consideration of dependencies choice, and development workflows.

### Accessibility

- Use clear and descriptive messages, prompts, and error outputs.
- Ensure the CLI input and output works with a wide range of terminal types and assistive technologies.

## Examples in practice

- Support global CLI flags in local commands, for predictable behavior and consistency across different parts of the CLI

## Updating the principles

- Order principles from broadest to most specific scope.
- If unsure about whether a given consideration belongs to the principles, add "Examples in practice" instead.
- Occasionally review the examples to see if they suggest updates or additions to the principles.

## References

- [Wagtail product strategy](https://wagtail.org/product-strategy/)
- [The Zen of Wagtail](https://docs.wagtail.org/en/stable/getting_started/the_zen_of_wagtail.html)
