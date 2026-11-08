using System.Buffers.Binary;
using System.Reflection.PortableExecutable;
using System.Runtime.InteropServices;

namespace Aicf.Dotnet.TestSupport;

internal static class PublishedExecutable
{
    internal static string Require(string? path, string tool, string variable)
    {
        var expected = OperatingSystem.IsWindows() ? $"{tool}.exe" : tool;
        Assert.True(path is not null && Path.IsPathFullyQualified(path) && File.Exists(path) &&
            string.Equals(Path.GetFileName(path), expected, StringComparison.OrdinalIgnoreCase),
            $"Set {variable} to the absolute path of the staged {expected} executable. Selected path: {path}");

        using var executable = File.OpenRead(path!);
        bool matchesHost;
        if (OperatingSystem.IsWindows() && RuntimeInformation.ProcessArchitecture == Architecture.X64)
        {
            using var pe = new PEReader(executable);
            matchesHost = pe.PEHeaders.CoffHeader.Machine == Machine.Amd64 &&
                pe.PEHeaders.PEHeader is not null && !pe.HasMetadata;
        }
        else
        {
            Span<byte> header = stackalloc byte[20];
            executable.ReadExactly(header);
            matchesHost = (OperatingSystem.IsLinux(), OperatingSystem.IsMacOS(), RuntimeInformation.ProcessArchitecture) switch
            {
                (true, _, Architecture.X64) => header[..6].SequenceEqual("\u007fELF\u0002\u0001"u8) &&
                    BinaryPrimitives.ReadUInt16LittleEndian(header[18..]) == 0x3e,
                (_, true, Architecture.Arm64) => BinaryPrimitives.ReadUInt32LittleEndian(header) == 0xfeedfacf &&
                    BinaryPrimitives.ReadUInt32LittleEndian(header[4..]) == 0x0100000c,
                _ => false
            };
        }
        Assert.True(matchesHost, $"The staged {expected} executable does not match the current host ({RuntimeInformation.RuntimeIdentifier}).");
        return path!;
    }
}
