using AicfWebApi.Application;
using AicfWebApi.Models.Requests;
using AicfWebApi.Models.Responses;
using Microsoft.AspNetCore.Mvc;

namespace AicfWebApi.Controllers;

[ApiController]
[Route("api/work-items")]
public sealed class WorkItemsController : ControllerBase
{
    [HttpPost]
    public async Task<ActionResult<WorkItemResponse>> Create(
        [FromBody] CreateWorkItemRequest request,
        [FromServices] ICreateWorkItemUseCase useCase,
        CancellationToken cancellationToken)
    {
        if (string.IsNullOrWhiteSpace(request.Title))
            return BadRequest();

        var item = await useCase.ExecuteAsync(
            new CreateWorkItemInput(request.Title), cancellationToken);

        return CreatedAtAction(nameof(Get), new { id = item.Id },
            new WorkItemResponse(item.Id, item.Title));
    }

    [HttpGet("{id:guid}")]
    public async Task<ActionResult<WorkItemResponse>> Get(
        Guid id,
        [FromServices] IGetWorkItemUseCase useCase,
        CancellationToken cancellationToken)
    {
        var item = await useCase.ExecuteAsync(id, cancellationToken);
        if (item is null)
            return NotFound();

        return Ok(new WorkItemResponse(item.Id, item.Title));
    }
}
