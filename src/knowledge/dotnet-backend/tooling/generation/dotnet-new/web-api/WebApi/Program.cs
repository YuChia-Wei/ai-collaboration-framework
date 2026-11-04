using AicfWebApi.Application;
using AicfWebApi.Domain;
using AicfWebApi.Infrastructure;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();
builder.Services.AddSingleton<InMemoryWorkItems>();
builder.Services.AddSingleton<IAggregateRepository<WorkItem, Guid>>(
    services => services.GetRequiredService<InMemoryWorkItems>());
builder.Services.AddSingleton<IWorkItemQueries>(
    services => services.GetRequiredService<InMemoryWorkItems>());
builder.Services.AddTransient<ICreateWorkItemUseCase, CreateWorkItemUseCase>();
builder.Services.AddTransient<IGetWorkItemUseCase, GetWorkItemUseCase>();

var app = builder.Build();

app.MapControllers();
app.Run();
