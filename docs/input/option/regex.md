# Regex

## Keywords
* `regexes`
    * **Description**: A list of named regex definitions to be used elsewhere.
    * **Scope**: Global
    * **Type**: List[Object]
    * **Required**: False
    * **Default**: `null`
    * **Fields**:
        * `name`
            * **Description**: The name the regex is to be referred by
            * **Type**: String
            * **Required**: True
        * `value`
            * **Description**: The regex expression itself
            * **Type**: String
            * **Required**: True
* `regex`
    * **Description**: The name of a predefined regex or a regex expression defined in place.
Used for filtering and group scoping.
    * **Scope**: Hierarchical
        * Group scope not yet supported
    * **Type**: String
    * **Required**: False
    * **Default**: `null`
* `regex-expression`
    * **Description**: Forces the interpretation of `regex` to be a regex expression if `true`
or as a named regex if `false`. If `null`, then `regex` will be interpreted as a named
regex if there is a matching pre-defined regex with that name, else it will be interpreted
as a regex expression.
    * **Scope**: Hierarchical
        * Group scope not yet supported
    * **Type**: Boolean
    * **Required**: False
    * **Default**: `null`

## Description

Filter filenames such that they only enter the playlist if they match the regex expression.
Applies only to the filename and not the full path. This filtering is done on top of any
existing filtering by other options such as `whitelist` and `blacklist`. Files are filtered
out before they're considered for interleaving or other options like `timed`.

You can create a named capture group called `group`, e.g. `(?P<group>.+)` in the
regex expression to [create groups](TODO) for interleaving and
[group scope](/input/scope/group-scope) purposes.

A regex can be forced to be interpreted as a regex expression instead of a named regex by setting
`regex-expression` to `true`. It can be forced to be interpreted as a named regex by
setting it to `false`. It defaults to testing if the value is a named regex first before
assuming it's an expression.

## Examples

**Example 1**

Take the following input yml:

```yaml
regexes:
  - name: simple
    value: '.+ - [0-9]+\.mkv'
locations:
  - name: /my/location/foo
    regex: simple
```

And consider the following list of file paths:

```
🔴 /my/location/foo/foo show - 1.mkv
❌ /my/location/foo/foo show - 2.mp4
🔴 /my/location/foo/foo show - 3.mkv
🔷 /my/location/foo/bar show - 1.mkv
🔷 /my/location/foo/bar show - 2.mkv
🔷 /my/location/foo/bar show - 3.mkv
🟪 /my/location/foo/simple show - 1.mkv
```

The following playlist would be created

```
🔷 /my/location/foo/bar show - 1.mkv
🔷 /my/location/foo/bar show - 2.mkv
🔷 /my/location/foo/bar show - 3.mkv
🔴 /my/location/foo/foo show - 1.mkv
🔴 /my/location/foo/foo show - 3.mkv
🟪 /my/location/foo/simple show - 1.mkv
```

A regex named `simple`, with the value `.+ - [0-9]+\.mkv` is defined. It is then used at the
[location scope](/input/scope/location-scope) `/my/location/foo`.

`foo show - 2.mp4` does not get matched by the regex
due to having a `.mp4` extension and gets filtered out of the playlist. Everything within the
`/my/location/foo` location was then alphabetized by file name.

**Example 2**
Take the following input yml:
```yaml
locations:
  - name: /my/location/foo
    regex:  '.+ - [0-9]+\.mkv'
```

This will be functionally equivalent to Example 1 above. Instead of using a named regex, one is
simply defined where it is used. If the value of `regex` is not found in the list of regex names,
then it is assumed to be a regex expression itself.

**Example 3**
Take the following input yml:

```yaml
regexes:
  - name: simple
    value: '.+ - [0-9]+\.mkv'
locations:
  - name: /my/location/foo
    regex: simple
    regex-expression: true
```

And consider the following list of file paths:

```
🔴 /my/location/foo/foo show - 1.mkv
❌ /my/location/foo/foo show - 2.mp4
🔴 /my/location/foo/foo show - 3.mkv
🔷 /my/location/foo/bar show - 1.mkv
🔷 /my/location/foo/bar show - 2.mkv
🔷 /my/location/foo/bar show - 3.mkv
🟪 /my/location/foo/simple show - 1.mkv
```

The following playlist would be created

```
🟪 /my/location/foo/simple show - 1.mkv
```

`regex-expression` was set to `true`, so `regex: simple` was interpreted as the regex expression
`simple`. Only `simple show - 1.mkv` matches this regex expression, so it is the only thing in the
playlist.

**Example 4**

Take the following input yml:

```yaml
regexes:
  - name: simple
    value: '(?P<group>.+) - [0-9]+\.mkv'
locations:
  - name: /my/location/foo
    regex: simple
```

And consider the following list of file paths:

```
🔴 /my/location/foo/foo show - 1.mkv
❌ /my/location/foo/foo show - 2.mp4
🔴 /my/location/foo/foo show - 3.mkv
🔷 /my/location/foo/bar show - 1.mkv
🔷 /my/location/foo/bar show - 2.mkv
🔷 /my/location/foo/bar show - 3.mkv
```

The following playlist would be created

```
🔷 /my/location/foo/bar show - 1.mkv
🔴 /my/location/foo/foo show - 1.mkv
🔷 /my/location/foo/bar show - 2.mkv
🟪 /my/location/foo/simple show - 1.mkv
🔷 /my/location/foo/bar show - 3.mkv
🔴 /my/location/foo/foo show - 3.mkv
```

Just like the last example, a regex named `simple`, with the value `.+ - [0-9]+\.mkv` is defined.
It is then used at the location scope `/my/location/foo`.

Also like the last example, `foo show - 2.mp4` was filtered out, but this time the regex has
created a `foo show` and `bar show` group due to the named capture group,
and the files in these groups were interlaced after the filtering took place.
