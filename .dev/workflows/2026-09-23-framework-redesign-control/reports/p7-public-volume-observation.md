# V2 public-write refusal and F: read-only inventory

The #373 executor reported actual Lesson explain/query success, followed by
create refusal: unsupported / filesystem, "Initial Windows writes require local
NTFS." Later Lesson writes stopped; original output/residue stay worker-owned.
This is a failed public setup, not a Lesson lifecycle pass.

The coordinator independently performed only bounded read-only OS inventory.
No product module was imported, no record/file was created, no volume format,
path policy, public guard or native writer was changed.

| Time / surface | Actual observation |
| --- | --- |
| 2026-09-23T16:12:33+08:00, .NET DriveInfo | F: reports NTFS, Fixed, IsReady=true. CIM inventory was access-denied and is not a successful observation. |
| 2026-09-23T16:14:23+08:00, default restricted execution | GetVolumePathNameW for F:/framework-next returned success and F:/framework-next/ as its root. GetVolumeInformationW on that string returned false, error 144 and empty filesystem, both with optional output pointers null and with them provided. |
| 2026-09-23T16:15:29+08:00, normally approved read-only escalation | Same volume-path result and volume-info failure 144; Path('F:/framework-next').resolve(strict=True) failed WinError 1. This bounded comparison did not remove the observed limitation. |
| 2026-09-23T16:19:42+08:00, direct drive-root inventory | QueryDosDeviceW identifies F: as `\Device\OSFMDisk0`; GetVolumeInformationW on explicit F:/ succeeds and reports NTFS. No native write or alternate-root product call was performed. |

Successful API calls do not give meaningful last-error evidence; only errors
from the failed calls above are used. DriveInfo's NTFS report is not proof that
the public tool's distinct volume-query path succeeds. These observations do
not identify a particular driver defect, prove canonical-path safety, establish
native write/durability behavior or authorize a path/drive fallback.

The explicit drive-root success narrows the difference to the queried path/API
sequence on this host; it does not prove that replacing the returned volume
path with a drive anchor would preserve nested mount, reparse, containment or
identity guarantees. The device mapping is an observation, not a diagnosed
driver defect or an authorization to reconfigure the RAM disk.

Microsoft documents [GetVolumePathNameW](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getvolumepathnamew)
as returning the containing volume mount point; successful return values do not
require the last-error value to be zero. Its [error-code reference](https://learn.microsoft.com/en-us/windows/win32/debug/system-error-codes--0-499-)
identifies error 1 as ERROR_INVALID_FUNCTION and 144 as ERROR_DIR_NOT_ROOT.
These API contracts explain the recorded refusal category; they do not explain
why this host returned that directory string or prove an alternate safe root.

Graph-first inspection of only the current Lesson scripts directory produced
122 nodes / 566 edges / zero skips, with no Git attestation. Exact root HEAD was
c10d874dc658d86ba9e3cf064271ffcfe4a25a14 and product source was unchanged. The
local_write_backend function, source lines 334-372, uses GetVolumePathNameW,
checks local fixed/RAM type, then GetVolumeInformationW; failure or a non-NTFS
answer produces the same refusal. The guard stays unchanged.

Coordinator sent the observations to the original V2 executor with instructions
to retain actual public results, stop repeated shared setup failures and keep
source reasoning / external inventory / executed cases distinct. Distinct
read-only or negative cases may continue where meaningful. Identical native
writer setup is not retried across families solely to reproduce this failure.
All blocked path/policy writes remain with their original owners and approvals.

Next owner: coordinator/P7 after #373's exact return and the original #368
confirmation. Resolve the supported path/volume contract with evidence before
new native trials or root adoption; no silent relaxation, alternate drive or
claim of public/native acceptance.
