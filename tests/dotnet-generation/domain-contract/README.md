# Domain contract regression

Run `dotnet run --project ContractCases.csproj -p:PublishedContractsDir=<verified-dll-directory>`.
Supply ArchPrecept.Contracts.Domain and Domain.EventSourcing 0.0.3-preview DLLs under `domain/lib/net8.0` and `eventsourcing/lib/net8.0`.
Fixtures exercise reconstruction, commit and projector behavior; they are not distributed to downstream projects.
