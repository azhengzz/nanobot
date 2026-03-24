#!/usr/bin/env python3
"""
JMX File Format Validator

Validates JMeter JMX file format and structure.
Provides detailed error messages for AI to identify and fix issues.
"""

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional

import click


class ValidationError:
    """Represents a validation error with detailed context."""

    def __init__(
        self,
        category: str,
        message: str,
        element: Optional[str] = None,
        line: Optional[int] = None,
        suggestion: Optional[str] = None,
    ):
        self.category = category
        self.message = message
        self.element = element
        self.line = line
        self.suggestion = suggestion

    def to_dict(self) -> dict:
        """Convert error to dictionary for JSON output."""
        return {
            "category": self.category,
            "message": self.message,
            "element": self.element,
            "line": self.line,
            "suggestion": self.suggestion,
        }

    def __str__(self) -> str:
        """Format error for display."""
        parts = [f"[{self.category}]"]
        if self.element:
            parts.append(f" {self.element}")
        if self.line:
            parts.append(f" (line {self.line})")
        parts.append(f": {self.message}")
        if self.suggestion:
            parts.append(f"\n    Suggestion: {self.suggestion}")
        return "".join(parts)


class JMXValidator:
    """Validates JMX file format and basic structure."""

    def __init__(self, jmx_path: Path):
        self.jmx_path = jmx_path
        self.errors: list[ValidationError] = []
        self.warnings: list[ValidationError] = []
        self.root: Optional[ET.Element] = None

    def validate(self) -> bool:
        """Run all validation checks. Returns True if valid."""
        try:
            content = self.jmx_path.read_text(encoding="utf-8")
        except Exception as e:
            self.errors.append(ValidationError(
                category="file",
                message=f"Cannot read file: {e}",
                suggestion="Check file permissions and encoding"
            ))
            return False

        # Check for BOM
        if content.startswith("\ufeff"):
            self.warnings.append(ValidationError(
                category="encoding",
                message="File contains UTF-8 BOM marker",
                suggestion="Consider saving without BOM for better compatibility"
            ))

        # Check XML declaration
        if not content.strip().startswith("<?xml"):
            self.warnings.append(ValidationError(
                category="xml_declaration",
                message="Missing XML declaration",
                suggestion='Add <?xml version="1.0" encoding="UTF-8"?> at the beginning',
            ))

        # Check for empty file
        if not content.strip():
            self.errors.append(ValidationError(
                category="file",
                message="File is empty",
                suggestion="Add JMX content to the file"
            ))
            return False

        # Parse XML
        try:
            self.root = ET.fromstring(content)
        except ET.ParseError as e:
            self._parse_xml_error(str(e))
            return False

        # Run validation checks
        self._validate_root_element()
        self._validate_basic_structure()
        self._validate_hash_tree_pairing()

        return len(self.errors) == 0

    def _parse_xml_error(self, error_msg: str) -> None:
        """Parse XML error message to extract line and context."""
        # ET.ParseError format: "message: line X, column Y"
        line_match = re.search(r"line (\d+)", error_msg)

        line = int(line_match.group(1)) if line_match else None

        # Categorize common XML errors
        category = "xml_syntax"
        suggestion = None

        if "mismatched tag" in error_msg or "not matched" in error_msg:
            category = "xml_structure"
            suggestion = "Check for missing closing tags or incorrect nesting"
        elif "unclosed token" in error_msg:
            category = "xml_syntax"
            suggestion = "Check for missing closing quotes, brackets, or > at end of tag"
        elif "invalid element" in error_msg or "not found" in error_msg:
            category = "xml_structure"
            suggestion = "Verify element names are spelled correctly"
        elif "encoding" in error_msg.lower():
            category = "encoding"
            suggestion = "Ensure file is saved as UTF-8 encoding"
        elif "parse error" in error_msg.lower():
            category = "xml_syntax"
            suggestion = "Check for special characters that need to be escaped (like & < >)"

        self.errors.append(ValidationError(
            category=category,
            message=error_msg,
            line=line,
            suggestion=suggestion,
        ))

    def _validate_root_element(self) -> None:
        """Validate root element is jmeterTestPlan."""
        if self.root is None:
            return

        if self.root.tag != "jmeterTestPlan":
            self.errors.append(ValidationError(
                category="structure",
                message=f"Root element must be 'jmeterTestPlan', found '{self.root.tag}'",
                element=self.root.tag,
                suggestion="Wrap content in <jmeterTestPlan version='1.2'> element",
            ))

    def _validate_basic_structure(self) -> None:
        """Validate basic JMX structure."""
        if self.root is None:
            return

        # Check for hashTree at root level
        root_hash_tree = self.root.find("hashTree")
        if root_hash_tree is None:
            self.errors.append(ValidationError(
                category="structure",
                message="jmeterTestPlan must contain a hashTree child element",
                element="hashTree",
                suggestion='Add <hashTree> element as immediate child of jmeterTestPlan',
            ))
            return

        # Check for TestPlan
        test_plan = root_hash_tree.find("TestPlan")
        if test_plan is None:
            self.errors.append(ValidationError(
                category="structure",
                message="TestPlan element not found inside hashTree",
                element="TestPlan",
                suggestion="Add a <TestPlan> element inside the first hashTree",
            ))

    def _validate_hash_tree_pairing(self) -> None:
        """
        Validate hashTree elements are properly paired.
        In JMX, elements that can contain children should be followed by a hashTree.
        """
        if self.root is None:
            return

        # Check that TestPlan has a following hashTree sibling
        test_plan = self.root.find(".//TestPlan")
        if test_plan is not None:
            parent = self._get_parent(test_plan)
            if parent is not None:
                siblings = list(parent)
                tp_index = siblings.index(test_plan)
                if tp_index + 1 < len(siblings) and siblings[tp_index + 1].tag != "hashTree":
                    self.warnings.append(ValidationError(
                        category="structure",
                        message="TestPlan should be followed by a hashTree element",
                        element="TestPlan",
                        suggestion="Add a <hashTree> element immediately after TestPlan",
                    ))

    def _get_parent(self, elem: ET.Element) -> Optional[ET.Element]:
        """Get parent element of given element."""
        for parent in self.root.iter():
            if elem in list(parent):
                return parent
        return None


