using SnippetTool;

namespace SnippetTool.UnitTests;

public sealed class ExpansionTests
{
    /// <summary>
    /// Rejects missing, unknown, and invalid parameter values with their respective error codes.
    /// </summary>
    [Theory]
    [InlineData("parameterName", "identifier", null, null, "missing-parameter")]
    [InlineData("parameterName", "identifier", "extra", "value", "unknown-parameter")]
    [InlineData("parameterName", "identifier", "parameterName", "class", "invalid-parameter")]
    [InlineData("returnType", "enum", "returnType", "List<int>", "invalid-parameter")]
    public void Should_reject_invalid_parameter_inputs_when_rendering(
        string name, string kind, string? suppliedName, string? suppliedValue, string expectedCode)
    {
        Dictionary<string, ParameterDefinition> definitions = null!;
        List<Expansion.Part> parts = null!;
        Dictionary<string, string?>? parameters = null;
        Exception? failure = null;

        this.Given(GivenADeclaredPlaceholderAndSuppliedParameters, "a declared placeholder and supplied parameters")
            .When(WhenRenderingThePlaceholder, "rendering the placeholder")
            .Then(ThenReportTheExpectedParameterError, "report the expected parameter error")
            .BDDfy();

        void GivenADeclaredPlaceholderAndSuppliedParameters()
        {
            definitions = new() { [name] = new(kind, null, kind == "enum" ? ["Task<string>", "void"] : null) };
            parts = Expansion.Parse("${" + name + "}", definitions);
            parameters = suppliedName is null ? null : new() { [suppliedName] = suppliedValue };
        }

        void WhenRenderingThePlaceholder() =>
            failure = Record.Exception(() => Expansion.Render(parts, definitions, parameters, 0, "lf"));

        void ThenReportTheExpectedParameterError() =>
            Assert.Equal(expectedCode, Assert.IsType<SnippetError>(failure).Code);
    }

    /// <summary>
    /// Distinguishes undeclared placeholders from malformed placeholder syntax.
    /// </summary>
    [Theory]
    [InlineData("return ${unknown};", "unknown-placeholder")]
    [InlineData("return ${variable;", "invalid-placeholder")]
    public void Should_reject_unknown_or_malformed_placeholders_when_parsing_the_body(string body, string expectedCode)
    {
        Dictionary<string, ParameterDefinition> definitions = null!;
        Exception? failure = null;

        this.Given(GivenOnlyTheVariableDeclaration, "only the variable declaration")
            .When(WhenParsingTheBody, "parsing the body")
            .Then(ThenReportTheExpectedPlaceholderError, "report the expected placeholder error")
            .BDDfy();

        void GivenOnlyTheVariableDeclaration() => definitions = new() { ["variable"] = new("identifier", null, null) };
        void WhenParsingTheBody() => failure = Record.Exception(() => Expansion.Parse(body, definitions));
        void ThenReportTheExpectedPlaceholderError() => Assert.Equal(expectedCode, Assert.IsType<SnippetError>(failure).Code);
    }

    /// <summary>
    /// Rejects an unsupported parameter kind during definition validation.
    /// </summary>
    [Fact]
    public void Should_reject_an_unknown_kind_when_validating_a_parameter_definition()
    {
        // Given
        var definition = new ParameterDefinition("script", null, null);

        // When / Then
        var failure = Assert.Throws<SnippetError>(() => Expansion.ValidateDefinition("comment", definition));
        Assert.Equal("invalid-catalog", failure.Code);
    }

    /// <summary>
    /// Preserves Unicode, literal placeholder text, blank lines, indentation, and the requested CRLF endings.
    /// </summary>
    [Fact]
    public void Should_preserve_unicode_and_literal_placeholders_when_expanding_with_indent_and_crlf()
    {
        const string body = """
            // ${comment}

            if (true) {
                var ${variable} = "$${顯示}";
                return ${variable};
            }
            """;
        const string expected = "    // first\r\n    // second ${verbatim}\r\n\r\n    if (true) {\r\n" +
            "        var result = \"${顯示}\";\r\n        return result;\r\n    }";
        Dictionary<string, ParameterDefinition> definitions = null!;
        Dictionary<string, string?> parameters = null!;
        string? rendered = null;

        this.Given(GivenTheUnicodeBodyParameters, "the unicode body parameters")
            .When(WhenParsingAndExpandingTheBody, "parsing and expanding the body")
            .Then(ThenPreserveTheExactExpandedText, "preserve the exact expanded text")
            .BDDfy();

        void GivenTheUnicodeBodyParameters()
        {
            definitions = new()
            {
                ["variable"] = new("identifier", null, null),
                ["comment"] = new("text", null, null)
            };
            parameters = new()
            {
                ["variable"] = "result",
                ["comment"] = "first\r\n// second ${verbatim}"
            };
        }

        void WhenParsingAndExpandingTheBody() =>
            rendered = Expansion.Render(Expansion.Parse(body, definitions), definitions, parameters, 4, "crlf");

        void ThenPreserveTheExactExpandedText() => Assert.Equal(expected, rendered);
    }
}
