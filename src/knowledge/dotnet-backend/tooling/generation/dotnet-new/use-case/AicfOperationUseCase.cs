using System;
using System.Threading;
using System.Threading.Tasks;

namespace AicfTemplateNamespace;

public sealed class AicfOperationUseCase : IAicfOperationUseCase
{
    public Task<AicfOperationOutput> ExecuteAsync(
        AicfOperationInput input,
        CancellationToken cancellationToken)
    {
        cancellationToken.ThrowIfCancellationRequested();
        ArgumentException.ThrowIfNullOrWhiteSpace(input.Text);
        var text = input.Text.Trim();
        return Task.FromResult(new AicfOperationOutput(text, text.Length));
    }
}
