using System.ComponentModel;
using System.Runtime.InteropServices;
using System.Text;
using Microsoft.Win32.SafeHandles;

namespace RefactorTool;

internal static class Paths
{
    public static StringComparer Comparer => OperatingSystem.IsWindows() ? StringComparer.OrdinalIgnoreCase : StringComparer.Ordinal;
    public static bool IsWithin(string path, string directory) => Path.GetRelativePath(directory, path) is var relative &&
        !Path.IsPathRooted(relative) && relative != ".." && !relative.StartsWith(".." + Path.DirectorySeparatorChar, StringComparison.Ordinal);
    public static void RegularFile(string path)
    {
        Data.Require(File.Exists(path), "missing_file", $"Required file is missing: {path}");
        var reparse = FirstReparsePoint(path);
        Data.Require(reparse is null, "linked_path", $"Symbolic/reparse paths are unsupported: {reparse}");
    }
    public static string? FirstReparsePoint(string path)
    {
        for (FileSystemInfo? entry = new FileInfo(path); entry is not null; entry = entry is FileInfo file ? file.Directory : ((DirectoryInfo)entry).Parent)
            if ((entry.Attributes & FileAttributes.ReparsePoint) != 0) return entry.FullName;
        return null;
    }
    public static void RegularDirectory(string path)
    {
        Data.Require(Directory.Exists(path), "missing_directory", $"Plan directory must already exist: {path}");
        for (var directory = new DirectoryInfo(path); directory is not null; directory = directory.Parent)
            Data.Require((directory.Attributes & FileAttributes.ReparsePoint) == 0, "linked_path", $"Symbolic/reparse paths are unsupported: {directory.FullName}");
    }

    public static string CanonicalFile(FileStream stream)
    {
        // Resolve the object reached by this open, including junctions and
        // file links. Do not resolve a path separately from the handle hashed
        // and retained by apply.
        var path = new StringBuilder(512);
        const uint volumeNameNt = 2;
        uint flags = 0;
        while (true)
        {
            var length = GetFinalPathNameByHandle(stream.SafeFileHandle, path, (uint)path.Capacity, flags);
            if (length == 0)
            {
                var error = Marshal.GetLastWin32Error();
                if (flags == 0 && error is 1 or 3 or 50)
                {
                    flags = volumeNameNt;
                    continue;
                }
                throw new IOException($"Cannot resolve the open file path ({error}): {stream.Name}", new Win32Exception(error));
            }
            if (length < path.Capacity) return path.ToString();
            path.EnsureCapacity(checked((int)length + 1));
        }
    }

    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, ExactSpelling = true, SetLastError = true, EntryPoint = "GetFinalPathNameByHandleW")]
    private static extern uint GetFinalPathNameByHandle(SafeFileHandle handle, StringBuilder path, uint capacity, uint flags);
}
