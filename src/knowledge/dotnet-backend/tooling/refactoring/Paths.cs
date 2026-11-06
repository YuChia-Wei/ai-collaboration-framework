namespace RefactorTool;

internal static class Paths
{
    public static StringComparer Comparer => OperatingSystem.IsWindows() ? StringComparer.OrdinalIgnoreCase : StringComparer.Ordinal;
    public static bool IsWithin(string path, string directory) => Path.GetRelativePath(directory, path) is var relative &&
        !Path.IsPathRooted(relative) && relative != ".." && !relative.StartsWith(".." + Path.DirectorySeparatorChar, StringComparison.Ordinal);
    public static void RegularFile(string path)
    {
        Data.Require(File.Exists(path), "missing_file", $"Required file is missing: {path}");
        for (FileSystemInfo? entry = new FileInfo(path); entry is not null; entry = entry is FileInfo file ? file.Directory : ((DirectoryInfo)entry).Parent)
            Data.Require((entry.Attributes & FileAttributes.ReparsePoint) == 0, "linked_path", $"Symbolic/reparse paths are unsupported: {entry.FullName}");
        Data.Require((File.GetAttributes(path) & FileAttributes.Directory) == 0, "not_regular_file", $"Expected a regular file: {path}");
    }
    public static void RegularDirectory(string path)
    {
        Data.Require(Directory.Exists(path), "missing_directory", $"Plan directory must already exist: {path}");
        for (var directory = new DirectoryInfo(path); directory is not null; directory = directory.Parent)
            Data.Require((directory.Attributes & FileAttributes.ReparsePoint) == 0, "linked_path", $"Symbolic/reparse paths are unsupported: {directory.FullName}");
    }
}
