# Global Scope

## Description

The location scope refers to the set of options for a particular location from the list of
`locations` defined in the global scope.

This scope inherits hierarchical options from
the global scope. This scope may also override any options from the global scope, taking
affect for the defined location.

## Supported options

* Unique options
    * name (required)
    * regex
    * groups
    * disabled
    * additional
* hierarchical options
    * whitelist
    * blacklist
    * priority
    * timed