@click.group(name="validate_jmx", help="Validate JMeter JMX file format and structure")
def cli():
    """JMX file format validator."""
    pass


@cli.command()
@click.argument("jmx_file", type=click.Path(exists=True), required=True)
@click.option("--json-output", "-j", is_flag=True, help="Output results in JSON format")
def validate(jmx_file: str, json_output: bool):
    """
    Validate a JMeter JMX file.

    Checks for:
    - XML syntax errors (unclosed tags, invalid characters, etc.)
    - Basic JMX structure (jmeterTestPlan, hashTree, TestPlan)
    - hashTree element pairing

    Example: validate_jmx validate test.jmx
    """
    jmx_path = Path(jmx_file).resolve()

    validator = JMXValidator(jmx_path)
    is_valid = validator.validate()

    if json_output:
        result = {
            "file": str(jmx_path),
            "valid": is_valid,
            "errors": [e.to_dict() for e in validator.errors],
            "warnings": [w.to_dict() for w in validator.warnings],
        }
        click.echo(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        _print_summary(validator.errors, validator.warnings, jmx_path)

    sys.exit(0 if is_valid else 1)


def _print_summary(
    errors: list[ValidationError],
    warnings: list[ValidationError],
    jmx_path: Path,
) -> None:
    """Print validation summary."""
    click.echo(f"\nValidating: {jmx_path}\n")

    if not errors and not warnings:
        click.echo(click.style("✓ JMX file is valid!", fg="green"))
        return

    if errors:
        click.echo(click.style(f"✗ Found {len(errors)} error(s):", fg="red", bold=True))
        click.echo()
        for i, error in enumerate(errors, 1):
            click.echo(f"  {i}. {error}")
            click.echo()

    if warnings:
        click.echo(click.style(f"⚠ Found {len(warnings)} warning(s):", fg="yellow", bold=True))
        click.echo()
        for i, warning in enumerate(warnings, 1):
            click.echo(f"  {i}. {warning}")
            click.echo()

    click.echo(f"Total: {len(errors)} error(s), {len(warnings)} warning(s)")


if __name__ == "__main__":
    cli()
