# Priority

## Keywords
* `priority`
    * **Description**: Priority level of the group. The lower the priority, the higher it is on
the playlist. Everything having the same priority with be interleaved together as a single
[priority group](TODO). Anything with different priority will be sorted.
    * **Scope**: Hierarchical
    * **Type**: Integer
    * **Required**: False
    * **Default** Largest possible integer your system architecture supports

## Description

A number representing how to order shows in the playlist. Files with lower priority values are
always placed above files with higher priority values. This should be thought in terms of "This is
my #1 priority show", hence priority 1 files will be placed higher in the playlist before priority
2 files.

If two or more groups of files have the same priority level, then those groups will be interleaved
together into a single "priority group". This "priority group" will exist above or below other
"priority groups" depending on their relative priority levels.

Unless explicitly defined or inherited from other scopes, groups will default to 2^64-1 or 2^32-1
depending on if you're using 64bit or 32bit python, respectively. This means by default, files have
the lowest possible priority, meaning any explicitly defined or inherited priorities will always
be placed above files with undefined priorities.


## Examples

Take the following input yml:

```yaml
locations:
  - name: /my/location/foo
    priority: 1
  - name: /my/location/bar
    priority: 1
  - name: /my/location/baz
    priority: 2
  - name: /my/location/fiz
    priority: 2
  - name: /my/location/terrible
    priority: 999
```

Given the following list of file paths:
```
🔴 /my/location/foo/foo show - 1.mkv
🔴 /my/location/foo/foo show - 2.mkv
🔷 /my/location/bar/bar show - 1.mkv
🔷 /my/location/bar/bar show - 2.mkv
💛 /my/location/baz/baz show - 1.mkv
💛 /my/location/baz/baz show - 2.mkv
🟪 /my/location/fiz/fiz show - 1.mkv
🟪 /my/location/fiz/fiz show - 2.mkv
⭕ /my/location/terible/terrible show - 1.mkv
⭕ /my/location/terible/terrible show - 2.mkv
```

The following playlist order would occur

```
🔷 /my/location/bar/bar show - 1.mkv
🔴 /my/location/foo/foo show - 1.mkv
🔷 /my/location/bar/bar show - 2.mkv
🔴 /my/location/foo/foo show - 2.mkv
💛 /my/location/baz/baz show - 1.mkv
🟪 /my/location/fiz/fiz show - 1.mkv
💛 /my/location/baz/baz show - 2.mkv
🟪 /my/location/fiz/fiz show - 2.mkv
⭕ /my/location/terible/terrible show - 1.mkv
⭕ /my/location/terible/terrible show - 2.mkv
```

Notice how "foo" (🔴) and "bar" (🔷) shows are interleaved together, "baz" (💛) and "fiz" (🟪)
shows are interleaved together, but "foo" (🔴) and "bar" (🔷) shows are not interleaved with
"baz" (💛) and "fiz" (🟪) shows. The two independently interleaved groups were instead prioritized
based on their priority values, with the "foo"/"bar" (🔴/🔷) group prioritized above the
"baz"/"fiz" (💛/🟪) group. "terrible" (⭕) show, meanwhile, is at the very bottom and not
interleaved with anything because no other group shares its priority level.
