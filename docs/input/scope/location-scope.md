# Location Scope

## Description

The location scope refers to the set of options for a particular location from the list of
`locations` defined in the global scope.

This scope inherits hierarchical options from
the global scope. This scope may also override any options from the global scope, taking
effect for the defined location.

## Supported options

* Unique options
    * `name`
        * **Description**: Primary absolute directory path Interleave Playlist should
search in for files. Does not search in sub-folders.
        * **Type**: String
        * **Required**: True
    * [`groups`](/input/scope/group-scope)
        * **Description**: Please see section on the [group scope](/input/scope/group-scope)
for more details.
        * **Type**: List[Group]
        * **Required**: False
        * **Default**: `null`
    * `disabled`
        * **Description**: Tells Interleave Playlist to ignore this location rule
        * **Type**: Boolean
        * **Required**: False
        * **Default**: `false`
    * `additional`
        * **Description**: Additional absolute directory paths Interleave Playlist should search
in for files. All files found from these additional directories, as well as the primary directory,
will belong to the same location group. They will share the same set of options defined
in the location group, barring group overrides. Does not search in sub-folders.
        * **Type**: List[String]
        * **Required**: False
        * **Default**: `null`
* hierarchical options
    * [`whitelist`](/input/option/blackwhitelist)
    * [`blacklist`](/input/option/blackwhitelist)
    * [`regex`](/input/option/regex)
    * [`priority`](/input/option/priority)
    * [`weight`](/input/option/weight)
    * [`timed`](/input/option/timed)
