using System;
using System.Threading;
using System.Threading.Tasks;

namespace AicfTemplateNamespace;

public interface IAicfOperationUseCase
{
    Task<AicfOperationOutput> ExecuteAsync(
        AicfOperationInput input,
        CancellationToken cancellationToken);
}
