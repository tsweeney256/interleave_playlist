# Blacklist & Whitelist

## Keywords

* `blacklist`
    * **Description**: List of case-insensitive strings not allowed to be in filenames. Filters
files out of the playlist if anything in the blacklist is present in the filename.
    * **Scope**: Hierarchical
    * **Type**: List[String]
    * **Required**: False
    * **Default**: `null`
* `whitelist`
    * **Description**: List of case-insensitive strings that must be present in filenames. Filters
files out of the playlist if nothing in the whitelist is present in the filename.
    * **Scope**: Hierarchical
    * **Type**: List[String]
    * **Required**: False
    * **Default**: `null`

## Description

`blacklist` and `whitelist` are case-insensitive lists of disallowed or allowed substrings,
respectively, to be present in filenames. This filtering is done on top of any existing
filtering such `regex`. Files are filtered out before they're considered for interleaving or
other options like `timed`. Only filenames are considered for filtering, not the full paths.

## Examples

**Example #1**

Take the following input yml:

```yaml
blacklist:
  - 720p
  - 1280x720
locations:
  - name: /my/location/foo/
  - name: /my/location/bar/720p/
```
Given the following file paths, this is what will be placed in the playlist:

* ❌ **/my/location/foo/show (720P).mkv**
    * `720p` is a case-insensitive subset of `show (720P).mkv`
* ❌ **/my/location/foo/show (1280x720).mkv**
    * `1280x720` is a case-insensitive subset of `show (1280x720).mkv`
* ✅ **/my/location/foo/show.avi**
    * nothing in the blacklist is a subset of `show.avi`
* ✅ **/my/location/bar/720p/show.avi**
    * nothing in the blacklist is a subset of `show.avi`, even if the full path contains `720p`

**Example #2**

Take the following input yml:
```yaml
whitelist:
  - mp4
  - mkv
locations:
  - name: /my/location/foo/
  - name: /my/location/bar/mp4/
```

Given the following file paths, this is what will be placed in the playlist:

* ✅ **/my/location/foo/show.MKV**
    * `mkv` is a case-insensitive subset of `show.MKV`
* ✅ **/my/location/foo/show.mp4**
    * `mp4` is a case-insensitive subset of `show.mp4`
* ❌ **/my/location/foo/show.avi**
    * nothing in the whitelist is a subset of `show.avi`
* ❌ **/my/location/bar/mp4/show.avi**
    * nothing in the whitelist is a subset of `show.avi`, even if the full path contains `mp4`
