# Global Scope

## Description

The group scope refers to the set of options for a particular group from the
optional list of `groups` from the location scope.

This scope inherits hierarchical options from the location scope, and transitively
inherits options from the global scope, if not overridden by the location scope.
This scope may also override any options from the location scope, taking affect for
the defined group.

In order to use group level options, it is required to use the regex option from the location
scope. This regex must further use a [named capture group](https://docs.python.org/3/howto/regex.html#non-capturing-and-named-groups) of `group`,
e.g. `(?P<group>.+)`, in order to dynamically capture group names from your files. If
these two requirements are not present, any supplied `groups` are silently ignored.

Individual groups apply their options to files based on the group's `name` option.
if the value of `name` is found anywhere within the derived group for a file, case insensitively,
then that group's options are applied to it (i.e. being a case-insensitive
subset of the file's derived group). If multiple group `name` values match a group
associated to a file, then the group defined first takes precedence.

## Supported options

* Unique options
    * name (required)
* Hierarchical options
    * whitelist
    * blacklist
    * priority
    * timed

## Examples

Take the following input yaml
```yaml
priority: 10
locations:
  - name: /my/location/foo
    regex: '(?P<group>.+) - [0-9]+.mkv'
    groups:
      - name: 'AWESOME'
        priority: 1
      - name: 'cool'
        priority: 2
      - name: 'terrible'
        priority: 999
      - name: 'show'
        priority: 3
  - name: /my/location/bar
    groups:
      - name: 'alright'
        priority: 4
  - name: /my/location/baz
    regex: '.+'
    groups:
      - name: 'meh'
        priority: 5
```

Given the following file paths, this is what their priorities will be

* **/my/location/foo/awesome show - 01.mkv**
    * priority: 1
    * `AWESOME` is a case-insensitive subset of `awesome show`
* **/my/location/foo/cool show - 01.mkv**
    * priority: 2
    * `cool` is a case-insensitive subset of `cool show`
* **/my/location/foo/terrible show - 01.mkv**
    * priority: 999
    * `terrible` is a case-insensitive subset of `terrible show`
* **/my/location/foo/good show - 01.mkv**
    * priority: 5
    * `show` is a case-insensitive subset of `good show`
    * does not affect previous files because this is defined after other matching rules
* **/my/location/foo/sick movie.mkv**
    * priority: 10
    * no group name matches `sick movie`, so global priority is inherited
* **/my/location/bar/alright show - 01.mkv**
    * priority: 10
    * no regex is defined, so group options are ignored and inherits global priority
* **/my/location/baz/meh show - 01.mkv**
    * priority: 10
    * no capturing group named `group` is defined in the regex, so group options
are ignored and inherits global priority
