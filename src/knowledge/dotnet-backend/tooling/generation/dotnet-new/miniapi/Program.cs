using AicfMiniApi.Application;
using AicfMiniApi.Domain;
using AicfMiniApi.Infrastructure;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddSingleton<InMemoryWorkItems>();
builder.Services.AddSingleton<IAggregateRepository<WorkItem, Guid>>(
    services => services.GetRequiredService<InMemoryWorkItems>());
builder.Services.AddSingleton<IWorkItemQueries>(
    services => services.GetRequiredService<InMemoryWorkItems>());
builder.Services.AddTransient<ICreateWorkItemUseCase, CreateWorkItemUseCase>();
builder.Services.AddTransient<IGetWorkItemUseCase, GetWorkItemUseCase>();

var app = builder.Build();

app.MapPost("/work-items", async (
    CreateWorkItemRequest request,
    ICreateWorkItemUseCase useCase,
    CancellationToken cancellationToken) =>
{
    if (string.IsNullOrWhiteSpace(request.Title))
        return Results.BadRequest();

    var item = await useCase.ExecuteAsync(
        new CreateWorkItemInput(request.Title), cancellationToken);
    return Results.CreatedAtRoute("GetWorkItem", new { id = item.Id }, item);
});

app.MapGet("/work-items/{id:guid}", async (
    Guid id,
    IGetWorkItemUseCase useCase,
    CancellationToken cancellationToken) =>
{
    var item = await useCase.ExecuteAsync(id, cancellationToken);
    return item is null ? Results.NotFound() : Results.Ok(item);
}).WithName("GetWorkItem");

app.Run();

internal sealed record CreateWorkItemRequest(string? Title);
